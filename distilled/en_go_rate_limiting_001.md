# Rate Limiting in Go

## Problem

Implement a rate limiter that controls the rate of requests to prevent system overload and ensure fair resource allocation. The rate limiter should support multiple algorithms and provide flexible configuration options.

### Requirements
- Token bucket algorithm implementation
- Sliding window rate limiting
- Distributed rate limiting support
- Per-client rate limiting
- Configurable limits and windows
- Thread-safe implementation

## Implementation

### Token Bucket Rate Limiter

```go
package ratelimit

import (
	"context"
	"sync"
	"time"
)

// TokenBucket implements the token bucket algorithm
type TokenBucket struct {
	mu           sync.Mutex
	rate         float64 // tokens per second
	capacity     float64 // maximum tokens
	tokens       float64 // current tokens
	lastUpdated  time.Time
}

// NewTokenBucket creates a new token bucket rate limiter
func NewTokenBucket(rate, capacity float64) *TokenBucket {
	return &TokenBucket{
		rate:        rate,
		capacity:    capacity,
		tokens:      capacity,
		lastUpdated: time.Now(),
	}
}

// Allow checks if a request can proceed
func (tb *TokenBucket) Allow() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastUpdated).Seconds()
	tb.lastUpdated = now

	// Add tokens based on elapsed time
	tb.tokens = min(tb.capacity, tb.tokens+elapsed*tb.rate)

	if tb.tokens >= 1.0 {
		tb.tokens--
		return true
	}

	return false
}

// Wait blocks until a token is available or context is cancelled
func (tb *TokenBucket) Wait(ctx context.Context) error {
	for {
		if tb.Allow() {
			return nil
		}

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(10 * time.Millisecond):
			continue
		}
	}
}

// Reserve reserves a token for future use
func (tb *TokenBucket) Reserve() time.Duration {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastUpdated).Seconds()
	tb.lastUpdated = now
	tb.tokens = min(tb.capacity, tb.tokens+elapsed*tb.rate)

	if tb.tokens >= 1.0 {
		tb.tokens--
		return 0
	}

	// Calculate time until next token is available
	needed := 1.0 - tb.tokens
	waitTime := time.Duration(needed/tb.rate) * time.Second
	return waitTime
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
```

### Sliding Window Rate Limiter

```go
package ratelimit

import (
	"sync"
	"time"
)

// SlidingWindow implements sliding window rate limiting
type SlidingWindow struct {
	mu       sync.Mutex
	limit    int
	window   time.Duration
	requests []time.Time
}

// NewSlidingWindow creates a new sliding window rate limiter
func NewSlidingWindow(limit int, window time.Duration) *SlidingWindow {
	return &SlidingWindow{
		limit:    limit,
		window:   window,
		requests: make([]time.Time, 0, limit),
	}
}

// Allow checks if a request can proceed
func (sw *SlidingWindow) Allow() bool {
	sw.mu.Lock()
	defer sw.mu.Unlock()

	now := time.Now()
	cutoff := now.Add(-sw.window)

	// Remove old requests outside the window
	valid := 0
	for _, req := range sw.requests {
		if req.After(cutoff) {
			sw.requests[valid] = req
			valid++
		}
	}
	sw.requests = sw.requests[:valid]

	// Check if under limit
	if len(sw.requests) < sw.limit {
		sw.requests = append(sw.requests, now)
		return true
	}

	return false
}

// Remaining returns the number of remaining requests in the window
func (sw *SlidingWindow) Remaining() int {
	sw.mu.Lock()
	defer sw.mu.Unlock()

	now := time.Now()
	cutoff := now.Add(-sw.window)

	count := 0
	for _, req := range sw.requests {
		if req.After(cutoff) {
			count++
		}
	}

	return sw.limit - count
}

// Reset clears all recorded requests
func (sw *SlidingWindow) Reset() {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	sw.requests = sw.requests[:0]
}
```

### Per-Client Rate Limiter

```go
package ratelimit

import (
	"sync"
	"time"
)

// ClientRateLimiter manages rate limiting per client
type ClientRateLimiter struct {
	mu      sync.RWMutex
	limiters map[string]*TokenBucket
	rate    float64
	capacity float64
}

// NewClientRateLimiter creates a new per-client rate limiter
func NewClientRateLimiter(rate, capacity float64) *ClientRateLimiter {
	return &ClientRateLimiter{
		limiters:  make(map[string]*TokenBucket),
		rate:      rate,
		capacity:  capacity,
	}
}

// Allow checks if a client can make a request
func (crl *ClientRateLimiter) Allow(clientID string) bool {
	crl.mu.RLock()
	limiter, exists := crl.limiters[clientID]
	crl.mu.RUnlock()

	if !exists {
		crl.mu.Lock()
		// Double-check after acquiring write lock
		if limiter, exists = crl.limiters[clientID]; !exists {
			limiter = NewTokenBucket(crl.rate, crl.capacity)
			crl.limiters[clientID] = limiter
		}
		crl.mu.Unlock()
	}

	return limiter.Allow()
}

// Cleanup removes inactive limiters
func (crl *ClientRateLimiter) Cleanup(inactiveAfter time.Duration) {
	crl.mu.Lock()
	defer crl.mu.Unlock()

	// In a real implementation, you'd track last activity time
	// and remove limiters that haven't been used recently
	// This is a simplified version
}

// GetStats returns statistics for all clients
func (crl *ClientRateLimiter) GetStats() map[string]int {
	crl.mu.RLock()
	defer crl.mu.RUnlock()

	stats := make(map[string]int)
	for clientID := range crl.limiters {
		stats[clientID]++
	}
	return stats
}
```

### HTTP Middleware

```go
package middleware

import (
	"encoding/json"
	"net/http"
	"time"
	
	"yourapp/ratelimit"
)

// RateLimitMiddleware creates HTTP middleware with rate limiting
type RateLimitMiddleware struct {
	limiter *ratelimit.ClientRateLimiter
}

// NewRateLimitMiddleware creates a new rate limit middleware
func NewRateLimitMiddleware(rate, capacity float64) *RateLimitMiddleware {
	return &RateLimitMiddleware{
		limiter: ratelimit.NewClientRateLimiter(rate, capacity),
	}
}

// Handler wraps an HTTP handler with rate limiting
func (rlm *RateLimitMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		clientID := getClientID(r)
		
		if !rlm.limiter.Allow(clientID) {
			rlm.respondRateLimited(w)
			return
		}
		
		next.ServeHTTP(w, r)
	})
}

func (rlm *RateLimitMiddleware) respondRateLimited(w http.ResponseWriter) {
	w.Header().Set("Retry-After", "1")
	w.Header().Set("X-RateLimit-Limit", "100")
	w.WriteHeader(http.StatusTooManyRequests)
	
	json.NewEncoder(w).Encode(map[string]interface{}{
		"error": "rate limit exceeded",
		"retry_after": time.Second,
	})
}

func getClientID(r *http.Request) string {
	// Try API key first
	if apiKey := r.Header.Get("X-API-Key"); apiKey != "" {
		return apiKey
	}
	
	// Fall back to IP address
	return r.RemoteAddr
}
```

## Tests

```go
package ratelimit_test

import (
	"context"
	"testing"
	"time"
	
	"yourapp/ratelimit"
)

func TestTokenBucket_Allow(t *testing.T) {
	// 10 requests per second, capacity of 10
	tb := ratelimit.NewTokenBucket(10, 10)
	
	// Should allow burst up to capacity
	for i := 0; i < 10; i++ {
		if !tb.Allow() {
			t.Errorf("Expected request %d to be allowed", i)
		}
	}
	
	// Should deny after capacity exhausted
	if tb.Allow() {
		t.Error("Expected request after capacity to be denied")
	}
}

func TestTokenBucket_Refill(t *testing.T) {
	tb := ratelimit.NewTokenBucket(10, 10)
	
	// Exhaust tokens
	for i := 0; i < 10; i++ {
		tb.Allow()
	}
	
	// Wait for refill
	time.Sleep(200 * time.Millisecond)
	
	// Should have 2 new tokens (10 req/s * 0.2s)
	if !tb.Allow() {
		t.Error("Expected request to be allowed after refill")
	}
}

func TestTokenBucket_Wait(t *testing.T) {
	tb := ratelimit.NewTokenBucket(100, 1)
	
	// Use the only token
	tb.Allow()
	
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()
	
	err := tb.Wait(ctx)
	if err == nil {
		t.Error("Expected timeout error")
	}
}

func TestSlidingWindow_Allow(t *testing.T) {
	// 5 requests per second
	sw := ratelimit.NewSlidingWindow(5, time.Second)
	
	// Should allow up to limit
	for i := 0; i < 5; i++ {
		if !sw.Allow() {
			t.Errorf("Expected request %d to be allowed", i)
		}
	}
	
	// Should deny after limit
	if sw.Allow() {
		t.Error("Expected request after limit to be denied")
	}
}

func TestSlidingWindow_WindowSliding(t *testing.T) {
	sw := ratelimit.NewSlidingWindow(2, 100*time.Millisecond)
	
	// Make 2 requests
	sw.Allow()
	sw.Allow()
	
	// Should be denied
	if sw.Allow() {
		t.Error("Expected request to be denied")
	}
	
	// Wait for window to slide
	time.Sleep(150 * time.Millisecond)
	
	// Should be allowed again
	if !sw.Allow() {
		t.Error("Expected request to be allowed after window slide")
	}
}

func TestClientRateLimiter(t *testing.T) {
	crl := ratelimit.NewClientRateLimiter(10, 5)
	
	// Client A should be rate limited independently
	for i := 0; i < 5; i++ {
		if !crl.Allow("clientA") {
			t.Errorf("Expected clientA request %d to be allowed", i)
		}
	}
	
	if crl.Allow("clientA") {
		t.Error("Expected clientA to be rate limited")
	}
	
	// Client B should have separate limit
	if !crl.Allow("clientB") {
		t.Error("Expected clientB to be allowed")
	}
}

func BenchmarkTokenBucket(b *testing.B) {
	tb := ratelimit.NewTokenBucket(1000000, 1000000)
	
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			tb.Allow()
		}
	})
}

func BenchmarkSlidingWindow(b *testing.B) {
	sw := ratelimit.NewSlidingWindow(1000000, time.Second)
	
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			sw.Allow()
		}
	})
}
```

## Complexity Analysis

### Time Complexity

1. **TokenBucket.Allow()**: O(1)
   - Simple arithmetic operations
   - Lock acquisition/release

2. **TokenBucket.Wait()**: O(1) per iteration
   - Polling with constant-time checks
   - Depends on token refill rate

3. **SlidingWindow.Allow()**: O(n) where n = requests in window
   - Must scan and remove expired requests
   - Can be optimized with circular buffer

4. **ClientRateLimiter.Allow()**: O(1) average
   - Hash map lookup for client limiter
   - O(1) for limiter operation

### Space Complexity

1. **TokenBucket**: O(1)
   - Fixed size state (counters, timestamps)

2. **SlidingWindow**: O(n) where n = limit
   - Stores timestamp for each request in window

3. **ClientRateLimiter**: O(c) where c = number of clients
   - One limiter per client

### Performance Characteristics

- **Token Bucket**: Best for burst handling, smooth average rate
- **Sliding Window**: More accurate request counting, higher memory usage
- **Per-Client**: Linear memory growth with client count, good concurrency

### Optimization Strategies

1. **Lazy Cleanup**: Remove expired entries only when accessed
2. **Circular Buffer**: Optimize sliding window storage
3. **Sharding**: Distribute per-client limiters across shards
4. **Approximation**: Use approximate algorithms for distributed scenarios
