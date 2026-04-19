# JavaScript Event Loop Deep Dive

## Problem

Implement a task scheduler that demonstrates JavaScript's event loop behavior, including microtasks, macrotasks, and proper execution order.

## Implementation

```javascript
// Event Loop Simulator - demonstrates task queuing behavior
class EventLoopSimulator {
  constructor() {
    this.macrotaskQueue = [];
    this.microtaskQueue = [];
    this.running = false;
  }

  // Schedule a macrotask (setTimeout, setInterval, I/O)
  queueMacrotask(task, name = 'anonymous') {
    this.macrotaskQueue.push({ task, name, type: 'macro' });
    return this;
  }

  // Schedule a microtask (Promise.then, queueMicrotask)
  queueMicrotask(task, name = 'anonymous') {
    this.microtaskQueue.push({ task, name, type: 'micro' });
    return this;
  }

  // Run the event loop until all queues are empty
  async run() {
    if (this.running) return;
    this.running = true;

    while (this.macrotaskQueue.length > 0 || this.microtaskQueue.length > 0) {
      // Process all microtasks before next macrotask
      while (this.microtaskQueue.length > 0) {
        const { task, name } = this.microtaskQueue.shift();
        console.log(`[Microtask] ${name}`);
        await task();
      }

      // Process one macrotask
      if (this.macrotaskQueue.length > 0) {
        const { task, name } = this.macrotaskQueue.shift();
        console.log(`[Macrotask] ${name}`);
        await task();
      }
    }

    this.running = false;
  }
}

// Practical: Task Priority Scheduler
class PriorityTaskScheduler {
  constructor() {
    this.queues = {
      high: [],
      normal: [],
      low: [],
    };
    this.processing = false;
  }

  schedule(task, priority = 'normal') {
    return new Promise((resolve, reject) => {
      this.queues[priority].push({
        task: async () => {
          try {
            const result = await task();
            resolve(result);
          } catch (err) {
            reject(err);
          }
        },
        priority,
      });
      this.processQueue();
    });
  }

  async processQueue() {
    if (this.processing) return;
    this.processing = true;

    while (this.hasTasks()) {
      // Process all high priority first
      if (this.queues.high.length > 0) {
        const { task } = this.queues.high.shift();
        await task();
        continue;
      }

      // Then normal priority
      if (this.queues.normal.length > 0) {
        const { task } = this.queues.normal.shift();
        await task();
        continue;
      }

      // Finally low priority
      if (this.queues.low.length > 0) {
        const { task } = this.queues.low.shift();
        await task();
      }
    }

    this.processing = false;
  }

  hasTasks() {
    return (
      this.queues.high.length > 0 ||
      this.queues.normal.length > 0 ||
      this.queues.low.length > 0
    );
  }
}

// Cooperative multitasking with yield points
class CooperativeScheduler {
  constructor(timeSlice = 10) {
    this.timeSlice = timeSlice;
    this.tasks = [];
    this.currentTask = null;
  }

  addTask(generator) {
    this.tasks.push(generator);
  }

  async runAll() {
    while (this.tasks.length > 0) {
      const task = this.tasks[0];
      const start = Date.now();

      let result = task.next();
      
      while (!result.done && Date.now() - start < this.timeSlice) {
        result = task.next();
      }

      if (result.done) {
        this.tasks.shift();
      }
      
      // Yield to event loop
      await new Promise(resolve => setTimeout(resolve, 0));
    }
  }
}

// Example: Chunked array processing
function* processLargeArray(array, chunkSize = 1000) {
  for (let i = 0; i < array.length; i += chunkSize) {
    const chunk = array.slice(i, i + chunkSize);
    // Process chunk
    chunk.forEach(item => {
      // Simulate work
      Math.sqrt(item);
    });
    yield; // Yield point
  }
}

// Debounce with leading/trailing options
function debounce(fn, delay, options = {}) {
  let timeoutId = null;
  let lastCallTime = 0;
  const { leading = false, trailing = true, maxWait } = options;

  return function (...args) {
    const now = Date.now();
    const shouldCallLeading = leading && now - lastCallTime > delay;
    
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    if (shouldCallLeading) {
      lastCallTime = now;
      fn.apply(this, args);
    }

    timeoutId = setTimeout(() => {
      timeoutId = null;
      if (trailing && (!leading || now - lastCallTime > delay)) {
        lastCallTime = Date.now();
        fn.apply(this, args);
      }
    }, delay);
  };
}

// Throttle with cancellation
function throttle(fn, interval) {
  let lastTime = 0;
  let timeoutId = null;
  let pendingArgs = null;

  const throttled = function (...args) {
    const now = Date.now();
    const timeSinceLast = now - lastTime;

    if (timeSinceLast >= interval) {
      lastTime = now;
      fn.apply(this, args);
    } else {
      pendingArgs = args;
      if (!timeoutId) {
        timeoutId = setTimeout(() => {
          timeoutId = null;
          lastTime = Date.now();
          if (pendingArgs) {
            fn.apply(this, pendingArgs);
            pendingArgs = null;
          }
        }, interval - timeSinceLast);
      }
    }
  };

  throttled.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    pendingArgs = null;
  };

  return throttled;
}

// Tests
const assert = require('assert');

async function testEventLoopSimulator() {
  const sim = new EventLoopSimulator();
  const order = [];

  sim
    .queueMacrotask(() => order.push(1), 'first macro')
    .queueMicrotask(() => order.push(2), 'first micro')
    .queueMicrotask(() => order.push(3), 'second micro')
    .queueMacrotask(() => order.push(4), 'second macro');

  await sim.run();
  
  // Microtasks run before next macrotask
  assert.deepStrictEqual(order, [1, 2, 3, 4]);
  console.log('✓ Event loop simulator test passed');
}

async function testPriorityScheduler() {
  const scheduler = new PriorityTaskScheduler();
  const order = [];

  scheduler.schedule(() => { order.push('low'); }, 'low');
  scheduler.schedule(() => { order.push('high'); }, 'high');
  scheduler.schedule(() => { order.push('normal'); }, 'normal');

  await new Promise(resolve => setTimeout(resolve, 50));
  
  assert.deepStrictEqual(order, ['high', 'normal', 'low']);
  console.log('✓ Priority scheduler test passed');
}

function testDebounce() {
  let callCount = 0;
  const debounced = debounce(() => callCount++, 10, { leading: true, trailing: false });

  debounced(); // Should call immediately (leading)
  debounced(); // Ignored
  debounced(); // Ignored

  assert.strictEqual(callCount, 1);
  console.log('✓ Debounce test passed');
}

function testThrottle() {
  let callCount = 0;
  const throttled = throttle(() => callCount++, 50);

  throttled(); // First call
  throttled(); // Throttled
  throttled(); // Throttled

  assert.strictEqual(callCount, 1);
  console.log('✓ Throttle test passed');
}

// Run tests
(async () => {
  await testEventLoopSimulator();
  await testPriorityScheduler();
  testDebounce();
  testThrottle();
  console.log('\nAll tests passed!');
})();
```

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| queueMacrotask | O(1) | O(1) |
| queueMicrotask | O(1) | O(1) |
| run (per task) | O(1) | O(1) |
| debounce | O(1) | O(1) |
| throttle | O(1) | O(1) |

## Key Concepts

1. **Microtasks** run immediately after the current task completes, before any macrotask
2. **Macrotasks** include setTimeout, setInterval, I/O operations
3. **Event Loop** processes all microtasks between each macrotask
4. **Cooperative Scheduling** yields control to prevent blocking
5. **Debounce/Throttle** control execution frequency for performance
