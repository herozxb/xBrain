# Redis Caching Patterns

## Pattern: Cache-Aside

### Implementation
```python
import redis
import json

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_user(user_id):
    """
    Cache-Aside pattern: Application manages cache explicitly
    """
    # Step 1: Check cache first
    cache_key = f"user:{user_id}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        # Cache hit - return cached data
        return json.loads(cached_data)
    
    # Step 2: Cache miss - fetch from database
    user_data = fetch_user_from_database(user_id)
    
    if user_data:
        # Step 3: Store in cache for future requests
        redis_client.setex(
            cache_key,
            3600,  # TTL: 1 hour
            json.dumps(user_data)
        )
    
    return user_data

def update_user(user_id, data):
    """
    Update database and invalidate cache
    """
    # Update database
    update_user_in_database(user_id, data)
    
    # Invalidate cache
    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)
```

### Explanation
The Cache-Aside pattern (also known as Lazy Loading) is the most common caching strategy. The application code explicitly manages the cache:
1. **Read Path**: Check cache first → if miss, fetch from database and populate cache
2. **Write Path**: Update database, then invalidate or update cache
3. **Benefits**: Simple to implement, only caches requested data
4. **Drawbacks**: Cache misses add latency, stale data possible if not invalidated properly
5. **Best for**: Read-heavy workloads where data is requested multiple times

---

## Pattern: Write-Through

### Implementation
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def write_through_save(user_id, user_data):
    """
    Write-Through pattern: Write to cache and database synchronously
    """
    cache_key = f"user:{user_id}"
    
    # Use Redis pipeline for atomic operations
    pipe = redis_client.pipeline()
    
    try:
        # Step 1: Write to cache
        pipe.setex(
            cache_key,
            3600,  # TTL: 1 hour
            json.dumps(user_data)
        )
        
        # Step 2: Write to database (in transaction)
        save_user_to_database(user_id, user_data)
        
        # Execute cache operation
        pipe.execute()
        
        return True
        
    except Exception as e:
        # Rollback if needed
        pipe.reset()
        raise e

def write_through_get(user_id):
    """
    Read from cache (data is guaranteed to be in sync)
    """
    cache_key = f"user:{user_id}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Fallback to database if cache expired
    user_data = fetch_user_from_database(user_id)
    
    if user_data:
        # Repopulate cache
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(user_data)
        )
    
    return user_data
```

### Explanation
The Write-Through pattern ensures cache-database consistency by writing to both cache and database synchronously:
1. **Write Path**: Data is written to cache AND database in the same transaction
2. **Read Path**: Read from cache (data should always be available)
3. **Benefits**: Data consistency guaranteed, fast reads
4. **Drawbacks**: Slower writes (two write operations), cache can grow large
5. **Best for**: Applications requiring strong consistency and read performance

---

## Pattern: Write-Behind (Write-Back)

### Implementation
```python
import redis
import json
import threading
import queue
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Queue for background writes
write_queue = queue.Queue()

class WriteBehindManager:
    def __init__(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_writes)
        self.worker_thread.daemon = True
        
    def start(self):
        self.worker_thread.start()
    
    def _process_writes(self):
        """
        Background worker that processes write operations
        """
        while self.running:
            try:
                # Get write operation from queue
                operation = write_queue.get(timeout=1)
                
                if operation:
                    user_id, user_data = operation
                    # Write to database asynchronously
                    save_user_to_database(user_id, user_data)
                    write_queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Write-behind error: {e}")
    
    def stop(self):
        self.running = False
        self.worker_thread.join()

# Start write-behind manager
write_behind = WriteBehindManager()
write_behind.start()

def write_behind_save(user_id, user_data):
    """
    Write-Behind pattern: Write to cache immediately, database later
    """
    cache_key = f"user:{user_id}"
    
    # Step 1: Write to cache immediately
    redis_client.setex(
        cache_key,
        3600,
        json.dumps(user_data)
    )
    
    # Step 2: Queue database write for later
    write_queue.put((user_id, user_data))
    
    return True

def write_behind_get(user_id):
    """
    Read from cache
    """
    cache_key = f"user:{user_id}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    return None
```

### Explanation
The Write-Behind pattern (also called Write-Back) optimizes write performance by decoupling cache and database writes:
1. **Write Path**: Write to cache immediately, queue database write for background processing
2. **Read Path**: Read from cache (very fast)
3. **Benefits**: Extremely fast writes, reduced database load, batch writes possible
4. **Drawbacks**: Risk of data loss if system fails before database write, complex to implement
5. **Best for**: Write-heavy workloads where eventual consistency is acceptable

---

## Pattern: Cache Invalidation

### Implementation
```python
import redis
import json
from datetime import datetime

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class CacheInvalidator:
    """
    Multiple cache invalidation strategies
    """
    
    @staticmethod
    def ttl_based_invalidation(user_id, user_data, ttl_seconds=3600):
        """
        Time-based expiration (TTL)
        """
        cache_key = f"user:{user_id}"
        redis_client.setex(
            cache_key,
            ttl_seconds,
            json.dumps({
                'data': user_data,
                'cached_at': datetime.now().isoformat()
            })
        )
    
    @staticmethod
    def explicit_invalidation(user_id):
        """
        Manual cache invalidation on data update
        """
        cache_key = f"user:{user_id}"
        redis_client.delete(cache_key)
    
    @staticmethod
    def pattern_based_invalidation(pattern):
        """
        Invalidate all keys matching a pattern
        """
        # Find all matching keys
        keys = redis_client.keys(pattern)
        
        if keys:
            # Delete all matching keys
            redis_client.delete(*keys)
            return len(keys)
        return 0
    
    @staticmethod
    def versioned_cache(user_id, user_data, version):
        """
        Version-based caching for cache busting
        """
        cache_key = f"user:{user_id}:v{version}"
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(user_data)
        )
        
        # Update version pointer
        redis_client.set(f"user:{user_id}:latest_version", version)
    
    @staticmethod
    def get_versioned_data(user_id):
        """
        Get data using version-based approach
        """
        # Get current version
        version = redis_client.get(f"user:{user_id}:latest_version")
        
        if version:
            version = version.decode('utf-8')
            cache_key = f"user:{user_id}:v{version}"
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
        
        return None
    
    @staticmethod
    def tag_based_invalidation(tags):
        """
        Invalidate cache by tags (e.g., invalidate all 'user-profile' caches)
        """
        for tag in tags:
            # Get all keys associated with this tag
            tag_key = f"tag:{tag}"
            keys = redis_client.smembers(tag_key)
            
            if keys:
                # Delete all tagged keys
                keys_to_delete = [k.decode('utf-8') for k in keys]
                if keys_to_delete:
                    redis_client.delete(*keys_to_delete)
                
                # Remove tag set
                redis_client.delete(tag_key)

# Usage examples
invalidator = CacheInvalidator()

# Tag-based caching
def cache_with_tags(user_id, user_data, tags):
    """
    Cache data with associated tags for group invalidation
    """
    cache_key = f"user:{user_id}"
    
    # Store data
    redis_client.setex(cache_key, 3600, json.dumps(user_data))
    
    # Associate with tags
    for tag in tags:
        redis_client.sadd(f"tag:{tag}", cache_key)
```

### Explanation
Cache Invalidation strategies ensure data freshness and prevent stale cache:
1. **TTL-Based**: Automatic expiration after a set time (simplest approach)
2. **Explicit**: Manual deletion when data changes (most control)
3. **Pattern-Based**: Delete multiple keys matching a pattern (bulk operations)
4. **Versioned**: Use version numbers in keys to avoid stale reads
5. **Tag-Based**: Group related cache entries and invalidate by group
6. **Best for**: Different scenarios require different strategies; often combined

---

## Pattern: Rate Limiting with Redis

### Implementation
```python
import redis
import time
from datetime import datetime

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class RateLimiter:
    """
    Redis-based rate limiting implementations
    """
    
    @staticmethod
    def fixed_window_counter(user_id, limit=100, window_seconds=60):
        """
        Fixed Window Counter algorithm
        Simple but allows burst at window boundaries
        """
        current_window = int(time.time() // window_seconds)
        key = f"ratelimit:{user_id}:{current_window}"
        
        # Increment counter
        count = redis_client.incr(key)
        
        # Set expiry on first request
        if count == 1:
            redis_client.expire(key, window_seconds)
        
        # Check if limit exceeded
        if count > limit:
            ttl = redis_client.ttl(key)
            return {
                'allowed': False,
                'remaining': 0,
                'reset_in': ttl,
                'limit': limit
            }
        
        return {
            'allowed': True,
            'remaining': limit - count,
            'reset_in': window_seconds,
            'limit': limit
        }
    
    @staticmethod
    def sliding_window_log(user_id, limit=100, window_seconds=60):
        """
        Sliding Window Log algorithm
        More accurate but uses more memory
        """
        key = f"ratelimit_log:{user_id}"
        now = time.time()
        window_start = now - window_seconds
        
        # Remove old entries
        redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = redis_client.zcard(key)
        
        if current_count >= limit:
            # Get oldest entry to calculate retry time
            oldest = redis_client.zrange(key, 0, 0, withscores=True)
            if oldest:
                reset_time = oldest[0][1] + window_seconds - now
                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_in': int(reset_time),
                    'limit': limit
                }
        
        # Add current request
        redis_client.zadd(key, {str(now): now})
        redis_client.expire(key, window_seconds + 1)
        
        return {
            'allowed': True,
            'remaining': limit - current_count - 1,
            'reset_in': window_seconds,
            'limit': limit
        }
    
    @staticmethod
    def token_bucket(user_id, capacity=100, refill_rate=1):
        """
        Token Bucket algorithm
        Allows bursting up to capacity
        """
        key = f"token_bucket:{user_id}"
        now = time.time()
        
        # Get current bucket state
        bucket_data = redis_client.hgetall(key)
        
        if bucket_data:
            tokens = float(bucket_data[b'tokens'])
            last_refill = float(bucket_data[b'last_refill'])
            
            # Calculate tokens to add
            time_passed = now - last_refill
            tokens_to_add = time_passed * refill_rate
            
            # Refill tokens (up to capacity)
            tokens = min(capacity, tokens + tokens_to_add)
        else:
            tokens = capacity
        
        # Check if request can be processed
        if tokens >= 1:
            tokens -= 1
            
            # Update bucket
            redis_client.hset(key, mapping={
                'tokens': tokens,
                'last_refill': now
            })
            redis_client.expire(key, 3600)  # 1 hour expiry
            
            return {
                'allowed': True,
                'remaining': int(tokens),
                'limit': capacity
            }
        else:
            # Calculate time until next token
            retry_after = (1 - tokens) / refill_rate
            
            return {
                'allowed': False,
                'remaining': 0,
                'reset_in': int(retry_after),
                'limit': capacity
            }
    
    @staticmethod
    def leaky_bucket(user_id, capacity=100, leak_rate=10):
        """
        Leaky Bucket algorithm
        Smooths out request rate
        """
        key = f"leaky_bucket:{user_id}"
        now = time.time()
        
        # Get current queue state
        bucket_data = redis_client.hgetall(key)
        
        if bucket_data:
            queue_level = int(bucket_data[b'queue_level'])
            last_leak = float(bucket_data[b'last_leak'])
            
            # Calculate leaked requests
            time_passed = now - last_leak
            leaked = int(time_passed * leak_rate)
            
            # Decrease queue level
            queue_level = max(0, queue_level - leaked)
        else:
            queue_level = 0
        
        # Check if queue has space
        if queue_level < capacity:
            queue_level += 1
            
            # Update bucket
            redis_client.hset(key, mapping={
                'queue_level': queue_level,
                'last_leak': now
            })
            redis_client.expire(key, 3600)
            
            return {
                'allowed': True,
                'remaining': capacity - queue_level,
                'limit': capacity
            }
        else:
            return {
                'allowed': False,
                'remaining': 0,
                'reset_in': int(1 / leak_rate),
                'limit': capacity
            }

# Decorator for rate limiting
def rate_limit(limit=100, window=60, algorithm='fixed_window'):
    """
    Decorator to apply rate limiting to functions
    """
    def decorator(func):
        def wrapper(user_id, *args, **kwargs):
            limiter = RateLimiter()
            
            if algorithm == 'fixed_window':
                result = limiter.fixed_window_counter(user_id, limit, window)
            elif algorithm == 'sliding_window':
                result = limiter.sliding_window_log(user_id, limit, window)
            elif algorithm == 'token_bucket':
                result = limiter.token_bucket(user_id, limit, refill_rate=limit/window)
            elif algorithm == 'leaky_bucket':
                result = limiter.leaky_bucket(user_id, limit, leak_rate=limit/window)
            else:
                result = limiter.fixed_window_counter(user_id, limit, window)
            
            if not result['allowed']:
                raise Exception(f"Rate limit exceeded. Retry in {result['reset_in']} seconds")
            
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator

# Usage example
@rate_limit(limit=10, window=60, algorithm='sliding_window')
def api_endpoint(user_id):
    return {"message": "Success"}
```

### Explanation
Redis is excellent for distributed rate limiting due to its speed and atomic operations:
1. **Fixed Window Counter**: Simple, divides time into fixed windows, allows bursting at boundaries
2. **Sliding Window Log**: Accurate, uses sorted sets to track individual requests, higher memory usage
3. **Token Bucket**: Allows bursting up to capacity, tokens refill over time, good for API limits
4. **Leaky Bucket**: Processes requests at constant rate, smooths traffic, good for throttling
5. **Benefits**: Distributed, atomic operations, precise control, real-time
6. **Best for**: API rate limiting, DDoS protection, resource throttling, quota management
