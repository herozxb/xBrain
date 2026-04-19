# JavaScript Closures Advanced Patterns

## Problem

Demonstrate advanced closure patterns including module patterns, memoization, private state, and function factories with practical examples.

## Implementation

```javascript
// Module Pattern with Private State
function createCounter() {
  let count = 0; // Private variable
  
  return {
    increment() {
      return ++count;
    },
    decrement() {
      return --count;
    },
    getCount() {
      return count;
    },
    reset() {
      count = 0;
    }
  };
}

// Advanced: Private class fields simulation
function createBankAccount(initialBalance) {
  let balance = initialBalance;
  let transactions = [];
  
  function recordTransaction(type, amount) {
    transactions.push({
      type,
      amount,
      balance: balance,
      timestamp: Date.now()
    });
  }
  
  return {
    deposit(amount) {
      if (amount <= 0) throw new Error('Invalid amount');
      balance += amount;
      recordTransaction('deposit', amount);
      return balance;
    },
    withdraw(amount) {
      if (amount <= 0) throw new Error('Invalid amount');
      if (amount > balance) throw new Error('Insufficient funds');
      balance -= amount;
      recordTransaction('withdrawal', amount);
      return balance;
    },
    getBalance() {
      return balance;
    },
    getTransactions() {
      return [...transactions]; // Return copy
    }
  };
}

// Memoization with Closure
function memoize(fn) {
  const cache = new Map();
  
  return function (...args) {
    const key = JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

// With TTL support
function memoizeWithTTL(fn, ttlMs = 60000) {
  const cache = new Map();
  
  return function (...args) {
    const key = JSON.stringify(args);
    const now = Date.now();
    
    if (cache.has(key)) {
      const { value, timestamp } = cache.get(key);
      if (now - timestamp < ttlMs) {
        return value;
      }
    }
    
    const result = fn.apply(this, args);
    cache.set(key, { value: result, timestamp: now });
    return result;
  };
}

// Function Factory Pattern
function createValidator(rules) {
  return function (value) {
    const errors = [];
    
    for (const [ruleName, ruleFn] of Object.entries(rules)) {
      const result = ruleFn(value);
      if (result !== true) {
        errors.push({ rule: ruleName, message: result });
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  };
}

// Curry function implementation
function curry(fn) {
  const arity = fn.length;
  
  return function curried(...args) {
    if (args.length >= arity) {
      return fn.apply(this, args);
    }
    
    return function (...moreArgs) {
      return curried.apply(this, [...args, ...moreArgs]);
    };
  };
}

// Example curried functions
const add = curry((a, b, c) => a + b + c);
const multiply = curry((a, b) => a * b);

// Partial application
function partial(fn, ...presetArgs) {
  return function (...laterArgs) {
    return fn(...presetArgs, ...laterArgs);
  };
}

// Once pattern
function once(fn) {
  let called = false;
  let result;
  
  return function (...args) {
    if (called) {
      return result;
    }
    
    called = true;
    result = fn.apply(this, args);
    return result;
  };
}

// Singleton pattern with closure
function createSingleton(factory) {
  let instance = null;
  
  return function () {
    if (instance === null) {
      instance = factory();
    }
    return instance;
  };
}

// Rate limiter with closure
function createRateLimiter(maxCalls, windowMs) {
  let calls = [];
  
  return function () {
    const now = Date.now();
    
    // Remove old calls outside window
    calls = calls.filter(time => now - time < windowMs);
    
    if (calls.length >= maxCalls) {
      return false; // Rate limited
    }
    
    calls.push(now);
    return true;
  };
}

// Event emitter with closure
function createEventEmitter() {
  const listeners = new Map();
  
  return {
    on(event, callback) {
      if (!listeners.has(event)) {
        listeners.set(event, new Set());
      }
      listeners.get(event).add(callback);
      
      // Return unsubscribe function
      return () => {
        listeners.get(event).delete(callback);
      };
    },
    
    emit(event, data) {
      const callbacks = listeners.get(event);
      if (callbacks) {
        callbacks.forEach(cb => cb(data));
      }
    },
    
    off(event, callback) {
      const callbacks = listeners.get(event);
      if (callbacks) {
        callbacks.delete(callback);
      }
    }
  };
}

// Composition with closures
const compose = (...fns) => x => fns.reduceRight((acc, fn) => fn(acc), x);
const pipe = (...fns) => x => fns.reduce((acc, fn) => fn(acc), x);

// Tests
const assert = require('assert');

function testCounter() {
  const counter = createCounter();
  assert.strictEqual(counter.increment(), 1);
  assert.strictEqual(counter.increment(), 2);
  assert.strictEqual(counter.decrement(), 1);
  assert.strictEqual(counter.getCount(), 1);
  counter.reset();
  assert.strictEqual(counter.getCount(), 0);
  console.log('✓ Counter test passed');
}

function testBankAccount() {
  const account = createBankAccount(100);
  assert.strictEqual(account.getBalance(), 100);
  account.deposit(50);
  assert.strictEqual(account.getBalance(), 150);
  account.withdraw(30);
  assert.strictEqual(account.getBalance(), 120);
  assert.strictEqual(account.getTransactions().length, 2);
  console.log('✓ Bank account test passed');
}

function testMemoize() {
  let callCount = 0;
  const expensiveFn = (n) => {
    callCount++;
    return n * n;
  };
  
  const memoized = memoize(expensiveFn);
  
  assert.strictEqual(memoized(5), 25);
  assert.strictEqual(callCount, 1);
  
  memoized(5); // Should use cache
  assert.strictEqual(callCount, 1);
  
  memoized(6);
  assert.strictEqual(callCount, 2);
  
  console.log('✓ Memoize test passed');
}

function testCurry() {
  const addThree = add(1)(2)(3);
  assert.strictEqual(addThree, 6);
  
  const addOneTwo = add(1, 2);
  assert.strictEqual(addOneTwo(3), 6);
  
  console.log('✓ Curry test passed');
}

function testRateLimiter() {
  const limiter = createRateLimiter(3, 1000);
  
  assert.strictEqual(limiter(), true);
  assert.strictEqual(limiter(), true);
  assert.strictEqual(limiter(), true);
  assert.strictEqual(limiter(), false); // Rate limited
  console.log('✓ Rate limiter test passed');
}

function testEventEmitter() {
  const emitter = createEventEmitter();
  const events = [];
  
  emitter.on('test', data => events.push(data));
  emitter.emit('test', 'hello');
  emitter.emit('test', 'world');
  
  assert.deepStrictEqual(events, ['hello', 'world']);
  console.log('✓ Event emitter test passed');
}

// Run all tests
testCounter();
testBankAccount();
testMemoize();
testCurry();
testRateLimiter();
testEventEmitter();
console.log('\nAll tests passed!');
```

## Complexity

| Pattern | Time | Space |
|---------|------|-------|
| createCounter | O(1) | O(1) |
| memoize lookup | O(k) where k=args | O(n) for cache |
| curry | O(1) | O(1) |
| rate limiter check | O(w) window size | O(c) calls |
| event emitter emit | O(n) listeners | O(n) listeners |

## Key Patterns

1. **Encapsulation**: Closures hide private state from external access
2. **Memoization**: Cache results to avoid recomputation
3. **Function Factories**: Generate specialized functions dynamically
4. **Currying**: Transform multi-arg functions into chainable single-arg functions
5. **Singletons**: Ensure only one instance exists via closure scope
