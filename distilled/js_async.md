# JavaScript 异步编程精要

## 1. Promise 实现

### 核心概念
Promise 是异步编程的基础，表示一个未来才会知道结果的操作。有三种状态：pending、fulfilled、rejected。

### 手写 Promise 实现

```javascript
class MyPromise {
  constructor(executor) {
    this.state = 'pending';
    this.value = undefined;
    this.reason = undefined;
    this.onFulfilledCallbacks = [];
    this.onRejectedCallbacks = [];

    const resolve = (value) => {
      if (this.state === 'pending') {
        this.state = 'fulfilled';
        this.value = value;
        this.onFulfilledCallbacks.forEach(fn => fn());
      }
    };

    const reject = (reason) => {
      if (this.state === 'pending') {
        this.state = 'rejected';
        this.reason = reason;
        this.onRejectedCallbacks.forEach(fn => fn());
      }
    };

    try {
      executor(resolve, reject);
    } catch (error) {
      reject(error);
    }
  }

  then(onFulfilled, onRejected) {
    onFulfilled = typeof onFulfilled === 'function' ? onFulfilled : v => v;
    onRejected = typeof onRejected === 'function' ? onRejected : e => { throw e; };

    const promise2 = new MyPromise((resolve, reject) => {
      const fulfillTask = () => {
        queueMicrotask(() => {
          try {
            const x = onFulfilled(this.value);
            this.resolvePromise(promise2, x, resolve, reject);
          } catch (error) {
            reject(error);
          }
        });
      };

      const rejectTask = () => {
        queueMicrotask(() => {
          try {
            const x = onRejected(this.reason);
            this.resolvePromise(promise2, x, resolve, reject);
          } catch (error) {
            reject(error);
          }
        });
      };

      if (this.state === 'fulfilled') {
        fulfillTask();
      } else if (this.state === 'rejected') {
        rejectTask();
      } else {
        this.onFulfilledCallbacks.push(fulfillTask);
        this.onRejectedCallbacks.push(rejectTask);
      }
    });

    return promise2;
  }

  resolvePromise(promise2, x, resolve, reject) {
    if (promise2 === x) {
      return reject(new TypeError('Chaining cycle detected'));
    }
    if (x instanceof MyPromise) {
      x.then(resolve, reject);
    } else if (typeof x === 'object' && x !== null && typeof x.then === 'function') {
      let called = false;
      try {
        x.then(
          y => {
            if (called) return;
            called = true;
            this.resolvePromise(promise2, y, resolve, reject);
          },
          r => {
            if (called) return;
            called = true;
            reject(r);
          }
        );
      } catch (error) {
        if (called) return;
        reject(error);
      }
    } else {
      resolve(x);
    }
  }

  catch(onRejected) {
    return this.then(null, onRejected);
  }

  finally(onFinally) {
    return this.then(
      value => MyPromise.resolve(onFinally()).then(() => value),
      reason => MyPromise.resolve(onFinally()).then(() => { throw reason; })
    );
  }

  static resolve(value) {
    return new MyPromise(resolve => resolve(value));
  }

  static reject(reason) {
    return new MyPromise((_, reject) => reject(reason));
  }

  static all(promises) {
    return new MyPromise((resolve, reject) => {
      const result = [];
      let count = 0;
      promises.forEach((p, i) => {
        MyPromise.resolve(p).then(value => {
          result[i] = value;
          if (++count === promises.length) resolve(result);
        }, reject);
      });
    });
  }

  static race(promises) {
    return new MyPromise((resolve, reject) => {
      promises.forEach(p => MyPromise.resolve(p).then(resolve, reject));
    });
  }

  static allSettled(promises) {
    return new MyPromise(resolve => {
      const result = [];
      let count = 0;
      promises.forEach((p, i) => {
        MyPromise.resolve(p).then(
          value => {
            result[i] = { status: 'fulfilled', value };
            if (++count === promises.length) resolve(result);
          },
          reason => {
            result[i] = { status: 'rejected', reason };
            if (++count === promises.length) resolve(result);
          }
        );
      });
    });
  }
}
```

### 使用示例

```javascript
// 基本使用
const promise = new MyPromise((resolve, reject) => {
  setTimeout(() => resolve('成功!'), 1000);
});

promise
  .then(result => {
    console.log(result); // 成功!
    return '链式调用';
  })
  .then(result => console.log(result)) // 链式调用
  .catch(error => console.error(error));

// Promise.all 示例
const p1 = MyPromise.resolve(1);
const p2 = new MyPromise(r => setTimeout(() => r(2), 500));
const p3 = MyPromise.resolve(3);

MyPromise.all([p1, p2, p3]).then(results => {
  console.log(results); // [1, 2, 3]
});
```

---

## 2. async/await

### 核心概念
async/await 是 Promise 的语法糖，让异步代码看起来像同步代码，更易读易写。

### 实现原理

```javascript
// async 函数返回 Promise
async function asyncFunc() {
  return 'value';
}
// 等价于
function asyncFunc() {
  return Promise.resolve('value');
}

// await 等待 Promise 解决
async function example() {
  const result = await asyncFunc();
  console.log(result);
}

// 上面代码等价于下面的 generator + promise 实现
function generatorToAsync(generatorFunc) {
  return function() {
    const gen = generatorFunc.apply(this, arguments);
    
    return new Promise((resolve, reject) => {
      function step(key, arg) {
        let result;
        try {
          result = gen[key](arg);
        } catch (error) {
          return reject(error);
        }
        
        const { value, done } = result;
        if (done) {
          return resolve(value);
        } else {
          return Promise.resolve(value).then(
            val => step('next', val),
            err => step('throw', err)
          );
        }
      }
      
      step('next');
    });
  };
}
```

### 实用示例

```javascript
// 模拟 API 请求
const fetchUser = (id) => new Promise(resolve => 
  setTimeout(() => resolve({ id, name: `User ${id}` }), 500)
);

const fetchPosts = (userId) => new Promise(resolve =>
  setTimeout(() => resolve([`Post1 by ${userId}`, `Post2 by ${userId}`]), 300)
);

// 串行请求
async function getUserPosts(userId) {
  try {
    console.log('获取用户信息...');
    const user = await fetchUser(userId);
    
    console.log('获取用户文章...');
    const posts = await fetchPosts(user.id);
    
    return { user, posts };
  } catch (error) {
    console.error('出错了:', error);
    throw error;
  } finally {
    console.log('请求完成');
  }
}

// 并行请求
async function getParallelData() {
  const [users, posts] = await Promise.all([
    fetchUser(1),
    fetchPosts(1)
  ]);
  return { users, posts };
}

// 错误处理模式
async function robustFetch() {
  // 模式1: try/catch
  try {
    const data = await fetchUser(1);
  } catch (e) {
    console.error(e);
  }
  
  // 模式2: catch 方法
  const data = await fetchUser(1).catch(e => {
    console.error(e);
    return null; // 默认值
  });
  
  // 模式3: Result 数组
  const [result, error] = await fetchUser(1)
    .then(r => [r, null])
    .catch(e => [null, e]);
}

// 使用示例
getUserPosts(1).then(console.log);
// 输出:
// 获取用户信息...
// 获取用户文章...
// 请求完成
// { user: { id: 1, name: 'User 1' }, posts: ['Post1 by 1', 'Post2 by 1'] }
```

---

## 3. 事件循环

### 核心概念
JavaScript 是单线程的，通过事件循环（Event Loop）实现非阻塞 I/O。

```
┌───────────────────────────┐
│        Call Stack         │
│   (调用栈 - LIFO)          │
└─────────────┬─────────────┘
              │
┌─────────────▼─────────────┐
│       Web APIs            │
│   (定时器、DOM、HTTP)       │
└─────────────┬─────────────┘
              │
┌─────────────▼─────────────┐
│      Callback Queue       │
│   (回调队列 - FIFO)         │
│  ┌─────────────────────┐  │
│  │   Macro Task Queue  │  │
│  │   setTimeout, I/O   │  │
│  └─────────────────────┘  │
│  ┌─────────────────────┐  │
│  │   Micro Task Queue  │  │
│  │   Promise, Mutation │  │
│  └─────────────────────┘  │
└───────────────────────────┘
```

### 执行流程

```javascript
// 事件循环流程示例
console.log('1. 脚本开始');

setTimeout(() => {
  console.log('2. setTimeout 宏任务');
}, 0);

Promise.resolve()
  .then(() => {
    console.log('3. Promise 微任务 1');
  })
  .then(() => {
    console.log('4. Promise 微任务 2');
  });

console.log('5. 脚本结束');

// 输出顺序:
// 1. 脚本开始
// 5. 脚本结束
// 3. Promise 微任务 1
// 4. Promise 微任务 2
// 2. setTimeout 宏任务
```

### 复杂示例

```javascript
// 事件循环执行顺序详解
async function async1() {
  console.log('async1 start');
  await async2();
  console.log('async1 end');
}

async function async2() {
  console.log('async2');
}

console.log('script start');

setTimeout(function() {
  console.log('setTimeout');
}, 0);

async1();

new Promise(function(resolve) {
  console.log('promise1');
  resolve();
}).then(function() {
  console.log('promise2');
});

console.log('script end');

/*
执行顺序分析:
1. script start          - 同步代码
2. async1 start          - async1() 同步执行
3. async2                - async2() 同步执行
4. promise1              - Promise 构造函数同步执行
5. script end            - 同步代码结束
--- 调用栈清空，执行微任务 ---
6. async1 end            - await 后的代码作为微任务
7. promise2              - Promise.then 微任务
--- 微任务清空，执行下一个宏任务 ---
8. setTimeout            - 宏任务队列
*/
```

### 事件循环实现模拟

```javascript
class EventLoop {
  constructor() {
    this.macroTaskQueue = [];
    this.microTaskQueue = [];
    this.running = false;
  }

  // 添加宏任务
  addMacroTask(callback) {
    this.macroTaskQueue.push(callback);
    if (!this.running) this.run();
  }

  // 添加微任务
  addMicroTask(callback) {
    this.microTaskQueue.push(callback);
  }

  // 运行事件循环
  run() {
    this.running = true;
    
    while (this.macroTaskQueue.length > 0 || this.microTaskQueue.length > 0) {
      // 1. 执行所有微任务
      while (this.microTaskQueue.length > 0) {
        const task = this.microTaskQueue.shift();
        task();
      }
      
      // 2. 取出一个宏任务执行
      if (this.macroTaskQueue.length > 0) {
        const task = this.macroTaskQueue.shift();
        task();
      }
      
      // 3. 渲染（如果有需要）
      // this.render();
    }
    
    this.running = false;
  }
}

// 使用示例
const loop = new EventLoop();

loop.addMacroTask(() => {
  console.log('Macro 1');
  loop.addMicroTask(() => console.log('  Micro from Macro 1'));
});

loop.addMacroTask(() => {
  console.log('Macro 2');
});

// 输出: Macro 1, Micro from Macro 1, Macro 2
```

---

## 4. 微任务/宏任务

### 区别对比

| 类型 | 宏任务 (Macro Task) | 微任务 (Micro Task) |
|------|---------------------|---------------------|
| 来源 | setTimeout, setInterval, setImmediate, I/O, UI 渲染 | Promise.then/catch/finally, MutationObserver, queueMicrotask, process.nextTick (Node) |
| 执行时机 | 每次事件循环取一个 | 每次事件循环清空队列 |
| 优先级 | 低 | 高 |

### 代码示例

```javascript
// 微任务优先级高于宏任务
console.log('=== 微任务 vs 宏任务 ===');

setTimeout(() => console.log('1. 宏任务 setTimeout'), 0);

Promise.resolve().then(() => console.log('2. 微任务 Promise'));

queueMicrotask(() => console.log('3. 微任务 queueMicrotask'));

console.log('4. 同步代码');

// 输出: 4 -> 2 -> 3 -> 1

console.log('\n=== 嵌套示例 ===');

setTimeout(() => {
  console.log('A. 外层 setTimeout');
  Promise.resolve().then(() => {
    console.log('B. 内层 Promise');
  });
}, 0);

Promise.resolve().then(() => {
  console.log('C. 外层 Promise');
  setTimeout(() => {
    console.log('D. 内层 setTimeout');
  }, 0);
});

// 输出: C -> A -> B -> D
```

### MutationObserver 示例

```javascript
// MutationObserver 是微任务
const observer = new MutationObserver(() => {
  console.log('MutationObserver 微任务');
});

const target = document.getElementById('target');
if (target) {
  observer.observe(target, { childList: true });
  target.textContent = 'changed';
}

// 执行顺序测试
setTimeout(() => console.log('setTimeout'), 0);
Promise.resolve().then(() => console.log('Promise'));
queueMicrotask(() => console.log('queueMicrotask'));
// 如果 DOM 变化触发: queueMicrotask -> Promise -> MutationObserver -> setTimeout
```

### process.nextTick (Node.js)

```javascript
// Node.js 中 process.nextTick 优先级最高
// 执行顺序: nextTick -> Promise -> setTimeout

setImmediate(() => console.log('1. setImmediate'));
setTimeout(() => console.log('2. setTimeout'), 0);
Promise.resolve().then(() => console.log('3. Promise'));
process.nextTick(() => console.log('4. nextTick'));

// 输出: 4 -> 3 -> 2 -> 1 (Node.js 环境)
```

---

## 5. 并发控制

### 为什么需要并发控制？

```javascript
// 问题: 无限制的并发请求
const urls = Array.from({ length: 100 }, (_, i) => `https://api.example.com/${i}`);

// ❌ 错误做法 - 同时发起 100 个请求
Promise.all(urls.map(url => fetch(url)))
  .then(results => console.log(results))
  .catch(err => console.error(err)); // 可能导致服务器拒绝或内存溢出
```

### 实现方案

#### 方案1: 基础并发控制

```javascript
class ConcurrencyPool {
  constructor(maxConcurrency) {
    this.maxConcurrency = maxConcurrency;
    this.running = 0;
    this.queue = [];
  }

  async run(task) {
    if (this.running >= this.maxConcurrency) {
      await new Promise(resolve => this.queue.push(resolve));
    }
    
    this.running++;
    try {
      return await task();
    } finally {
      this.running--;
      const next = this.queue.shift();
      if (next) next();
    }
  }
}

// 使用示例
const pool = new ConcurrencyPool(3);

const tasks = urls.map(url => 
  pool.run(() => fetch(url).then(r => r.json()))
);

const results = await Promise.all(tasks);
```

#### 方案2: Promise.all 并发控制

```javascript
async function limitConcurrency(tasks, limit) {
  const results = [];
  const executing = [];
  
  for (const [index, task] of tasks.entries()) {
    const promise = Promise.resolve().then(() => task());
    results[index] = promise;
    
    if (limit <= tasks.length) {
      const exec = promise.then(() => {
        executing.splice(executing.indexOf(exec), 1);
      });
      executing.push(exec);
      
      if (executing.length >= limit) {
        await Promise.race(executing);
      }
    }
  }
  
  return Promise.all(results);
}

// 使用示例
const tasks = urls.map(url => () => fetch(url));
const results = await limitConcurrency(tasks, 5); // 最多 5 个并发
```

#### 方案3: 完整的并发控制器

```javascript
class TaskScheduler {
  constructor(concurrency = 5) {
    this.concurrency = concurrency;
    this.running = 0;
    this.queue = [];
    this.results = [];
    this.errors = [];
  }

  // 添加任务
  add(task, ...args) {
    return new Promise((resolve, reject) => {
      this.queue.push({
        task,
        args,
        resolve,
        reject
      });
      this.schedule();
    });
  }

  // 调度执行
  schedule() {
    while (this.running < this.concurrency && this.queue.length > 0) {
      const { task, args, resolve, reject } = this.queue.shift();
      this.running++;
      
      Promise.resolve()
        .then(() => task(...args))
        .then(result => {
          resolve(result);
          this.results.push(result);
        })
        .catch(error => {
          reject(error);
          this.errors.push(error);
        })
        .finally(() => {
          this.running--;
          this.schedule();
        });
    }
  }

  // 等待所有任务完成
  async all() {
    while (this.running > 0 || this.queue.length > 0) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return this.results;
  }
}

// 使用示例
const scheduler = new TaskScheduler(3);

// 添加任务
const taskPromises = urls.map(url => 
  scheduler.add(async (url) => {
    const res = await fetch(url);
    return res.json();
  }, url)
);

// 获取所有结果
const allResults = await Promise.all(taskPromises);
console.log('完成:', allResults.length, '错误:', scheduler.errors.length);
```

#### 方案4: async-pool 库实现

```javascript
// 简化版 async-pool
async function asyncPool(poolLimit, array, iteratorFn) {
  const ret = [];
  const executing = new Set();
  
  for (const item of array) {
    const promise = iteratorFn(item);
    ret.push(promise);
    executing.add(promise);
    
    const clean = () => executing.delete(promise);
    promise.then(clean, clean);
    
    if (executing.size >= poolLimit) {
      await Promise.race(executing);
    }
  }
  
  return Promise.all(ret);
}

// 实际应用示例
async function fetchWithConcurrency() {
  const urls = [
    'https://jsonplaceholder.typicode.com/todos/1',
    'https://jsonplaceholder.typicode.com/todos/2',
    'https://jsonplaceholder.typicode.com/todos/3',
    'https://jsonplaceholder.typicode.com/todos/4',
    'https://jsonplaceholder.typicode.com/todos/5',
  ];

  const results = await asyncPool(2, urls, async (url) => {
    console.log(`开始请求: ${url}`);
    const res = await fetch(url);
    const data = await res.json();
    console.log(`完成请求: ${url}`);
    return data;
  });

  console.log('所有请求完成:', results);
}

// 执行
fetchWithConcurrency();
```

### 高级场景: 失败重试

```javascript
class RetryableTaskScheduler {
  constructor(options = {}) {
    this.concurrency = options.concurrency || 5;
    this.maxRetries = options.maxRetries || 3;
    this.retryDelay = options.retryDelay || 1000;
    this.running = 0;
    this.queue = [];
  }

  async add(task, ...args) {
    return new Promise((resolve, reject) => {
      const taskWrapper = {
        task,
        args,
        resolve,
        reject,
        retries: 0
      };
      this.queue.push(taskWrapper);
      this.schedule();
    });
  }

  async executeTask(taskWrapper) {
    const { task, args, resolve, reject, retries } = taskWrapper;
    
    try {
      const result = await task(...args);
      resolve(result);
    } catch (error) {
      if (retries < this.maxRetries) {
        console.log(`任务失败，第 ${retries + 1} 次重试...`);
        await new Promise(r => setTimeout(r, this.retryDelay * (retries + 1)));
        taskWrapper.retries++;
        this.queue.unshift(taskWrapper);
      } else {
        reject(new Error(`任务失败，已重试 ${this.maxRetries} 次: ${error.message}`));
      }
    } finally {
      this.running--;
      this.schedule();
    }
  }

  schedule() {
    while (this.running < this.concurrency && this.queue.length > 0) {
      this.running++;
      const taskWrapper = this.queue.shift();
      this.executeTask(taskWrapper);
    }
  }
}

// 使用示例
const retryScheduler = new RetryableTaskScheduler({
  concurrency: 3,
  maxRetries: 3,
  retryDelay: 500
});

// 模拟可能失败的请求
const unstableFetch = (url) => {
  return new Promise((resolve, reject) => {
    if (Math.random() > 0.5) {
      resolve({ url, success: true });
    } else {
      reject(new Error('Network error'));
    }
  });
};

const promises = urls.map(url => 
  retryScheduler.add(unstableFetch, url)
);

Promise.allSettled(promises).then(results => {
  console.log('任务执行结果:', results);
});
```

---

## 总结

| 概念 | 核心要点 |
|------|----------|
| **Promise** | 三种状态、链式调用、静态方法 (all/race/allSettled) |
| **async/await** | Promise 语法糖、try/catch 错误处理、串行/并行控制 |
| **事件循环** | 单线程、调用栈、回调队列、循环执行 |
| **微任务/宏任务** | 微任务优先级高、清空微任务再取宏任务 |
| **并发控制** | 限制并发数、队列管理、错误处理、重试机制 |
