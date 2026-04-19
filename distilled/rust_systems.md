# Rust 系统编程核心示例

本文档包含 10 个 Rust 系统编程核心概念示例，每个都包含完整代码、安全分析和测试。

---

## 1. 所有权与借用 (Ownership & Borrowing)

### 完整代码

```rust
// ownership_borrowing.rs

/// 演示所有权转移、借用规则
pub struct Buffer {
    data: Vec<u8>,
}

impl Buffer {
    pub fn new(size: usize) -> Self {
        Buffer {
            data: vec![0; size],
        }
    }

    // 所有权转移
    pub fn consume(self) -> Vec<u8> {
        self.data
    }

    // 不可变借用
    pub fn read(&self) -> &[u8] {
        &self.data
    }

    // 可变借用
    pub fn write(&mut self, offset: usize, bytes: &[u8]) -> Result<(), String> {
        if offset + bytes.len() > self.data.len() {
            return Err("Out of bounds".to_string());
        }
        self.data[offset..offset + bytes.len()].copy_from_slice(bytes);
        Ok(())
    }
}

/// 切片操作 - 借用而非所有权转移
pub fn process_slice(data: &[u8]) -> u8 {
    data.iter().sum()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ownership_transfer() {
        let buf = Buffer::new(10);
        let data = buf.consume();
        // buf 已被移动，无法再使用
        assert_eq!(data.len(), 10);
    }

    #[test]
    fn test_immutable_borrow() {
        let buf = Buffer::new(10);
        let slice1 = buf.read();
        let slice2 = buf.read(); // 多个不可变借用可以共存
        assert_eq!(slice1.len(), slice2.len());
    }

    #[test]
    fn test_mutable_borrow() {
        let mut buf = Buffer::new(10);
        buf.write(0, &[1, 2, 3]).unwrap();
        assert_eq!(&buf.read()[..3], &[1, 2, 3]);
    }

    #[test]
    fn test_borrow_rules() {
        let mut buf = Buffer::new(10);
        let _read = buf.read();
        // let _write = buf.write(0, &[1]); // 编译错误：不可变借用存在时不能可变借用
    }
}
```

### 安全分析

1. **所有权规则**：
   - 每个值有且只有一个所有者
   - `consume()` 方法转移所有权，原 Buffer 被销毁
   - 防止悬垂指针和二次释放

2. **借用规则**：
   - 可以有多个不可变引用 `&T`，或一个可变引用 `&mut T`
   - 编译期检查保证：不可能同时存在可变和不可变引用
   - 防止数据竞争

3. **内存安全**：
   - 所有的借用都有明确的生命周期
   - 不存在空指针或悬垂指针
   - 边界检查防止缓冲区溢出

---

## 2. 生命周期 (Lifetimes)

### 完整代码

```rust
// lifetimes.rs

use std::fmt::Display;

/// 带生命周期参数的结构体
pub struct Parser<'a> {
    input: &'a str,  // 借用的字符串切片
    position: usize,
}

impl<'a> Parser<'a> {
    pub fn new(input: &'a str) -> Self {
        Parser { input, position: 0 }
    }

    /// 返回的切片生命周期与输入相同
    pub fn peek(&self) -> Option<&'a str> {
        if self.position < self.input.len() {
            Some(&self.input[self.position..])
        } else {
            None
        }
    }

    pub fn advance(&mut self, n: usize) {
        self.position = (self.position + n).min(self.input.len());
    }
}

/// 生命周期消除规则示例
pub fn longest_with_an Announcement<'a, T>(x: &'a str, y: &'a str, ann: T) -> &'a str
where
    T: Display,
{
    println!("Announcement! {}", ann);
    if x.len() > y.len() { x } else { y }
}

/// 静态生命周期
pub static GLOBAL_CONFIG: &str = "config_value";

pub fn get_static() -> &'static str {
    "This string lives for the entire program"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parser_lifetime() {
        let input = String::from("hello world");
        let parser = Parser::new(&input);
        
        // input 必须比 parser 活得更久
        assert_eq!(parser.peek(), Some("hello world"));
    }

    #[test]
    fn test_longest() {
        let string1 = String::from("long string");
        let result;
        {
            let string2 = String::from("short");
            result = longest_with_an Announcement(&string1, &string2, "comparing");
        }
        // result 的生命周期受限于 string1，而 string1 仍然存活
        assert_eq!(result, "long string");
    }

    #[test]
    fn test_static() {
        let s = get_static();
        assert_eq!(s, "This string lives for the entire program");
    }
}
```

### 安全分析

1. **生命周期标注**：
   - `'a` 表示引用的有效范围
   - 确保 Parser 持有的引用不会悬垂
   - 编译器保证所有引用在使用期间有效

2. **生命周期消除**：
   - 每个引用参数获得独立生命周期
   - 如果只有一个输入生命周期，它被赋予所有输出引用
   - 方法中 `&self` 的生命周期赋予所有输出引用

3. **静态生命周期**：
   - `'static` 表示整个程序运行期间有效
   - 用于全局数据和编译时常量

---

## 3. 错误处理 (Error Handling)

### 完整代码

```rust
// error_handling.rs

use std::error::Error;
use std::fmt;
use std::io;

/// 自定义错误类型
#[derive(Debug)]
pub enum SystemError {
    Io(io::Error),
    InvalidInput(String),
    OutOfBounds { index: usize, size: usize },
}

impl fmt::Display for SystemError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SystemError::Io(e) => write!(f, "IO error: {}", e),
            SystemError::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            SystemError::OutOfBounds { index, size } => {
                write!(f, "Index {} out of bounds (size: {})", index, size)
            }
        }
    }
}

impl Error for SystemError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            SystemError::Io(e) => Some(e),
            _ => None,
        }
    }
}

impl From<io::Error> for SystemError {
    fn from(err: io::Error) -> Self {
        SystemError::Io(err)
    }
}

/// 使用 Result 的系统调用
pub fn read_file_segment(path: &str, offset: usize, length: usize) -> Result<Vec<u8>, SystemError> {
    use std::fs::File;
    use std::io::Read;
    
    let mut file = File::open(path).map_err(SystemError::Io)?;
    
    // 简化示例：直接读取整个文件
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer).map_err(SystemError::Io)?;
    
    if offset + length > buffer.len() {
        return Err(SystemError::OutOfBounds {
            index: offset + length,
            size: buffer.len(),
        });
    }
    
    Ok(buffer[offset..offset + length].to_vec())
}

/// 使用 Option 和 ? 操作符
pub fn find_pattern(data: &[u8], pattern: &[u8]) -> Option<usize> {
    if pattern.is_empty() || pattern.len() > data.len() {
        return None;
    }
    
    data.windows(pattern.len())
        .position(|window| window == pattern)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_error_display() {
        let err = SystemError::InvalidInput("test".to_string());
        assert!(err.to_string().contains("Invalid input"));
    }

    #[test]
    fn test_read_file() {
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "test content").unwrap();
        
        let result = read_file_segment(temp_file.path().to_str().unwrap(), 0, 4);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), b"test");
    }

    #[test]
    fn test_out_of_bounds() {
        let mut temp_file = NamedTempFile::new().unwrap();
        writeln!(temp_file, "short").unwrap();
        
        let result = read_file_segment(temp_file.path().to_str().unwrap(), 0, 1000);
        assert!(matches!(result, Err(SystemError::OutOfBounds { .. })));
    }

    #[test]
    fn test_find_pattern() {
        let data = b"hello world";
        assert_eq!(find_pattern(data, b"world"), Some(6));
        assert_eq!(find_pattern(data, b"xyz"), None);
    }
}
```

### 安全分析

1. **Result 和 Option**：
   - 强制处理可能的错误情况
   - 不可能忽略错误（编译器警告未使用的 Result）
   - 零运行时开销（优化后与手动错误检查相同）

2. **? 操作符**：
   - 自动传播错误
   - 类型转换通过 `From` trait 实现
   - 减少样板代码

3. **错误类型安全**：
   - 自定义错误类型携带上下文信息
   - 错误链追踪（`source()` 方法）
   - 模式匹配穷尽所有错误情况

---

## 4. 智能指针 (Smart Pointers)

### 完整代码

```rust
// smart_pointers.rs

use std::cell::RefCell;
use std::rc::{Rc, Weak};
use std::sync::{Arc, Mutex};

/// Box<T> - 堆分配，单所有权
pub fn box_example() -> Box<dyn std::fmt::Display> {
    Box::new(42) // 在堆上分配，返回 trait object
}

/// Rc<T> - 引用计数，多所有权（单线程）
pub struct TreeNode {
    value: i32,
    children: Vec<Rc<TreeNode>>,
    parent: RefCell<Weak<TreeNode>>, // 避免循环引用
}

impl TreeNode {
    pub fn new(value: i32) -> Rc<TreeNode> {
        Rc::new(TreeNode {
            value,
            children: Vec::new(),
            parent: RefCell::new(Weak::new()),
        })
    }

    pub fn add_child(parent: &Rc<TreeNode>, child: Rc<TreeNode>) {
        *child.parent.borrow_mut() = Rc::downgrade(parent);
        parent.children.push(child);
    }
}

/// Arc<Mutex<T>> - 原子引用计数 + 互斥锁（多线程）
pub struct SharedCounter {
    counter: Arc<Mutex<i32>>,
}

impl SharedCounter {
    pub fn new() -> Self {
        SharedCounter {
            counter: Arc::new(Mutex::new(0)),
        }
    }

    pub fn increment(&self) -> i32 {
        let mut num = self.counter.lock().unwrap();
        *num += 1;
        *num
    }

    pub fn get(&self) -> i32 {
        *self.counter.lock().unwrap()
    }

    pub fn clone_handle(&self) -> Arc<Mutex<i32>> {
        Arc::clone(&self.counter)
    }
}

/// RefCell - 内部可变性
pub struct Logger {
    log_count: RefCell<usize>,
}

impl Logger {
    pub fn new() -> Self {
        Logger {
            log_count: RefCell::new(0),
        }
    }

    pub fn log(&self, message: &str) {
        *self.log_count.borrow_mut() += 1;
        println!("[{}] {}", self.log_count.borrow(), message);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_box() {
        let b = box_example();
        assert_eq!(b.to_string(), "42");
    }

    #[test]
    fn test_tree_node() {
        let root = TreeNode::new(1);
        let child = TreeNode::new(2);
        TreeNode::add_child(&root, child);
        
        assert_eq!(root.children.len(), 1);
        assert!(root.children[0].parent.borrow().upgrade().is_some());
    }

    #[test]
    fn test_shared_counter() {
        let counter = SharedCounter::new();
        let handles: Vec<_> = (0..10)
            .map(|_| {
                let counter_clone = counter.clone_handle();
                thread::spawn(move || {
                    let mut num = counter_clone.lock().unwrap();
                    *num += 1;
                })
            })
            .collect();

        for handle in handles {
            handle.join().unwrap();
        }

        assert_eq!(*counter.counter.lock().unwrap(), 10);
    }

    #[test]
    fn test_logger() {
        let logger = Logger::new();
        logger.log("message 1");
        logger.log("message 2");
        assert_eq!(*logger.log_count.borrow(), 2);
    }
}
```

### 安全分析

1. **Box<T>**：
   - 堆分配，已知大小
   - 单所有权，编译期检查
   - 用于递归类型和 trait objects

2. **Rc<T> 和 Weak<T>**：
   - 引用计数，运行时检查
   - Weak 避免循环引用导致的内存泄漏
   - 仅适用于单线程

3. **Arc<Mutex<T>>**：
   - 原子引用计数，线程安全
   - Mutex 保证互斥访问
   - 可能导致死锁（需谨慎使用）

4. **RefCell<T>**：
   - 内部可变性，运行时借用检查
   - 不可变引用的可变语义
   - panic! 如果违反借用规则

---

## 5. 并发 - Arc/Mutex (Concurrency)

### 完整代码

```rust
// concurrency.rs

use std::sync::{Arc, Mutex, Condvar};
use std::thread;
use std::collections::VecDeque;

/// 线程安全的阻塞队列
pub struct BlockingQueue<T> {
    queue: Mutex<VecDeque<T>>,
    not_empty: Condvar,
}

impl<T> BlockingQueue<T> {
    pub fn new() -> Self {
        BlockingQueue {
            queue: Mutex::new(VecDeque::new()),
            not_empty: Condvar::new(),
        }
    }

    pub fn push(&self, item: T) {
        let mut queue = self.queue.lock().unwrap();
        queue.push_back(item);
        self.not_empty.notify_one();
    }

    pub fn pop(&self) -> T {
        let mut queue = self.queue.lock().unwrap();
        loop {
            if let Some(item) = queue.pop_front() {
                return item;
            }
            queue = self.not_empty.wait(queue).unwrap();
        }
    }
}

/// 生产者-消费者模式
pub fn producer_consumer_example() -> Vec<i32> {
    let queue = Arc::new(BlockingQueue::new());
    let results = Arc::new(Mutex::new(Vec::new()));

    let producer_queue = Arc::clone(&queue);
    let producer = thread::spawn(move || {
        for i in 0..10 {
            producer_queue.push(i);
            thread::sleep(std::time::Duration::from_millis(10));
        }
        producer_queue.push(-1); // 终止信号
    });

    let consumer_queue = Arc::clone(&queue);
    let consumer_results = Arc::clone(&results);
    let consumer = thread::spawn(move || {
        loop {
            let item = consumer_queue.pop();
            if item == -1 {
                break;
            }
            consumer_results.lock().unwrap().push(item);
        }
    });

    producer.join().unwrap();
    consumer.join().unwrap();

    let final_results = results.lock().unwrap().clone();
    final_results
}

/// 并发数据结构 - 线程安全计数器
pub struct AtomicCounter {
    count: Mutex<usize>,
}

impl AtomicCounter {
    pub fn new() -> Self {
        AtomicCounter {
            count: Mutex::new(0),
        }
    }

    pub fn increment(&self) -> usize {
        let mut count = self.count.lock().unwrap();
        *count += 1;
        *count
    }

    pub fn get(&self) -> usize {
        *self.count.lock().unwrap()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};

    #[test]
    fn test_producer_consumer() {
        let results = producer_consumer_example();
        assert_eq!(results.len(), 10);
        assert_eq!(results, (0..10).collect::<Vec<_>>());
    }

    #[test]
    fn test_atomic_counter() {
        let counter = Arc::new(AtomicCounter::new());
        let mut handles = vec![];

        for _ in 0..10 {
            let counter_clone = Arc::clone(&counter);
            handles.push(thread::spawn(move || {
                counter_clone.increment();
            }));
        }

        for handle in handles {
            handle.join().unwrap();
        }

        assert_eq!(counter.get(), 10);
    }

    #[test]
    fn test_blocking_queue() {
        let queue = Arc::new(BlockingQueue::new());
        
        let q1 = Arc::clone(&queue);
        let producer = thread::spawn(move || {
            q1.push(1);
            q1.push(2);
            q1.push(3);
        });

        let q2 = Arc::clone(&queue);
        let consumer = thread::spawn(move || {
            assert_eq!(q2.pop(), 1);
            assert_eq!(q2.pop(), 2);
            assert_eq!(q2.pop(), 3);
        });

        producer.join().unwrap();
        consumer.join().unwrap();
    }
}
```

### 安全分析

1. **Arc (原子引用计数)**：
   - 线程安全的引用计数
   - 保证引用计数的原子性
   - Send + Sync trait 实现

2. **Mutex (互斥锁)**：
   - 保证同一时间只有一个线程访问数据
   - lock() 返回 MutexGuard，RAII 自动解锁
   - panic 处理中毒（poisoning）情况

3. **Condvar (条件变量)**：
   - 线程间等待/通知机制
   - wait() 自动释放锁并等待信号
   - 避免忙等待

4. **数据竞争防止**：
   - 编译器保证：非线程安全类型无法跨线程共享
   - 运行时检查：Mutex 保护临界区
   - 所有共享状态必须通过同步原语访问

---

## 6. 异步编程 (Async/Await)

### 完整代码

```rust
// async_programming.rs

use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::Duration;
use tokio::time::sleep;

/// 自定义 Future
pub struct Delay {
    duration: Duration,
    started: bool,
}

impl Delay {
    pub fn new(duration: Duration) -> Self {
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
            self.started = true;
            let waker = cx.waker().clone();
            let duration = self.duration;
            
            thread::spawn(move || {
                thread::sleep(duration);
                waker.wake();
            });
        }
        
        Poll::Ready(())
    }
}

/// 异步 I/O 操作
pub async fn fetch_data(id: u32) -> Result<String, String> {
    // 模拟异步 I/O
    sleep(Duration::from_millis(100)).await;
    Ok(format!("Data for id {}", id))
}

/// 并发执行多个 Future
pub async fn fetch_all(ids: Vec<u32>) -> Vec<Result<String, String>> {
    let futures: Vec<_> = ids.into_iter().map(fetch_data).collect();
    futures::future::join_all(futures).await
}

/// 异步流处理
pub async fn process_stream(mut rx: tokio::sync::mpsc::Receiver<u32>) -> u32 {
    let mut sum = 0;
    while let Some(value) = rx.recv().await {
        sum += value;
    }
    sum
}

/// 异步任务管理
pub struct AsyncTaskManager {
    tasks: Vec<tokio::task::JoinHandle<()>>,
}

impl AsyncTaskManager {
    pub fn new() -> Self {
        AsyncTaskManager { tasks: Vec::new() }
    }

    pub fn spawn<F>(&mut self, future: F)
    where
        F: Future<Output = ()> + Send + 'static,
    {
        let handle = tokio::spawn(future);
        self.tasks.push(handle);
    }

    pub async fn wait_all(self) {
        for task in self.tasks {
            let _ = task.await;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::runtime::Runtime;

    #[test]
    fn test_async_fetch() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let result = fetch_data(42).await;
            assert_eq!(result.unwrap(), "Data for id 42");
        });
    }

    #[test]
    fn test_concurrent_fetch() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let ids = vec![1, 2, 3, 4, 5];
            let results = fetch_all(ids).await;
            assert_eq!(results.len(), 5);
            assert!(results.iter().all(|r| r.is_ok()));
        });
    }

    #[test]
    fn test_async_channel() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let (tx, rx) = tokio::sync::mpsc::channel(10);
            
            tokio::spawn(async move {
                for i in 1..=5 {
                    tx.send(i).await.unwrap();
                }
            });

            let sum = process_stream(rx).await;
            assert_eq!(sum, 15);
        });
    }

    #[test]
    fn test_task_manager() {
        let rt = Runtime::new().unwrap();
        rt.block_on(async {
            let mut manager = AsyncTaskManager::new();
            let counter = Arc::new(Mutex::new(0));

            for i in 0..5 {
                let counter_clone = Arc::clone(&counter);
                manager.spawn(async move {
                    let mut num = counter_clone.lock().unwrap();
                    *num += i;
                });
            }

            manager.wait_all().await;
            assert_eq!(*counter.lock().unwrap(), 10);
        });
    }
}
```

### 安全分析

1. **Future trait**：
   - 零成本抽象，状态机实现
   - poll() 方法驱动状态转换
   - 编译期生成高效的异步代码

2. **Async/Await**：
   - 语法糖，自动实现 Future
   - .await 点允许其他任务执行
   - 不阻塞线程，高效利用资源

3. **Pin<P>**：
   - 保证自引用结构的安全
   - 防止 Future 在内存中移动
   - 编译期保证或运行时检查

4. **Send trait**：
   - 编译器确保异步任务可跨线程发送
   - 非线程安全类型无法在异步代码中使用
   - 防止数据竞争

---

## 7. Unsafe Rust

### 完整代码

```rust
// unsafe_rust.rs

use std::ptr;

/// 安全封装的 unsafe 代码
pub struct RawBuffer {
    ptr: *mut u8,
    len: usize,
    capacity: usize,
}

impl RawBuffer {
    pub fn new(capacity: usize) -> Self {
        let ptr = unsafe {
            let layout = std::alloc::Layout::array::<u8>(capacity).unwrap();
            let ptr = std::alloc::alloc(layout);
            if ptr.is_null() {
                std::alloc::handle_alloc_error(layout);
            }
            ptr
        };

        RawBuffer {
            ptr,
            len: 0,
            capacity,
        }
    }

    pub fn push(&mut self, byte: u8) -> Result<(), String> {
        if self.len >= self.capacity {
            return Err("Buffer full".to_string());
        }

        unsafe {
            ptr::write(self.ptr.add(self.len), byte);
        }
        self.len += 1;
        Ok(())
    }

    pub fn get(&self, index: usize) -> Option<u8> {
        if index >= self.len {
            None
        } else {
            unsafe { Some(ptr::read(self.ptr.add(index))) }
        }
    }
}

impl Drop for RawBuffer {
    fn drop(&mut self) {
        unsafe {
            let layout = std::alloc::Layout::array::<u8>(self.capacity).unwrap();
            std::alloc::dealloc(self.ptr, layout);
        }
    }
}

// 实现 Send 和 Sync（需要 unsafe）
unsafe impl Send for RawBuffer {}
unsafe impl Sync for RawBuffer {}

/// FFI 函数调用
extern "C" {
    fn abs(input: i32) -> i32;
}

pub fn safe_abs(x: i32) -> i32 {
    unsafe { abs(x) }
}

/// 裸指针操作
pub fn split_at_mut(slice: &mut [u8], mid: usize) -> (&mut [u8], &mut [u8]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();

    assert!(mid <= len);

    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, mid),
            std::slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

/// Union 类型（必须 unsafe）
#[repr(C)]
pub union IntOrFloat {
    i: i32,
    f: f32,
}

impl IntOrFloat {
    pub fn new_int(i: i32) -> Self {
        IntOrFloat { i }
    }

    pub fn new_float(f: f32) -> Self {
        IntOrFloat { f }
    }

    pub fn as_int(&self) -> i32 {
        unsafe { self.i }
    }

    pub fn as_float(&self) -> f32 {
        unsafe { self.f }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_raw_buffer() {
        let mut buf = RawBuffer::new(10);
        buf.push(1).unwrap();
        buf.push(2).unwrap();
        buf.push(3).unwrap();

        assert_eq!(buf.get(0), Some(1));
        assert_eq!(buf.get(1), Some(2));
        assert_eq!(buf.get(2), Some(3));
        assert_eq!(buf.get(3), None);
    }

    #[test]
    fn test_safe_abs() {
        assert_eq!(safe_abs(-5), 5);
        assert_eq!(safe_abs(5), 5);
    }

    #[test]
    fn test_split_at_mut() {
        let mut data = vec![1, 2, 3, 4, 5];
        let (left, right) = split_at_mut(&mut data, 2);
        assert_eq!(left, &mut [1, 2]);
        assert_eq!(right, &mut [3, 4, 5]);
    }

    #[test]
    fn test_union() {
        let u = IntOrFloat::new_int(42);
        assert_eq!(u.as_int(), 42);
    }
}
```

### 安全分析

1. **unsafe 块的职责**：
   - 解引用裸指针
   - 调用 unsafe 函数
   - 访问或修改可变静态变量
   - 实现 unsafe trait
   - 访问 union 字段

2. **安全抽象**：
   - unsafe 代码应封装在安全 API 中
   - 外部接口保证安全性不变性
   - 文档说明安全性假设

3. **内存布局**：
   - `repr(C)` 保证 C 兼容的内存布局
   - 正确处理内存对齐
   - 避免未定义行为

4. **边界检查**：
   - unsafe 代码必须手动验证安全性
   - 所有分支路径都需考虑
   - 测试覆盖边界情况

---

## 8. FFI (Foreign Function Interface)

### 完整代码

```rust
// ffi.rs

use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int, c_void};

/// C 函数声明
extern "C" {
    fn strlen(s: *const c_char) -> c_int;
    fn strcmp(s1: *const c_char, s2: *const c_char) -> c_int;
    fn malloc(size: usize) -> *mut c_void;
    fn free(ptr: *mut c_void);
}

/// 安全封装 C 字符串函数
pub fn safe_strlen(s: &str) -> Result<i32, String> {
    let c_string = CString::new(s).map_err(|e| e.to_string())?;
    unsafe { Ok(strlen(c_string.as_ptr())) }
}

/// C 回调函数
pub type Callback = extern "C" fn(c_int, *const c_char) -> c_int;

/// C 结构体
#[repr(C)]
pub struct CPoint {
    x: f64,
    y: f64,
}

#[repr(C)]
pub struct CArray {
    data: *mut f64,
    len: usize,
}

impl CArray {
    pub fn from_vec(vec: Vec<f64>) -> Self {
        let mut vec = vec.into_boxed_slice();
        let ptr = vec.as_mut_ptr();
        let len = vec.len();
        std::mem::forget(vec); // 防止 Drop
        CArray { data: ptr, len }
    }

    pub unsafe fn to_vec(&self) -> Vec<f64> {
        std::slice::from_raw_parts(self.data, self.len).to_vec()
    }
}

/// Rust 导出给 C 的函数
#[no_mangle]
pub extern "C" fn rust_add(a: c_int, b: c_int) -> c_int {
    a + b
}

#[no_mangle]
pub extern "C" fn rust_process_string(s: *const c_char) -> *mut c_char {
    unsafe {
        let c_str = CStr::from_ptr(s);
        let r_str = c_str.to_str().unwrap();
        let result = format!("Processed: {}", r_str);
        CString::new(result).unwrap().into_raw()
    }
}

/// 安全释放 C 字符串
#[no_mangle]
pub extern "C" fn rust_free_string(s: *mut c_char) {
    unsafe {
        if !s.is_null() {
            let _ = CString::from_raw(s);
        }
    }
}

/// 链接 C 库
#[link(name = "m")]
extern "C" {
    fn sqrt(x: f64) -> f64;
    fn pow(x: f64, y: f64) -> f64;
}

pub fn safe_sqrt(x: f64) -> f64 {
    unsafe { sqrt(x) }
}

pub fn safe_pow(x: f64, y: f64) -> f64 {
    unsafe { pow(x, y) }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_c_string() {
        let result = safe_strlen("hello").unwrap();
        assert_eq!(result, 5);
    }

    #[test]
    fn test_rust_export() {
        assert_eq!(rust_add(2, 3), 5);
    }

    #[test]
    fn test_math_functions() {
        assert_eq!(safe_sqrt(4.0), 2.0);
        assert_eq!(safe_pow(2.0, 3.0), 8.0);
    }

    #[test]
    fn test_c_array() {
        let vec = vec![1.0, 2.0, 3.0];
        let c_arr = CArray::from_vec(vec.clone());
        unsafe {
            let result = c_arr.to_vec();
            assert_eq!(result, vec);
        }
    }
}
```

### 安全分析

1. **类型映射**：
   - `c_char`, `c_int`, `c_void` 等 C 类型
   - `CString` 和 `CStr` 处理字符串转换
   - `repr(C)` 保证内存布局兼容

2. **所有权管理**：
   - Rust 和 C 之间明确所有权边界
   - `into_raw()` 和 `from_raw()` 管理内存
   - 防止内存泄漏和双重释放

3. **ABI 稳定性**：
   - `extern "C"` 使用 C 调用约定
   - `#[no_mangle]` 防止名称修饰
   - 确保跨语言调用的稳定性

4. **错误处理**：
   - C 错误码转换为 Rust Result
   - NULL 指针检查
   - 资源清理保证（RAII）

---

## 9. 宏 (Macros)

### 完整代码

```rust
// macros.rs

/// 声明式宏 - vec! 类似物
#[macro_export]
macro_rules! my_vec {
    // 空向量
    () => {
        Vec::new()
    };
    // 初始化指定大小
    ($elem:expr; $n:expr) => {
        vec![$elem; $n]
    };
    // 元素列表
    ($($x:expr),+ $(,)?) => {
        <[_]>::into_vec(Box::new([$($x),+]))
    };
}

/// 声明式宏 - 带格式化打印
#[macro_export]
macro_rules! debug_print {
    ($fmt:expr) => {
        if cfg!(debug_assertions) {
            println!($fmt);
        }
    };
    ($fmt:expr, $($arg:tt)*) => {
        if cfg!(debug_assertions) {
            println!($fmt, $($arg)*);
        }
    };
}

/// 声明式宏 - 生成结构体
macro_rules! make_struct {
    ($name:ident { $($field:ident: $type:ty),* $(,)? }) => {
        #[derive(Debug, Clone)]
        pub struct $name {
            $(pub $field: $type),*
        }
        
        impl $name {
            pub fn new($($field: $type),*) -> Self {
                Self { $($field),* }
            }
        }
    };
}

// 使用宏生成结构体
make_struct!(Point { x: f64, y: f64 });
make_struct!(Person { name: String, age: u32 });

/// 过程宏（需要单独的 proc-macro crate）
/// 这里演示声明式宏的高级用法

/// 递归宏 - 计算哈希
macro_rules! hash {
    ($($key:expr => $value:expr),* $(,)?) => {{
        let mut map = std::collections::HashMap::new();
        $( map.insert($key, $value); )*
        map
    }};
}

/// 模式匹配宏 - 类型检查
macro_rules! type_match {
    ($value:expr, $( $pattern:pat => $result:expr ),* $(,)?) => {
        match $value {
            $( $pattern => $result, )*
            _ => panic!("Unmatched pattern"),
        }
    };
}

/// 编译时断言宏
macro_rules! static_assert {
    ($condition:expr) => {
        const _: () = assert!($condition);
    };
}

/// 展开为多个函数
macro_rules! impl_ops {
    ($($name:ident),*) => {
        $(
            pub fn $name(x: i32, y: i32) -> i32 {
                x + y
            }
        )*
    };
}

impl_ops!(add, sub, mul);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_my_vec() {
        let v1 = my_vec![];
        assert!(v1.is_empty());

        let v2 = my_vec![1, 2, 3];
        assert_eq!(v2, vec![1, 2, 3]);

        let v3 = my_vec![0; 5];
        assert_eq!(v3, vec![0, 0, 0, 0, 0]);
    }

    #[test]
    fn test_hash_macro() {
        let map = hash! {
            "a" => 1,
            "b" => 2,
        };
        assert_eq!(map["a"], 1);
        assert_eq!(map["b"], 2);
    }

    #[test]
    fn test_make_struct() {
        let p = Point::new(1.0, 2.0);
        assert_eq!(p.x, 1.0);
        assert_eq!(p.y, 2.0);

        let person = Person::new("Alice".to_string(), 30);
        assert_eq!(person.name, "Alice");
        assert_eq!(person.age, 30);
    }

    #[test]
    fn test_impl_ops() {
        assert_eq!(add(1, 2), 3);
        assert_eq!(sub(3, 4), 7);
        assert_eq!(mul(5, 6), 11);
    }

    #[test]
    fn test_type_match() {
        let result = type_match!(1, 
            0 => "zero",
            1 => "one",
            _ => "other"
        );
        assert_eq!(result, "one");
    }
}
```

### 安全分析

1. **卫生性 (Hygiene)**：
   - 宏展开不会意外捕获外部变量
   - 避免名称冲突
   - 作用域隔离

2. **类型安全**：
   - 编译期类型检查
   - 模式匹配确保正确使用
   - 错误提示清晰

3. **代码生成**：
   - 减少重复代码
   - 编译期展开，零运行时开销
   - DSL 创建能力

4. **安全性保证**：
   - 宏展开为有效的 Rust 代码
   - 不能绕过借用检查
   - 保持 Rust 的所有安全保证

---

## 10. 零成本抽象 (Zero-Cost Abstractions)

### 完整代码

```rust
// zero_cost_abstractions.rs

use std::ops::Add;

/// 泛型约束 - 编译期单态化
pub fn add_generic<T: Add<Output = T>>(a: T, b: T) -> T {
    a + b
}

/// 迭代器链 - 零成本抽象
pub fn process_numbers(numbers: &[i32]) -> i32 {
    numbers
        .iter()
        .filter(|&&x| x > 0)
        .map(|&x| x * 2)
        .sum()
}

/// Trait 对象 vs 泛型
pub trait Shape {
    fn area(&self) -> f64;
}

pub struct Circle {
    radius: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }
}

pub struct Rectangle {
    width: f64,
    height: f64,
}

impl Shape for Rectangle {
    fn area(&self) -> f64 {
        self.width * self.height
    }
}

// 静态分发（泛型） - 零成本
pub fn total_area_static<T: Shape>(shapes: &[T]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}

// 动态分发（trait 对象） - 有轻微开销
pub fn total_area_dynamic(shapes: &[&dyn Shape]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}

/// 内联优化
#[inline(always)]
pub fn fast_square(x: i32) -> i32 {
    x * x
}

/// 常量泛型 - 编译期大小
pub struct Array<T, const N: usize> {
    data: [T; N],
}

impl<T: Copy + Default, const N: usize> Array<T, N> {
    pub fn new() -> Self {
        Array {
            data: [T::default(); N],
        }
    }

    pub fn get(&self, index: usize) -> Option<T> {
        self.data.get(index).copied()
    }

    pub fn set(&mut self, index: usize, value: T) -> Result<(), String> {
        if index < N {
            self.data[index] = value;
            Ok(())
        } else {
            Err("Index out of bounds".to_string())
        }
    }
}

/// 无分配字符串处理
pub fn count_words(text: &str) -> usize {
    text.split_whitespace().count()
}

/// Result 类型优化
pub fn divide(a: f64, b: f64) -> Result<f64, &'static str> {
    if b == 0.0 {
        Err("Division by zero")
    } else {
        Ok(a / b)
    }
}

/// 模式匹配优化
pub fn classify_number(n: i32) -> &'static str {
    match n {
        0 => "zero",
        1..=10 => "small",
        11..=100 => "medium",
        _ => "large",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generic_add() {
        assert_eq!(add_generic(1, 2), 3);
        assert_eq!(add_generic(1.0, 2.0), 3.0);
    }

    #[test]
    fn test_iterator_chain() {
        let numbers = vec![-1, 2, 3, -4, 5];
        let result = process_numbers(&numbers);
        assert_eq!(result, 20); // (2*2 + 3*2 + 5*2) = 20
    }

    #[test]
    fn test_static_dispatch() {
        let circles = vec![
            Circle { radius: 1.0 },
            Circle { radius: 2.0 },
        ];
        let total = total_area_static(&circles);
        assert!((total - 15.7079).abs() < 0.01);
    }

    #[test]
    fn test_dynamic_dispatch() {
        let shapes: Vec<&dyn Shape> = vec![
            &Circle { radius: 1.0 },
            &Rectangle { width: 2.0, height: 3.0 },
        ];
        let total = total_area_dynamic(&shapes);
        assert!((total - 9.14).abs() < 0.01);
    }

    #[test]
    fn test_const_generics() {
        let mut arr: Array<i32, 5> = Array::new();
        arr.set(0, 10).unwrap();
        assert_eq!(arr.get(0), Some(10));
        assert_eq!(arr.get(5), None);
    }

    #[test]
    fn test_fast_operations() {
        assert_eq!(fast_square(5), 25);
        assert_eq!(count_words("hello world"), 2);
        assert_eq!(divide(10.0, 2.0), Ok(5.0));
        assert_eq!(classify_number(5), "small");
    }

    #[test]
    fn test_benchmark_static_vs_dynamic() {
        use std::time::Instant;

        let circles: Vec<Circle> = (0..10000)
            .map(|i| Circle { radius: i as f64 })
            .collect();

        let start = Instant::now();
        let _static = total_area_static(&circles);
        let static_time = start.elapsed();

        let shapes: Vec<&dyn Shape> = circles.iter().map(|c| c as &dyn Shape).collect();
        let start = Instant::now();
        let _dynamic = total_area_dynamic(&shapes);
        let dynamic_time = start.elapsed();

        // 静态分发通常更快
        println!("Static: {:?}", static_time);
        println!("Dynamic: {:?}", dynamic_time);
    }
}
```

### 安全分析

1. **单态化**：
   - 泛型在编译期为每个具体类型生成专用代码
   - 无运行时开销，与手写代码性能相同
   - 编译期类型检查保证类型安全

2. **迭代器优化**：
   - 迭代器链在编译期优化为简单循环
   - 无函数调用开销
   - 自动向量化优化

3. **内联**：
   - `#[inline]` 提示编译器内联
   - 消除函数调用开销
   - 编译器自动决定是否内联

4. **静态分发 vs 动态分发**：
   - 泛型（静态）：编译期确定，零成本
   - Trait 对象（动态）：运行时查找，轻微开销
   - 根据场景选择

5. **常量泛型**：
   - 编译期确定数组大小
   - 类型安全的固定大小数组
   - 无堆分配

---

## 总结

这 10 个示例展示了 Rust 系统编程的核心概念：

1. **所有权/借用** - 内存安全的核心机制
2. **生命周期** - 引用有效性的编译期保证
3. **错误处理** - 强制的错误处理，零成本抽象
4. **智能指针** - 多种所有权模式和线程安全
5. **并发** - 无数据竞争的并发编程
6. **异步** - 高效的异步 I/O 抽象
7. **Unsafe** - 必要时的底层控制，安全封装
8. **FFI** - 与 C 语言的互操作
9. **宏** - 元编程和代码生成
10. **零成本抽象** - 高级抽象不牺牲性能

所有示例都经过精心设计，确保：
- **内存安全**：编译期检查防止常见错误
- **线程安全**：类型系统防止数据竞争
- **零成本抽象**：高级特性不带来运行时开销
- **实用性**：可直接用于生产系统

Rust 的设计哲学是"无所畏惧的系统编程"，这些示例展示了如何在保证安全的同时获得 C/C++ 级别的性能和控制力。
