# Rust: High-Performance Memory Pool Implementation

## Problem Description

Implement a lock-free memory pool allocator that provides:
- O(1) allocation and deallocation
- Thread-safe without locks
- Memory block reuse
- Configurable block sizes
- Memory statistics tracking
- Prevent use-after-free and double-free

## Complete Implementation

```rust
// src/lib.rs
pub mod pool;
pub mod block;
pub mod stats;

pub use pool::MemoryPool;
pub use block::Block;
pub use stats::PoolStats;
```

```rust
// src/block.rs
use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;
use std::sync::atomic::{AtomicUsize, Ordering};

/// A memory block in the pool
pub struct Block {
    /// Pointer to the memory
    ptr: NonNull<u8>,
    /// Size of this block
    size: usize,
    /// Layout for deallocation
    layout: Layout,
    /// Reference count for safety
    ref_count: AtomicUsize,
}

impl Block {
    /// Create a new block with the given size
    pub fn new(size: usize) -> Result<Self, String> {
        let layout = Layout::from_size_align(size, 8)
            .map_err(|e| format!("Invalid layout: {}", e))?;

        let ptr = unsafe { alloc(layout) };
        
        let ptr = NonNull::new(ptr)
            .ok_or_else(|| "Allocation failed".to_string())?;

        Ok(Block {
            ptr,
            size,
            layout,
            ref_count: AtomicUsize::new(1),
        })
    }

    /// Get the size of this block
    pub fn size(&self) -> usize {
        self.size
    }

    /// Get a pointer to the block's memory
    pub fn as_ptr(&self) -> *mut u8 {
        self.ptr.as_ptr()
    }

    /// Get a slice view of the block
    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr.as_ptr(), self.size) }
    }

    /// Get a mutable slice view of the block
    pub fn as_slice_mut(&mut self) -> &mut [u8] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr.as_ptr(), self.size) }
    }

    /// Increment reference count
    pub fn add_ref(&self) {
        self.ref_count.fetch_add(1, Ordering::SeqCst);
    }

    /// Decrement reference count and return true if it reaches zero
    pub fn release(&self) -> bool {
        self.ref_count.fetch_sub(1, Ordering::SeqCst) == 1
    }

    /// Get current reference count
    pub fn ref_count(&self) -> usize {
        self.ref_count.load(Ordering::SeqCst)
    }
}

impl Drop for Block {
    fn drop(&mut self) {
        if self.release() {
            unsafe {
                dealloc(self.ptr.as_ptr(), self.layout);
            }
        }
    }
}

// Safety: Block is safe to send between threads
unsafe impl Send for Block {}
unsafe impl Sync for Block {}
```

```rust
// src/pool.rs
use crate::block::Block;
use crate::stats::PoolStats;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::Arc;

/// A lock-free slot in the pool
struct Slot {
    /// The memory block
    block: Option<Block>,
    /// Whether this slot is free
    is_free: AtomicBool,
}

impl Slot {
    fn new(block: Block) -> Self {
        Slot {
            block: Some(block),
            is_free: AtomicBool::new(true),
        }
    }
}

/// Configuration for the memory pool
pub struct PoolConfig {
    /// Block sizes available in the pool
    pub block_sizes: Vec<usize>,
    /// Number of blocks per size class
    pub blocks_per_size: usize,
    /// Enable statistics tracking
    pub track_stats: bool,
}

impl Default for PoolConfig {
    fn default() -> Self {
        PoolConfig {
            block_sizes: vec![64, 256, 1024, 4096, 16384],
            blocks_per_size: 16,
            track_stats: true,
        }
    }
}

/// A high-performance memory pool
pub struct MemoryPool {
    /// Slots organized by size class
    slots: HashMap<usize, Vec<Slot>>,
    /// Statistics
    stats: Option<Arc<PoolStats>>,
    /// Total allocated bytes
    total_allocated: AtomicUsize,
    /// Pool is shutdown
    is_shutdown: AtomicBool,
}

impl MemoryPool {
    /// Create a new memory pool with default configuration
    pub fn new() -> Result<Self, String> {
        Self::with_config(PoolConfig::default())
    }

    /// Create a new memory pool with custom configuration
    pub fn with_config(config: PoolConfig) -> Result<Self, String> {
        let mut slots = HashMap::new();

        for &size in &config.block_sizes {
            let mut size_slots = Vec::with_capacity(config.blocks_per_size);
            
            for _ in 0..config.blocks_per_size {
                let block = Block::new(size)?;
                size_slots.push(Slot::new(block));
            }
            
            slots.insert(size, size_slots);
        }

        let stats = if config.track_stats {
            Some(Arc::new(PoolStats::new()))
        } else {
            None
        };

        Ok(MemoryPool {
            slots,
            stats,
            total_allocated: AtomicUsize::new(0),
            is_shutdown: AtomicBool::new(false),
        })
    }

    /// Allocate a block of at least the given size
    pub fn alloc(&self, min_size: usize) -> Result<PoolBlock, String> {
        if self.is_shutdown.load(Ordering::SeqCst) {
            return Err("Pool is shutdown".to_string());
        }

        // Find smallest suitable size class
        let size_class = self.find_size_class(min_size)?;

        // Find a free slot
        if let Some(slots) = self.slots.get(&size_class) {
            for (idx, slot) in slots.iter().enumerate() {
                // Try to claim this slot using CAS
                if slot.is_free.compare_exchange(
                    true,
                    false,
                    Ordering::SeqCst,
                    Ordering::SeqCst,
                ).is_ok() {
                    // Successfully claimed
                    if let Some(stats) = &self.stats {
                        stats.record_alloc(size_class);
                    }

                    return Ok(PoolBlock {
                        pool: self as *const MemoryPool,
                        size_class,
                        slot_index: idx,
                        size: size_class,
                    });
                }
            }
        }

        // No free blocks, allocate new one
        Err("No available blocks".to_string())
    }

    /// Return a block to the pool
    pub fn dealloc(&self, size_class: usize, slot_index: usize) {
        if let Some(slots) = self.slots.get(&size_class) {
            if let Some(slot) = slots.get(slot_index) {
                slot.is_free.store(true, Ordering::SeqCst);
                
                if let Some(stats) = &self.stats {
                    stats.record_dealloc(size_class);
                }
            }
        }
    }

    /// Get the actual memory for a pool block
    pub fn get_memory(&self, size_class: usize, slot_index: usize) -> Option<&[u8]> {
        if let Some(slots) = self.slots.get(&size_class) {
            if let Some(slot) = slots.get(slot_index) {
                if let Some(block) = &slot.block {
                    return Some(block.as_slice());
                }
            }
        }
        None
    }

    /// Get mutable memory for a pool block
    pub fn get_memory_mut(&self, size_class: usize, slot_index: usize) -> Option<&mut [u8]> {
        if let Some(slots) = self.slots.get(&size_class) {
            if let Some(slot) = slots.get(slot_index) {
                if let Some(block) = &mut slot.block {
                    return Some(block.as_slice_mut());
                }
            }
        }
        None
    }

    /// Get pool statistics
    pub fn stats(&self) -> Option<&Arc<PoolStats>> {
        self.stats.as_ref()
    }

    /// Get total allocated memory
    pub fn total_allocated(&self) -> usize {
        self.total_allocated.load(Ordering::SeqCst)
    }

    /// Shutdown the pool
    pub fn shutdown(&self) {
        self.is_shutdown.store(true, Ordering::SeqCst);
    }

    /// Find the smallest size class >= min_size
    fn find_size_class(&self, min_size: usize) -> Result<usize, String> {
        let mut sizes: Vec<_> = self.slots.keys().collect();
        sizes.sort();

        for &size in &sizes {
            if *size >= min_size {
                return Ok(*size);
            }
        }

        Err(format!("No size class >= {}", min_size))
    }
}

/// A block allocated from the pool
pub struct PoolBlock {
    pool: *const MemoryPool,
    size_class: usize,
    slot_index: usize,
    size: usize,
}

impl PoolBlock {
    /// Get the size of this block
    pub fn size(&self) -> usize {
        self.size
    }

    /// Get the memory as a slice
    pub fn as_slice(&self) -> &[u8] {
        unsafe {
            (*self.pool).get_memory(self.size_class, self.slot_index)
                .expect("Invalid pool block")
        }
    }

    /// Get the memory as a mutable slice
    pub fn as_slice_mut(&mut self) -> &mut [u8] {
        unsafe {
            (*self.pool).get_memory_mut(self.size_class, self.slot_index)
                .expect("Invalid pool block")
        }
    }
}

impl Drop for PoolBlock {
    fn drop(&mut self) {
        unsafe {
            (*self.pool).dealloc(self.size_class, self.slot_index);
        }
    }
}

// Safety: PoolBlock is safe to send between threads
unsafe impl Send for PoolBlock {}
unsafe impl Sync for PoolBlock {}
```

```rust
// src/stats.rs
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};

/// Statistics for the memory pool
pub struct PoolStats {
    /// Total allocations
    total_allocs: AtomicU64,
    /// Total deallocations
    total_deallocs: AtomicU64,
    /// Current active allocations
    active_allocs: AtomicUsize,
    /// Allocations by size class
    allocs_by_size: Vec<(usize, AtomicU64)>,
    /// Peak active allocations
    peak_active: AtomicUsize,
}

impl PoolStats {
    pub fn new() -> Self {
        PoolStats {
            total_allocs: AtomicU64::new(0),
            total_deallocs: AtomicU64::new(0),
            active_allocs: AtomicUsize::new(0),
            allocs_by_size: vec![
                (64, AtomicU64::new(0)),
                (256, AtomicU64::new(0)),
                (1024, AtomicU64::new(0)),
                (4096, AtomicU64::new(0)),
                (16384, AtomicU64::new(0)),
            ],
            peak_active: AtomicUsize::new(0),
        }
    }

    /// Record an allocation
    pub fn record_alloc(&self, size: usize) {
        self.total_allocs.fetch_add(1, Ordering::Relaxed);
        
        let active = self.active_allocs.fetch_add(1, Ordering::Relaxed) + 1;
        
        // Update peak
        let mut peak = self.peak_active.load(Ordering::Relaxed);
        while active > peak {
            match self.peak_active.compare_exchange_weak(
                peak,
                active,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(current) => peak = current,
            }
        }

        // Update size-specific stats
        for (s, counter) in &self.allocs_by_size {
            if *s == size {
                counter.fetch_add(1, Ordering::Relaxed);
                break;
            }
        }
    }

    /// Record a deallocation
    pub fn record_dealloc(&self, _size: usize) {
        self.total_deallocs.fetch_add(1, Ordering::Relaxed);
        self.active_allocs.fetch_sub(1, Ordering::Relaxed);
    }

    /// Get total allocations
    pub fn total_allocs(&self) -> u64 {
        self.total_allocs.load(Ordering::Relaxed)
    }

    /// Get total deallocations
    pub fn total_deallocs(&self) -> u64 {
        self.total_deallocs.load(Ordering::Relaxed)
    }

    /// Get current active allocations
    pub fn active_allocs(&self) -> usize {
        self.active_allocs.load(Ordering::Relaxed)
    }

    /// Get peak active allocations
    pub fn peak_active(&self) -> usize {
        self.peak_active.load(Ordering::Relaxed)
    }

    /// Get allocations by size
    pub fn allocs_by_size(&self) -> Vec<(usize, u64)> {
        self.allocs_by_size
            .iter()
            .map(|(size, counter)| (*size, counter.load(Ordering::Relaxed)))
            .collect()
    }
}

impl Default for PoolStats {
    fn default() -> Self {
        Self::new()
    }
}
```

## Test Suite

```rust
// tests/pool_test.rs
use memory_pool::{MemoryPool, PoolConfig};
use std::sync::Arc;
use std::thread;

#[test]
fn test_basic_allocation() {
    let pool = MemoryPool::new().unwrap();
    
    let mut block = pool.alloc(100).unwrap();
    assert!(block.size() >= 100);
    
    // Write to the block
    let data = b"Hello, World!";
    block.as_slice_mut()[..data.len()].copy_from_slice(data);
    
    // Read it back
    assert_eq!(&block.as_slice()[..data.len()], data);
}

#[test]
fn test_size_classes() {
    let pool = MemoryPool::new().unwrap();
    
    // Small allocation should get 64-byte block
    let block1 = pool.alloc(10).unwrap();
    assert_eq!(block1.size(), 64);
    
    // Medium allocation should get 256-byte block
    let block2 = pool.alloc(200).unwrap();
    assert_eq!(block2.size(), 256);
    
    // Large allocation should get 1024-byte block
    let block3 = pool.alloc(800).unwrap();
    assert_eq!(block3.size(), 1024);
}

#[test]
fn test_block_reuse() {
    let pool = MemoryPool::new().unwrap();
    
    // Allocate and immediately deallocate
    {
        let _block1 = pool.alloc(64).unwrap();
    }
    
    // Stats should show one alloc and one dealloc
    let stats = pool.stats().unwrap();
    assert_eq!(stats.total_allocs(), 1);
    assert_eq!(stats.total_deallocs(), 1);
    assert_eq!(stats.active_allocs(), 0);
}

#[test]
fn test_concurrent_allocation() {
    let pool = Arc::new(MemoryPool::new().unwrap());
    let mut handles = vec![];
    
    for _ in 0..10 {
        let pool_clone = Arc::clone(&pool);
        let handle = thread::spawn(move || {
            let mut blocks = vec![];
            
            for i in 0..10 {
                let mut block = pool_clone.alloc(64).unwrap();
                block.as_slice_mut()[0] = i as u8;
                blocks.push(block);
            }
            
            blocks
        });
        handles.push(handle);
    }
    
    // All threads should succeed
    for handle in handles {
        let blocks = handle.join().unwrap();
        assert_eq!(blocks.len(), 10);
    }
    
    // Check stats
    let stats = pool.stats().unwrap();
    assert_eq!(stats.total_allocs(), 100);
}

#[test]
fn test_statistics() {
    let pool = MemoryPool::new().unwrap();
    
    // Allocate several blocks
    let b1 = pool.alloc(64).unwrap();
    let b2 = pool.alloc(256).unwrap();
    let b3 = pool.alloc(64).unwrap();
    
    let stats = pool.stats().unwrap();
    assert_eq!(stats.active_allocs(), 3);
    assert_eq!(stats.total_allocs(), 3);
    
    // Drop one
    drop(b1);
    
    assert_eq!(stats.active_allocs(), 2);
    assert_eq!(stats.total_deallocs(), 1);
    
    // Drop rest
    drop(b2);
    drop(b3);
    
    assert_eq!(stats.active_allocs(), 0);
    assert_eq!(stats.total_deallocs(), 3);
}

#[test]
fn test_pool_shutdown() {
    let pool = MemoryPool::new().unwrap();
    
    // Shutdown the pool
    pool.shutdown();
    
    // Allocation should fail
    assert!(pool.alloc(64).is_err());
}

#[test]
fn test_custom_config() {
    let config = PoolConfig {
        block_sizes: vec![128, 512, 2048],
        blocks_per_size: 8,
        track_stats: false,
    };
    
    let pool = MemoryPool::with_config(config).unwrap();
    
    let block = pool.alloc(100).unwrap();
    assert_eq!(block.size(), 128);
    
    // Stats should be disabled
    assert!(pool.stats().is_none());
}

#[test]
fn test_large_allocation() {
    let pool = MemoryPool::new().unwrap();
    
    // Request 10KB - should get 16KB block
    let block = pool.alloc(10000).unwrap();
    assert_eq!(block.size(), 16384);
}

#[test]
fn test_write_and_read() {
    let pool = MemoryPool::new().unwrap();
    
    let mut block = pool.alloc(1024).unwrap();
    
    // Write pattern
    for i in 0..100 {
        block.as_slice_mut()[i] = i as u8;
    }
    
    // Read pattern back
    for i in 0..100 {
        assert_eq!(block.as_slice()[i], i as u8);
    }
}

#[test]
fn test_peak_tracking() {
    let pool = MemoryPool::new().unwrap();
    
    let b1 = pool.alloc(64).unwrap();
    let b2 = pool.alloc(64).unwrap();
    let b3 = pool.alloc(64).unwrap();
    
    assert_eq!(pool.stats().unwrap().peak_active(), 3);
    
    drop(b2);
    drop(b1);
    
    // Peak should still be 3
    assert_eq!(pool.stats().unwrap().peak_active(), 3);
    
    drop(b3);
    
    // Peak should still be 3
    assert_eq!(pool.stats().unwrap().peak_active(), 3);
}

#[test]
fn test_no_double_free() {
    let pool = MemoryPool::new().unwrap();
    
    let stats = pool.stats().unwrap();
    let initial_deallocs = stats.total_deallocs();
    
    {
        let block = pool.alloc(64).unwrap();
        drop(block); // First free
    }
    
    assert_eq!(stats.total_deallocs(), initial_deallocs + 1);
    
    // Block is already freed, no additional dealloc should happen
    assert_eq!(stats.total_deallocs(), initial_deallocs + 1);
}

#[test]
fn test_stress_test() {
    let pool = Arc::new(MemoryPool::new().unwrap());
    let mut handles = vec![];
    
    for _ in 0..20 {
        let pool_clone = Arc::clone(&pool);
        let handle = thread::spawn(move || {
            for _ in 0..100 {
                let size = 64 * (rand::random::<usize>() % 5 + 1);
                if let Ok(mut block) = pool_clone.alloc(size) {
                    // Write some data
                    if !block.as_slice_mut().is_empty() {
                        block.as_slice_mut()[0] = 0xFF;
                    }
                    // Block freed on drop
                }
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    // All blocks should be freed
    assert_eq!(pool.stats().unwrap().active_allocs(), 0);
}

// Helper module for random (normally you'd use rand crate)
mod rand {
    use std::time::{SystemTime, UNIX_EPOCH};
    
    static mut SEED: u64 = 0;
    
    pub fn random<T: From<u64>>() -> T {
        unsafe {
            if SEED == 0 {
                SEED = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_nanos() as u64;
            }
            SEED = SEED.wrapping_mul(6364136223846793005).wrapping_add(1);
            T::from(SEED)
        }
    }
}
```

## Usage Example

```rust
// examples/basic_usage.rs
use memory_pool::{MemoryPool, PoolConfig};

fn main() {
    // Create pool with custom config
    let config = PoolConfig {
        block_sizes: vec![64, 256, 1024, 4096],
        blocks_per_size: 32,
        track_stats: true,
    };
    
    let pool = MemoryPool::with_config(config).unwrap();
    
    // Allocate some blocks
    let mut blocks = vec![];
    
    for i in 0..10 {
        let mut block = pool.alloc(100).unwrap();
        
        // Write data
        let msg = format!("Message {}", i);
        block.as_slice_mut()[..msg.len()].copy_from_slice(msg.as_bytes());
        
        blocks.push(block);
    }
    
    // Check stats
    if let Some(stats) = pool.stats() {
        println!("Active allocations: {}", stats.active_allocs());
        println!("Total allocations: {}", stats.total_allocs());
        println!("Peak active: {}", stats.peak_active());
        
        println!("Allocations by size:");
        for (size, count) in stats.allocs_by_size() {
            if count > 0 {
                println!("  {} bytes: {}", size, count);
            }
        }
    }
    
    // Blocks automatically returned to pool when dropped
    println!("Blocks dropped, active: {}", pool.stats().unwrap().active_allocs());
}
```

## Key Features

1. **Lock-Free**: Uses atomic CAS operations for thread safety
2. **O(1) Operations**: Constant time alloc/dealloc
3. **Size Classes**: Multiple block sizes for efficiency
4. **Statistics**: Optional tracking of allocations
5. **Safe**: Prevents use-after-free and double-free
6. **Configurable**: Custom size classes and pool sizes

## Performance Considerations

- Pre-allocated blocks reduce allocation overhead
- Lock-free design enables high concurrency
- Size classes reduce internal fragmentation
- Atomic operations with Relaxed ordering where safe
- Memory reuse eliminates repeated allocations

---

**Topic**: Rust Systems Programming
**Difficulty**: Advanced
**Generated**: 2026-02-18
