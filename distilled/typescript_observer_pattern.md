# TypeScript Pattern: Observer Pattern with Type Safety

## Problem Statement
Implement a type-safe Observer pattern that allows objects to subscribe to and receive notifications about state changes, with full TypeScript type inference and compile-time safety.

## Solution Code

```typescript
// Core types for the Observer pattern
type EventHandler<T> = (data: T) => void;
type Unsubscribe = () => void;

// Event emitter with full type safety
interface EventMap {
  [key: string]: unknown;
}

class TypedEventEmitter<Events extends EventMap> {
  private listeners: Map<keyof Events, Set<EventHandler<any>>> = new Map();

  /**
   * Subscribe to an event
   * @returns Unsubscribe function
   */
  on<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>): Unsubscribe {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    
    const handlers = this.listeners.get(event)!;
    handlers.add(handler);

    // Return unsubscribe function
    return () => {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.listeners.delete(event);
      }
    };
  }

  /**
   * Subscribe to an event (fires once then unsubscribes)
   */
  once<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>): Unsubscribe {
    const wrapper: EventHandler<Events[K]> = (data) => {
      unsubscribe();
      handler(data);
    };
    
    const unsubscribe = this.on(event, wrapper);
    return unsubscribe;
  }

  /**
   * Emit an event to all subscribers
   */
  emit<K extends keyof Events>(event: K, data: Events[K]): void {
    const handlers = this.listeners.get(event);
    if (!handlers) return;

    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in event handler for "${String(event)}":`, error);
      }
    });
  }

  /**
   * Remove all listeners for an event (or all events)
   */
  off<K extends keyof Events>(event?: K): void {
    if (event) {
      this.listeners.delete(event);
    } else {
      this.listeners.clear();
    }
  }

  /**
   * Get listener count for an event
   */
  listenerCount<K extends keyof Events>(event: K): number {
    return this.listeners.get(event)?.size ?? 0;
  }
}

// ============================================
// Example: Stock Price Monitor
// ============================================

interface StockEvents {
  priceChange: { symbol: string; price: number; change: number };
  alert: { symbol: string; message: string; level: 'warning' | 'critical' };
  marketOpen: { time: Date };
  marketClose: { time: Date };
}

interface Stock {
  symbol: string;
  name: string;
  price: number;
}

class StockMonitor extends TypedEventEmitter<StockEvents> {
  private stocks: Map<string, Stock> = new Map();
  private alertThresholds: Map<string, { high: number; low: number }> = new Map();

  addStock(stock: Stock): void {
    this.stocks.set(stock.symbol, stock);
  }

  setAlertThreshold(symbol: string, high: number, low: number): void {
    this.alertThresholds.set(symbol, { high, low });
  }

  updatePrice(symbol: string, newPrice: number): void {
    const stock = this.stocks.get(symbol);
    if (!stock) {
      throw new Error(`Stock ${symbol} not found`);
    }

    const change = newPrice - stock.price;
    stock.price = newPrice;

    // Emit price change event
    this.emit('priceChange', { symbol, price: newPrice, change });

    // Check alert thresholds
    const thresholds = this.alertThresholds.get(symbol);
    if (thresholds) {
      if (newPrice >= thresholds.high) {
        this.emit('alert', {
          symbol,
          message: `Price ${newPrice} reached high threshold ${thresholds.high}`,
          level: 'warning'
        });
      } else if (newPrice <= thresholds.low) {
        this.emit('alert', {
          symbol,
          message: `Price ${newPrice} fell below low threshold ${thresholds.low}`,
          level: 'critical'
        });
      }
    }
  }

  openMarket(): void {
    this.emit('marketOpen', { time: new Date() });
  }

  closeMarket(): void {
    this.emit('marketClose', { time: new Date() });
  }
}

// ============================================
// Example: Reactive State Store
// ============================================

interface StateChangeEvents<T> {
  change: { oldValue: T; newValue: T };
  reset: { previousValue: T };
}

class ReactiveStore<T extends object> extends TypedEventEmitter<StateChangeEvents<T>> {
  private state: T;
  private initialState: T;

  constructor(initialState: T) {
    super();
    this.state = { ...initialState };
    this.initialState = { ...initialState };
  }

  getState(): Readonly<T> {
    return this.state;
  }

  setState(updater: (state: T) => T): void {
    const oldValue = { ...this.state };
    this.state = updater({ ...this.state });
    this.emit('change', { oldValue, newValue: { ...this.state } });
  }

  reset(): void {
    const previousValue = { ...this.state };
    this.state = { ...this.initialState };
    this.emit('reset', { previousValue });
  }
}

// ============================================
// Usage Example
// ============================================

const monitor = new StockMonitor();

// Subscribe to price changes
const unsubPrice = monitor.on('priceChange', ({ symbol, price, change }) => {
  console.log(`${symbol}: $${price.toFixed(2)} (${change >= 0 ? '+' : ''}${change.toFixed(2)})`);
});

// Subscribe to alerts with async handling
monitor.on('alert', async ({ symbol, message, level }) => {
  const emoji = level === 'critical' ? '🚨' : '⚠️';
  console.log(`${emoji} ${symbol}: ${message}`);
});

// One-time subscription for market open
monitor.once('marketOpen', ({ time }) => {
  console.log(`Market opened at ${time.toLocaleTimeString()}`);
});

// Setup stocks and thresholds
monitor.addStock({ symbol: 'AAPL', name: 'Apple Inc.', price: 175.00 });
monitor.setAlertThreshold('AAPL', 180, 170);

// Simulate market
monitor.openMarket();
monitor.updatePrice('AAPL', 176.50);
monitor.updatePrice('AAPL', 180.25); // Should trigger high alert
monitor.closeMarket();

// Cleanup
unsubPrice();
```

## Unit Tests

```typescript
import { TypedEventEmitter, ReactiveStore, StockMonitor } from './observer_pattern';

describe('TypedEventEmitter', () => {
  interface TestEvents {
    foo: { value: number };
    bar: { message: string };
  }

  let emitter: TypedEventEmitter<TestEvents>;

  beforeEach(() => {
    emitter = new TypedEventEmitter<TestEvents>();
  });

  describe('on()', () => {
    it('should call handler when event is emitted', () => {
      const handler = jest.fn();
      emitter.on('foo', handler);
      
      emitter.emit('foo', { value: 42 });
      
      expect(handler).toHaveBeenCalledWith({ value: 42 });
    });

    it('should support multiple handlers for same event', () => {
      const handler1 = jest.fn();
      const handler2 = jest.fn();
      
      emitter.on('foo', handler1);
      emitter.on('foo', handler2);
      emitter.emit('foo', { value: 10 });
      
      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
    });

    it('should return unsubscribe function', () => {
      const handler = jest.fn();
      const unsub = emitter.on('foo', handler);
      
      unsub();
      emitter.emit('foo', { value: 1 });
      
      expect(handler).not.toHaveBeenCalled();
    });

    it('should not affect other handlers when one unsubscribes', () => {
      const handler1 = jest.fn();
      const handler2 = jest.fn();
      
      const unsub1 = emitter.on('foo', handler1);
      emitter.on('foo', handler2);
      
      unsub1();
      emitter.emit('foo', { value: 5 });
      
      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
    });
  });

  describe('once()', () => {
    it('should only fire once', () => {
      const handler = jest.fn();
      emitter.once('foo', handler);
      
      emitter.emit('foo', { value: 1 });
      emitter.emit('foo', { value: 2 });
      
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith({ value: 1 });
    });
  });

  describe('emit()', () => {
    it('should not throw when emitting event with no listeners', () => {
      expect(() => emitter.emit('foo', { value: 1 })).not.toThrow();
    });

    it('should continue emitting even if handler throws', () => {
      const errorHandler = jest.fn(() => { throw new Error('test'); });
      const normalHandler = jest.fn();
      
      emitter.on('foo', errorHandler);
      emitter.on('foo', normalHandler);
      
      emitter.emit('foo', { value: 1 });
      
      expect(normalHandler).toHaveBeenCalled();
    });
  });

  describe('off()', () => {
    it('should remove all listeners for specific event', () => {
      const handler1 = jest.fn();
      const handler2 = jest.fn();
      
      emitter.on('foo', handler1);
      emitter.on('foo', handler2);
      emitter.off('foo');
      emitter.emit('foo', { value: 1 });
      
      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).not.toHaveBeenCalled();
    });

    it('should clear all listeners when called without event', () => {
      const fooHandler = jest.fn();
      const barHandler = jest.fn();
      
      emitter.on('foo', fooHandler);
      emitter.on('bar', barHandler);
      emitter.off();
      
      emitter.emit('foo', { value: 1 });
      emitter.emit('bar', { message: 'test' });
      
      expect(fooHandler).not.toHaveBeenCalled();
      expect(barHandler).not.toHaveBeenCalled();
    });
  });

  describe('listenerCount()', () => {
    it('should return correct count', () => {
      expect(emitter.listenerCount('foo')).toBe(0);
      
      emitter.on('foo', () => {});
      emitter.on('foo', () => {});
      
      expect(emitter.listenerCount('foo')).toBe(2);
    });
  });
});

describe('ReactiveStore', () => {
  interface TestState {
    count: number;
    name: string;
  }

  let store: ReactiveStore<TestState>;

  beforeEach(() => {
    store = new ReactiveStore<TestState>({ count: 0, name: 'test' });
  });

  it('should return current state', () => {
    expect(store.getState()).toEqual({ count: 0, name: 'test' });
  });

  it('should update state and emit change event', () => {
    const handler = jest.fn();
    store.on('change', handler);
    
    store.setState(state => ({ ...state, count: 5 }));
    
    expect(store.getState().count).toBe(5);
    expect(handler).toHaveBeenCalledWith({
      oldValue: { count: 0, name: 'test' },
      newValue: { count: 5, name: 'test' }
    });
  });

  it('should reset to initial state and emit reset event', () => {
    const handler = jest.fn();
    store.on('reset', handler);
    
    store.setState(s => ({ ...s, count: 100 }));
    store.reset();
    
    expect(store.getState().count).toBe(0);
    expect(handler).toHaveBeenCalled();
  });
});

describe('StockMonitor', () => {
  let monitor: StockMonitor;

  beforeEach(() => {
    monitor = new StockMonitor();
    monitor.addStock({ symbol: 'TEST', name: 'Test Stock', price: 100 });
  });

  it('should emit priceChange event', () => {
    const handler = jest.fn();
    monitor.on('priceChange', handler);
    
    monitor.updatePrice('TEST', 105);
    
    expect(handler).toHaveBeenCalledWith({
      symbol: 'TEST',
      price: 105,
      change: 5
    });
  });

  it('should emit alert when threshold exceeded', () => {
    const alertHandler = jest.fn();
    monitor.setAlertThreshold('TEST', 110, 90);
    monitor.on('alert', alertHandler);
    
    monitor.updatePrice('TEST', 115);
    
    expect(alertHandler).toHaveBeenCalledWith(
      expect.objectContaining({ symbol: 'TEST', level: 'warning' })
    );
  });

  it('should throw for unknown stock', () => {
    expect(() => monitor.updatePrice('UNKNOWN', 100)).toThrow('not found');
  });
});
```

## Analysis

### Pattern Structure

```
Subject (Observable)
    ├── listeners: Map<Event, Set<Handler>>
    ├── on(event, handler): Unsubscribe
    ├── off(event): void
    └── emit(event, data): void

Observer
    └── handler(data): void
```

### Key Benefits of This Implementation

1. **Type Safety**: Full TypeScript inference for event payloads
   ```typescript
   emitter.on('priceChange', (data) => {
     // data.symbol and data.price are typed!
   });
   ```

2. **Memory Leak Prevention**: Returns unsubscribe function by default

3. **Error Isolation**: Handlers that throw don't break other handlers

### When to Use Observer Pattern

✅ **Use when:**
- Building event-driven systems
- Creating reactive UIs
- Implementing pub/sub messaging
- Decoupling components

❌ **Avoid when:**
- Simple 1:1 communication (use direct calls)
- Performance-critical hot paths
- You need guaranteed delivery (use message queues)

### Comparison with Alternatives

| Pattern | Coupling | Use Case |
|---------|----------|----------|
| Observer | Loose | Event broadcasting |
| Pub/Sub | Very loose | Distributed systems |
| Callback | Tight | Async operations |
| Promise | Tight | One-time async |
| RxJS Observable | Loose | Streams, backpressure |

### Production Considerations

1. **Memory Leaks**: Always unsubscribe in `useEffect` cleanup or component unmount
2. **Performance**: For high-frequency events, consider batching or throttling
3. **Testing**: Mock emitters in unit tests for isolation
