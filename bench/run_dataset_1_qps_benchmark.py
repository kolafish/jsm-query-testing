#!/usr/bin/env python3
import argparse
import json
import math
import random
import statistics
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import mysql.connector


@dataclass
class QuerySpec:
    qid: str
    pattern: str
    description: str
    weight: int
    expected_row_count: int
    sql: str


def load_corpus(path: Path) -> list[QuerySpec]:
    data = json.loads(path.read_text())
    return [
        QuerySpec(
            qid=item["id"],
            pattern=item["pattern"],
            description=item["description"],
            weight=item["weight"],
            expected_row_count=item["expected_row_count"],
            sql=item["sql"],
        )
        for item in data
    ]


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (len(sorted_values) - 1) * p
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return sorted_values[lo]
    frac = rank - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def make_conn(args):
    return mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        autocommit=True,
        use_pure=True,
        connection_timeout=10,
    )


def warmup(args, corpus: list[QuerySpec]) -> list[dict]:
    conn = make_conn(args)
    cursor = conn.cursor()
    results = []
    try:
        for spec in corpus:
            start = time.perf_counter()
            cursor.execute(spec.sql)
            rows = cursor.fetchall()
            elapsed = (time.perf_counter() - start) * 1000
            results.append(
                {
                    "id": spec.qid,
                    "pattern": spec.pattern,
                    "description": spec.description,
                    "latency_ms": round(elapsed, 3),
                    "row_count": len(rows),
                    "expected_row_count": spec.expected_row_count,
                    "row_count_match": len(rows) == spec.expected_row_count,
                }
            )
    finally:
        cursor.close()
        conn.close()
    return results


def worker(args, corpus, cumulative_weights, start_barrier, stop_at, seed, out_list):
    rng = random.Random(seed)
    conn = make_conn(args)
    cursor = conn.cursor()
    local = {
        "completed": 0,
        "errors": 0,
        "latencies_ms": [],
        "pattern_counts": {},
        "pattern_latencies_ms": {},
        "row_count_mismatches": 0,
    }
    try:
        start_barrier.wait()
        while time.perf_counter() < stop_at:
            spec = corpus[rng.choices(range(len(corpus)), cum_weights=cumulative_weights, k=1)[0]]
            start = time.perf_counter()
            try:
                cursor.execute(spec.sql)
                rows = cursor.fetchall()
                elapsed_ms = (time.perf_counter() - start) * 1000
                local["completed"] += 1
                local["latencies_ms"].append(elapsed_ms)
                local["pattern_counts"][spec.qid] = local["pattern_counts"].get(spec.qid, 0) + 1
                local["pattern_latencies_ms"].setdefault(spec.qid, []).append(elapsed_ms)
                if len(rows) != spec.expected_row_count:
                    local["row_count_mismatches"] += 1
            except Exception:
                local["errors"] += 1
    finally:
        cursor.close()
        conn.close()
        out_list.append(local)


def summarize_run(corpus: list[QuerySpec], started_at: float, ended_at: float, worker_stats: list[dict]) -> dict:
    total_completed = sum(item["completed"] for item in worker_stats)
    total_errors = sum(item["errors"] for item in worker_stats)
    total_mismatches = sum(item["row_count_mismatches"] for item in worker_stats)
    latencies = sorted(
        latency
        for item in worker_stats
        for latency in item["latencies_ms"]
    )
    elapsed = ended_at - started_at
    query_map = {spec.qid: spec for spec in corpus}
    per_pattern = []
    for spec in corpus:
        counts = sum(item["pattern_counts"].get(spec.qid, 0) for item in worker_stats)
        pats = sorted(
            latency
            for item in worker_stats
            for latency in item["pattern_latencies_ms"].get(spec.qid, [])
        )
        per_pattern.append(
            {
                "id": spec.qid,
                "pattern": spec.pattern,
                "description": spec.description,
                "completed": counts,
                "qps": round(counts / elapsed, 3) if elapsed else 0.0,
                "p50_ms": round(percentile(pats, 0.50), 3) if pats else None,
                "p95_ms": round(percentile(pats, 0.95), 3) if pats else None,
                "p99_ms": round(percentile(pats, 0.99), 3) if pats else None,
                "avg_ms": round(statistics.fmean(pats), 3) if pats else None,
                "weight": query_map[spec.qid].weight,
                "expected_row_count": query_map[spec.qid].expected_row_count,
            }
        )
    return {
        "elapsed_seconds": round(elapsed, 3),
        "completed": total_completed,
        "errors": total_errors,
        "row_count_mismatches": total_mismatches,
        "qps": round(total_completed / elapsed, 3) if elapsed else 0.0,
        "p50_ms": round(percentile(latencies, 0.50), 3) if latencies else None,
        "p95_ms": round(percentile(latencies, 0.95), 3) if latencies else None,
        "p99_ms": round(percentile(latencies, 0.99), 3) if latencies else None,
        "avg_ms": round(statistics.fmean(latencies), 3) if latencies else None,
        "per_pattern": per_pattern,
    }


def main():
    parser = argparse.ArgumentParser(description="Run a simple concurrent QPS benchmark for dataset 1.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=34006)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="jsm_testcase2")
    parser.add_argument("--corpus", type=Path, default=Path("bench/dataset_1_qps_corpus.json"))
    parser.add_argument("--duration", type=int, default=20, help="seconds per concurrency level")
    parser.add_argument("--concurrency", type=int, nargs="+", default=[1, 4, 8])
    parser.add_argument("--output", type=Path, default=Path("bench/results/latest_dataset_1_qps_benchmark.json"))
    args = parser.parse_args()

    corpus = load_corpus(args.corpus)
    cumulative_weights = []
    running = 0
    for spec in corpus:
        running += spec.weight
        cumulative_weights.append(running)

    warmup_results = warmup(args, corpus)
    runs = []
    for concurrency in args.concurrency:
        worker_stats = []
        barrier = threading.Barrier(concurrency + 1)
        stop_at = time.perf_counter() + args.duration
        threads = [
            threading.Thread(
                target=worker,
                args=(args, corpus, cumulative_weights, barrier, stop_at, 20260421 + i, worker_stats),
                daemon=True,
            )
            for i in range(concurrency)
        ]
        for thread in threads:
            thread.start()
        started_at = time.perf_counter()
        barrier.wait()
        for thread in threads:
            thread.join()
        ended_at = time.perf_counter()
        run = summarize_run(corpus, started_at, ended_at, worker_stats)
        run["concurrency"] = concurrency
        runs.append(run)

    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus_path": str(args.corpus),
        "database": {
            "host": args.host,
            "port": args.port,
            "user": args.user,
            "database": args.database,
        },
        "duration_seconds_per_run": args.duration,
        "warmup": warmup_results,
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"Wrote benchmark result to {args.output}")
    print("Warmup:")
    for item in warmup_results:
        match = "ok" if item["row_count_match"] else "mismatch"
        print(f"  {item['id']}: {item['latency_ms']} ms, rows={item['row_count']} ({match})")
    print("Runs:")
    for run in runs:
        print(
            f"  c={run['concurrency']}: qps={run['qps']}, "
            f"p50={run['p50_ms']} ms, p95={run['p95_ms']} ms, p99={run['p99_ms']} ms, "
            f"errors={run['errors']}, mismatches={run['row_count_mismatches']}"
        )


if __name__ == "__main__":
    main()
