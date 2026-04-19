# Go Worker Pools

## 1. Basic Worker Pool

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

// Job represents a task to be processed
type Job struct {
	ID   int
	Data interface{}
}

// Result represents the processed result
type Result struct {
	Job    Job
	Value  interface{}
	Err    error
}

// Worker processes jobs from the jobs channel
func Worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	
	for job := range jobs {
		fmt.Printf("Worker %d: Processing job %d\n", id, job.ID)
		
		// Simulate work
		time.Sleep(100 * time.Millisecond)
		
		results <- Result{
			Job:   job,
			Value: fmt.Sprintf("Processed by worker %d", id),
		}
	}
}

// WorkerPool manages a pool of workers
type WorkerPool struct {
	workers   int
	jobs      chan Job
	results   chan Result
	wg        sync.WaitGroup
}

func NewWorkerPool(workers, bufferSize int) *WorkerPool {
	return &WorkerPool{
		workers: workers,
		jobs:    make(chan Job, bufferSize),
		results: make(chan Result, bufferSize),
	}
}

func (p *WorkerPool) Start() {
	for i := 1; i <= p.workers; i++ {
		p.wg.Add(1)
		go Worker(i, p.jobs, p.results, &p.wg)
	}
}

func (p *WorkerPool) Submit(job Job) {
	p.jobs <- job
}

func (p *WorkerPool) Results() <-chan Result {
	return p.results
}

func (p *WorkerPool) Stop() {
	close(p.jobs)
	p.wg.Wait()
	close(p.results)
}

// Usage
func main() {
	pool := NewWorkerPool(3, 10)
	pool.Start()

	// Submit jobs
	go func() {
		for i := 1; i <= 10; i++ {
			pool.Submit(Job{ID: i})
		}
	}()

	// Collect results
	go func() {
		for result := range pool.Results() {
			fmt.Printf("Result: Job %d -> %v\n", result.Job.ID, result.Value)
		}
	}()

	time.Sleep(2 * time.Second)
	pool.Stop()
}
```

## 2. Graceful Shutdown with Context

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type WorkerPoolWithContext struct {
	workers int
	jobs    chan Job
	results chan Result
	wg      sync.WaitGroup
	ctx     context.Context
	cancel  context.CancelFunc
}

func NewWorkerPoolWithContext(workers, bufferSize int) *WorkerPoolWithContext {
	ctx, cancel := context.WithCancel(context.Background())
	return &WorkerPoolWithContext{
		workers: workers,
		jobs:    make(chan Job, bufferSize),
		results: make(chan Result, bufferSize),
		ctx:     ctx,
		cancel:  cancel,
	}
}

func (p *WorkerPoolWithContext) worker(id int) {
	defer p.wg.Done()
	
	for {
		select {
		case <-p.ctx.Done():
			fmt.Printf("Worker %d: Shutting down\n", id)
			return
		case job, ok := <-p.jobs:
			if !ok {
				return
			}
			
			// Check context before processing
			select {
			case <-p.ctx.Done():
				fmt.Printf("Worker %d: Job %d cancelled\n", id, job.ID)
				return
			default:
				result := p.processJob(id, job)
				select {
				case p.results <- result:
				case <-p.ctx.Done():
					return
				}
			}
		}
	}
}

func (p *WorkerPoolWithContext) processJob(workerID int, job Job) Result {
	// Simulate processing
	time.Sleep(50 * time.Millisecond)
	return Result{
		Job:   job,
		Value: fmt.Sprintf("Job %d processed by worker %d", job.ID, workerID),
	}
}

func (p *WorkerPoolWithContext) Start() {
	for i := 1; i <= p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *WorkerPoolWithContext) Submit(job Job) error {
	select {
	case p.jobs <- job:
		return nil
	case <-p.ctx.Done():
		return fmt.Errorf("pool is shutting down")
	}
}

func (p *WorkerPoolWithContext) Shutdown(timeout time.Duration) {
	// Stop accepting new jobs
	p.cancel()
	
	// Wait for workers with timeout
	done := make(chan struct{})
	go func() {
		p.wg.Wait()
		close(done)
	}()
	
	select {
	case <-done:
		fmt.Println("All workers stopped gracefully")
	case <-time.After(timeout):
		fmt.Println("Timeout waiting for workers")
	}
	
	close(p.jobs)
	close(p.results)
}

func (p *WorkerPoolWithContext) Results() <-chan Result {
	return p.results
}
```

## 3. Rate-Limited Worker Pool

```go
package main

import (
	"context"
	"golang.org/x/time/rate"
	"sync"
	"time"
)

type RateLimitedPool struct {
	workers  int
	limiter  *rate.Limiter
	jobs     chan Job
	results  chan Result
	wg       sync.WaitGroup
	ctx      context.Context
	cancel   context.CancelFunc
}

// NewRateLimitedPool creates a pool with rate limiting
// rps: requests per second, burst: maximum burst size
func NewRateLimitedPool(workers int, rps, burst int) *RateLimitedPool {
	ctx, cancel := context.WithCancel(context.Background())
	return &RateLimitedPool{
		workers: workers,
		limiter: rate.NewLimiter(rate.Limit(rps), burst),
		jobs:    make(chan Job, 100),
		results: make(chan Result, 100),
		ctx:     ctx,
		cancel:  cancel,
	}
}

func (p *RateLimitedPool) worker(id int) {
	defer p.wg.Done()
	
	for {
		select {
		case <-p.ctx.Done():
			return
		case job, ok := <-p.jobs:
			if !ok {
				return
			}
			
			// Wait for rate limiter
			if err := p.limiter.Wait(p.ctx); err != nil {
				// Context cancelled
				return
			}
			
			result := Result{
				Job:   job,
				Value: fmt.Sprintf("Processed at %v", time.Now()),
			}
			
			select {
			case p.results <- result:
			case <-p.ctx.Done():
				return
			}
		}
	}
}

func (p *RateLimitedPool) Start() {
	for i := 1; i <= p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *RateLimitedPool) Stop() {
	p.cancel()
	p.wg.Wait()
	close(p.jobs)
	close(p.results)
}
```

## 4. Dynamic Worker Pool (Auto-scaling)

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

type DynamicPool struct {
	minWorkers    int32
	maxWorkers    int32
	currentWorker int32
	jobs          chan Job
	results       chan Result
	wg            sync.WaitGroup
	ctx           context.Context
	cancel        context.CancelFunc
	mu            sync.Mutex
}

func NewDynamicPool(minWorkers, maxWorkers int) *DynamicPool {
	ctx, cancel := context.WithCancel(context.Background())
	p := &DynamicPool{
		minWorkers: int32(minWorkers),
		maxWorkers: int32(maxWorkers),
		jobs:       make(chan Job, 1000),
		results:    make(chan Result, 1000),
		ctx:        ctx,
		cancel:     cancel,
	}
	
	// Start minimum workers
	for i := 0; i < minWorkers; i++ {
		p.addWorker()
	}
	
	// Start auto-scaling monitor
	go p.monitor()
	
	return p
}

func (p *DynamicPool) addWorker() bool {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	current := atomic.LoadInt32(&p.currentWorker)
	if current >= p.maxWorkers {
		return false
	}
	
	atomic.AddInt32(&p.currentWorker, 1)
	p.wg.Add(1)
	
	go func(id int) {
		defer func() {
			atomic.AddInt32(&p.currentWorker, -1)
			p.wg.Done()
		}()
		
		for {
			select {
			case <-p.ctx.Done():
				return
			case job, ok := <-p.jobs:
				if !ok {
					return
				}
				p.processJob(id, job)
			}
		}
	}(int(current) + 1)
	
	return true
}

func (p *DynamicPool) removeWorker() bool {
	// Workers will exit when they receive ctx.Done()
	current := atomic.LoadInt32(&p.currentWorker)
	if current <= p.minWorkers {
		return false
	}
	
	// Send sentinel to trigger one worker to exit
	// (Implementation depends on specific requirements)
	return true
}

func (p *DynamicPool) monitor() {
	ticker := time.NewTicker(500 * time.Millisecond)
	defer ticker.Stop()
	
	for {
		select {
		case <-p.ctx.Done():
			return
		case <-ticker.C:
			p.scale()
		}
	}
}

func (p *DynamicPool) scale() {
	queueLen := len(p.jobs)
	currentWorkers := atomic.LoadInt32(&p.currentWorker)
	
	// Scale up if queue is building
	if queueLen > 50 && currentWorkers < p.maxWorkers {
		p.addWorker()
		fmt.Printf("Scaling up: %d workers\n", currentWorkers+1)
	}
	
	// Scale down if queue is empty (with minimum workers)
	if queueLen == 0 && currentWorkers > p.minWorkers {
		// Workers will naturally exit on idle
	}
}

func (p *DynamicPool) processJob(workerID int, job Job) {
	// Simulate work
	time.Sleep(100 * time.Millisecond)
	
	result := Result{
		Job:   job,
		Value: fmt.Sprintf("Processed by worker %d", workerID),
	}
	
	select {
	case p.results <- result:
	case <-p.ctx.Done():
	}
}

func (p *DynamicPool) Submit(job Job) {
	select {
	case p.jobs <- job:
	case <-p.ctx.Done():
	}
}

func (p *DynamicPool) Stop() {
	p.cancel()
	p.wg.Wait()
	close(p.jobs)
	close(p.results)
}

func (p *DynamicPool) Stats() (workers int, queueLen int) {
	return int(atomic.LoadInt32(&p.currentWorker)), len(p.jobs)
}
```

## 5. Worker Pool with Retry Logic

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type RetryConfig struct {
	MaxAttempts int
	Backoff     time.Duration
	MaxBackoff  time.Duration
}

type RetryableJob struct {
	Job        Job
	Attempts   int
	LastError error
}

type RetryablePool struct {
	workers int
	config  RetryConfig
	jobs    chan RetryableJob
	results chan Result
	wg      sync.WaitGroup
	ctx     context.Context
	cancel  context.CancelFunc
}

func NewRetryablePool(workers int, config RetryConfig) *RetryablePool {
	ctx, cancel := context.WithCancel(context.Background())
	return &RetryablePool{
		workers: workers,
		config:  config,
		jobs:    make(chan RetryableJob, 100),
		results: make(chan Result, 100),
		ctx:     ctx,
		cancel:  cancel,
	}
}

func (p *RetryablePool) worker(id int) {
	defer p.wg.Done()
	
	for {
		select {
		case <-p.ctx.Done():
			return
		case retryJob, ok := <-p.jobs:
			if !ok {
				return
			}
			
			result := p.processWithRetry(id, retryJob)
			
			// If failed and can retry, re-queue
			if result.Err != nil && retryJob.Attempts < p.config.MaxAttempts {
				retryJob.Attempts++
				retryJob.LastError = result.Err
				
				// Exponential backoff
				backoff := p.config.Backoff * time.Duration(1<<uint(retryJob.Attempts-1))
				if backoff > p.config.MaxBackoff {
					backoff = p.config.MaxBackoff
				}
				
				time.Sleep(backoff)
				
				select {
				case p.jobs <- retryJob:
					fmt.Printf("Retrying job %d (attempt %d)\n", 
						retryJob.Job.ID, retryJob.Attempts)
				case <-p.ctx.Done():
					return
				}
			} else {
				select {
				case p.results <- result:
				case <-p.ctx.Done():
					return
				}
			}
		}
	}
}

func (p *RetryablePool) processWithRetry(workerID int, retryJob RetryableJob) Result {
	// Simulate processing that might fail
	job := retryJob.Job
	
	// Simulate failure for demonstration (fails first 2 attempts)
	if retryJob.Attempts < 2 {
		return Result{
			Job:  job,
			Err:  fmt.Errorf("simulated failure"),
		}
	}
	
	return Result{
		Job:   job,
		Value: fmt.Sprintf("Job %d succeeded after %d attempts", job.ID, retryJob.Attempts+1),
	}
}

func (p *RetryablePool) Start() {
	for i := 1; i <= p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *RetryablePool) Submit(job Job) {
	retryJob := RetryableJob{
		Job:      job,
		Attempts: 0,
	}
	
	select {
	case p.jobs <- retryJob:
	case <-p.ctx.Done():
	}
}

func (p *RetryablePool) Stop() {
	p.cancel()
	p.wg.Wait()
	close(p.jobs)
	close(p.results)
}

func (p *RetryablePool) Results() <-chan Result {
	return p.results
}
```

## 6. Priority Worker Pool

```go
package main

import (
	"container/heap"
	"context"
	"sync"
	"time"
)

type Priority int

const (
	PriorityLow Priority = iota
	PriorityNormal
	PriorityHigh
	PriorityCritical
)

type PriorityJob struct {
	Job
	Priority Priority
	Index    int // for heap implementation
}

// Priority queue implementation
type PriorityQueue []*PriorityJob

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Priority > pq[j].Priority // Higher priority first
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].Index = i
	pq[j].Index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*PriorityJob)
	item.Index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.Index = -1
	*pq = old[0 : n-1]
	return item
}

type PriorityPool struct {
	workers int
	queue   PriorityQueue
	mu      sync.Mutex
	cond    *sync.Cond
	results chan Result
	ctx     context.Context
	cancel  context.CancelFunc
	wg      sync.WaitGroup
}

func NewPriorityPool(workers int) *PriorityPool {
	ctx, cancel := context.WithCancel(context.Background())
	p := &PriorityPool{
		workers: workers,
		queue:   make(PriorityQueue, 0),
		results: make(chan Result, 100),
		ctx:     ctx,
		cancel:  cancel,
	}
	p.cond = sync.NewCond(&p.mu)
	heap.Init(&p.queue)
	return p
}

func (p *PriorityPool) worker(id int) {
	defer p.wg.Done()
	
	for {
		p.mu.Lock()
		
		// Wait for jobs
		for p.queue.Len() == 0 {
			select {
			case <-p.ctx.Done():
				p.mu.Unlock()
				return
			default:
				p.cond.Wait()
			}
		}
		
		// Get highest priority job
		job := heap.Pop(&p.queue).(*PriorityJob)
		p.mu.Unlock()
		
		// Process job
		result := Result{
			Job:   job.Job,
			Value: fmt.Sprintf("Priority %d job processed", job.Priority),
		}
		
		select {
		case p.results <- result:
		case <-p.ctx.Done():
			return
		}
	}
}

func (p *PriorityPool) Submit(job Job, priority Priority) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	priorityJob := &PriorityJob{
		Job:      job,
		Priority: priority,
	}
	
	heap.Push(&p.queue, priorityJob)
	p.cond.Signal()
}

func (p *PriorityPool) Start() {
	for i := 1; i <= p.workers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *PriorityPool) Stop() {
	p.cancel()
	p.cond.Broadcast() // Wake up all waiting workers
	p.wg.Wait()
	close(p.results)
}

func (p *PriorityPool) Results() <-chan Result {
	return p.results
}
```

## Summary Table

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| Basic Pool | Simple parallel processing | Easy to implement | No graceful shutdown |
| Context Pool | Long-running tasks | Cancellation support | More complex |
| Rate Limited | API calls, external services | Prevents overload | Adds latency |
| Dynamic Pool | Variable workload | Auto-scaling | More overhead |
| Retry Pool | Unreliable operations | Automatic retries | May delay failures |
| Priority Pool | Mixed priority tasks | Important jobs first | More memory |

## Best Practices

1. **Use buffered channels** - Prevent blocking on job submission
2. **Implement graceful shutdown** - Use context for cancellation
3. **Limit goroutine creation** - Pool workers, don't spawn per task
4. **Handle panics** - Recover in worker functions
5. **Monitor pool health** - Track queue length, worker count
6. **Set appropriate timeouts** - Don't wait forever
7. **Consider rate limiting** - Protect external services
