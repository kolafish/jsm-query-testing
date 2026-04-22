package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"math/rand"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

type stringListFlag []string

func (f *stringListFlag) String() string {
	return strings.Join(*f, " | ")
}

func (f *stringListFlag) Set(value string) error {
	*f = append(*f, value)
	return nil
}

type QuerySpec struct {
	ID               string `json:"id"`
	Pattern          string `json:"pattern"`
	Description      string `json:"description"`
	Weight           int    `json:"weight"`
	ExpectedRowCount int    `json:"expected_row_count"`
	SQL              string `json:"sql"`
}

type WarmupResult struct {
	ID               string  `json:"id"`
	Pattern          string  `json:"pattern"`
	Description      string  `json:"description"`
	LatencyMS        float64 `json:"latency_ms"`
	RowCount         int     `json:"row_count"`
	ExpectedRowCount int     `json:"expected_row_count"`
	RowCountMatch    bool    `json:"row_count_match"`
}

type WorkerStats struct {
	Completed          int
	Errors             int
	LatenciesMS        []float64
	PatternCounts      map[string]int
	PatternLatenciesMS map[string][]float64
	RowCountMismatches int
}

type PatternSummary struct {
	ID               string   `json:"id"`
	Pattern          string   `json:"pattern"`
	Description      string   `json:"description"`
	Completed        int      `json:"completed"`
	QPS              float64  `json:"qps"`
	P50MS            *float64 `json:"p50_ms"`
	P95MS            *float64 `json:"p95_ms"`
	P99MS            *float64 `json:"p99_ms"`
	AvgMS            *float64 `json:"avg_ms"`
	Weight           int      `json:"weight"`
	ExpectedRowCount int      `json:"expected_row_count"`
}

type RunSummary struct {
	ElapsedSeconds     float64          `json:"elapsed_seconds"`
	Completed          int              `json:"completed"`
	Errors             int              `json:"errors"`
	RowCountMismatches int              `json:"row_count_mismatches"`
	QPS                float64          `json:"qps"`
	P50MS              *float64         `json:"p50_ms"`
	P95MS              *float64         `json:"p95_ms"`
	P99MS              *float64         `json:"p99_ms"`
	AvgMS              *float64         `json:"avg_ms"`
	PerPattern         []PatternSummary `json:"per_pattern"`
	Concurrency        int              `json:"concurrency"`
}

type Output struct {
	GeneratedAt           string         `json:"generated_at"`
	CorpusPath            string         `json:"corpus_path"`
	Mode                  string         `json:"mode"`
	Database              map[string]any `json:"database"`
	DurationSecondsPerRun int            `json:"duration_seconds_per_run"`
	Warmup                []WarmupResult `json:"warmup"`
	Runs                  []RunSummary   `json:"runs"`
}

func loadCorpus(path string) ([]QuerySpec, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var corpus []QuerySpec
	if err := json.Unmarshal(data, &corpus); err != nil {
		return nil, err
	}
	return corpus, nil
}

func percentile(sortedValues []float64, p float64) *float64 {
	if len(sortedValues) == 0 {
		return nil
	}
	if len(sortedValues) == 1 {
		v := sortedValues[0]
		return &v
	}
	rank := float64(len(sortedValues)-1) * p
	lo := int(math.Floor(rank))
	hi := int(math.Ceil(rank))
	if lo == hi {
		v := sortedValues[lo]
		return &v
	}
	frac := rank - float64(lo)
	v := sortedValues[lo]*(1-frac) + sortedValues[hi]*frac
	return &v
}

func average(values []float64) *float64 {
	if len(values) == 0 {
		return nil
	}
	var sum float64
	for _, v := range values {
		sum += v
	}
	v := sum / float64(len(values))
	return &v
}

func mustCountRows(rows *sql.Rows) (int, error) {
	cols, err := rows.Columns()
	if err != nil {
		return 0, err
	}
	raw := make([]any, len(cols))
	dest := make([]any, len(cols))
	for i := range raw {
		dest[i] = &raw[i]
	}
	count := 0
	for rows.Next() {
		if err := rows.Scan(dest...); err != nil {
			return count, err
		}
		count++
	}
	if err := rows.Err(); err != nil {
		return count, err
	}
	return count, nil
}

func runQuery(ctx context.Context, queryer interface {
	QueryContext(context.Context, string, ...any) (*sql.Rows, error)
}, sqlText string) (int, error) {
	rows, err := queryer.QueryContext(ctx, sqlText)
	if err != nil {
		return 0, err
	}
	defer rows.Close()
	return mustCountRows(rows)
}

func applySessionSQL(ctx context.Context, execer interface {
	ExecContext(context.Context, string, ...any) (sql.Result, error)
}, statements []string) error {
	for _, stmt := range statements {
		if _, err := execer.ExecContext(ctx, stmt); err != nil {
			return err
		}
	}
	return nil
}

func warmup(ctx context.Context, db *sql.DB, corpus []QuerySpec, sessionSQL []string) ([]WarmupResult, error) {
	results := make([]WarmupResult, 0, len(corpus))
	conn, err := db.Conn(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	if err := applySessionSQL(ctx, conn, sessionSQL); err != nil {
		return nil, fmt.Errorf("warmup init sql: %w", err)
	}
	for _, spec := range corpus {
		start := time.Now()
		rowCount, err := runQuery(ctx, conn, spec.SQL)
		if err != nil {
			return nil, fmt.Errorf("warmup %s: %w", spec.ID, err)
		}
		latency := float64(time.Since(start).Microseconds()) / 1000.0
		results = append(results, WarmupResult{
			ID:               spec.ID,
			Pattern:          spec.Pattern,
			Description:      spec.Description,
			LatencyMS:        math.Round(latency*1000) / 1000,
			RowCount:         rowCount,
			ExpectedRowCount: spec.ExpectedRowCount,
			RowCountMatch:    rowCount == spec.ExpectedRowCount,
		})
	}
	return results, nil
}

func worker(ctx context.Context, db *sql.DB, corpus []QuerySpec, cumulative []int, seed int64, stopAt time.Time, sessionSQL []string, out chan<- WorkerStats) {
	stats := WorkerStats{
		PatternCounts:      map[string]int{},
		PatternLatenciesMS: map[string][]float64{},
	}
	conn, err := db.Conn(ctx)
	if err != nil {
		stats.Errors++
		out <- stats
		return
	}
	defer conn.Close()
	if err := applySessionSQL(ctx, conn, sessionSQL); err != nil {
		stats.Errors++
		out <- stats
		return
	}
	rng := rand.New(rand.NewSource(seed))
	for time.Now().Before(stopAt) {
		idx := pickWeighted(rng, cumulative)
		spec := corpus[idx]
		start := time.Now()
		qctx, cancel := context.WithTimeout(ctx, 10*time.Minute)
		rowCount, err := runQuery(qctx, conn, spec.SQL)
		cancel()
		if err != nil {
			stats.Errors++
			continue
		}
		elapsed := float64(time.Since(start).Microseconds()) / 1000.0
		stats.Completed++
		stats.LatenciesMS = append(stats.LatenciesMS, elapsed)
		stats.PatternCounts[spec.ID]++
		stats.PatternLatenciesMS[spec.ID] = append(stats.PatternLatenciesMS[spec.ID], elapsed)
		if rowCount != spec.ExpectedRowCount {
			stats.RowCountMismatches++
		}
	}
	out <- stats
}

func fixedQueryWorker(ctx context.Context, db *sql.DB, spec QuerySpec, stopAt time.Time, sessionSQL []string, limiter chan struct{}, out chan<- WorkerStats) {
	stats := WorkerStats{
		PatternCounts:      map[string]int{},
		PatternLatenciesMS: map[string][]float64{},
	}
	conn, err := db.Conn(ctx)
	if err != nil {
		stats.Errors++
		out <- stats
		return
	}
	defer conn.Close()
	if err := applySessionSQL(ctx, conn, sessionSQL); err != nil {
		stats.Errors++
		out <- stats
		return
	}
	for time.Now().Before(stopAt) {
		limiter <- struct{}{}
		start := time.Now()
		qctx, cancel := context.WithTimeout(ctx, 10*time.Minute)
		rowCount, err := runQuery(qctx, conn, spec.SQL)
		cancel()
		<-limiter
		if err != nil {
			stats.Errors++
			continue
		}
		elapsed := float64(time.Since(start).Microseconds()) / 1000.0
		stats.Completed++
		stats.LatenciesMS = append(stats.LatenciesMS, elapsed)
		stats.PatternCounts[spec.ID]++
		stats.PatternLatenciesMS[spec.ID] = append(stats.PatternLatenciesMS[spec.ID], elapsed)
		if rowCount != spec.ExpectedRowCount {
			stats.RowCountMismatches++
		}
	}
	out <- stats
}

func pickWeighted(rng *rand.Rand, cumulative []int) int {
	target := rng.Intn(cumulative[len(cumulative)-1]) + 1
	return sort.Search(len(cumulative), func(i int) bool { return cumulative[i] >= target })
}

func summarizeRun(corpus []QuerySpec, startedAt, endedAt time.Time, workerStats []WorkerStats, concurrency int) RunSummary {
	totalCompleted := 0
	totalErrors := 0
	totalMismatches := 0
	allLatencies := make([]float64, 0)
	queryMap := make(map[string]QuerySpec, len(corpus))
	for _, spec := range corpus {
		queryMap[spec.ID] = spec
	}
	for _, item := range workerStats {
		totalCompleted += item.Completed
		totalErrors += item.Errors
		totalMismatches += item.RowCountMismatches
		allLatencies = append(allLatencies, item.LatenciesMS...)
	}
	sort.Float64s(allLatencies)
	elapsed := endedAt.Sub(startedAt).Seconds()
	perPattern := make([]PatternSummary, 0, len(corpus))
	for _, spec := range corpus {
		count := 0
		pats := make([]float64, 0)
		for _, item := range workerStats {
			count += item.PatternCounts[spec.ID]
			pats = append(pats, item.PatternLatenciesMS[spec.ID]...)
		}
		sort.Float64s(pats)
		perPattern = append(perPattern, PatternSummary{
			ID:               spec.ID,
			Pattern:          spec.Pattern,
			Description:      spec.Description,
			Completed:        count,
			QPS:              round3(float64(count) / elapsed),
			P50MS:            percentile(pats, 0.50),
			P95MS:            percentile(pats, 0.95),
			P99MS:            percentile(pats, 0.99),
			AvgMS:            average(pats),
			Weight:           spec.Weight,
			ExpectedRowCount: spec.ExpectedRowCount,
		})
	}
	return RunSummary{
		ElapsedSeconds:     round3(elapsed),
		Completed:          totalCompleted,
		Errors:             totalErrors,
		RowCountMismatches: totalMismatches,
		QPS:                round3(float64(totalCompleted) / elapsed),
		P50MS:              percentile(allLatencies, 0.50),
		P95MS:              percentile(allLatencies, 0.95),
		P99MS:              percentile(allLatencies, 0.99),
		AvgMS:              average(allLatencies),
		PerPattern:         perPattern,
		Concurrency:        concurrency,
	}
}

func round3(v float64) float64 {
	return math.Round(v*1000) / 1000
}

func printSummary(warmup []WarmupResult, runs []RunSummary) {
	fmt.Println("Warmup:")
	for _, item := range warmup {
		match := "ok"
		if !item.RowCountMatch {
			match = "mismatch"
		}
		fmt.Printf("  %s: %.3f ms, rows=%d (%s)\n", item.ID, item.LatencyMS, item.RowCount, match)
	}
	fmt.Println("Runs:")
	for _, run := range runs {
		fmt.Printf(
			"  c=%d: qps=%.3f, p50=%s ms, p95=%s ms, p99=%s ms, errors=%d, mismatches=%d\n",
			run.Concurrency,
			run.QPS,
			formatPtr(run.P50MS),
			formatPtr(run.P95MS),
			formatPtr(run.P99MS),
			run.Errors,
			run.RowCountMismatches,
		)
	}
}

func formatPtr(v *float64) string {
	if v == nil {
		return "null"
	}
	return fmt.Sprintf("%.3f", *v)
}

func main() {
	host := flag.String("host", "127.0.0.1", "")
	port := flag.Int("port", 34008, "")
	user := flag.String("user", "root", "")
	password := flag.String("password", "", "")
	database := flag.String("database", "jsm_testcase2", "")
	corpusPath := flag.String("corpus", "bench/dataset_1_qps_corpus.json", "")
	mode := flag.String("mode", "shared-pool", "shared-pool or per-query-pool")
	duration := flag.Int("duration", 20, "seconds per concurrency level")
	outputPath := flag.String("output", "bench/results/latest_dataset_1_qps_benchmark_go.json", "")
	sleepBetween := flag.Int("sleep-between", 0, "seconds to sleep between concurrency levels")
	var sessionSQL stringListFlag
	flag.Var(&sessionSQL, "init-sql", "session SQL to execute once per connection before warmup/benchmark")
	flag.Parse()
	concurrencyArgs := flag.Args()
	if len(concurrencyArgs) == 0 {
		concurrencyArgs = []string{"1", "4", "8"}
	}
	concurrencyLevels := make([]int, 0, len(concurrencyArgs))
	for _, arg := range concurrencyArgs {
		var c int
		if _, err := fmt.Sscanf(arg, "%d", &c); err != nil || c <= 0 {
			fmt.Fprintf(os.Stderr, "invalid concurrency: %s\n", arg)
			os.Exit(2)
		}
		concurrencyLevels = append(concurrencyLevels, c)
	}

	corpus, err := loadCorpus(*corpusPath)
	if err != nil {
		panic(err)
	}
	cumulative := make([]int, 0, len(corpus))
	running := 0
	for _, spec := range corpus {
		running += spec.Weight
		cumulative = append(cumulative, running)
	}

	dsn := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?timeout=10s&readTimeout=10m&writeTimeout=30s&parseTime=true&multiStatements=true", *user, *password, *host, *port, *database)
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		panic(err)
	}
	defer db.Close()
	db.SetMaxOpenConns(max(64, len(concurrencyLevels)*2))
	db.SetMaxIdleConns(max(16, len(concurrencyLevels)))
	db.SetConnMaxLifetime(30 * time.Minute)

	ctx := context.Background()
	warm, err := warmup(ctx, db, corpus, sessionSQL)
	if err != nil {
		panic(err)
	}

	runs := make([]RunSummary, 0, len(concurrencyLevels))
	for _, concurrency := range concurrencyLevels {
		if *mode == "per-query-pool" {
			db.SetMaxOpenConns(len(corpus) + 4)
			db.SetMaxIdleConns(len(corpus))
		} else {
			db.SetMaxOpenConns(concurrency + 4)
			db.SetMaxIdleConns(concurrency)
		}
		stopAt := time.Now().Add(time.Duration(*duration) * time.Second)
		startedAt := time.Now()
		workerCount := concurrency
		if *mode == "per-query-pool" {
			workerCount = len(corpus)
		}
		out := make(chan WorkerStats, workerCount)
		var wg sync.WaitGroup
		if *mode == "per-query-pool" {
			limiter := make(chan struct{}, concurrency)
			for _, spec := range corpus {
				wg.Add(1)
				go func(spec QuerySpec) {
					defer wg.Done()
					fixedQueryWorker(ctx, db, spec, stopAt, sessionSQL, limiter, out)
				}(spec)
			}
		} else {
			for i := 0; i < concurrency; i++ {
				wg.Add(1)
				go func(i int) {
					defer wg.Done()
					worker(ctx, db, corpus, cumulative, int64(20260421+i), stopAt, sessionSQL, out)
				}(i)
			}
		}
		wg.Wait()
		close(out)
		stats := make([]WorkerStats, 0, workerCount)
		for item := range out {
			stats = append(stats, item)
		}
		endedAt := time.Now()
		runs = append(runs, summarizeRun(corpus, startedAt, endedAt, stats, concurrency))
		if *sleepBetween > 0 && concurrency != concurrencyLevels[len(concurrencyLevels)-1] {
			time.Sleep(time.Duration(*sleepBetween) * time.Second)
		}
	}

	out := Output{
		GeneratedAt:           time.Now().UTC().Format(time.RFC3339),
		CorpusPath:            *corpusPath,
		Mode:                  *mode,
		Database:              map[string]any{"host": *host, "port": *port, "user": *user, "database": *database},
		DurationSecondsPerRun: *duration,
		Warmup:                warm,
		Runs:                  runs,
	}

	if err := os.MkdirAll(filepath.Dir(*outputPath), 0o755); err != nil {
		panic(err)
	}
	data, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(*outputPath, data, 0o644); err != nil {
		panic(err)
	}
	fmt.Printf("Wrote benchmark result to %s\n", *outputPath)
	printSummary(warm, runs)
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
