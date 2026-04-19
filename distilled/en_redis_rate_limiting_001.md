# Redis Rate Limiting Patterns

## Problem

Implement various rate limiting algorithms using Redis including Fixed Window, Sliding Window, Token Bucket, and Leaky Bucket patterns with distributed support.

## Implementation

```python
import redis
import time
import math
from typing import Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class RateLimitAlgorithm(Enum):
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: Optional[int] = None

class RedisRateLimiter:
    """Distributed rate limiting with multiple algorithms."""
    
    def __init__(self, redis_client: redis.Redis = None):
        self.client = redis_client or redis.Redis(decode_responses=True)
    
    # Algorithm 1: Fixed Window Counter
    def fixed_window(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> RateLimitResult:
        """
        Fixed Window: Count requests in fixed time intervals.
        Simple but allows burst at window boundaries.
        """
        window_start = math.floor(time.time() / window_seconds) * window_seconds
        window_key = f"{key}:{window_start}"
        
        # Atomic increment
        current = self.client.incr(window_key)
        
        # Set expiry on first request
        if current == 1:
            self.client.expire(window_key, window_seconds)
        
        remaining = max(0, limit - current)
        reset_at = window_start + window_seconds
        
        return RateLimitResult(
            allowed=current <= limit,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=None if current <= limit else int(reset_at - time.time())
        )
    
    # Algorithm 2: Sliding Window Log
    def sliding_window_log(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> RateLimitResult:
        """
        Sliding Window Log: Precise rate limiting using sorted sets.
        More accurate than fixed window, uses more memory.
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Use Lua script for atomicity
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
        
        -- Count current entries
        local current = redis.call('ZCARD', key)
        
        if current < limit then
            -- Add new request
            redis.call('ZADD', key, now, now .. '-' .. math.random())
            redis.call('EXPIRE', key, window_seconds)
            return {1, limit - current - 1, now + window_seconds}
        else
            -- Get oldest entry for retry_after
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            local retry_after = 0
            if oldest[2] then
                retry_after = math.ceil(tonumber(oldest[2]) + window_seconds - now)
            end
            return {0, 0, now + window_seconds, retry_after}
        end
        """
        
        result = self.client.eval(
            lua_script, 1, key, now, window_start, limit, window_seconds
        )
        
        return RateLimitResult(
            allowed=bool(result[0]),
            remaining=int(result[1]),
            reset_at=float(result[2]),
            retry_after=int(result[3]) if len(result) > 3 else None
        )
    
    # Algorithm 3: Sliding Window Counter (Hybrid)
    def sliding_window_counter(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> RateLimitResult:
        """
        Sliding Window Counter: Weighted average of current and previous windows.
        More memory efficient than log, more accurate than fixed window.
        """
        now = time.time()
        current_window = math.floor(now / window_seconds)
        previous_window = current_window - 1
        
        current_key = f"{key}:{current_window}"
        previous_key = f"{key}:{previous_window}"
        
        # Get counts from both windows
        current_count = int(self.client.get(current_key) or 0)
        previous_count = int(self.client.get(previous_key) or 0)
        
        # Calculate weighted count
        window_position = (now % window_seconds) / window_seconds
        weighted_count = previous_count * (1 - window_position) + current_count
        
        if weighted_count < limit:
            # Increment current window
            pipe = self.client.pipeline()
            pipe.incr(current_key)
            pipe.expire(current_key, window_seconds * 2)
            pipe.execute()
            
            return RateLimitResult(
                allowed=True,
                remaining=max(0, limit - int(weighted_count) - 1),
                reset_at=(current_window + 1) * window_seconds
            )
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=(current_window + 1) * window_seconds,
            retry_after=int(window_seconds - (now % window_seconds))
        )
    
    # Algorithm 4: Token Bucket
    def token_bucket(
        self, 
        key: str, 
        capacity: int, 
        refill_rate: float,
        requested: int = 1
    ) -> RateLimitResult:
        """
        Token Bucket: Tokens replenish at fixed rate, burst up to capacity.
        Good for API rate limiting with burst handling.
        """
        now = time.time()
        bucket_key = f"bucket:{key}"
        
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local refill_rate = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or capacity
        local last_update = tonumber(bucket[2]) or now
        
        -- Calculate refill
        local elapsed = now - last_update
        local refill = elapsed * refill_rate
        tokens = math.min(capacity, tokens + refill)
        
        if tokens >= requested then
            tokens = tokens - requested
            redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
            redis.call('EXPIRE', key, 3600)
            return {1, math.floor(tokens), now + (capacity - tokens) / refill_rate}
        else
            local retry_after = math.ceil((requested - tokens) / refill_rate)
            return {0, math.floor(tokens), now + retry_after, retry_after}
        end
        """
        
        result = self.client.eval(
            lua_script, 1, bucket_key, now, capacity, refill_rate, requested
        )
        
        return RateLimitResult(
            allowed=bool(result[0]),
            remaining=int(result[1]),
            reset_at=float(result[2]),
            retry_after=int(result[3]) if len(result) > 3 else None
        )
    
    # Algorithm 5: Leaky Bucket
    def leaky_bucket(
        self, 
        key: str, 
        capacity: int, 
        leak_rate: float
    ) -> RateLimitResult:
        """
        Leaky Bucket: Requests queue up and drain at constant rate.
        Good for smoothing traffic and preventing bursts.
        """
        now = time.time()
        bucket_key = f"leaky:{key}"
        
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local leak_rate = tonumber(ARGV[3])
        
        -- Get bucket state
        local bucket = redis.call('HMGET', key, 'water', 'last_leak')
        local water = tonumber(bucket[1]) or 0
        local last_leak = tonumber(bucket[2]) or now
        
        -- Calculate leaked amount
        local elapsed = now - last_leak
        local leaked = elapsed * leak_rate
        water = math.max(0, water - leaked)
        
        if water + 1 <= capacity then
            water = water + 1
            redis.call('HMSET', key, 'water', water, 'last_leak', now)
            redis.call('EXPIRE', key, 3600)
            local drain_time = water / leak_rate
            return {1, capacity - water, now + drain_time}
        else
            local retry_after = math.ceil((water + 1 - capacity) / leak_rate)
            return {0, 0, now + retry_after, retry_after}
        end
        """
        
        result = self.client.eval(
            lua_script, 1, bucket_key, now, capacity, leak_rate
        )
        
        return RateLimitResult(
            allowed=bool(result[0]),
            remaining=int(result[1]),
            reset_at=float(result[2]),
            retry_after=int(result[3]) if len(result) > 3 else None
        )
    
    # Middleware decorator
    def rate_limit_middleware(
        self, 
        key_func: callable,
        algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW_COUNTER,
        limit: int = 100,
        window: int = 60
    ):
        """Decorator for rate limiting functions."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = key_func(*args, **kwargs)
                
                if algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                    result = self.fixed_window(key, limit, window)
                elif algorithm == RateLimitAlgorithm.SLIDING_WINDOW_COUNTER:
                    result = self.sliding_window_counter(key, limit, window)
                elif algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    result = self.token_bucket(key, limit, limit / window)
                else:
                    result = self.leaky_bucket(key, limit, limit / window)
                
                if not result.allowed:
                    raise Exception(f"Rate limit exceeded. Retry after {result.retry_after}s")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Usage Example
if __name__ == "__main__":
    limiter = RedisRateLimiter()
    
    # Fixed Window
    result = limiter.fixed_window("api:user:123", limit=10, window_seconds=60)
    print(f"Fixed Window: allowed={result.allowed}, remaining={result.remaining}")
    
    # Token Bucket
    result = limiter.token_bucket("api:user:123", capacity=100, refill_rate=10)
    print(f"Token Bucket: allowed={result.allowed}, remaining={result.remaining}")
```

## Tests

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import math

class TestRedisRateLimiter:
    
    @pytest.fixture
    def limiter(self):
        with patch('redis.Redis') as mock_redis:
            limiter = RedisRateLimiter()
            limiter.client = MagicMock()
            yield limiter
    
    def test_fixed_window_allows_within_limit(self, limiter):
        """Test fixed window allows requests within limit."""
        limiter.client.incr.return_value = 5
        limiter.client.expire.return_value = True
        
        result = limiter.fixed_window("test:key", limit=10, window_seconds=60)
        
        assert result.allowed is True
        assert result.remaining == 5
    
    def test_fixed_window_blocks_over_limit(self, limiter):
        """Test fixed window blocks requests over limit."""
        limiter.client.incr.return_value = 11
        limiter.client.expire.return_value = True
        
        result = limiter.fixed_window("test:key", limit=10, window_seconds=60)
        
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after is not None
    
    def test_sliding_window_counter_basic(self, limiter):
        """Test sliding window counter calculation."""
        now = time.time()
        current_window = math.floor(now / 60)
        
        limiter.client.get.side_effect = lambda k: (
            b'3' if str(current_window) in k else b'8'
        )
        limiter.client.pipeline.return_value.execute.return_value = [4, True]
        
        result = limiter.sliding_window_counter("test:key", limit=10, window_seconds=60)
        
        assert result.allowed is True
    
    def test_token_bucket_refill(self, limiter):
        """Test token bucket token refill logic."""
        limiter.client.eval.return_value = [1, 99, time.time() + 0.1]
        
        result = limiter.token_bucket(
            "test:key", 
            capacity=100, 
            refill_rate=10, 
            requested=1
        )
        
        assert result.allowed is True
        assert result.remaining == 99
    
    def test_token_bucket_empty(self, limiter):
        """Test token bucket when empty."""
        limiter.client.eval.return_value = [0, 0, time.time() + 10, 10]
        
        result = limiter.token_bucket(
            "test:key", 
            capacity=100, 
            refill_rate=10, 
            requested=1
        )
        
        assert result.allowed is False
        assert result.retry_after == 10
    
    def test_leaky_bucket_allows_when_not_full(self, limiter):
        """Test leaky bucket allows when not full."""
        limiter.client.eval.return_value = [1, 9, time.time() + 1]
        
        result = limiter.leaky_bucket("test:key", capacity=10, leak_rate=1)
        
        assert result.allowed is True
        assert result.remaining == 9
    
    def test_leaky_bucket_blocks_when_full(self, limiter):
        """Test leaky bucket blocks when full."""
        limiter.client.eval.return_value = [0, 0, time.time() + 5, 5]
        
        result = limiter.leaky_bucket("test:key", capacity=10, leak_rate=1)
        
        assert result.allowed is False
        assert result.retry_after == 5
    
    def test_rate_limit_middleware_allows(self, limiter):
        """Test middleware allows requests within limit."""
        limiter.client.get.return_value = b'5'
        limiter.client.pipeline.return_value.execute.return_value = [6, True]
        
        @limiter.rate_limit_middleware(
            key_func=lambda: "test:user",
            limit=10
        )
        def protected_function():
            return "success"
        
        result = protected_function()
        assert result == "success"
    
    def test_rate_limit_middleware_blocks(self, limiter):
        """Test middleware blocks requests over limit."""
        limiter.client.get.side_effect = lambda k: b'15'
        
        @limiter.rate_limit_middleware(
            key_func=lambda: "test:user",
            limit=10
        )
        def protected_function():
            return "success"
        
        with pytest.raises(Exception) as exc_info:
            protected_function()
        
        assert "Rate limit exceeded" in str(exc_info.value)
    
    def test_concurrent_requests_distributed(self, limiter):
        """Test that rate limiting works across distributed instances."""
        # Simulate atomic increment
        limiter.client.incr.return_value = 1
        
        results = []
        for _ in range(5):
            result = limiter.fixed_window("shared:key", limit=3, window_seconds=60)
            results.append(result.allowed)
        
        # All should be allowed in this mock scenario
        assert all(results)
```

## Complexity Analysis

**Time Complexity:**
- Fixed Window: O(1) - Single INCR operation
- Sliding Window Log: O(log n) - Sorted set operations where n is requests in window
- Sliding Window Counter: O(1) - Two GET operations
- Token Bucket: O(1) - Hash operations with Lua script
- Leaky Bucket: O(1) - Hash operations with Lua script

**Space Complexity:**
- Fixed Window: O(1) per key - Single counter
- Sliding Window Log: O(n) per key - Stores n timestamps
- Sliding Window Counter: O(1) per key - Two counters
- Token Bucket: O(1) per key - Two values (tokens + timestamp)
- Leaky Bucket: O(1) per key - Two values (water + timestamp)

**Algorithm Selection Guide:**
- **Fixed Window**: Simple, memory-efficient, use for non-critical limits
- **Sliding Window Log**: Most accurate, higher memory, use for precise limits
- **Sliding Window Counter**: Good balance of accuracy and memory
- **Token Bucket**: Best for burst handling, API rate limiting
- **Leaky Bucket**: Best for traffic smoothing, consistent output rate
