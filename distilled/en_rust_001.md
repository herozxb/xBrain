# Rust Systems Programming Examples

A collection of memory-safe systems programming patterns demonstrating Rust's ownership model and concurrency primitives.

---

## Topic: Ownership and Borrowing

### Implementation

```rust
/// Demonstrates Rust's ownership and borrowing rules
/// preventing common memory errors at compile time
fn ownership_demo() {
    // OWNERSHIP: Each value has a single owner
    let data = String::from("Hello, Rust!");
    
    // MOVE SEMANTICS: Ownership transfers, original becomes invalid
    let moved_data = data;
    // println!("{}", data);  // Compile error: value borrowed after move
    
    // BORROWING: Immutable references allow read-only access
    let reference = &moved_data;  // &T - immutable borrow
    println!("Borrowed: {}", reference);
    
    // Multiple immutable borrows are allowed simultaneously
    let ref1 = &moved_data;
    let ref2 = &moved_data;
    println!("Multiple refs: {} {}", ref1, ref2);
    
    // MUTABLE BORROW: &mut T allows modification
    let mut mutable_data = String::from("Modify me");
    let mutable_ref = &mut mutable_data;
    mutable_ref.push_str(" - modified!");
    println!("After mutation: {}", mutable_ref);
    
    // SAFETY: Cannot have mutable borrow while immutable borrows exist
    // let immut_ref = &mutable_data;
    // let mut_ref = &mut mutable_data;  // Compile error!
    // println!("{} {}", immut_ref, mut_ref);
}

/// Example: Safe buffer processing with lifetime annotations
fn process_buffer<'a>(input: &'a [u8]) -> &'a [u8] {
    // Lifetime 'a ensures returned reference is valid as long as input
    if input.len() > 5 {
        &input[0..5]  // Return slice with same lifetime
    } else {
        input
    }
}

/// Demonstrates ownership in function calls
fn take_ownership(s: String) {
    // Function now owns `s`, will be dropped at end of scope
    println!("Owned: {}", s);
}  // `s` is dropped here, memory freed

fn borrow_data(s: &String) {
    // Function borrows `s`, ownership remains with caller
    println!("Borrowed: {}", s);
}  // `s` not dropped, only reference goes out of scope

fn main() {
    let owned = String::from("Transfer ownership");
    take_ownership(owned);
    // owned is no longer valid here - ownership transferred
    
    let kept = String::from("Keep ownership");
    borrow_data(&kept);
    println!("Still valid: {}", kept);  // OK - we still own it
}
```

### Safety Analysis

**Memory Safety Guarantees:**

1. **No Dangling Pointers**: The borrow checker ensures references never outlive their referent. If a reference exists, the compiler guarantees the underlying data is still valid.

2. **No Double Free**: Each value has exactly one owner. When the owner goes out of scope, the value is dropped exactly once. Move semantics prevent accidental duplication of ownership.

3. **No Data Races**: The rule "mutable XOR shared" prevents data races at compile time. You cannot have a mutable reference while any other references exist, eliminating concurrent modification bugs.

4. **Lifetime Tracking**: Explicit lifetime annotations ('a) make reference validity visible in function signatures, ensuring returned references remain valid.

5. **Compile-Time Enforcement**: All ownership rules are enforced at compile time with zero runtime overhead. Invalid programs fail to compile rather than crashing at runtime.

**Comparison to C/C++**: In C++, similar patterns require manual memory management or smart pointers with runtime checks. Rust achieves the same safety through compile-time analysis.

---

## Topic: Smart Pointers (Box, Rc, Arc)

### Implementation

```rust
use std::rc::Rc;
use std::sync::Arc;
use std::cell::RefCell;

/// Box<T>: Heap allocation with single owner
fn box_demo() {
    // Box allocates on heap, provides owned pointer
    let boxed = Box::new(42);
    println!("Boxed value: {}", boxed);
    
    // Useful for recursive types where size is unknown at compile time
    #[derive(Debug)]
    enum List {
        Cons(i32, Box<List>),  // Box needed - List has infinite size
        Nil,
    }
    
    let list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
    println!("Recursive list: {:?}", list);
    
    // Box is deallocated when it goes out of scope
}

/// Rc<T>: Reference counted for multiple owners (single-threaded)
fn rc_demo() {
    // Rc enables shared ownership
    let shared = Rc::new(vec![1, 2, 3, 4, 5]);
    
    println!("Reference count: {}", Rc::strong_count(&shared));  // 1
    
    let clone1 = Rc::clone(&shared);
    println!("After clone: {}", Rc::strong_count(&shared));  // 2
    
    {
        let clone2 = Rc::clone(&shared);
        println!("Nested scope count: {}", Rc::strong_count(&shared));  // 3
    }  // clone2 dropped here
    
    println!("After inner scope: {}", Rc::strong_count(&shared));  // 2
    
    // All clones point to same data
    println!("Clone1 data: {:?}", clone1);
}

/// Arc<T>: Atomically reference counted for multiple owners (thread-safe)
fn arc_demo() {
    use std::thread;
    
    let shared_data = Arc::new(vec![1, 2, 3, 4, 5]);
    let mut handles = vec![];
    
    for i in 0..3 {
        let data_clone = Arc::clone(&shared_data);
        handles.push(thread::spawn(move || {
            println!("Thread {}: {:?}", i, *data_clone);
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

/// Combining interior mutability with shared ownership
fn interior_mutability_demo() {
    // RefCell provides runtime borrow checking for interior mutability
    let shared = Rc::new(RefCell::new(vec![1, 2, 3]));
    
    let clone1 = Rc::clone(&shared);
    let clone2 = Rc::clone(&shared);
    
    // Any clone can mutate - borrow checked at runtime
    clone1.borrow_mut().push(4);
    clone2.borrow_mut().push(5);
    
    println!("Modified vector: {:?}", *shared.borrow());
}

fn main() {
    box_demo();
    rc_demo();
    arc_demo();
    interior_mutability_demo();
}
```

### Safety Analysis

**Smart Pointer Safety Guarantees:**

1. **Box<T>**: Provides heap allocation with deterministic deallocation. Memory is freed when the Box goes out of scope. No reference counting overhead.

2. **Rc<T>**: Reference counting prevents premature deallocation. Memory is freed only when the last Rc is dropped. Runtime cost is minimal (increment/decrement operations).

3. **Arc<T>**: Uses atomic operations for thread-safe reference counting. Slightly slower than Rc due to atomic operations, but safe for concurrent access. Memory is freed when the last Arc across all threads is dropped.

4. **Interior Mutability (RefCell)**: Combines with Rc for shared mutable state. Runtime borrow checking panics if rules are violated:
   - Multiple immutable borrows OR
   - Single mutable borrow
   - Never both simultaneously

**Memory Safety**: All smart pointers prevent:
- Use-after-free: Memory only deallocated when no references exist
- Double-free: Reference counting ensures single deallocation
- Dangling pointers: References remain valid as long as pointer exists

**Thread Safety**: Arc uses atomic operations (SeqCst ordering) ensuring reference count updates are visible across threads. Rc deliberately does NOT implement Send to prevent data races.

**When to Use Each:**
- `Box`: Single owner, heap allocation needed
- `Rc`: Multiple owners, single-threaded only
- `Arc`: Multiple owners, multi-threaded
- `Rc<RefCell<T>>`: Multiple owners, mutation needed, single-threaded
- `Arc<Mutex<T>>`: Multiple owners, mutation needed, multi-threaded

---

## Topic: Error Handling (Result, Option)

### Implementation

```rust
use std::fs::File;
use std::io::{self, Read, Write};
use std::num::ParseIntError;

/// Option<T>: Represents presence or absence of a value
fn option_demo() -> Option<i32> {
    let maybe_value: Option<i32> = Some(42);
    
    // Pattern matching for explicit handling
    match maybe_value {
        Some(v) => println!("Found value: {}", v),
        None => println!("No value found"),
    }
    
    // Safe unwrapping with default
    let value = maybe_value.unwrap_or(0);
    
    // Chaining operations on optional values
    let result = maybe_value
        .filter(|&x| x > 20)
        .map(|x| x * 2)
        .ok_or("Value too small")?;
    
    Some(result)
}

/// Result<T, E>: Represents success or failure
fn result_demo() -> Result<String, io::Error> {
    // File operations return Result
    let mut file = File::open("config.txt")?;
    
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    
    Ok(contents)
}

/// Custom error types for better error handling
#[derive(Debug)]
enum AppError {
    Io(io::Error),
    Parse(ParseIntError),
    NotFound(String),
}

// Implement From traits for automatic conversion
impl From<io::Error> for AppError {
    fn from(err: io::Error) -> Self {
        AppError::Io(err)
    }
}

impl From<ParseIntError> for AppError {
    fn from(err: ParseIntError) -> Self {
        AppError::Parse(err)
    }
}

/// Combining multiple fallible operations
fn parse_config_file(path: &str) -> Result<Config, AppError> {
    let mut file = File::open(path)?;  // ? auto-converts io::Error to AppError
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    
    let port: u16 = contents.lines()
        .find(|line| line.starts_with("port="))
        .ok_or(AppError::NotFound("port configuration".into()))?
        .strip_prefix("port=")
        .ok_or(AppError::NotFound("port value".into()))?
        .parse()?;  // ? auto-converts ParseIntError to AppError
    
    Ok(Config { port })
}

#[derive(Debug)]
struct Config {
    port: u16,
}

/// Using combinators for functional error handling
fn functional_error_handling(input: &str) -> Result<i32, String> {
    input
        .parse::<i32>()
        .map_err(|e| format!("Parse failed: {}", e))
        .map(|n| n * 2)
        .and_then(|n| {
            if n > 100 {
                Ok(n)
            } else {
                Err("Value too small".into())
            }
        })
}

/// Early return pattern with Result
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Division by zero".into())
    } else {
        Ok(a / b)
    }
}

fn calculate(a: f64, b: f64, c: f64) -> Result<f64, String> {
    let x = divide(a, b)?;
    let y = divide(x, c)?;
    Ok(y + 1.0)
}

fn main() {
    // Option handling
    if let Some(v) = option_demo() {
        println!("Result: {}", v);
    }
    
    // Result handling
    match result_demo() {
        Ok(contents) => println!("Config: {}", contents),
        Err(e) => eprintln!("Error reading config: {}", e),
    }
    
    // Error propagation
    match parse_config_file("app.cfg") {
        Ok(config) => println!("Port: {}", config.port),
        Err(AppError::NotFound(msg)) => eprintln!("Not found: {}", msg),
        Err(e) => eprintln!("Error: {:?}", e),
    }
}
```

### Safety Analysis

**Error Handling Safety Guarantees:**

1. **No Null Pointers**: Option<T> replaces null. You must explicitly handle the None case; the compiler won't let you access a potentially absent value.

2. **Explicit Error Propagation**: The `?` operator automatically propagates errors up the call stack, ensuring errors are never silently ignored. Each function's return type documents its failure modes.

3. **Type-Safe Errors**: Result<T, E> makes error handling part of the type system. You cannot forget to handle errors - the compiler enforces it.

4. **Zero-Cost Abstractions**: Option and Result have no runtime overhead in the success path. The compiler optimizes away the enum variants.

5. **Composability**: Combinators (map, and_then, ok_or) allow chaining operations without explicit match statements, making code more readable while maintaining safety.

**Memory Safety in Error Paths:**

- **RAII (Resource Acquisition Is Initialization)**: When a function returns early via `?`, all local variables are automatically dropped. Resources are never leaked.

- **Unwinding**: In error paths, destructors run in reverse order of construction, ensuring proper cleanup.

**Best Practices:**

- Use `Option` when absence is expected (finding items, optional configuration)
- Use `Result` for operations that can fail (I/O, parsing, validation)
- Define custom error types with `From` implementations for clean error conversion
- Use `?` for early returns instead of nested match expressions
- Prefer combinators for simple transformations

**Comparison to Exceptions**: Unlike exceptions, Rust errors are explicit in function signatures, making control flow visible. No hidden stack unwinding across arbitrary code.

---

## Topic: Concurrent Access (Mutex, RwLock)

### Implementation

```rust
use std::sync::{Arc, Mutex, RwLock};
use std::thread;
use std::time::Duration;

/// Mutex<T>: Mutual exclusion for exclusive access
fn mutex_demo() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            // lock() returns MutexGuard, automatically unlocks when dropped
            let mut num = counter_clone.lock().unwrap();
            *num += 1;
            
            // MutexGuard dropped here, lock released
            println!("Thread incremented to: {}", *num);
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("Final count: {}", *counter.lock().unwrap());
}

/// RwLock<T>: Reader-writer lock for concurrent reads
fn rwlock_demo() {
    let data = Arc::new(RwLock::new(vec![1, 2, 3]));
    let mut handles = vec![];
    
    // Spawn multiple readers
    for i in 0..3 {
        let data_clone = Arc::clone(&data);
        handles.push(thread::spawn(move || {
            // Multiple read locks can be held simultaneously
            let read_data = data_clone.read().unwrap();
            println!("Reader {}: {:?}", i, *read_data);
        }));
    }
    
    // Spawn a writer
    {
        let data_clone = Arc::clone(&data);
        handles.push(thread::spawn(move || {
            // Write lock is exclusive - blocks all readers
            let mut write_data = data_clone.write().unwrap();
            write_data.push(4);
            println!("Writer added element");
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

/// Deadlock-free mutex usage patterns
fn deadlock_prevention() {
    let resource1 = Arc::new(Mutex::new("Resource 1"));
    let resource2 = Arc::new(Mutex::new("Resource 2"));
    
    let r1 = Arc::clone(&resource1);
    let r2 = Arc::clone(&resource2);
    
    // Always acquire locks in the same order to prevent deadlock
    let handle = thread::spawn(move || {
        let _guard1 = r1.lock().unwrap();  // Acquire first
        println!("Thread acquired resource1");
        
        // Small delay to make deadlock more likely if ordering is wrong
        thread::sleep(Duration::from_millis(10));
        
        let _guard2 = r2.lock().unwrap();  // Then second
        println!("Thread acquired resource2");
    });
    
    // Main thread acquires in same order
    let _guard1 = resource1.lock().unwrap();
    let _guard2 = resource2.lock().unwrap();
    println!("Main acquired both resources");
    
    handle.join().unwrap();
}

/// Condition variables for efficient waiting
use std::sync::Condvar;

fn condvar_demo() {
    let pair = Arc::new((Mutex::new(false), Condvar::new()));
    let pair_clone = Arc::clone(&pair);
    
    // Waiting thread
    let waiter = thread::spawn(move || {
        let (lock, cvar) = &*pair_clone;
        let mut started = lock.lock().unwrap();
        
        // Wait for condition, loop to handle spurious wakeups
        while !*started {
            started = cvar.wait(started).unwrap();
        }
        
        println!("Waiter thread proceeding!");
    });
    
    // Signaling thread
    thread::sleep(Duration::from_millis(100));
    {
        let (lock, cvar) = &*pair;
        let mut started = lock.lock().unwrap();
        *started = true;
        cvar.notify_one();  // Wake up waiting thread
    }
    
    waiter.join().unwrap();
}

/// Thread-safe shared state with interior mutability
struct SharedCounter {
    count: Mutex<i32>,
}

impl SharedCounter {
    fn new() -> Self {
        SharedCounter {
            count: Mutex::new(0),
        }
    }
    
    fn increment(&self) -> i32 {
        let mut num = self.count.lock().unwrap();
        *num += 1;
        *num
    }
    
    fn get(&self) -> i32 {
        *self.count.lock().unwrap()
    }
}

fn main() {
    mutex_demo();
    rwlock_demo();
    deadlock_prevention();
    condvar_demo();
}
```

### Safety Analysis

**Concurrency Safety Guarantees:**

1. **Mutex Guarantees Mutual Exclusion**: Only one thread can hold the lock at a time. The type system enforces this through `MutexGuard<T>` which provides mutable access only while the lock is held.

2. **RwLock Allows Concurrent Reads**: Multiple threads can hold read locks simultaneously, but write locks are exclusive. This improves performance for read-heavy workloads.

3. **Poisoning Prevents Undefined Behavior**: If a thread panics while holding a lock, the lock becomes "poisoned". Subsequent lock attempts return `PoisonError`, preventing access to potentially inconsistent data.

4. **RAII Lock Management**: Locks are automatically released when the guard goes out of scope. You cannot forget to unlock a mutex.

**Memory Safety:**

- **Data Race Prevention**: The combination of Rust's ownership system and lock types makes data races impossible. You cannot access the data without holding the lock.
- **Send + Sync Traits**: Types inside `Arc<Mutex<T>>` must implement `Send`, ensuring safe transfer between threads. The `Sync` trait is automatically implemented for types protected by locks.

**Deadlock Prevention Strategies:**

1. **Lock Ordering**: Always acquire multiple locks in a consistent order
2. **Lock Duration**: Hold locks for the minimum time necessary
3. **Avoid Nested Locks**: When possible, restructure code to avoid needing multiple locks
4. **Use Condvar**: For waiting on conditions, use condition variables instead of polling

**Performance Considerations:**

- **Mutex vs RwLock**: Use RwLock when reads significantly outnumber writes
- **Lock Contention**: High contention degrades performance; consider lock-free data structures
- **Lock Granularity**: Finer-grained locks reduce contention but increase complexity

**Comparison to Manual Locking**: In C/C++, forgetting to unlock is a common bug. Rust's RAII guards make this impossible.

---

## Topic: Async/Await Basics

### Implementation

```rust
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::Duration;
use tokio::time::sleep;

/// Basic async function
async fn say_hello() {
    println!("Hello, async world!");
}

/// Async function returning a value
async fn compute_value() -> i32 {
    // Simulate async work
    sleep(Duration::from_millis(100)).await;
    42
}

/// Async function with error handling
async fn fetch_data(id: u32) -> Result<String, String> {
    sleep(Duration::from_millis(50)).await;
    
    if id == 0 {
        Err("Invalid ID".into())
    } else {
        Ok(format!("Data for ID {}", id))
    }
}

/// Combining multiple async operations
async fn fetch_multiple(ids: Vec<u32>) -> Vec<Result<String, String>> {
    let mut results = vec![];
    
    for id in ids {
        // Sequential execution - each await pauses this task
        let result = fetch_data(id).await;
        results.push(result);
    }
    
    results
}

/// Concurrent execution with join!
async fn concurrent_fetch(id1: u32, id2: u32) -> (Result<String, String>, Result<String, String>) {
    // Both futures run concurrently
    tokio::join!(fetch_data(id1), fetch_data(id2))
}

/// Select for racing futures
async fn race_fetch(id1: u32, id2: u32) -> Result<String, String> {
    use tokio::select;
    
    // Returns as soon as either completes
    select! {
        result = fetch_data(id1) => result,
        result = fetch_data(id2) => result,
    }
}

/// Custom Future implementation
struct Delay {
    duration: Duration,
    started: bool,
}

impl Delay {
    fn new(duration: Duration) -> Self {
        Delay {
            duration,
            started: false,
        }
    }
}

impl Future for Delay {
    type Output = ();
    
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        if !self.started {
            // Schedule a wake-up after the duration
            let waker = cx.waker().clone();
            let duration = self.duration;
            
            thread::spawn(move || {
                std::thread::sleep(duration);
                waker.wake();  // Wake the executor to poll again
            });
            
            self.started = true;
        }
        
        // If time hasn't elapsed, return Pending
        Poll::Pending
    }
}

/// Async stream processing
async fn process_stream() {
    use tokio_stream::StreamExt;
    
    let mut stream = tokio_stream::iter(1..=5);
    
    while let Some(value) = stream.next().await {
        println!("Processing: {}", value);
        sleep(Duration::from_millis(100)).await;
    }
}

/// Async channel communication
async fn async_channel_demo() {
    use tokio::sync::mpsc;
    
    let (tx, mut rx) = mpsc::channel(32);
    
    // Spawn task that sends messages
    let sender = tokio::spawn(async move {
        for i in 0..5 {
            tx.send(format!("Message {}", i)).await.unwrap();
            sleep(Duration::from_millis(50)).await;
        }
    });
    
    // Receive messages
    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }
    
    sender.await.unwrap();
}

/// Async with timeout
async fn fetch_with_timeout(id: u32) -> Result<String, String> {
    match tokio::time::timeout(
        Duration::from_millis(30),
        fetch_data(id)
    ).await {
        Ok(Ok(data)) => Ok(data),
        Ok(Err(e)) => Err(e),
        Err(_) => Err("Timeout".into()),
    }
}

#[tokio::main]
async fn main() {
    // Basic async calls
    say_hello().await;
    
    let value = compute_value().await;
    println!("Computed: {}", value);
    
    // Error handling
    match fetch_data(1).await {
        Ok(data) => println!("Success: {}", data),
        Err(e) => eprintln!("Error: {}", e),
    }
    
    // Concurrent execution
    let (r1, r2) = concurrent_fetch(1, 2).await;
    println!("Results: {:?}, {:?}", r1, r2);
    
    // Racing futures
    let winner = race_fetch(1, 2).await;
    println!("Winner: {:?}", winner);
    
    // Async channels
    async_channel_demo().await;
    
    // Stream processing
    process_stream().await;
}
```

### Safety Analysis

**Async Safety Guarantees:**

1. **Non-Blocking by Design**: Async code yields control back to the executor when waiting, allowing other tasks to run. The `.await` point is where suspension occurs.

2. **Cancellation Safety**: When a future is dropped, its state is cleaned up properly. However, care must be taken to ensure operations are cancellable (e.g., buffered writes may be lost).

3. **No Data Races**: Async code follows the same ownership rules as synchronous code. Multiple concurrent tasks cannot access the same mutable state without synchronization.

4. **Pinned Memory**: Futures that reference themselves (self-referential structs) use `Pin<T>` to ensure they aren't moved in memory after polling begins.

**Memory Safety in Async Context:**

- **Lifetime Propagation**: Async functions capture their arguments. The compiler ensures captured references remain valid for the lifetime of the future.
- **Send Trait**: Futures spawned on a multi-threaded executor must implement `Send`, ensuring all captured data is safe to transfer between threads.

**Common Pitfalls:**

1. **Blocking in Async**: Never call blocking functions (like `std::thread::sleep`) in async code. Use async equivalents (`tokio::time::sleep`).

2. **Holding Locks Across Await**: Never hold a `Mutex` lock across an `.await` point - this can cause deadlocks. Use `tokio::sync::Mutex` instead.

3. **Cancellation**: Dropping a future cancels it. Ensure cleanup happens correctly (e.g., dropping a half-written buffer).

**Executor Model:**

- **Work-Stealing**: Tokio's multi-threaded scheduler distributes work across threads
- **Cooperative Scheduling**: Tasks voluntarily yield at `.await` points
- **Efficient I/O**: Uses epoll/kqueue/IOCP for efficient I/O multiplexing

**Comparison to Threads:**

- **Lower Overhead**: Async tasks are cheaper than OS threads (stack size, context switch)
- **Better Scalability**: Can handle thousands of concurrent tasks
- **Cooperative**: Tasks must yield; CPU-bound work should be offloaded to blocking threads

**When to Use Async:**

- High-concurrency I/O workloads (servers, databases)
- Many connections with low CPU usage per connection
- When you need to handle thousands of simultaneous operations

---

## Summary

These examples demonstrate Rust's approach to systems programming:

1. **Compile-Time Safety**: Most memory errors are caught at compile time
2. **Zero-Cost Abstractions**: Safety features have no runtime overhead
3. **Explicit Control**: The programmer has fine-grained control over memory and concurrency
4. **Composable Primitives**: Small, safe components combine into larger systems
5. **Thread Safety Guaranteed**: Data races are impossible in safe Rust

Each example shows patterns that would require careful manual management in C/C++ but are enforced automatically by Rust's type system.
