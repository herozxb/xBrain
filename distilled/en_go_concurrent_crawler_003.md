# Go: Concurrent Web Crawler with Rate Limiting

## Problem Description

Build a production-ready web crawler that implements:
- Concurrent crawling with configurable workers
- Rate limiting per domain
- URL deduplication with bloom filter
- Depth-limited crawling
- Polite crawling with robots.txt support
- Graceful shutdown

## Complete Implementation

```go
// crawler/crawler.go
package crawler

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"sync"
	"time"

	"github.com/temoto/robotstxt"
)

// Result represents a crawled page result
type Result struct {
	URL   string
	Title string
	Links []string
	Error error
}

// Config holds crawler configuration
type Config struct {
	MaxWorkers     int
	MaxDepth       int
	RequestTimeout time.Duration
	UserAgent      string
	RateLimit      time.Duration // Per-domain rate limit
}

// Crawler is the main crawler struct
type Crawler struct {
	config     Config
	httpClient *http.Client
	visited    *URLSet
	rateLimit  *RateLimiter
	robots     *RobotsCache
	results    chan Result
	wg         sync.WaitGroup
}

// New creates a new crawler instance
func New(config Config) *Crawler {
	if config.MaxWorkers <= 0 {
		config.MaxWorkers = 10
	}
	if config.RequestTimeout <= 0 {
		config.RequestTimeout = 30 * time.Second
	}
	if config.RateLimit <= 0 {
		config.RateLimit = 1 * time.Second
	}
	if config.UserAgent == "" {
		config.UserAgent = "GoCrawler/1.0"
	}

	return &Crawler{
		config: config,
		httpClient: &http.Client{
			Timeout: config.RequestTimeout,
		},
		visited:   NewURLSet(),
		rateLimit: NewRateLimiter(config.RateLimit),
		robots:    NewRobotsCache(),
		results:   make(chan Result, 100),
	}
}

// job represents a crawl job
type job struct {
	URL   string
	Depth int
}

// Crawl starts crawling from the given seed URLs
func (c *Crawler) Crawl(ctx context.Context, seeds []string) <-chan Result {
	jobs := make(chan job, 1000)

	// Start workers
	for i := 0; i < c.config.MaxWorkers; i++ {
		c.wg.Add(1)
		go c.worker(ctx, jobs)
	}

	// Send seed URLs
	go func() {
		for _, seed := range seeds {
			if !c.visited.Add(seed) {
				continue
			}
			jobs <- job{URL: seed, Depth: 0}
		}
	}()

	// Close results channel when done
	go func() {
		c.wg.Wait()
		close(c.results)
	}()

	return c.results
}

// worker processes crawl jobs
func (c *Crawler) worker(ctx context.Context, jobs <-chan job) {
	defer c.wg.Done()

	for {
		select {
		case <-ctx.Done():
			return
		case job, ok := <-jobs:
			if !ok {
				return
			}
			c.processJob(ctx, job, jobs)
		}
	}
}

// processJob processes a single crawl job
func (c *Crawler) processJob(ctx context.Context, j job, jobs chan<- job) {
	// Check depth limit
	if c.config.MaxDepth > 0 && j.Depth >= c.config.MaxDepth {
		return
	}

	// Parse URL
	parsedURL, err := url.Parse(j.URL)
	if err != nil {
		c.results <- Result{URL: j.URL, Error: fmt.Errorf("invalid URL: %w", err)}
		return
	}

	// Check robots.txt
	if !c.robots.Allowed(ctx, parsedURL, c.config.UserAgent) {
		c.results <- Result{URL: j.URL, Error: fmt.Errorf("blocked by robots.txt")}
		return
	}

	// Apply rate limiting
	c.rateLimit.Wait(parsedURL.Host)

	// Fetch page
	page, err := c.fetch(ctx, j.URL)
	if err != nil {
		c.results <- Result{URL: j.URL, Error: err}
		return
	}

	// Extract links
	links := extractLinks(page.Content, parsedURL)
	
	// Queue new links
	var newLinks []string
	for _, link := range links {
		if c.visited.Add(link) {
			newLinks = append(newLinks, link)
			
			select {
			case jobs <- job{URL: link, Depth: j.Depth + 1}:
			default:
				// Job queue full, skip
			}
		}
	}

	c.results <- Result{
		URL:   j.URL,
		Title: page.Title,
		Links: newLinks,
	}
}

// fetch retrieves a web page
func (c *Crawler) fetch(ctx context.Context, urlStr string) (*Page, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", urlStr, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("User-Agent", c.config.UserAgent)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("fetch: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("status %d", resp.StatusCode)
	}

	return ParsePage(resp.Body)
}

// Shutdown gracefully stops the crawler
func (c *Crawler) Shutdown() {
	c.httpClient.CloseIdleConnections()
}
```

```go
// crawler/urlset.go
package crawler

import (
	"sync"

	"github.com/bits-and-blooms/bloom/v3"
)

// URLSet tracks visited URLs with bloom filter optimization
type URLSet struct {
	mu       sync.RWMutex
	visited  map[string]bool
	bloom    *bloom.BloomFilter
	fallback bool
}

// NewURLSet creates a new URL set
func NewURLSet() *URLSet {
	return &URLSet{
		visited:  make(map[string]bool),
		bloom:    bloom.NewWithEstimates(1000000, 0.01),
		fallback: false,
	}
}

// Add attempts to add a URL, returns false if already visited
func (s *URLSet) Add(url string) bool {
	s.mu.RLock()
	
	// Check bloom filter first
	if s.bloom.TestString(url) {
		// Might be a false positive, check exact map
		if s.visited[url] {
			s.mu.RUnlock()
			return false
		}
	}
	s.mu.RUnlock()

	s.mu.Lock()
	defer s.mu.Unlock()

	// Double check after acquiring write lock
	if s.visited[url] {
		return false
	}

	s.visited[url] = true
	s.bloom.AddString(url)
	return true
}

// Contains checks if a URL has been visited
func (s *URLSet) Contains(url string) bool {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.bloom.TestString(url) && s.visited[url]
}

// Size returns the number of visited URLs
func (s *URLSet) Size() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.visited)
}
```

```go
// crawler/ratelimiter.go
package crawler

import (
	"sync"
	"time"
)

// RateLimiter implements per-domain rate limiting
type RateLimiter struct {
	mu       sync.Mutex
	delay    time.Duration
	lastSeen map[string]time.Time
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(delay time.Duration) *RateLimiter {
	return &RateLimiter{
		delay:    delay,
		lastSeen: make(map[string]time.Time),
	}
}

// Wait blocks until it's okay to make a request to the given domain
func (r *RateLimiter) Wait(domain string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	last, exists := r.lastSeen[domain]
	if !exists {
		r.lastSeen[domain] = time.Now()
		return
	}

	elapsed := time.Since(last)
	if elapsed < r.delay {
		time.Sleep(r.delay - elapsed)
	}

	r.lastSeen[domain] = time.Now()
}
```

```go
// crawler/robots.go
package crawler

import (
	"context"
	"net/http"
	"net/url"
	"sync"
	"time"

	"github.com/temoto/robotstxt"
)

// RobotsCache caches robots.txt data per domain
type RobotsCache struct {
	mu     sync.RWMutex
	client *http.Client
	cache  map[string]*robotstxt.RobotsData
}

// NewRobotsCache creates a new robots cache
func NewRobotsCache() *RobotsCache {
	return &RobotsCache{
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
		cache: make(map[string]*robotstxt.RobotsData),
	}
}

// Allowed checks if a URL is allowed by robots.txt
func (r *RobotsCache) Allowed(ctx context.Context, u *url.URL, userAgent string) bool {
	domain := u.Hostname()

	// Check cache
	r.mu.RLock()
	robots, exists := r.cache[domain]
	r.mu.RUnlock()

	if !exists {
		robots = r.fetchRobots(ctx, domain)
		r.mu.Lock()
		r.cache[domain] = robots
		r.mu.Unlock()
	}

	if robots == nil {
		// No robots.txt, assume allowed
		return true
	}

	return robots.TestAgent(u.Path, userAgent)
}

// fetchRobots retrieves robots.txt for a domain
func (r *RobotsCache) fetchRobots(ctx context.Context, domain string) *robotstxt.RobotsData {
	robotsURL := "http://" + domain + "/robots.txt"

	req, err := http.NewRequestWithContext(ctx, "GET", robotsURL, nil)
	if err != nil {
		return nil
	}

	resp, err := r.client.Do(req)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil
	}

	robots, err := robotstxt.FromResponse(resp)
	if err != nil {
		return nil
	}

	return robots
}
```

## Test Suite

```go
// crawler/crawler_test.go
package crawler

import (
	"context"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"
)

func TestCrawlerBasic(t *testing.T) {
	// Setup test server
	var requestCount int64
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt64(&requestCount, 1)
		
		switch r.URL.Path {
		case "/":
			w.Header().Set("Content-Type", "text/html")
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`<html><head><title>Home</title></head><body><a href="/page1">Page 1</a><a href="/page2">Page 2</a></body></html>`))
		case "/page1":
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`<html><head><title>Page 1</title></head><body><a href="/page3">Page 3</a></body></html>`))
		case "/page2":
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`<html><head><title>Page 2</title></head><body></body></html>`))
		case "/page3":
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`<html><head><title>Page 3</title></head><body></body></html>`))
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer server.Close()

	// Create crawler
	config := Config{
		MaxWorkers:     2,
		MaxDepth:       2,
		RequestTimeout: 5 * time.Second,
		RateLimit:      10 * time.Millisecond,
	}

	crawler := New(config)
	defer crawler.Shutdown()

	// Crawl
	ctx := context.Background()
	results := crawler.Crawl(ctx, []string{server.URL})

	// Collect results
	var pages []Result
	for result := range results {
		pages = append(pages, result)
	}

	// Verify
	if len(pages) < 3 {
		t.Errorf("Expected at least 3 pages, got %d", len(pages))
	}

	// Check home page was crawled
	found := false
	for _, p := range pages {
		if p.URL == server.URL+"/" {
			found = true
			if p.Title != "Home" {
				t.Errorf("Expected title 'Home', got '%s'", p.Title)
			}
		}
	}
	if !found {
		t.Error("Home page not found in results")
	}
}

func TestRateLimiting(t *testing.T) {
	// Setup test server
	var requestTimes []time.Time
	var mu sync.Mutex
	
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		requestTimes = append(requestTimes, time.Now())
		mu.Unlock()
		
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`<html><head><title>Test</title></head><body></body></html>`))
	}))
	defer server.Close()

	// Create crawler with rate limit
	config := Config{
		MaxWorkers:     1,
		MaxDepth:       0,
		RequestTimeout: 5 * time.Second,
		RateLimit:      100 * time.Millisecond,
	}

	crawler := New(config)
	defer crawler.Shutdown()

	// Crawl same URL multiple times via different paths
	ctx := context.Background()
	
	// Create unique URLs that all redirect to same domain
	urls := []string{
		server.URL + "/page1",
		server.URL + "/page2",
		server.URL + "/page3",
	}

	results := crawler.Crawl(ctx, urls)
	
	// Drain results
	for range results {
	}

	mu.Lock()
	times := requestTimes
	mu.Unlock()

	// Verify rate limiting
	for i := 1; i < len(times); i++ {
		diff := times[i].Sub(times[i-1])
		if diff < 90*time.Millisecond {
			t.Errorf("Rate limit violated: %v between requests", diff)
		}
	}
}

func TestDepthLimit(t *testing.T) {
	// Setup test server with deep structure
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`<html><head><title>Page</title></head><body><a href="/deeper">Deeper</a></body></html>`))
	}))
	defer server.Close()

	// Create crawler with depth limit
	config := Config{
		MaxWorkers:     1,
		MaxDepth:       2,
		RequestTimeout: 5 * time.Second,
		RateLimit:      10 * time.Millisecond,
	}

	crawler := New(config)
	defer crawler.Shutdown()

	ctx := context.Background()
	results := crawler.Crawl(ctx, []string{server.URL + "/start"})

	// Count results
	count := 0
	for range results {
		count++
	}

	// Should be exactly 3 pages (depth 0, 1, 2)
	if count != 3 {
		t.Errorf("Expected 3 pages with depth limit 2, got %d", count)
	}
}

func TestRobotsTxt(t *testing.T) {
	// Setup test server with robots.txt
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/robots.txt" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`User-agent: *
Disallow: /private/
`))
			return
		}

		if r.URL.Path == "/private/secret" {
			t.Error("Should not access /private/secret")
		}

		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`<html><head><title>Public</title></head><body></body></html>`))
	}))
	defer server.Close()

	// Create crawler
	config := Config{
		MaxWorkers:     1,
		MaxDepth:       0,
		RequestTimeout: 5 * time.Second,
		RateLimit:      10 * time.Millisecond,
	}

	crawler := New(config)
	defer crawler.Shutdown()

	ctx := context.Background()
	results := crawler.Crawl(ctx, []string{
		server.URL + "/public",
		server.URL + "/private/secret",
	})

	var errors int
	for result := range results {
		if result.Error != nil {
			errors++
		}
	}

	if errors == 0 {
		t.Error("Expected error for /private/secret blocked by robots.txt")
	}
}

func TestURLDeduplication(t *testing.T) {
	// Setup test server
	var requestCount int64
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt64(&requestCount, 1)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`<html><head><title>Test</title></head><body></body></html>`))
	}))
	defer server.Close()

	urlSet := NewURLSet()
	url := server.URL + "/page"

	// Try to add same URL multiple times
	for i := 0; i < 10; i++ {
		urlSet.Add(url)
	}

	// Should only count as 1
	if urlSet.Size() != 1 {
		t.Errorf("Expected size 1, got %d", urlSet.Size())
	}
}

func TestGracefulShutdown(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(100 * time.Millisecond)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`<html><head><title>Test</title></head><body></body></html>`))
	}))
	defer server.Close()

	config := Config{
		MaxWorkers:     2,
		MaxDepth:       0,
		RequestTimeout: 5 * time.Second,
		RateLimit:      10 * time.Millisecond,
	}

	crawler := New(config)

	ctx, cancel := context.WithCancel(context.Background())
	
	// Start crawling
	results := crawler.Crawl(ctx, []string{server.URL + "/page1", server.URL + "/page2"})

	// Cancel after short time
	time.Sleep(50 * time.Millisecond)
	cancel()

	// Drain results
	for range results {
	}

	// Shutdown should complete without deadlock
	crawler.Shutdown()
}

func TestConcurrentCrawling(t *testing.T) {
	// Setup test server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(50 * time.Millisecond) // Simulate slow response
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`<html><head><title>Test</title></head><body></body></html>`))
	}))
	defer server.Close()

	config := Config{
		MaxWorkers:     5,
		MaxDepth:       0,
		RequestTimeout: 5 * time.Second,
		RateLimit:      10 * time.Millisecond,
	}

	crawler := New(config)
	defer crawler.Shutdown()

	start := time.Now()
	
	ctx := context.Background()
	urls := make([]string, 10)
	for i := 0; i < 10; i++ {
		urls[i] = server.URL + "/page" + string(rune('0'+i))
	}

	results := crawler.Crawl(ctx, urls)
	
	// Drain results
	for range results {
	}

	elapsed := time.Since(start)

	// With 5 workers, 10 pages @ 50ms each should take ~100ms, not 500ms
	if elapsed > 200*time.Millisecond {
		t.Errorf("Concurrent crawling too slow: %v", elapsed)
	}
}
```

## Usage Example

```go
// main.go
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"./crawler"
)

func main() {
	config := crawler.Config{
		MaxWorkers:     10,
		MaxDepth:       3,
		RequestTimeout: 30 * time.Second,
		UserAgent:      "MyBot/1.0",
		RateLimit:      1 * time.Second,
	}

	c := crawler.New(config)
	defer c.Shutdown()

	// Handle shutdown gracefully
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		fmt.Println("\nShutting down...")
		cancel()
	}()

	// Start crawling
	seeds := []string{
		"https://example.com",
		"https://example.org",
	}

	results := c.Crawl(ctx, seeds)

	// Process results
	for result := range results {
		if result.Error != nil {
			log.Printf("Error crawling %s: %v", result.URL, result.Error)
			continue
		}

		fmt.Printf("Crawled: %s (Title: %s, Links: %d)\n",
			result.URL, result.Title, len(result.Links))
	}
}
```

## Key Features

1. **Concurrent Workers**: Configurable worker pool for parallel crawling
2. **Rate Limiting**: Per-domain rate limiting to be polite
3. **URL Deduplication**: Bloom filter + exact map for memory efficiency
4. **Depth Limiting**: Prevent infinite crawling
5. **Robots.txt**: Automatic robots.txt parsing and compliance
6. **Graceful Shutdown**: Context-based cancellation

## Performance Considerations

- Bloom filter reduces memory usage for URL tracking
- Per-domain rate limiting prevents server overload
- Worker pool limits concurrent connections
- HTTP connection reuse via shared client

---

**Topic**: Go Concurrency Patterns
**Difficulty**: Intermediate-Advanced
**Generated**: 2026-02-18
