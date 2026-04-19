# Redis Caching Patterns

## Problem

Implement common Redis caching patterns including Cache-Aside, Write-Through, and Cache-Invalidation strategies with proper error handling and TTL management.

## Implementation

```python
import redis
import json
import functools
from typing import Optional, Any, Callable, TypeVar, T
from datetime import timedelta
import hashlib

T = TypeVar('T')

class RedisCacheManager:
    """Comprehensive Redis caching patterns implementation."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    # Pattern 1: Cache-Aside (Lazy Loading)
    def cache_aside_get(
        self, 
        key: str, 
        db_fetch: Callable[[], T],
        ttl: int = None
    ) -> T:
        """
        Cache-Aside pattern: Check cache first, fetch from DB on miss.
        Most common caching pattern.
        """
        # Try cache first
        cached = self.client.get(key)
        if cached is not None:
            return json.loads(cached)
        
        # Cache miss - fetch from database
        data = db_fetch()
        
        # Store in cache
        self.client.setex(
            key, 
            ttl or self.default_ttl, 
            json.dumps(data, default=str)
        )
        return data
    
    # Pattern 2: Write-Through
    def write_through(
        self, 
        key: str, 
        data: Any, 
        db_write: Callable[[Any], bool],
        ttl: int = None
    ) -> bool:
        """
        Write-Through pattern: Write to cache and database simultaneously.
        Ensures cache-database consistency.
        """
        # Write to database first
        if not db_write(data):
            return False
        
        # Then update cache
        self.client.setex(
            key, 
            ttl or self.default_ttl, 
            json.dumps(data, default=str)
        )
        return True
    
    # Pattern 3: Write-Behind (Write-Back)
    def write_behind(
        self, 
        key: str, 
        data: Any,
        write_queue: list
    ) -> bool:
        """
        Write-Behind pattern: Write to cache immediately, 
        persist to database asynchronously.
        """
        # Update cache immediately
        self.client.set(key, json.dumps(data, default=str))
        
        # Queue for async database write
        write_queue.append({'key': key, 'data': data})
        return True
    
    # Pattern 4: Refresh-Ahead
    def refresh_ahead_get(
        self, 
        key: str, 
        db_fetch: Callable[[], T],
        refresh_threshold: float = 0.8,
        ttl: int = None
    ) -> T:
        """
        Refresh-Ahead: Proactively refresh cache before expiration.
        refresh_threshold: percentage of TTL before refresh (0.8 = 80%)
        """
        ttl = ttl or self.default_ttl
        cached = self.client.get(key)
        
        if cached is not None:
            data = json.loads(cached)
            # Check remaining TTL
            remaining_ttl = self.client.ttl(key)
            if remaining_ttl < ttl * (1 - refresh_threshold):
                # Async refresh (in production, use background task)
                self.client.setex(key, ttl, json.dumps(db_fetch(), default=str))
            return data
        
        # Cache miss
        data = db_fetch()
        self.client.setex(key, ttl, json.dumps(data, default=str))
        return data
    
    # Cache Invalidation Strategies
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0
    
    def invalidate_tag(self, tag: str) -> int:
        """Tag-based invalidation using Redis sets."""
        tag_key = f"tag:{tag}"
        keys = self.client.smembers(tag_key)
        if keys:
            deleted = self.client.delete(*keys)
            self.client.delete(tag_key)
            return deleted
        return 0
    
    def tag_key(self, key: str, tags: list) -> None:
        """Associate a key with tags for group invalidation."""
        for tag in tags:
            self.client.sadd(f"tag:{tag}", key)
    
    # Decorator for easy caching
    def cached(
        self, 
        key_prefix: str, 
        ttl: int = None,
        key_builder: Callable = None
    ):
        """Decorator for caching function results."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    args_hash = hashlib.md5(
                        str((args, kwargs)).encode()
                    ).hexdigest()[:8]
                    cache_key = f"{key_prefix}:{func.__name__}:{args_hash}"
                
                return self.cache_aside_get(
                    cache_key,
                    lambda: func(*args, **kwargs),
                    ttl
                )
            return wrapper
        return decorator


# Usage Examples
if __name__ == "__main__":
    cache = RedisCacheManager()
    
    # Cache-Aside pattern
    def fetch_user(user_id: int) -> dict:
        print(f"Fetching user {user_id} from database...")
        return {"id": user_id, "name": f"User{user_id}"}
    
    user = cache.cache_aside_get(
        "user:1", 
        lambda: fetch_user(1),
        ttl=300
    )
    print(f"User: {user}")
    
    # Using decorator
    @cache.cached("products", ttl=600)
    def get_product(product_id: int) -> dict:
        print(f"Fetching product {product_id}...")
        return {"id": product_id, "price": 99.99}
    
    product = get_product(1)  # Fetches from DB
    product = get_product(1)  # Fetches from cache
```

## Tests

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import time

class TestRedisCachingPatterns:
    
    @pytest.fixture
    def cache_manager(self):
        with patch('redis.Redis') as mock_redis:
            manager = RedisCacheManager()
            manager.client = MagicMock()
            yield manager
    
    def test_cache_aside_hit(self, cache_manager):
        """Test cache-aside pattern with cache hit."""
        cache_manager.client.get.return_value = '{"id": 1, "name": "Test"}'
        
        result = cache_manager.cache_aside_get(
            "user:1",
            lambda: {"id": 1, "name": "DB User"}
        )
        
        assert result == {"id": 1, "name": "Test"}
        cache_manager.client.get.assert_called_once_with("user:1")
        cache_manager.client.setex.assert_not_called()
    
    def test_cache_aside_miss(self, cache_manager):
        """Test cache-aside pattern with cache miss."""
        cache_manager.client.get.return_value = None
        
        db_data = {"id": 1, "name": "DB User"}
        result = cache_manager.cache_aside_get(
            "user:1",
            lambda: db_data,
            ttl=300
        )
        
        assert result == db_data
        cache_manager.client.setex.assert_called_once()
    
    def test_write_through_success(self, cache_manager):
        """Test write-through pattern success."""
        db_write_mock = Mock(return_value=True)
        data = {"id": 1, "name": "Test"}
        
        result = cache_manager.write_through(
            "user:1",
            data,
            db_write_mock,
            ttl=300
        )
        
        assert result is True
        db_write_mock.assert_called_once_with(data)
        cache_manager.client.setex.assert_called_once()
    
    def test_write_through_db_failure(self, cache_manager):
        """Test write-through with database failure."""
        db_write_mock = Mock(return_value=False)
        
        result = cache_manager.write_through(
            "user:1",
            {"id": 1},
            db_write_mock
        )
        
        assert result is False
        cache_manager.client.setex.assert_not_called()
    
    def test_invalidate_pattern(self, cache_manager):
        """Test pattern-based cache invalidation."""
        cache_manager.client.keys.return_value = ["user:1", "user:2"]
        cache_manager.client.delete.return_value = 2
        
        result = cache_manager.invalidate_pattern("user:*")
        
        assert result == 2
        cache_manager.client.keys.assert_called_once_with("user:*")
    
    def test_tag_based_invalidation(self, cache_manager):
        """Test tag-based cache invalidation."""
        cache_manager.client.smembers.return_value = {"product:1", "product:2"}
        cache_manager.client.delete.return_value = 2
        
        result = cache_manager.invalidate_tag("products")
        
        assert result == 2
    
    def test_cached_decorator(self, cache_manager):
        """Test caching decorator."""
        cache_manager.client.get.return_value = None
        
        call_count = 0
        
        @cache_manager.cached("test", ttl=60)
        def expensive_function(n):
            nonlocal call_count
            call_count += 1
            return n * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert call_count == 2  # Called twice (no cache hit in mock)
    
    def test_refresh_ahead_triggers_refresh(self, cache_manager):
        """Test refresh-ahead triggers refresh when TTL is low."""
        cache_manager.client.get.return_value = '{"data": "test"}'
        cache_manager.client.ttl.return_value = 50  # Low TTL
        cache_manager.client.setex.return_value = True
        
        result = cache_manager.refresh_ahead_get(
            "key",
            lambda: {"data": "fresh"},
            ttl=300
        )
        
        assert result == {"data": "test"}
        cache_manager.client.setex.assert_called()
```

## Complexity Analysis

**Time Complexity:**
- Cache-Aside Get: O(1) for cache hit, O(f) + O(1) for cache miss where f is DB fetch time
- Write-Through: O(db_write) + O(1) for cache update
- Pattern Invalidation: O(n) where n is number of matching keys
- Tag Invalidation: O(m) where m is number of tagged keys

**Space Complexity:**
- O(k) where k is the total cached data size
- Tag-based invalidation adds O(t × m) for tag-key mappings

**Best Practices:**
- Use Cache-Aside for read-heavy workloads
- Use Write-Through for consistency-critical data
- Implement circuit breakers for cache failures
- Set appropriate TTLs based on data volatility
- Use connection pooling for high-throughput scenarios
