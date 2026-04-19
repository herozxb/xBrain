# Go Pipelines

## Overview

Pipelines in Go are a powerful pattern for processing data in stages. Each stage is a goroutine that receives data from an upstream stage via a channel, processes it, and sends it downstream via another channel. This enables concurrent, composable, and efficient data processing.

## Core Concepts

### Basic Pipeline Structure

```go
package main

import (
    "fmt"
    "math"
)

// Stage 1: Generator - converts a list to a channel
func generator(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Stage 2: Square - squares each number
func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// Stage 3: Filter - removes negative numbers
func filter(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            if n >= 0 {
                out <- n
            }
        }
    }()
    return out
}

// Consumer - prints results
func consumer(in <-chan int) {
    for n := range in {
        fmt.Println(n)
    }
}

func main() {
    // Set up the pipeline
    nums := generator(1, 2, 3, 4, 5)
    squared := square(nums)
    
    // Consume
    consumer(squared)
}
```

## Advanced Patterns

### Fan-Out, Fan-In

```go
package main

import (
    "fmt"
    "math/rand"
    "sync"
    "time"
)

// Producer
func producer(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Worker - multiple instances process concurrently
func worker(id int, in <-chan int) <-chan string {
    out := make(chan string)
    go func() {
        defer close(out)
        for n := range in {
            // Simulate work
            time.Sleep(time.Duration(rand.Intn(500)) * time.Millisecond)
            result := fmt.Sprintf("Worker %d: processed %d -> %d", id, n, n*n)
            out <- result
        }
    }()
    return out
}

// Fan-in - merges multiple channels into one
func merge(channels ...<-chan string) <-chan string {
    var wg sync.WaitGroup
    out := make(chan string)
    
    // Start an output goroutine for each input channel
    collect := func(ch <-chan string) {
        defer wg.Done()
        for val := range ch {
            out <- val
        }
    }
    
    wg.Add(len(channels))
    for _, ch := range channels {
        go collect(ch)
    }
    
    // Close out when all collect goroutines complete
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}

func main() {
    rand.Seed(time.Now().UnixNano())
    
    // Producer
    input := producer(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    
    // Fan-out to 3 workers
    c1 := worker(1, input)
    c2 := worker(2, input)
    c3 := worker(3, input)
    
    // Fan-in
    merged := merge(c1, c2, c3)
    
    // Consume
    for result := range merged {
        fmt.Println(result)
    }
}
```

### Pipeline with Error Handling

```go
package main

import (
    "errors"
    "fmt"
)

type Result struct {
    Value int
    Error error
}

func safeGenerator(nums ...int) <-chan Result {
    out := make(chan Result)
    go func() {
        defer close(out)
        for _, n := range nums {
            if n < 0 {
                out <- Result{Error: errors.New("negative number")}
            } else {
                out <- Result{Value: n}
            }
        }
    }()
    return out
}

func safeSquare(in <-chan Result) <-chan Result {
    out := make(chan Result)
    go func() {
        defer close(out)
        for r := range in {
            if r.Error != nil {
                out <- r // Pass error through
            } else {
                out <- Result{Value: r.Value * r.Value}
            }
        }
    }()
    return out
}

func safeSqrt(in <-chan Result) <-chan Result {
    out := make(chan Result)
    go func() {
        defer close(out)
        for r := range in {
            if r.Error != nil {
                out <- r // Pass error through
            } else if r.Value < 0 {
                out <- Result{Error: errors.New("cannot sqrt negative")}
            } else {
                out <- Result{Value: int(math.Sqrt(float64(r.Value)))}
            }
        }
    }()
    return out
}

func main() {
    nums := safeGenerator(1, -2, 3, 4, -5)
    squared := safeSquare(nums)
    results := safeSqrt(squared)
    
    for r := range results {
        if r.Error != nil {
            fmt.Printf("Error: %v\n", r.Error)
        } else {
            fmt.Printf("Result: %d\n", r.Value)
        }
    }
}
```

### Bounded Parallelism

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func boundedPipeline(input <-chan int, numWorkers int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    
    // Semaphore to limit concurrency
    sem := make(chan struct{}, numWorkers)
    
    go func() {
        for n := range input {
            // Acquire semaphore
            sem <- struct{}{}
            wg.Add(1)
            
            go func(num int) {
                defer wg.Done()
                defer func() { <-sem }() // Release semaphore
                
                // Simulate work
                time.Sleep(100 * time.Millisecond)
                out <- num * num
            }(n)
        }
        
        // Wait for all workers to complete
        go func() {
            wg.Wait()
            close(out)
        }()
    }()
    
    return out
}

func main() {
    input := make(chan int)
    
    // Start producer
    go func() {
        defer close(input)
        for i := 1; i <= 20; i++ {
            input <- i
        }
    }()
    
    // Process with max 5 workers
    output := boundedPipeline(input, 5)
    
    // Consume
    for result := range output {
        fmt.Println(result)
    }
}
```

### Context-Aware Pipeline

```go
package main

import (
    "context"
    "fmt"
    "time"
)

func contextAwareGenerator(ctx context.Context, nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            select {
            case out <- n:
            case <-ctx.Done():
                fmt.Println("Generator cancelled")
                return
            }
        }
    }()
    return out
}

func contextAwareSquare(ctx context.Context, in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for {
            select {
            case n, ok := <-in:
                if !ok {
                    return
                }
                out <- n * n
            case <-ctx.Done():
                fmt.Println("Square cancelled")
                return
            }
        }
    }()
    return out
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
    defer cancel()
    
    input := contextAwareGenerator(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    squared := contextAwareSquare(ctx, input)
    
    for n := range squared {
        fmt.Println(n)
        time.Sleep(20 * time.Millisecond) // Simulate slow consumer
    }
}
```

### Pipeline with Buffering

```go
package main

import (
    "fmt"
    "time"
)

// Buffered pipeline stages for better throughput
func fastProducer(count int) <-chan int {
    out := make(chan int, 10) // Buffer for smooth flow
    go func() {
        defer close(out)
        for i := 0; i < count; i++ {
            out <- i
        }
    }()
    return out
}

func slowConsumer(in <-chan int) {
    for n := range in {
        time.Sleep(100 * time.Millisecond) // Simulate slow processing
        fmt.Println("Processed:", n)
    }
}

// Batch processor - groups items for batch operations
func batcher(in <-chan int, batchSize int) <-chan []int {
    out := make(chan []int)
    go func() {
        defer close(out)
        batch := make([]int, 0, batchSize)
        
        for n := range in {
            batch = append(batch, n)
            if len(batch) >= batchSize {
                out <- batch
                batch = make([]int, 0, batchSize)
            }
        }
        
        // Send remaining items
        if len(batch) > 0 {
            out <- batch
        }
    }()
    return out
}

func main() {
    input := fastProducer(25)
    batches := batcher(input, 5)
    
    for batch := range batches {
        fmt.Println("Batch:", batch)
    }
}
```

### Tee Pipeline - Split to Multiple Consumers

```go
package main

import (
    "fmt"
    "sync"
)

// Tee splits one channel into two
func tee(in <-chan int) (_, _ <-chan int) {
    out1 := make(chan int)
    out2 := make(chan int)
    
    go func() {
        defer close(out1)
        defer close(out2)
        
        for n := range in {
            var out1, out2 = out1, out2
            for i := 0; i < 2; i++ {
                select {
                case out1 <- n:
                    out1 = nil
                case out2 <- n:
                    out2 = nil
                }
            }
        }
    }()
    
    return out1, out2
}

// Or channel - returns first value from any channel
func or(channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    
    multiplex := func(ch <-chan int) {
        defer wg.Done()
        for n := range ch {
            out <- n
        }
    }
    
    wg.Add(len(channels))
    for _, ch := range channels {
        go multiplex(ch)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}

func main() {
    input := make(chan int)
    
    go func() {
        defer close(input)
        for i := 1; i <= 5; i++ {
            input <- i
        }
    }()
    
    // Split into two channels
    ch1, ch2 := tee(input)
    
    // Consume from both
    go func() {
        for n := range ch1 {
            fmt.Printf("Consumer 1: %d\n", n)
        }
    }()
    
    for n := range ch2 {
        fmt.Printf("Consumer 2: %d\n", n)
    }
}
```

## Real-World Example: Log Processing Pipeline

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "regexp"
    "strings"
    "time"
)

type LogEntry struct {
    Timestamp time.Time
    Level     string
    Message   string
    Source    string
}

type Stats struct {
    Total    int
    Errors   int
    Warnings int
    BySource map[string]int
}

// Stage 1: Read lines from file
func readLines(filename string) <-chan string {
    out := make(chan string)
    go func() {
        defer close(out)
        
        file, err := os.Open(filename)
        if err != nil {
            fmt.Println("Error:", err)
            return
        }
        defer file.Close()
        
        scanner := bufio.NewScanner(file)
        for scanner.Scan() {
            out <- scanner.Text()
        }
    }()
    return out
}

// Stage 2: Parse log entries
func parseLines(in <-chan string) <-chan LogEntry {
    out := make(chan LogEntry)
    go func() {
        defer close(out)
        
        logPattern := regexp.MustCompile(`(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+) - (.+)`)
        
        for line := range in {
            matches := logPattern.FindStringSubmatch(line)
            if matches != nil {
                timestamp, _ := time.Parse("2006-01-02 15:04:05", matches[1])
                out <- LogEntry{
                    Timestamp: timestamp,
                    Level:     matches[2],
                    Message:   matches[3],
                    Source:    matches[4],
                }
            }
        }
    }()
    return out
}

// Stage 3: Filter by level
func filterByLevel(in <-chan LogEntry, levels ...string) <-chan LogEntry {
    out := make(chan LogEntry)
    allowed := make(map[string]bool)
    for _, l := range levels {
        allowed[strings.ToUpper(l)] = true
    }
    
    go func() {
        defer close(out)
        for entry := range in {
            if allowed[strings.ToUpper(entry.Level)] {
                out <- entry
            }
        }
    }()
    return out
}

// Stage 4: Aggregate statistics
func aggregateStats(in <-chan LogEntry) <-chan Stats {
    out := make(chan Stats)
    go func() {
        defer close(out)
        
        stats := Stats{
            BySource: make(map[string]int),
        }
        
        for entry := range in {
            stats.Total++
            stats.BySource[entry.Source]++
            
            switch strings.ToUpper(entry.Level) {
            case "ERROR":
                stats.Errors++
            case "WARNING":
                stats.Warnings++
            }
        }
        
        out <- stats
    }()
    return out
}

func main() {
    // Create sample log file
    filename := "sample.log"
    content := `2024-01-15 10:30:15 [INFO] Application started - main
2024-01-15 10:30:16 [ERROR] Connection failed - database
2024-01-15 10:30:17 [WARNING] High memory usage - monitor
2024-01-15 10:30:18 [INFO] User logged in - auth
2024-01-15 10:30:19 [ERROR] Query timeout - database
2024-01-15 10:30:20 [INFO] Request processed - api`
    os.WriteFile(filename, []byte(content), 0644)
    
    // Build pipeline
    lines := readLines(filename)
    entries := parseLines(lines)
    filtered := filterByLevel(entries, "ERROR", "WARNING")
    statsChan := aggregateStats(filtered)
    
    // Get results
    stats := <-statsChan
    
    fmt.Printf("Total logs: %d\n", stats.Total)
    fmt.Printf("Errors: %d\n", stats.Errors)
    fmt.Printf("Warnings: %d\n", stats.Warnings)
    fmt.Println("By source:")
    for source, count := range stats.BySource {
        fmt.Printf("  %s: %d\n", source, count)
    }
}
```

## Best Practices

1. **Always close channels** - Use `defer close(out)` to prevent goroutine leaks
2. **Channel ownership** - Writers own and close channels, readers just read
3. **Buffer wisely** - Use buffers to decouple stages but don't over-buffer
4. **Handle cancellation** - Use context for graceful shutdown
5. **Error propagation** - Pass errors through the pipeline
6. **Limit goroutines** - Use semaphores for bounded parallelism
7. **Monitor pipeline** - Track metrics for production pipelines

## When to Use

- Data transformation workflows
- Log processing and analysis
- ETL (Extract, Transform, Load) operations
- Stream processing
- Image/video processing
- Network request handling
- Batch job processing
