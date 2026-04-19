# Rust System: Thread-Safe LRU Cache

## Problem Statement
Implement a memory-safe, thread-safe LRU (Least Recently Used) cache with configurable capacity, TTL (time-to-live) support, and proper memory management using Rust's ownership system.

## Solution Code

```rust
use std::collections::HashMap;
use std::time::{Duration, Instant};
use std::sync::{Arc, RwLock};
use std::hash::Hash;
use std::ptr::NonNull;

/// Node in the doubly-linked list for LRU ordering
struct Node<K, V> {
    key: K,
    value: V,
    expires_at: Option<Instant>,
    prev: Option<NonNull<Node<K, V>>>,
    next: Option<NonNull<Node<K, V>>>,
}

/// LRU Cache with thread-safe access and TTL support
pub struct LruCache<K, V> {
    capacity: usize,
    ttl: Option<Duration>,
    map: HashMap<K, NonNull<Node<K, V>>>,
    head: Option<NonNull<Node<K, V>>>,
    tail: Option<NonNull<Node<K, V>>>,
}

impl<K: Hash + Eq + Clone, V: Clone> LruCache<K, V> {
    /// Create a new LRU cache with the given capacity
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            ttl: None,
            map: HashMap::with_capacity(capacity),
            head: None,
            tail: None,
        }
    }

    /// Set TTL for cache entries
    pub fn with_ttl(mut self, ttl: Duration) -> Self {
        self.ttl = Some(ttl);
        self
    }

    /// Get a value from the cache
    pub fn get(&mut self, key: &K) -> Option<V> {
        let node_ptr = self.map.get(key).copied()?;
        
        // Safety: node_ptr is valid because it's in our map
        let node = unsafe { node_ptr.as_ref() };
        
        // Check TTL
        if let Some(expires_at) = node.expires_at {
            if Instant::now() > expires_at {
                // Entry expired, remove it
                self.remove_node(node_ptr);
                self.map.remove(key);
                return None;
            }
        }
        
        // Move to front (most recently used)
        self.detach_node(node_ptr);
        self.attach_to_front(node_ptr);
        
        Some(node.value.clone())
    }

    /// Insert a value into the cache
    pub fn put(&mut self, key: K, value: V) -> Option<V> {
        // Check if key already exists
        if let Some(&node_ptr) = self.map.get(&key) {
            // Update existing node
            unsafe {
                let node = node_ptr.as_ptr();
                (*node).value = value.clone();
                (*node).expires_at = self.ttl.map(|t| Instant::now() + t);
            }
            
            // Move to front
            self.detach_node(node_ptr);
            self.attach_to_front(node_ptr);
            
            return Some(value);
        }
        
        // Evict if at capacity
        if self.map.len() >= self.capacity {
            self.evict_lru();
        }
        
        // Create new node
        let node = Box::new(Node {
            key: key.clone(),
            value,
            expires_at: self.ttl.map(|t| Instant::now() + t),
            prev: None,
            next: None,
        });
        
        let node_ptr = NonNull::new(Box::into_raw(node)).unwrap();
        
        // Add to map and list
        self.map.insert(key, node_ptr);
        self.attach_to_front(node_ptr);
        
        None
    }

    /// Remove a value from the cache
    pub fn remove(&mut self, key: &K) -> Option<V> {
        let node_ptr = self.map.remove(key)?;
        self.remove_node(node_ptr);
        
        // Safety: node_ptr is valid
        unsafe {
            let node = Box::from_raw(node_ptr.as_ptr());
            Some(node.value)
        }
    }

    /// Check if key exists (and is not expired)
    pub fn contains_key(&mut self, key: &K) -> bool {
        self.get(key).is_some()
    }

    /// Get current cache size
    pub fn len(&self) -> usize {
        self.map.len()
    }

    /// Check if cache is empty
    pub fn is_empty(&self) -> bool {
        self.map.is_empty()
    }

    /// Clear all entries
    pub fn clear(&mut self) {
        // Free all nodes
        while let Some(node_ptr) = self.head {
            self.detach_node(node_ptr);
            unsafe {
                let _ = Box::from_raw(node_ptr.as_ptr());
            }
        }
        self.map.clear();
    }

    /// Remove expired entries
    pub fn prune_expired(&mut self) -> usize {
        let now = Instant::now();
        let mut expired_keys = Vec::new();
        
        for (&key, &node_ptr) in &self.map {
            unsafe {
                if let Some(expires_at) = (*node_ptr.as_ptr()).expires_at {
                    if now > expires_at {
                        expired_keys.push(key.clone());
                    }
                }
            }
        }
        
        let count = expired_keys.len();
        for key in expired_keys {
            self.remove(&key);
        }
        
        count
    }

    // Private helper methods

    fn attach_to_front(&mut self, node_ptr: NonNull<Node<K, V>>) {
        unsafe {
            let node = node_ptr.as_ptr();
            (*node).prev = None;
            (*node).next = self.head;
            
            if let Some(head_ptr) = self.head {
                (*head_ptr.as_ptr()).prev = Some(node_ptr);
            }
            
            self.head = Some(node_ptr);
            
            if self.tail.is_none() {
                self.tail = Some(node_ptr);
            }
        }
    }

    fn detach_node(&mut self, node_ptr: NonNull<Node<K, V>>) {
        unsafe {
            let node = node_ptr.as_ptr();
            
            // Update prev node's next pointer
            if let Some(prev_ptr) = (*node).prev {
                (*prev_ptr.as_ptr()).next = (*node).next;
            } else {
                self.head = (*node).next;
            }
            
            // Update next node's prev pointer
            if let Some(next_ptr) = (*node).next {
                (*next_ptr.as_ptr()).prev = (*node).prev;
            } else {
                self.tail = (*node).prev;
            }
            
            (*node).prev = None;
            (*node).next = None;
        }
    }

    fn remove_node(&mut self, node_ptr: NonNull<Node<K, V>>) {
        self.detach_node(node_ptr);
        unsafe {
            let _ = Box::from_raw(node_ptr.as_ptr());
        }
    }

    fn evict_lru(&mut self) {
        if let Some(tail_ptr) = self.tail {
            unsafe {
                let key = (*tail_ptr.as_ptr()).key.clone();
                self.map.remove(&key);
            }
            self.remove_node(tail_ptr);
        }
    }
}

impl<K, V> Drop for LruCache<K, V> {
    fn drop(&mut self) {
        self.clear();
    }
}

// Thread-safe wrapper using Arc<RwLock>
pub struct ThreadSafeLruCache<K, V> {
    inner: Arc<RwLock<LruCache<K, V>>>,
}

impl<K: Hash + Eq + Clone + Send + Sync, V: Clone + Send + Sync> ThreadSafeLruCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self {
            inner: Arc::new(RwLock::new(LruCache::new(capacity))),
        }
    }

    pub fn with_ttl(capacity: usize, ttl: Duration) -> Self {
        Self {
            inner: Arc::new(RwLock::new(
                LruCache::new(capacity).with_ttl(ttl)
            )),
        }
    }

    pub fn get(&self, key: &K) -> Option<V> {
        self.inner.write().unwrap().get(key)
    }

    pub fn put(&self, key: K, value: V) -> Option<V> {
        self.inner.write().unwrap().put(key, value)
    }

    pub fn remove(&self, key: &K) -> Option<V> {
        self.inner.write().unwrap().remove(key)
    }

    pub fn len(&self) -> usize {
        self.inner.read().unwrap().len()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.read().unwrap().is_empty()
    }

    pub fn clear(&self) {
        self.inner.write().unwrap().clear();
    }

    pub fn prune_expired(&self) -> usize {
        self.inner.write().unwrap().prune_expired()
    }
}

impl<K, V> Clone for ThreadSafeLruCache<K, V> {
    fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }
}

// ============================================
// Example: HTTP Response Cache
// ============================================

use std::thread;
use std::time::Duration;

fn main() {
    // Create a thread-safe cache with 100 capacity and 5-minute TTL
    let cache = ThreadSafeLruCache::<String, String>::with_ttl(
        100,
        Duration::from_secs(300),
    );
    
    // Spawn multiple threads accessing the cache
    let handles: Vec<_> = (0..5)
        .map(|i| {
            let cache = cache.clone();
            thread::spawn(move || {
                let key = format!("key_{}", i % 3);
                
                // Try to get from cache
                if let Some(value) = cache.get(&key) {
                    println!("Thread {}: Cache hit for {}", i, key);
                    return value;
                }
                
                // Cache miss, compute and store
                println!("Thread {}: Cache miss for {}", i, key);
                let value = format!("value_for_{}", key);
                cache.put(key.clone(), value.clone());
                value
            })
        })
        .collect();
    
    for handle in handles {
        let result = handle.join().unwrap();
        println!("Result: {}", result);
    }
    
    println!("Cache size: {}", cache.len());
}

// ============================================
// Example: Async-compatible Cache
// ============================================

#[cfg(feature = "async")]
pub mod async_cache {
    use super::*;
    use tokio::sync::RwLock;
    
    pub struct AsyncLruCache<K, V> {
        inner: Arc<RwLock<LruCache<K, V>>>,
    }
    
    impl<K: Hash + Eq + Clone + Send + Sync, V: Clone + Send + Sync> AsyncLruCache<K, V> {
        pub fn new(capacity: usize) -> Self {
            Self {
                inner: Arc::new(RwLock::new(LruCache::new(capacity))),
            }
        }
        
        pub async fn get(&self, key: &K) -> Option<V> {
            self.inner.write().await.get(key)
        }
        
        pub async fn put(&self, key: K, value: V) -> Option<V> {
            self.inner.write().await.put(key, value)
        }
        
        pub async fn get_or_insert<F, Fut>(&self, key: K, f: F) -> V
        where
            F: FnOnce() -> Fut,
            Fut: std::future::Future<Output = V>,
        {
            if let Some(value) = self.get(&key).await {
                return value;
            }
            
            let value = f().await;
            self.put(key, value.clone()).await;
            value
        }
    }
}
```

## Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_basic_put_get() {
        let mut cache = LruCache::new(3);
        
        cache.put("a", 1);
        cache.put("b", 2);
        cache.put("c", 3);
        
        assert_eq!(cache.get(&"a"), Some(1));
        assert_eq!(cache.get(&"b"), Some(2));
        assert_eq!(cache.get(&"c"), Some(3));
    }

    #[test]
    fn test_eviction() {
        let mut cache = LruCache::new(2);
        
        cache.put("a", 1);
        cache.put("b", 2);
        cache.put("c", 3); // Should evict "a"
        
        assert_eq!(cache.get(&"a"), None);
        assert_eq!(cache.get(&"b"), Some(2));
        assert_eq!(cache.get(&"c"), Some(3));
    }

    #[test]
    fn test_lru_order() {
        let mut cache = LruCache::new(3);
        
        cache.put("a", 1);
        cache.put("b", 2);
        cache.put("c", 3);
        
        // Access "a", making it most recently used
        cache.get(&"a");
        
        // Add new item, should evict "b" (not "a")
        cache.put("d", 4);
        
        assert_eq!(cache.get(&"a"), Some(1));
        assert_eq!(cache.get(&"b"), None); // Evicted
        assert_eq!(cache.get(&"c"), Some(3));
        assert_eq!(cache.get(&"d"), Some(4));
    }

    #[test]
    fn test_update_existing() {
        let mut cache = LruCache::new(2);
        
        cache.put("a", 1);
        cache.put("a", 2);
        
        assert_eq!(cache.len(), 1);
        assert_eq!(cache.get(&"a"), Some(2));
    }

    #[test]
    fn test_remove() {
        let mut cache = LruCache::new(2);
        
        cache.put("a", 1);
        assert_eq!(cache.remove(&"a"), Some(1));
        assert_eq!(cache.get(&"a"), None);
        assert_eq!(cache.len(), 0);
    }

    #[test]
    fn test_clear() {
        let mut cache = LruCache::new(3);
        
        cache.put("a", 1);
        cache.put("b", 2);
        cache.put("c", 3);
        
        cache.clear();
        
        assert!(cache.is_empty());
        assert_eq!(cache.len(), 0);
    }

    #[test]
    fn test_ttl_expiry() {
        let mut cache = LruCache::new(2)
            .with_ttl(Duration::from_millis(50));
        
        cache.put("a", 1);
        
        // Should still be valid
        assert_eq!(cache.get(&"a"), Some(1));
        
        // Wait for expiry
        thread::sleep(Duration::from_millis(100));
        
        // Should be expired now
        assert_eq!(cache.get(&"a"), None);
    }

    #[test]
    fn test_prune_expired() {
        let mut cache = LruCache::new(10)
            .with_ttl(Duration::from_millis(50));
        
        cache.put("a", 1);
        cache.put("b", 2);
        
        thread::sleep(Duration::from_millis(100));
        
        cache.put("c", 3); // Fresh entry
        
        let pruned = cache.prune_expired();
        
        assert_eq!(pruned, 2);
        assert_eq!(cache.len(), 1);
        assert_eq!(cache.get(&"c"), Some(3));
    }

    #[test]
    fn test_thread_safe_basic() {
        let cache = ThreadSafeLruCache::new(100);
        
        cache.put("a", 1);
        
        let cache_clone = cache.clone();
        let handle = thread::spawn(move || {
            cache_clone.put("b", 2);
            cache_clone.get(&"a")
        });
        
        let result = handle.join().unwrap();
        assert_eq!(result, Some(1));
        assert_eq!(cache.len(), 2);
    }

    #[test]
    fn test_thread_safe_concurrent_access() {
        let cache = ThreadSafeLruCache::new(100);
        
        let handles: Vec<_> = (0..10)
            .map(|i| {
                let cache = cache.clone();
                thread::spawn(move || {
                    for j in 0..10 {
                        let key = format!("key_{}_{}", i, j);
                        cache.put(key.clone(), i * 10 + j);
                        cache.get(&key);
                    }
                })
            })
            .collect();
        
        for handle in handles {
            handle.join().unwrap();
        }
        
        assert_eq!(cache.len(), 100);
    }

    #[test]
    fn test_zero_capacity() {
        let mut cache: LruCache<i32, i32> = LruCache::new(0);
        cache.put(1, 1);
        assert_eq!(cache.get(&1), None);
    }

    #[test]
    fn test_contains_key() {
        let mut cache = LruCache::new(2)
            .with_ttl(Duration::from_millis(50));
        
        cache.put("a", 1);
        assert!(cache.contains_key(&"a"));
        
        thread::sleep(Duration::from_millis(100));
        assert!(!cache.contains_key(&"a"));
    }
}

// Run with: cargo test
```

## Analysis

### Memory Safety Guarantees

Rust's ownership system ensures:

1. **No Use-After-Free**: `NonNull` pointers are always valid while in the map
2. **No Double-Free**: `Drop` implementation clears all nodes exactly once
3. **No Data Races**: `RwLock` provides exclusive write access, shared read access

### Architecture

```
┌─────────────────────────────────────────┐
│           ThreadSafeLruCache            │
│  ┌────────────────────────────────────┐ │
│  │        Arc<RwLock<LruCache>>       │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │          LruCache            │  │ │
│  │  │  ┌────────┐    ┌───────────┐ │  │ │
│  │  │  │HashMap │◄──►│ Linked    │ │  │ │
│  │  │  │        │    │ List      │ │  │ │
│  │  │  └────────┘    └───────────┘ │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Performance

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| get | O(1) | HashMap + list pointer update |
| put | O(1) | HashMap insert + list ops |
| remove | O(1) | HashMap remove + list detach |
| evict_lru | O(1) | Just pop from tail |

### When to Use LRU Cache

✅ **Use for:**
- Database query caching
- API response caching
- Computed result memoization
- Web page caching

❌ **Avoid when:**
- Cache hit rate is very low
- Values are very small (overhead > benefit)
- Strong consistency required

### Production Considerations

1. **Memory Limits**: Implement max bytes instead of max entries for large values
2. **Metrics**: Track hit rate, eviction count, average latency
3. **Monitoring**: Alert on low hit rates (< 70%)
4. **Warmup**: Pre-populate cache on startup for known hot keys
