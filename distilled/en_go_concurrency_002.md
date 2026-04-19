# Go Concurrency Patterns

A collection of essential Go concurrency patterns with complete implementations and explanations.

---

## Pattern: Worker Pool with Graceful Shutdown

### Implementation

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Job represents a unit of work
type Job struct {
	ID int
}

// Result represents the processed result
type Result struct {
	JobID int
	Value string
	Err   error
}

// WorkerPool manages a pool of workers
type WorkerPool struct {
	numWorkers int
	jobs       chan Job
	results    chan Result
	wg         sync.WaitGroup
	ctx        context.Context
	cancel     context.CancelFunc
}

// NewWorkerPool creates a new worker pool
func NewWorkerPool(numWorkers int, bufferSize int) *WorkerPool {
	ctx, cancel := context.WithCancel(context.Background())
	return &WorkerPool{
		numWorkers: numWorkers,
		jobs:       make(chan Job, bufferSize),
		results:    make(chan Result, bufferSize),
		ctx:        ctx,
		cancel:     cancel,
	}
}

// worker processes jobs from the jobs channel
func (wp *WorkerPool) worker(id int) {
	defer wp.wg.Done()
	
	for {
		select {
		case <-wp.ctx.Done():
			// Context cancelled - drain remaining jobs if needed
			fmt.Printf("Worker %d: shutting down\n", id)
			return
		case job, ok := <-wp.jobs:
			if !ok {
				// Channel closed
				fmt.Printf("Worker %d: jobs channel closed\n", id)
				return
			}
			
			// Process the job
			fmt.Printf("Worker %d: processing job %d\n", id, job.ID)
			result := Result{
				JobID: job.ID,
				Value: fmt.Sprintf("Processed by worker %d", id),
			}
			
			// Simulate work
			time.Sleep(100 * time.Millisecond)
			
			// Send result with context check
			select {
			case <-wp.ctx.Done():
				fmt.Printf("Worker %d: cancelled while sending result\n", id)
				return
			case wp.results <- result:
			}
		}
	}
}

// Start initializes all workers
func (wp *WorkerPool) Start() {
	for i := 0; i < wp.numWorkers; i++ {
		wp.wg.Add(1)
		go wp.worker(i)
	}
}

// Submit adds a job to the pool
func (wp *WorkerPool) Submit(job Job) error {
	select {
	case <-wp.ctx.Done():
		return fmt.Errorf("worker pool is shutting down")
	case wp.jobs <- job:
		return nil
	}
}

// Shutdown gracefully stops all workers
func (wp *WorkerPool) Shutdown() {
	// Close jobs channel - no more jobs will be accepted
	close(wp.jobs)
	
	// Wait for all workers to finish current jobs
	wp.wg.Wait()
	
	// Close results channel
	close(wp.results)
	
	// Cancel context
	wp.cancel()
}

// Results returns the results channel
func (wp *WorkerPool) Results() <-chan Result {
	return wp.results
}

// StopImmediately cancels all workers immediately
func (wp *WorkerPool) StopImmediately() {
	wp.cancel()
}

func main() {
	// Create a worker pool with 3 workers
	pool := NewWorkerPool(3, 10)
	pool.Start()
	
	// Submit jobs
	go func() {
		for i := 0; i < 10; i++ {
			if err := pool.Submit(Job{ID: i}); err != nil {
				fmt.Printf("Failed to submit job %d: %v\n", i, err)
			}
		}
	}()
	
	// Collect results
	go func() {
		for result := range pool.Results() {
			fmt.Printf("Result: JobID=%d, Value=%s\n", result.JobID, result.Value)
		}
	}()
	
	// Simulate running for a while
	time.Sleep(2 * time.Second)
	
	// Graceful shutdown
	fmt.Println("\nInitiating graceful shutdown...")
	pool.Shutdown()
	fmt.Println("Shutdown complete")
}
```

### Explanation

The Worker Pool pattern manages a fixed number of goroutines (workers) that process jobs from a shared queue. This implementation includes several key features:

1. **Controlled Concurrency**: Limits the number of concurrent goroutines to prevent resource exhaustion
2. **Graceful Shutdown**: Uses context and channel closing to ensure in-flight jobs complete before shutdown
3. **Job Queue**: Buffered channels provide a queue for incoming jobs
4. **Result Collection**: Results channel allows collecting processed outputs

**How Graceful Shutdown Works**:
- `close(wp.jobs)` signals no more jobs will be sent
- Workers finish processing current jobs from the channel
- `sync.WaitGroup` ensures all workers complete before closing results
- Context cancellation handles immediate stop scenarios

**Benefits**:
- Prevents resource exhaustion from unbounded goroutine creation
- Provides backpressure when job queue is full
- Clean shutdown ensures no data loss

---

## Pattern: Pipeline with Stages

### Implementation

```go
package main

import (
	"context"
	"fmt"
)

// Stage 1: Generator - produces initial data
func generator(ctx context.Context, nums ...int) <-chan int {
	out := make(chan int)
	
	go func() {
		defer close(out)
		for _, n := range nums {
			select {
			case <-ctx.Done():
				return
			case out <- n:
			}
		}
	}()
	
	return out
}

// Stage 2: Square - squares each number
func square(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	
	go func() {
		defer close(out)
		for n := range in {
			select {
			case <-ctx.Done():
				return
			case out <- n * n:
			}
		}
	}()
	
	return out
}

// Stage 3: Filter - removes even numbers
func filter(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	
	go func() {
		defer close(out)
		for n := range in {
			if n%2 != 0 { // Keep odd numbers only
				select {
				case <-ctx.Done():
					return
				case out <- n:
				}
			}
		}
	}()
	
	return out
}

// Stage 4: Double - doubles each number
func double(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	
	go func() {
		defer close(out)
		for n := range in {
			select {
			case <-ctx.Done():
				return
			case out <- n * 2:
			}
		}
	}()
	
	return out
}

// Sink: Consumer - processes final results
func consumer(ctx context.Context, in <-chan int) {
	for {
		select {
		case <-ctx.Done():
			fmt.Println("Consumer: context cancelled")
			return
		case n, ok := <-in:
			if !ok {
				fmt.Println("Consumer: channel closed")
				return
			}
			fmt.Printf("Result: %d\n", n)
		}
	}
}

func main() {
	// Create a context with cancellation
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	// Build the pipeline
	// Input: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
	nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	
	// Stage 1: Generate numbers
	genOut := generator(ctx, nums...)
	
	// Stage 2: Square each number (1, 4, 9, 16, 25, 36, 49, 64, 81, 100)
	squareOut := square(ctx, genOut)
	
	// Stage 3: Filter odd numbers (1, 9, 25, 49, 81)
	filterOut := filter(ctx, squareOut)
	
	// Stage 4: Double each number (2, 18, 50, 98, 162)
	doubleOut := double(ctx, filterOut)
	
	// Consume results
	fmt.Println("Processing pipeline:")
	fmt.Println("Input: 1-10")
	fmt.Println("After square: 1, 4, 9, 16, 25, 36, 49, 64, 81, 100")
	fmt.Println("After filter (odd only): 1, 9, 25, 49, 81")
	fmt.Println("After double: 2, 18, 50, 98, 162")
	fmt.Println("\nResults:")
	consumer(ctx, doubleOut)
}
```

### Explanation

The Pipeline pattern chains multiple processing stages together, where each stage is a goroutine that:
- Receives data from an upstream channel
- Processes the data
- Sends results to a downstream channel

**Key Components**:
1. **Generator Stage**: Produces the initial data stream
2. **Processing Stages**: Transform or filter data (square, filter, double)
3. **Consumer/Sink**: Final stage that consumes processed results

**How It Works**:
- Each stage runs in its own goroutine
- Stages communicate through channels
- Data flows through the pipeline one item at a time
- Closing input channel propagates closure through pipeline

**Context Integration**:
- Each stage checks `ctx.Done()` to support cancellation
- Allows graceful shutdown of entire pipeline

**Benefits**:
- Clean separation of concerns
- Easy to add/remove stages
- Natural backpressure through channel blocking
- Concurrent processing across stages

---

## Pattern: Fan-out/Fan-in

### Implementation

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Producer generates jobs
func producer(ctx context.Context, jobs []string) <-chan string {
	out := make(chan string)
	
	go func() {
		defer close(out)
		for _, job := range jobs {
			select {
			case <-ctx.Done():
				return
			case out <- job:
			}
		}
	}()
	
	return out
}

// Worker processes jobs (fan-out targets)
func worker(ctx context.Context, id int, in <-chan string) <-chan string {
	out := make(chan string)
	
	go func() {
		defer close(out)
		for job := range in {
			select {
			case <-ctx.Done():
				return
			default:
				// Simulate work with varying duration
				time.Sleep(time.Duration(100+id*50) * time.Millisecond)
				result := fmt.Sprintf("[Worker %d] Processed: %s", id, job)
				select {
				case <-ctx.Done():
					return
				case out <- result:
				}
			}
		}
	}()
	
	return out
}

// Fan-out: Distributes work to multiple workers
func fanOut(ctx context.Context, in <-chan string, numWorkers int) []<-chan string {
	channels := make([]<-chan string, numWorkers)
	
	for i := 0; i < numWorkers; i++ {
		// Each worker reads from the same input channel
		channels[i] = worker(ctx, i, in)
	}
	
	return channels
}

// Fan-in: Merges multiple channels into one
func fanIn(ctx context.Context, channels ...<-chan string) <-chan string {
	var wg sync.WaitGroup
	out := make(chan string)
	
	// Start a goroutine for each input channel
	output := func(ch <-chan string) {
		defer wg.Done()
		for msg := range ch {
			select {
			case <-ctx.Done():
				return
			case out <- msg:
			}
		}
	}
	
	wg.Add(len(channels))
	for _, ch := range channels {
		go output(ch)
	}
	
	// Close output channel when all inputs are done
	go func() {
		wg.Wait()
		close(out)
	}()
	
	return out
}

// Alternative fanIn using reflect.Select (more complex but handles dynamic channels)
func fanInReflect(ctx context.Context, channels ...<-chan string) <-chan string {
	out := make(chan string)
	
	go func() {
		defer close(out)
		
		// Simple approach: spawn goroutine per channel
		var wg sync.WaitGroup
		for _, ch := range channels {
			wg.Add(1)
			go func(c <-chan string) {
				defer wg.Done()
				for {
					select {
					case <-ctx.Done():
						return
					case msg, ok := <-c:
						if !ok {
							return
						}
						select {
						case <-ctx.Done():
							return
						case out <- msg:
						}
					}
				}
			}(ch)
		}
		wg.Wait()
	}()
	
	return out
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	// Create jobs
	jobs := []string{
		"task-A", "task-B", "task-C", "task-D", "task-E",
		"task-F", "task-G", "task-H", "task-I", "task-J",
	}
	
	// Producer
	fmt.Println("Starting producer...")
	jobChan := producer(ctx, jobs)
	
	// Fan-out to 4 workers
	fmt.Println("Fanning out to 4 workers...")
	workerChans := fanOut(ctx, jobChan, 4)
	
	// Fan-in to merge results
	fmt.Println("Fanning in results...")
	resultChan := fanIn(ctx, workerChans...)
	
	// Consume merged results
	fmt.Println("\nResults:")
	for result := range resultChan {
		fmt.Println(result)
	}
	
	fmt.Println("\nAll jobs completed!")
}
```

### Explanation

The Fan-out/Fan-in pattern distributes work across multiple goroutines and then merges their results.

**Fan-out**:
- Multiple goroutines read from the same input channel
- Work is distributed automatically (each job goes to one available worker)
- Enables parallel processing of independent tasks

**Fan-in**:
- Multiple output channels merge into a single channel
- Uses a goroutine per input channel
- `sync.WaitGroup` coordinates channel closing

**How Distribution Works**:
- Go's channel semantics handle load balancing automatically
- When a worker is ready, it reads from the shared input channel
- Faster workers process more items; slower workers process fewer

**Key Design Points**:
1. Each worker has its own output channel
2. Fan-in merges all output channels
3. Context enables cancellation across all goroutines
4. Proper channel closing prevents goroutine leaks

**Use Cases**:
- CPU-bound tasks that can run in parallel
- I/O operations (API calls, file processing)
- Web scraping with rate limiting per worker

---

## Pattern: Context Timeout Handling

### Implementation

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

var (
	ErrTimeout      = errors.New("operation timed out")
	ErrCancelled    = errors.New("operation cancelled")
	ErrDeadlineExceeded = errors.New("deadline exceeded")
)

// slowOperation simulates a slow operation
func slowOperation(ctx context.Context, duration time.Duration) (string, error) {
	select {
	case <-time.After(duration):
		return "Operation completed successfully", nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

// fetchData simulates fetching data with timeout
func fetchData(ctx context.Context, url string, timeout time.Duration) (string, error) {
	// Create a child context with timeout
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel() // Important: always call cancel to release resources
	
	// Start the operation
	type result struct {
		data string
		err  error
	}
	
	resultChan := make(chan result, 1)
	
	go func() {
		// Simulate slow API call
		time.Sleep(500 * time.Millisecond)
		resultChan <- result{
			data: fmt.Sprintf("Data from %s", url),
			err:  nil,
		}
	}()
	
	// Wait for result or timeout
	select {
	case <-ctx.Done():
		return "", fmt.Errorf("fetch %s: %w", url, ctx.Err())
	case res := <-resultChan:
		return res.data, res.err
	}
}

// parallelFetch fetches multiple URLs with overall timeout
func parallelFetch(ctx context.Context, urls []string, timeout time.Duration) []string {
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()
	
	type result struct {
		url  string
		data string
		err  error
	}
	
	results := make(chan result, len(urls))
	
	// Fetch all URLs in parallel
	for _, url := range urls {
		go func(u string) {
			data, err := fetchWithRetry(ctx, u, 3)
			results <- result{url: u, data: data, err: err}
		}(url)
	}
	
	// Collect results
	var output []string
	for i := 0; i < len(urls); i++ {
		select {
		case <-ctx.Done():
			output = append(output, fmt.Sprintf("Timeout: collected %d/%d results", i, len(urls)))
			return output
		case res := <-results:
			if res.err != nil {
				output = append(output, fmt.Sprintf("%s: Error - %v", res.url, res.err))
			} else {
				output = append(output, fmt.Sprintf("%s: %s", res.url, res.data))
			}
		}
	}
	
	return output
}

// fetchWithRetry fetches with exponential backoff
func fetchWithRetry(ctx context.Context, url string, maxRetries int) (string, error) {
	var lastErr error
	
	for attempt := 0; attempt < maxRetries; attempt++ {
		// Check if context is cancelled before attempting
		select {
		case <-ctx.Done():
			return "", ctx.Err()
		default:
		}
		
		// Simulate fetch
		data, err := mockFetch(ctx, url)
		if err == nil {
			return data, nil
		}
		
		lastErr = err
		
		// Exponential backoff
		backoff := time.Duration(attempt+1) * 100 * time.Millisecond
		select {
		case <-ctx.Done():
			return "", ctx.Err()
		case <-time.After(backoff):
			// Continue to next retry
		}
	}
	
	return "", fmt.Errorf("after %d retries: %w", maxRetries, lastErr)
}

// mockFetch simulates a flaky API
func mockFetch(ctx context.Context, url string) (string, error) {
	select {
	case <-ctx.Done():
		return "", ctx.Err()
	case <-time.After(100 * time.Millisecond):
		// Simulate 70% success rate
		if time.Now().UnixNano()%10 < 7 {
			return fmt.Sprintf("[DATA:%s]", url), nil
		}
		return "", errors.New("temporary failure")
	}
}

// deadlineExample demonstrates using deadline instead of timeout
func deadlineExample() {
	// Set deadline to 2 seconds from now
	deadline := time.Now().Add(2 * time.Second)
	ctx, cancel := context.WithDeadline(context.Background(), deadline)
	defer cancel()
	
	fmt.Println("Deadline example:")
	fmt.Printf("Deadline at: %v\n", deadline.Format("15:04:05.000"))
	
	// Try to complete an operation
	data, err := slowOperation(ctx, 1*time.Second)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Success: %s\n", data)
	}
}

func main() {
	fmt.Println("=== Context Timeout Examples ===\n")
	
	// Example 1: Simple timeout
	fmt.Println("1. Simple timeout (200ms timeout, 100ms operation):")
	ctx1, cancel1 := context.WithTimeout(context.Background(), 200*time.Millisecond)
	defer cancel1()
	
	result, err := slowOperation(ctx1, 100*time.Millisecond)
	fmt.Printf("   Result: %s, Error: %v\n\n", result, err)
	
	// Example 2: Operation exceeds timeout
	fmt.Println("2. Operation exceeds timeout (100ms timeout, 500ms operation):")
	ctx2, cancel2 := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel2()
	
	result, err = slowOperation(ctx2, 500*time.Millisecond)
	fmt.Printf("   Result: %s, Error: %v\n\n", result, err)
	
	// Example 3: Fetch with timeout
	fmt.Println("3. Fetch with timeout:")
	ctx3, cancel3 := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel3()
	
	data, err := fetchData(ctx3, "https://api.example.com/data", 2*time.Second)
	fmt.Printf("   Data: %s, Error: %v\n\n", data, err)
	
	// Example 4: Parallel fetch with overall timeout
	fmt.Println("4. Parallel fetch with overall timeout:")
	urls := []string{"url1", "url2", "url3", "url4"}
	results := parallelFetch(context.Background(), urls, 2*time.Second)
	for _, r := range results {
		fmt.Printf("   %s\n", r)
	}
	
	fmt.Println()
	
	// Example 5: Deadline example
	deadlineExample()
}
```

### Explanation

Context timeout handling is crucial for building resilient systems that respect time constraints.

**Context Types**:
1. **context.WithTimeout**: Set a duration after which context cancels
2. **context.WithDeadline**: Set an absolute time when context cancels
3. **context.WithCancel**: Manual cancellation control

**Key Patterns**:

**Pattern 1: Long-running Operation**
```go
select {
case <-time.After(duration):
    // Operation completed
case <-ctx.Done():
    // Context cancelled/timeout
}
```

**Pattern 2: Propagating Context**
- Pass context as first parameter to all functions
- Child contexts inherit cancellation from parent
- Call `cancel()` to release resources

**Pattern 3: Timeout in goroutines**
- Use result channels with select
- Timeout prevents indefinite blocking

**Best Practices**:
1. Always `defer cancel()` to prevent context leaks
2. Check `ctx.Done()` in loops
3. Handle context errors appropriately (`Canceled`, `DeadlineExceeded`)
4. Use context for cancellation signals, not data storage

---

## Pattern: Rate Limiting Implementation

### Implementation

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// RateLimiter interface
type RateLimiter interface {
	Wait(ctx context.Context) error
	Allow() bool
}

// SimpleRateLimiter - token bucket algorithm
type SimpleRateLimiter struct {
	tokens     chan struct{}
	refillRate time.Duration
	stopChan   chan struct{}
}

// NewSimpleRateLimiter creates a rate limiter
// rate: requests per second
func NewSimpleRateLimiter(rate int) *SimpleRateLimiter {
	rl := &SimpleRateLimiter{
		tokens:     make(chan struct{}, rate),
		refillRate: time.Second / time.Duration(rate),
		stopChan:   make(chan struct{}),
	}
	
	// Initially fill the bucket
	for i := 0; i < rate; i++ {
		rl.tokens <- struct{}{}
	}
	
	// Start refiller
	go rl.refill(rate)
	
	return rl
}

func (rl *SimpleRateLimiter) refill(burst int) {
	ticker := time.NewTicker(rl.refillRate)
	defer ticker.Stop()
	
	for {
		select {
		case <-rl.stopChan:
			return
		case <-ticker.C:
			select {
			case rl.tokens <- struct{}{}:
			default:
				// Bucket full, drop token
			}
		}
	}
}

func (rl *SimpleRateLimiter) Stop() {
	close(rl.stopChan)
}

func (rl *SimpleRateLimiter) Wait(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-rl.tokens:
		return nil
	}
}

func (rl *SimpleRateLimiter) Allow() bool {
	select {
	case <-rl.tokens:
		return true
	default:
		return false
	}
}

// SlidingWindowRateLimiter - sliding window algorithm
type SlidingWindowRateLimiter struct {
	mu          sync.Mutex
	window      time.Duration
	maxRequests int
	requests    []time.Time
}

// NewSlidingWindowRateLimiter creates a sliding window limiter
func NewSlidingWindowRateLimiter(window time.Duration, maxRequests int) *SlidingWindowRateLimiter {
	return &SlidingWindowRateLimiter{
		window:      window,
		maxRequests: maxRequests,
		requests:    make([]time.Time, 0, maxRequests),
	}
}

func (sw *SlidingWindowRateLimiter) Allow() bool {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	
	now := time.Now()
	windowStart := now.Add(-sw.window)
	
	// Remove old requests
	validIdx := 0
	for i, t := range sw.requests {
		if t.After(windowStart) {
			validIdx = i
			break
		}
	}
	sw.requests = sw.requests[validIdx:]
	
	// Check if under limit
	if len(sw.requests) >= sw.maxRequests {
		return false
	}
	
	sw.requests = append(sw.requests, now)
	return true
}

func (sw *SlidingWindowRateLimiter) Wait(ctx context.Context) error {
	for {
		if sw.Allow() {
			return nil
		}
		
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(10 * time.Millisecond):
			// Retry
		}
	}
}

// LeakyBucketRateLimiter - leaky bucket algorithm
type LeakyBucketRateLimiter struct {
	capacity   int
	available  int
	leakRate   time.Duration
	lastLeak   time.Time
	mu         sync.Mutex
}

// NewLeakyBucketRateLimiter creates a leaky bucket limiter
func NewLeakyBucketRateLimiter(capacity int, leakRate time.Duration) *LeakyBucketRateLimiter {
	return &LeakyBucketRateLimiter{
		capacity:  capacity,
		available: capacity,
		leakRate:  leakRate,
		lastLeak:  time.Now(),
	}
}

func (lb *LeakyBucketRateLimiter) leak() {
	now := time.Now()
	elapsed := now.Sub(lb.lastLeak)
	
	// Calculate how many tokens have leaked
	leaked := int(elapsed / lb.leakRate)
	if leaked > 0 {
		lb.available = min(lb.capacity, lb.available+leaked)
		lb.lastLeak = now
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func (lb *LeakyBucketRateLimiter) Allow() bool {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	
	lb.leak()
	
	if lb.available > 0 {
		lb.available--
		return true
	}
	
	return false
}

func (lb *LeakyBucketRateLimiter) Wait(ctx context.Context) error {
	for {
		if lb.Allow() {
			return nil
		}
		
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(lb.leakRate):
			// Retry after leak
		}
	}
}

// API client with rate limiting
type RateLimitedClient struct {
	limiter RateLimiter
	client  *mockHTTPClient
}

type mockHTTPClient struct{}

func (m *mockHTTPClient) Get(url string) string {
	time.Sleep(50 * time.Millisecond) // Simulate network delay
	return fmt.Sprintf("Response from %s", url)
}

func NewRateLimitedClient(limiter RateLimiter) *RateLimitedClient {
	return &RateLimitedClient{
		limiter: limiter,
		client:  &mockHTTPClient{},
	}
}

func (c *RateLimitedClient) Get(ctx context.Context, url string) (string, error) {
	if err := c.limiter.Wait(ctx); err != nil {
		return "", fmt.Errorf("rate limit wait: %w", err)
	}
	return c.client.Get(url), nil
}

func main() {
	fmt.Println("=== Rate Limiting Examples ===\n")
	
	// Example 1: Token Bucket (Simple Rate Limiter)
	fmt.Println("1. Token Bucket Rate Limiter (5 req/sec):")
	limiter1 := NewSimpleRateLimiter(5)
	defer limiter1.Stop()
	
	start := time.Now()
	for i := 0; i < 10; i++ {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		err := limiter1.Wait(ctx)
		elapsed := time.Since(start)
		fmt.Printf("   Request %d at %vms - Error: %v\n", i+1, elapsed.Milliseconds(), err)
		cancel()
	}
	
	fmt.Println()
	
	// Example 2: Sliding Window Rate Limiter
	fmt.Println("2. Sliding Window Rate Limiter (3 req/500ms):")
	limiter2 := NewSlidingWindowRateLimiter(500*time.Millisecond, 3)
	
	for i := 0; i < 8; i++ {
		allowed := limiter2.Allow()
		fmt.Printf("   Request %d: Allowed=%v\n", i+1, allowed)
		time.Sleep(150 * time.Millisecond)
	}
	
	fmt.Println()
	
	// Example 3: Leaky Bucket Rate Limiter
	fmt.Println("3. Leaky Bucket Rate Limiter (capacity=3, 200ms leak):")
	limiter3 := NewLeakyBucketRateLimiter(3, 200*time.Millisecond)
	
	for i := 0; i < 8; i++ {
		allowed := limiter3.Allow()
		fmt.Printf("   Request %d: Allowed=%v\n", i+1, allowed)
		time.Sleep(100 * time.Millisecond)
	}
	
	fmt.Println()
	
	// Example 4: Rate-limited API client
	fmt.Println("4. Rate-limited API Client (3 req/sec):")
	clientLimiter := NewSimpleRateLimiter(3)
	defer clientLimiter.Stop()
	
	client := NewRateLimitedClient(clientLimiter)
	
	urls := []string{
		"https://api.example.com/1",
		"https://api.example.com/2",
		"https://api.example.com/3",
		"https://api.example.com/4",
		"https://api.example.com/5",
	}
	
	var wg sync.WaitGroup
	start = time.Now()
	
	for i, url := range urls {
		wg.Add(1)
		go func(idx int, u string) {
			defer wg.Done()
			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()
			
			resp, err := client.Get(ctx, u)
			elapsed := time.Since(start)
			fmt.Printf("   [%vms] Request %d: %s (err=%v)\n", 
				elapsed.Milliseconds(), idx+1, resp, err)
		}(i, url)
	}
	
	wg.Wait()
}
```

### Explanation

Rate limiting controls the rate at which operations can be performed, preventing overload and ensuring fair resource usage.

**Three Main Algorithms**:

**1. Token Bucket (Simple Rate Limiter)**:
- Tokens are added at fixed rate to bucket
- Each request consumes one token
- Allows burst up to bucket capacity
- Best for: APIs with burst tolerance

**2. Sliding Window**:
- Tracks timestamps of recent requests
- Count requests within time window
- More accurate than fixed window
- Best for: Strict rate limiting without bursts

**3. Leaky Bucket**:
- Requests fill the bucket
- Bucket drains at constant rate
- Smooths out burst traffic
- Best for: Traffic shaping, network traffic

**Implementation Features**:
- `Allow()`: Non-blocking check if request is allowed
- `Wait(ctx)`: Blocking wait with context support
- Thread-safe with mutex protection
- Context integration for cancellation

**Use Cases**:
- API rate limiting
- Database connection throttling
- Web scraping with politeness
- Preventing resource exhaustion

---

## Summary

These five patterns form the foundation of robust concurrent Go programs:

1. **Worker Pool**: Controlled concurrency with graceful shutdown
2. **Pipeline**: Composable data processing stages
3. **Fan-out/Fan-in**: Parallel processing with result aggregation
4. **Context Timeout**: Cancellation and deadline management
5. **Rate Limiting**: Traffic control and resource protection

Each pattern can be combined and adapted to fit specific requirements. Understanding when to use each pattern is key to writing efficient and maintainable concurrent code in Go.
