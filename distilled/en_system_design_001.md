# System Design Patterns

> Collection of essential distributed system patterns with Python implementations

---

## Pattern: Load Balancer Algorithms

### Implementation

```python
import random
from typing import List
from collections import deque
import hashlib

class Server:
    def __init__(self, name: str, weight: int = 1):
        self.name = name
        self.weight = weight
        self.connections = 0
    
    def __repr__(self):
        return f"Server({self.name}, weight={self.weight}, conns={self.connections})"

class LoadBalancer:
    def __init__(self, servers: List[Server]):
        self.servers = servers
        self.round_robin_index = 0
        self.weighted_index = 0
        self.current_weight = 0
        self.max_weight = max(s.weight for s in servers)
        self.gcd = self._compute_gcd([s.weight for s in servers])
    
    def _compute_gcd(self, weights: List[int]) -> int:
        from math import gcd
        result = weights[0]
        for w in weights[1:]:
            result = gcd(result, w)
        return result
    
    # Round Robin - Simple rotation through servers
    def round_robin(self) -> Server:
        server = self.servers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.servers)
        return server
    
    # Weighted Round Robin - Respect server capacity
    def weighted_round_robin(self) -> Server:
        while True:
            self.weighted_index = (self.weighted_index + 1) % len(self.servers)
            if self.weighted_index == 0:
                self.current_weight -= self.gcd
                if self.current_weight <= 0:
                    self.current_weight = self.max_weight
            if self.servers[self.weighted_index].weight >= self.current_weight:
                return self.servers[self.weighted_index]
    
    # Least Connections - Route to least busy server
    def least_connections(self) -> Server:
        return min(self.servers, key=lambda s: s.connections)
    
    # IP Hash - Consistent routing for same client
    def ip_hash(self, client_ip: str) -> Server:
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(self.servers)
        return self.servers[index]
    
    # Random - Simple random selection
    def random_select(self) -> Server:
        return random.choice(self.servers)


# Usage example
servers = [
    Server("server1", weight=3),
    Server("server2", weight=2),
    Server("server3", weight=1)
]

lb = LoadBalancer(servers)

# Different algorithms for different needs
print("Round Robin:", [lb.round_robin().name for _ in range(6)])
print("Least Conns:", lb.least_connections().name)
print("IP Hash:", lb.ip_hash("192.168.1.100").name)
```

### Explanation

**Architecture Overview:**

Load balancers distribute incoming network traffic across multiple servers to ensure no single server becomes overwhelmed. This improves responsiveness, availability, and reliability.

**Key Algorithms:**

1. **Round Robin**: Cycles through servers sequentially. Simple and fair for homogeneous servers.

2. **Weighted Round Robin**: Assigns more requests to higher-capacity servers based on weights. Ideal for heterogeneous infrastructure.

3. **Least Connections**: Routes to the server with fewest active connections. Adapts to varying request processing times.

4. **IP Hash**: Uses client IP to determine server, ensuring session persistence (sticky sessions).

5. **Random**: Simple distribution with no state tracking. Works well at scale with law of large numbers.

**Use Cases:**
- Web servers behind a reverse proxy (Nginx, HAProxy)
- Microservices gateway routing
- Database read replicas distribution
- CDN edge server selection

**Considerations:**
- Health checks to remove unhealthy servers
- Session persistence requirements
- Server capacity heterogeneity
- Geographic distribution for latency optimization

---

## Pattern: Circuit Breaker

### Implementation

```python
import time
from enum import Enum
from typing import Optional, Callable, Any
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            self.half_open_calls += 1
            if self.success_count >= self.half_open_max_calls:
                self._reset()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self._trip()
        elif self.failure_count >= self.failure_threshold:
            self._trip()
    
    def _trip(self):
        self.state = CircuitState.OPEN
        self.success_count = 0
        self.half_open_calls = 0
    
    def _reset(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.half_open_calls = 0
                return True
            return False
        
        # HALF_OPEN
        if self.half_open_calls < self.half_open_max_calls:
            return True
        return False
    
    def call(self, func: Callable, fallback: Optional[Callable] = None, *args, **kwargs) -> Any:
        if not self.can_execute():
            if fallback:
                return fallback(*args, **kwargs)
            raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            if fallback:
                return fallback(*args, **kwargs)
            raise
    
    @property
    def status(self) -> dict:
        return {
            "state": self.state.value,
            "failures": self.failure_count,
            "successes": self.success_count
        }


# Decorator usage
def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0):
    cb = CircuitBreaker(failure_threshold, recovery_timeout)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, None, *args, **kwargs)
        wrapper.circuit_breaker = cb
        return wrapper
    return decorator


# Usage example
class ExternalService:
    def __init__(self):
        self.cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10.0)
    
    def call_api(self, data: str) -> str:
        def fallback(data):
            return f"Cached response for: {data}"
        
        # Simulate API call
        def api_call(data):
            # In real scenario, this would make HTTP request
            import random
            if random.random() < 0.6:  # 60% failure rate
                raise ConnectionError("Service unavailable")
            return f"Success: {data}"
        
        return self.cb.call(api_call, fallback, data)


service = ExternalService()
for i in range(10):
    try:
        result = service.call_api(f"request_{i}")
        print(f"Request {i}: {result} | CB State: {service.cb.status}")
    except Exception as e:
        print(f"Request {i}: Error - {e} | CB State: {service.cb.status}")
```

### Explanation

**Architecture Overview:**

The Circuit Breaker pattern prevents cascading failures in distributed systems by detecting failures and stopping requests to failing services. It operates like an electrical circuit breaker, "tripping" when too many failures occur.

**Three States:**

1. **CLOSED**: Normal operation. Requests flow through. Failure count monitored.

2. **OPEN**: Circuit tripped. All requests fail fast without attempting the call. After timeout, transitions to HALF_OPEN.

3. **HALF_OPEN**: Test state. Allows limited requests to check if service recovered. Success → CLOSED, Failure → OPEN.

**Key Components:**

- **Failure Threshold**: Number of failures before tripping
- **Recovery Timeout**: Time to wait before attempting recovery
- **Fallback Function**: Alternative response when circuit is open
- **Half-Open Max Calls**: Number of test calls allowed during recovery

**Use Cases:**
- Microservices communication
- External API calls
- Database connections
- Message queue publishers

**Benefits:**
- Prevents cascading failures
- Fails fast, saving resources
- Allows graceful degradation
- Automatic recovery detection

**Best Practices:**
- Set appropriate thresholds based on SLAs
- Implement meaningful fallbacks (cache, default values)
- Monitor circuit state metrics
- Use different breakers for different services

---

## Pattern: Rate Limiter (Token Bucket)

### Implementation

```python
import time
from threading import Lock
from typing import Dict, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class TokenBucket:
    capacity: float          # Maximum tokens
    tokens: float            # Current tokens
    refill_rate: float       # Tokens added per second
    last_refill: float       # Last refill timestamp
    
    def refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now
    
    def consume(self, tokens: float = 1.0) -> bool:
        self.refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def time_until_available(self, tokens: float = 1.0) -> float:
        self.refill()
        if self.tokens >= tokens:
            return 0.0
        needed = tokens - self.tokens
        return needed / self.refill_rate


class RateLimiter:
    """
    Token Bucket Rate Limiter with per-client tracking.
    
    Each client gets their own bucket with configurable capacity and refill rate.
    """
    
    def __init__(
        self,
        capacity: float = 100.0,
        refill_rate: float = 10.0,  # tokens per second
        cost_per_request: float = 1.0
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.cost_per_request = cost_per_request
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = Lock()
    
    def _get_bucket(self, client_id: str) -> TokenBucket:
        if client_id not in self.buckets:
            self.buckets[client_id] = TokenBucket(
                capacity=self.capacity,
                tokens=self.capacity,  # Start full
                refill_rate=self.refill_rate,
                last_refill=time.time()
            )
        return self.buckets[client_id]
    
    def allow_request(self, client_id: str, tokens: Optional[float] = None) -> bool:
        """
        Check if request should be allowed.
        Returns True if allowed, False if rate limited.
        """
        with self.lock:
            bucket = self._get_bucket(client_id)
            cost = tokens if tokens is not None else self.cost_per_request
            return bucket.consume(cost)
    
    def wait_time(self, client_id: str, tokens: Optional[float] = None) -> float:
        """
        Get seconds until client can make request.
        """
        with self.lock:
            bucket = self._get_bucket(client_id)
            cost = tokens if tokens is not None else self.cost_per_request
            return bucket.time_until_available(cost)
    
    def get_status(self, client_id: str) -> dict:
        """
        Get current bucket status for a client.
        """
        with self.lock:
            bucket = self._get_bucket(client_id)
            bucket.refill()
            return {
                "client_id": client_id,
                "tokens_available": bucket.tokens,
                "capacity": bucket.capacity,
                "refill_rate": bucket.refill_rate,
                "utilization": 1 - (bucket.tokens / bucket.capacity)
            }


class SlidingWindowRateLimiter:
    """
    Alternative implementation using sliding window algorithm.
    Better for strict rate limiting (exactly N requests per window).
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def _cleanup(self, client_id: str):
        now = time.time()
        cutoff = now - self.window_seconds
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if ts > cutoff
        ]
    
    def allow_request(self, client_id: str) -> bool:
        with self.lock:
            self._cleanup(client_id)
            if len(self.requests[client_id]) < self.max_requests:
                self.requests[client_id].append(time.time())
                return True
            return False
    
    def remaining(self, client_id: str) -> int:
        with self.lock:
            self._cleanup(client_id)
            return self.max_requests - len(self.requests[client_id])


# Usage example
def simulate_api_requests():
    limiter = RateLimiter(capacity=10, refill_rate=2.0)
    
    client = "user_123"
    
    print("=== Token Bucket Rate Limiter Demo ===")
    print(f"Capacity: 10 tokens, Refill: 2 tokens/sec\n")
    
    # Burst of requests
    for i in range(15):
        allowed = limiter.allow_request(client)
        status = limiter.get_status(client)
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Rate Limited'} "
              f"| Tokens: {status['tokens_available']:.1f}")
    
    print("\nWaiting 3 seconds for refill...")
    time.sleep(3)
    
    for i in range(5):
        allowed = limiter.allow_request(client)
        status = limiter.get_status(client)
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Rate Limited'} "
              f"| Tokens: {status['tokens_available']:.1f}")


# API decorator
def rate_limit(limiter: RateLimiter, get_client_id: callable):
    def decorator(func):
        def wrapper(*args, **kwargs):
            client_id = get_client_id(*args, **kwargs)
            if not limiter.allow_request(client_id):
                wait = limiter.wait_time(client_id)
                raise Exception(f"Rate limited. Retry after {wait:.2f}s")
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    simulate_api_requests()
```

### Explanation

**Architecture Overview:**

The Token Bucket algorithm controls the rate of traffic by maintaining a bucket of tokens that are consumed per request and refilled at a constant rate. It allows for burst traffic up to the bucket capacity while maintaining an average rate limit.

**How It Works:**

1. **Bucket**: Container with maximum capacity (burst allowance)
2. **Tokens**: Each request consumes one or more tokens
3. **Refill Rate**: Tokens added periodically (e.g., 10 tokens/second)
4. **Request**: Allowed if tokens available, denied otherwise

**Key Concepts:**

- **Burst Capacity**: Full bucket allows rapid-fire requests up to capacity
- **Sustained Rate**: Long-term average limited by refill rate
- **Smooth Traffic**: No sharp cutoffs like fixed window limiters
- **Flexible Cost**: Different operations can consume different token amounts

**Token Bucket vs Sliding Window:**

| Feature | Token Bucket | Sliding Window |
|---------|--------------|----------------|
| Burst support | Yes | Limited |
| Memory usage | O(1) | O(n requests) |
| Precision | Average rate | Strict limit |
| Complexity | Low | Medium |

**Use Cases:**
- API rate limiting (per-user, per-API-key)
- Network traffic shaping
- Database query throttling
- Third-party API quota management
- DDoS protection

**Configuration Guidelines:**
- Set capacity for expected burst: `capacity = peak_rate × burst_duration`
- Set refill rate for average: `refill_rate = allowed_requests_per_second`
- Consider operation costs: expensive queries = more tokens

---

## Pattern: Cache-Aside (Lazy Loading)

### Implementation

```python
import time
import hashlib
import json
from typing import Optional, Any, Callable, Dict
from functools import wraps
from threading import Lock

class CacheEntry:
    def __init__(self, value: Any, ttl: float):
        self.value = value
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class InMemoryCache:
    """
    Simple in-memory cache implementation.
    In production, use Redis, Memcached, or similar.
    """
    
    def __init__(self, default_ttl: float = 300.0):
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            entry = self.cache.get(key)
            if entry is None or entry.is_expired():
                self.misses += 1
                if entry:
                    del self.cache[key]
                return None
            self.hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self.lock:
            self.cache[key] = CacheEntry(value, ttl or self.default_ttl)
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern (prefix)."""
        with self.lock:
            keys_to_delete = [k for k in self.cache if k.startswith(pattern)]
            for key in keys_to_delete:
                del self.cache[key]
            return len(keys_to_delete)
    
    def stats(self) -> dict:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "entries": len(self.cache)
    }


class CacheAsideService:
    """
    Cache-Aside Pattern Implementation
    
    Application manages both cache and database:
    - Read: Check cache → if miss, load from DB → update cache
    - Write: Update DB → invalidate/delete cache entry
    """
    
    def __init__(self, cache: InMemoryCache):
        self.cache = cache
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_or_load(
        self,
        key: str,
        loader: Callable[[], Any],
        ttl: Optional[float] = None
    ) -> Any:
        """
        Cache-Aside read pattern:
        1. Try cache first
        2. If miss, load from source
        3. Store in cache for future
        """
        # Step 1: Check cache
        value = self.cache.get(key)
        if value is not None:
            print(f"  [Cache HIT] Key: {key[:16]}...")
            return value
        
        print(f"  [Cache MISS] Key: {key[:16]}... Loading from source")
        
        # Step 2: Load from database/source
        value = loader()
        
        # Step 3: Update cache
        self.cache.set(key, value, ttl)
        
        return value
    
    def invalidate(self, key: str) -> bool:
        """
        Cache-Aside write pattern:
        After updating database, invalidate cache entry.
        """
        return self.cache.delete(key)
    
    def refresh(self, key: str, loader: Callable[[], Any], ttl: Optional[float] = None) -> Any:
        """Force refresh cache entry."""
        value = loader()
        self.cache.set(key, value, ttl)
        return value


def cached(cache_service: CacheAsideService, ttl: float = 300.0, key_prefix: str = ""):
    """
    Decorator for Cache-Aside pattern on functions.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}"
            args_key = cache_service._generate_key(*args, **kwargs)
            cache_key = f"{func_key}:{args_key}"
            
            return cache_service.get_or_load(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl
            )
        
        wrapper.cache_service = cache_service
        wrapper.invalidate = lambda *a, **kw: cache_service.invalidate(
            f"{key_prefix}:{func.__name__}:{cache_service._generate_key(*a, **kw)}"
        )
        
        return wrapper
    return decorator


# Simulated Database
class Database:
    def __init__(self):
        self.data = {
            "user:1": {"id": 1, "name": "Alice", "email": "alice@example.com"},
            "user:2": {"id": 2, "name": "Bob", "email": "bob@example.com"},
            "user:3": {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
        }
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Simulates slow database query."""
        time.sleep(0.1)  # Simulate latency
        return self.data.get(f"user:{user_id}")
    
    def update_user(self, user_id: int, updates: dict) -> dict:
        """Simulates database write."""
        time.sleep(0.05)
        key = f"user:{user_id}"
        if key in self.data:
            self.data[key].update(updates)
            return self.data[key]
        raise ValueError(f"User {user_id} not found")


# Usage Example
class UserService:
    def __init__(self):
        self.cache = InMemoryCache(default_ttl=60.0)
        self.cache_service = CacheAsideService(self.cache)
        self.db = Database()
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user with Cache-Aside pattern."""
        cache_key = f"user:{user_id}"
        return self.cache_service.get_or_load(
            cache_key,
            lambda: self.db.get_user(user_id),
            ttl=60.0
        )
    
    def update_user(self, user_id: int, updates: dict) -> dict:
        """
        Update user with Cache-Aside pattern:
        1. Update database
        2. Invalidate cache
        """
        # Update database
        user = self.db.update_user(user_id, updates)
        
        # Invalidate cache
        cache_key = f"user:{user_id}"
        self.cache_service.invalidate(cache_key)
        
        return user
    
    def get_cache_stats(self) -> dict:
        return self.cache.stats()


def demo_cache_aside():
    service = UserService()
    
    print("=== Cache-Aside Pattern Demo ===\n")
    
    # First read - cache miss
    print("1. First read (cache miss):")
    user = service.get_user(1)
    print(f"   Result: {user}\n")
    
    # Second read - cache hit
    print("2. Second read (cache hit):")
    user = service.get_user(1)
    print(f"   Result: {user}\n")
    
    # Update - invalidates cache
    print("3. Update user (invalidates cache):")
    user = service.update_user(1, {"email": "alice.new@example.com"})
    print(f"   Updated: {user}\n")
    
    # Read after update - cache miss (was invalidated)
    print("4. Read after update (cache miss):")
    user = service.get_user(1)
    print(f"   Result: {user}\n")
    
    # Cache stats
    print("5. Cache Statistics:")
    stats = service.get_cache_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    demo_cache_aside()
```

### Explanation

**Architecture Overview:**

The Cache-Aside pattern (also called Lazy Loading) separates cache management from the data store. The application code is responsible for maintaining cache consistency by checking cache first, loading from database on miss, and invalidating cache on updates.

**Read Flow:**
1. Application receives read request
2. Check cache for data
3. If found (HIT): return cached data
4. If not found (MISS): query database → store in cache → return data

**Write Flow:**
1. Application receives write request
2. Update database
3. Invalidate (delete) cache entry
4. Next read will load fresh data

**Key Principles:**

- **Lazy Loading**: Data loaded into cache only when requested
- **Explicit Invalidation**: Application must invalidate cache on writes
- **Eventual Consistency**: Cache might be stale briefly until invalidated
- **Fault Tolerance**: Cache failure doesn't break app (falls back to DB)

**Advantages:**
- Only caches actually-requested data
- Cache failures are non-fatal
- Works with any cache implementation
- Simple to understand and implement

**Disadvantages:**
- Cache miss penalty (two trips)
- Stale data risk if invalidation fails
- Cache stampede on miss
- Application code complexity

**Best Practices:**
- Set appropriate TTLs as safety net
- Use cache warming for hot data
- Implement cache stampede protection (locks, early refresh)
- Monitor hit rates and adjust strategies
- Consider Write-Through for write-heavy workloads

**Use Cases:**
- Web session storage
- User profile data
- Configuration/settings
- Frequently read, infrequently updated data
- API response caching

---

## Pattern: Message Queue

### Implementation

```python
import time
import threading
import queue
from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
import json
from abc import ABC, abstractmethod

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Message:
    id: str
    topic: str
    payload: Any
    created_at: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "payload": self.payload,
            "created_at": self.created_at,
            "retry_count": self.retry_count,
            "status": self.status.value,
            "error": self.error
        }

class MessageQueue:
    """
    In-memory message queue implementation.
    Production: Use RabbitMQ, Kafka, SQS, Redis Streams, etc.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.queues: Dict[str, queue.Queue] = {}
        self.dead_letter_queue: List[Message] = []
        self.handlers: Dict[str, List[Callable]] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()
    
    def create_queue(self, topic: str) -> None:
        """Create a queue for a topic."""
        with self.lock:
            if topic not in self.queues:
                self.queues[topic] = queue.Queue()
                self.handlers[topic] = []
    
    def publish(self, topic: str, payload: Any, message_id: Optional[str] = None) -> str:
        """
        Publish message to topic queue.
        Returns message ID.
        """
        if topic not in self.queues:
            self.create_queue(topic)
        
        msg_id = message_id or f"{topic}-{time.time()}-{id(payload)}"
        message = Message(
            id=msg_id,
            topic=topic,
            payload=payload
        )
        
        self.queues[topic].put(message)
        print(f"[{self.name}] Published to '{topic}': {msg_id[:30]}...")
        return msg_id
    
    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        """
        Subscribe handler to topic.
        Multiple handlers = competing consumers (load balancing).
        """
        if topic not in self.queues:
            self.create_queue(topic)
        
        self.handlers[topic].append(handler)
        print(f"[{self.name}] Subscribed handler to '{topic}'")
    
    def _process_message(self, message: Message) -> bool:
        """Process single message with error handling."""
        message.status = MessageStatus.PROCESSING
        
        handlers = self.handlers.get(message.topic, [])
        if not handlers:
            print(f"[{self.name}] No handlers for topic: {message.topic}")
            return False
        
        # Use first available handler (competing consumers)
        handler = handlers[message.retry_count % len(handlers)]
        
        try:
            handler(message)
            message.status = MessageStatus.COMPLETED
            print(f"[{self.name}] ✓ Completed: {message.id[:30]}...")
            return True
        except Exception as e:
            message.retry_count += 1
            message.error = str(e)
            
            if message.retry_count >= message.max_retries:
                message.status = MessageStatus.FAILED
                self.dead_letter_queue.append(message)
                print(f"[{self.name}] ✗ Failed (max retries): {message.id[:30]}... Error: {e}")
                return False
            else:
                message.status = MessageStatus.PENDING
                # Re-queue for retry
                self.queues[message.topic].put(message)
                print(f"[{self.name}] ↻ Retry {message.retry_count}/{message.max_retries}: {message.id[:30]}...")
                return False
    
    def start_workers(self, num_workers: int = 2) -> None:
        """Start background worker threads."""
        self.running = True
        
        def worker():
            while self.running:
                for topic, q in self.queues.items():
                    try:
                        message = q.get(timeout=0.1)
                        self._process_message(message)
                    except queue.Empty:
                        continue
        
        for i in range(num_workers):
            worker_thread = threading.Thread(target=worker, daemon=True)
            worker_thread.start()
            self.workers.append(worker_thread)
        
        print(f"[{self.name}] Started {num_workers} workers")
    
    def stop(self) -> None:
        """Stop all workers."""
        self.running = False
        for w in self.workers:
            w.join(timeout=1.0)
        print(f"[{self.name}] Stopped")
    
    def stats(self) -> dict:
        return {
            "name": self.name,
            "topics": list(self.queues.keys()),
            "queue_sizes": {t: q.qsize() for t, q in self.queues.items()},
            "dead_letter_count": len(self.dead_letter_queue),
            "workers": len(self.workers)
        }


# Publisher/Subscriber Pattern (Pub/Sub)
class PubSubBroker:
    """
    Publish-Subscribe pattern: One message → Multiple subscribers.
    Each subscriber gets a copy of the message.
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe to receive ALL messages on topic."""
        with self.lock:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
            self.subscriptions[topic].append(handler)
    
    def publish(self, topic: str, payload: Any) -> int:
        """Broadcast to all subscribers. Returns subscriber count."""
        handlers = self.subscriptions.get(topic, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                print(f"Handler error: {e}")
        return len(handlers)


# Request-Reply Pattern
class RequestReplyQueue:
    """
    Request-Reply pattern: Send request, wait for response.
    Implements correlation ID pattern for async reply matching.
    """
    
    def __init__(self, mq: MessageQueue):
        self.mq = mq
        self.pending_requests: Dict[str, queue.Queue] = {}
        self.lock = threading.Lock()
        
        # Subscribe to reply topic
        mq.subscribe("reply", self._handle_reply)
    
    def _handle_reply(self, message: Message) -> None:
        """Route reply to waiting request."""
        correlation_id = message.payload.get("correlation_id")
        reply_data = message.payload.get("data")
        
        with self.lock:
            if correlation_id in self.pending_requests:
                self.pending_requests[correlation_id].put(reply_data)
    
    def request(
        self,
        topic: str,
        payload: Any,
        timeout: float = 5.0
    ) -> Optional[Any]:
        """
        Send request and wait for reply.
        Blocks until reply received or timeout.
        """
        import uuid
        correlation_id = str(uuid.uuid4())
        
        # Create reply queue for this request
        reply_queue = queue.Queue()
        with self.lock:
            self.pending_requests[correlation_id] = reply_queue
        
        # Publish request with correlation ID
        request_payload = {
            "data": payload,
            "correlation_id": correlation_id,
            "reply_to": "reply"
        }
        self.mq.publish(topic, request_payload)
        
        # Wait for reply
        try:
            return reply_queue.get(timeout=timeout)
        except queue.Empty:
            return None
        finally:
            with self.lock:
                del self.pending_requests[correlation_id]
    
    def reply(self, correlation_id: str, data: Any) -> None:
        """Send reply for a request."""
        self.mq.publish("reply", {
            "correlation_id": correlation_id,
            "data": data
        })


# Usage Examples
def demo_message_queue():
    print("=== Message Queue Pattern Demo ===\n")
    
    mq = MessageQueue("OrderService")
    
    # Define handlers
    def process_payment(message: Message):
        order = message.payload
        print(f"  Processing payment for order: {order['order_id']}")
        if order.get("fail_payment"):
            raise Exception("Payment declined")
        time.sleep(0.1)  # Simulate processing
    
    def send_confirmation(message: Message):
        order = message.payload
        print(f"  Sending confirmation email to: {order['email']}")
        time.sleep(0.05)
    
    def update_inventory(message: Message):
        order = message.payload
        print(f"  Updating inventory for items: {order['items']}")
        time.sleep(0.05)
    
    # Subscribe handlers
    mq.subscribe("payment", process_payment)
    mq.subscribe("notification", send_confirmation)
    mq.subscribe("inventory", update_inventory)
    
    # Start workers
    mq.start_workers(num_workers=2)
    
    # Publish messages
    print("\n1. Publishing successful order:")
    mq.publish("payment", {
        "order_id": "ORD-001",
        "email": "customer@example.com",
        "items": ["item1", "item2"],
        "amount": 99.99
    })
    
    mq.publish("notification", {
        "order_id": "ORD-001",
        "email": "customer@example.com"
    })
    
    mq.publish("inventory", {
        "order_id": "ORD-001",
        "items": ["item1", "item2"]
    })
    
    print("\n2. Publishing order with payment failure:")
    mq.publish("payment", {
        "order_id": "ORD-002",
        "email": "fail@example.com",
        "items": ["item3"],
        "fail_payment": True
    })
    
    # Wait for processing
    time.sleep(2)
    
    # Stats
    print("\n3. Queue Statistics:")
    stats = mq.stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    mq.stop()


def demo_pubsub():
    print("\n=== Pub/Sub Pattern Demo ===\n")
    
    broker = PubSubBroker()
    
    # Multiple subscribers for same topic
    def log_analytics(payload):
        print(f"  [Analytics] Logged: {payload['event']}")
    
    def send_push(payload):
        print(f"  [Push] Sent notification: {payload['event']}")
    
    def update_dashboard(payload):
        print(f"  [Dashboard] Updated: {payload['event']}")
    
    broker.subscribe("user_action", log_analytics)
    broker.subscribe("user_action", send_push)
    broker.subscribe("user_action", update_dashboard)
    
    print("Publishing 'user_action' event:")
    subscribers = broker.publish("user_action", {"event": "user_login", "user_id": 123})
    print(f"Delivered to {subscribers} subscribers")


if __name__ == "__main__":
    demo_message_queue()
    demo_pubsub()
```

### Explanation

**Architecture Overview:**

Message Queues enable asynchronous communication between services by decoupling message production from consumption. Producers publish messages to queues, and consumers process them independently, enabling scalability, reliability, and loose coupling.

**Core Patterns:**

1. **Point-to-Point (Queue)**
   - One producer → One consumer
   - Messages processed once
   - Load balancing across consumers

2. **Publish-Subscribe (Topic)**
   - One producer → Multiple subscribers
   - Each subscriber receives copy
   - Event broadcasting

3. **Request-Reply**
   - Synchronous-like over async queue
   - Correlation IDs match requests to replies
   - Timeout handling for reliability

**Key Components:**

- **Producer/Publisher**: Creates and sends messages
- **Consumer/Subscriber**: Receives and processes messages
- **Queue/Topic**: Storage for messages until consumed
- **Broker**: Middleware managing message routing
- **Dead Letter Queue**: Stores failed messages

**Reliability Features:**

- **Retry Logic**: Automatic retries on failure
- **Dead Letter Queue**: Capture permanently failed messages
- **Message Persistence**: Survive broker restarts
- **Acknowledgments**: Confirm successful processing
- **Idempotency**: Handle duplicate messages safely

**Use Cases:**

| Pattern | Use Case |
|---------|----------|
| Point-to-Point | Order processing, email sending |
| Pub-Sub | Event notifications, logging |
| Request-Reply | Remote procedure calls, sync operations |

**Benefits:**
- **Decoupling**: Services don't need to know about each other
- **Scalability**: Add consumers to handle load
- **Reliability**: Messages survive failures
- **Buffering**: Handle traffic spikes gracefully
- **Async Processing**: Don't block user requests

**Production Considerations:**
- Message ordering guarantees
- Exactly-once vs at-least-once delivery
- Monitoring and alerting on queue depth
- Consumer scaling strategies
- Message serialization formats

---

## Summary

These five patterns form the foundation of resilient distributed systems:

| Pattern | Problem Solved | Key Benefit |
|---------|---------------|-------------|
| **Load Balancer** | Traffic distribution | High availability & scalability |
| **Circuit Breaker** | Cascading failures | Fault tolerance & fast failure |
| **Rate Limiter** | Resource exhaustion | Protection & fair usage |
| **Cache-Aside** | Slow data access | Performance optimization |
| **Message Queue** | Synchronous coupling | Decoupling & async processing |

**Integration Points:**

1. **Load Balancer** distributes requests across service instances
2. **Circuit Breaker** protects calls to external services/databases
3. **Rate Limiter** prevents abuse of your service endpoints
4. **Cache-Aside** reduces database load for frequently accessed data
5. **Message Queue** handles async operations and inter-service communication

Combined effectively, these patterns enable building scalable, resilient, and maintainable distributed systems.

---

*Document generated: 2025-02-18*
*Pattern collection: System Design Essentials v1.0*
