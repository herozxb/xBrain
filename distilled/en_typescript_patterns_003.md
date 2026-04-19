# TypeScript Design Patterns: Creational & Behavioral

## Pattern 1: Abstract Factory Pattern

### Problem Description
Create families of related objects without specifying their concrete classes.

### Solution

```typescript
// ============================================================
// Abstract Factory Pattern - UI Component Factory
// ============================================================

// Abstract Products
interface Button {
  render(): string;
  onClick(callback: () => void): void;
}

interface TextInput {
  render(): string;
  getValue(): string;
  setValue(value: string): void;
}

interface Checkbox {
  render(): string;
  isChecked(): boolean;
  toggle(): void;
}

// Concrete Products - Material Design
class MaterialButton implements Button {
  private callback?: () => void;

  render(): string {
    return '<button class="mdc-button mdc-button--raised">Material Button</button>';
  }

  onClick(callback: () => void): void {
    this.callback = callback;
  }

  click(): void {
    this.callback?.();
  }
}

class MaterialTextInput implements TextInput {
  private value = '';

  render(): string {
    return `<div class="mdc-text-field">
      <input type="text" class="mdc-text-field__input" value="${this.value}">
    </div>`;
  }

  getValue(): string {
    return this.value;
  }

  setValue(value: string): void {
    this.value = value;
  }
}

class MaterialCheckbox implements Checkbox {
  private checked = false;

  render(): string {
    return `<div class="mdc-checkbox">
      <input type="checkbox" class="mdc-checkbox__native-control" ${this.checked ? 'checked' : ''}>
    </div>`;
  }

  isChecked(): boolean {
    return this.checked;
  }

  toggle(): void {
    this.checked = !this.checked;
  }
}

// Concrete Products - iOS Style
class IOSButton implements Button {
  private callback?: () => void;

  render(): string {
    return '<button class="ios-button">iOS Button</button>';
  }

  onClick(callback: () => void): void {
    this.callback = callback;
  }

  click(): void {
    this.callback?.();
  }
}

class IOSTextInput implements TextInput {
  private value = '';

  render(): string {
    return `<input type="text" class="ios-textfield rounded-xl" value="${this.value}">`;
  }

  getValue(): string {
    return this.value;
  }

  setValue(value: string): void {
    this.value = value;
  }
}

class IOSCheckbox implements Checkbox {
  private checked = false;

  render(): string {
    return `<div class="ios-switch ${this.checked ? 'active' : ''}"></div>`;
  }

  isChecked(): boolean {
    return this.checked;
  }

  toggle(): void {
    this.checked = !this.checked;
  }
}

// Abstract Factory
interface UIComponentFactory {
  createButton(): Button;
  createTextInput(): TextInput;
  createCheckbox(): Checkbox;
}

// Concrete Factories
class MaterialUIFactory implements UIComponentFactory {
  createButton(): Button {
    return new MaterialButton();
  }

  createTextInput(): TextInput {
    return new MaterialTextInput();
  }

  createCheckbox(): Checkbox {
    return new MaterialCheckbox();
  }
}

class IOSUIFactory implements UIComponentFactory {
  createButton(): Button {
    return new IOSButton();
  }

  createTextInput(): TextInput {
    return new IOSTextInput();
  }

  createCheckbox(): Checkbox {
    return new IOSCheckbox();
  }
}

// Factory Provider
class FactoryProvider {
  static getFactory(theme: 'material' | 'ios'): UIComponentFactory {
    switch (theme) {
      case 'material':
        return new MaterialUIFactory();
      case 'ios':
        return new IOSUIFactory();
      default:
        throw new Error(`Unknown theme: ${theme}`);
    }
  }
}

// Client Code
class Application {
  private button: Button;
  private textInput: TextInput;
  private checkbox: Checkbox;

  constructor(factory: UIComponentFactory) {
    this.button = factory.createButton();
    this.textInput = factory.createTextInput();
    this.checkbox = factory.createCheckbox();
  }

  render(): string {
    return [
      this.button.render(),
      this.textInput.render(),
      this.checkbox.render()
    ].join('\n');
  }
}
```

### Tests

```typescript
import { describe, it, expect } from 'vitest';

describe('Abstract Factory Pattern', () => {
  it('should create Material UI components', () => {
    const factory = new MaterialUIFactory();
    const button = factory.createButton();
    const textInput = factory.createTextInput();
    const checkbox = factory.createCheckbox();

    expect(button.render()).toContain('mdc-button');
    expect(textInput.render()).toContain('mdc-text-field');
    expect(checkbox.render()).toContain('mdc-checkbox');
  });

  it('should create iOS UI components', () => {
    const factory = new IOSUIFactory();
    const button = factory.createButton();
    const textInput = factory.createTextInput();
    const checkbox = factory.createCheckbox();

    expect(button.render()).toContain('ios-button');
    expect(textInput.render()).toContain('ios-textfield');
    expect(checkbox.render()).toContain('ios-switch');
  });

  it('should create consistent component family', () => {
    const factory = FactoryProvider.getFactory('material');
    const app = new Application(factory);
    const rendered = app.render();

    expect(rendered).toContain('mdc-button');
    expect(rendered).toContain('mdc-text-field');
    expect(rendered).toContain('mdc-checkbox');
  });

  it('should handle button click callback', () => {
    const factory = new MaterialUIFactory();
    const button = factory.createButton() as MaterialButton;
    
    let clicked = false;
    button.onClick(() => { clicked = true; });
    button.click();
    
    expect(clicked).toBe(true);
  });

  it('should manage text input state', () => {
    const factory = new IOSUIFactory();
    const input = factory.createTextInput();
    
    input.setValue('test value');
    expect(input.getValue()).toBe('test value');
  });

  it('should toggle checkbox state', () => {
    const factory = new MaterialUIFactory();
    const checkbox = factory.createCheckbox();
    
    expect(checkbox.isChecked()).toBe(false);
    checkbox.toggle();
    expect(checkbox.isChecked()).toBe(true);
  });
});
```

### Analysis

**When to Use:**
- System needs to be independent of how its objects are created
- Family of related objects must be used together
- Need to provide a library of objects without exposing implementation

**Pros:**
- Ensures consistency among related products
- Avoids coupling concrete classes to client code
- Easy to add new product families

**Cons:**
- Adding new product types requires changing all factories
- Can lead to many small classes

---

## Pattern 2: Strategy Pattern

### Problem Description
Define a family of algorithms, encapsulate each one, and make them interchangeable.

### Solution

```typescript
// ============================================================
// Strategy Pattern - Payment Processing System
// ============================================================

// Strategy Interface
interface PaymentStrategy {
  pay(amount: number): Promise<PaymentResult>;
  validate(): boolean;
  getMethodName(): string;
}

interface PaymentResult {
  success: boolean;
  transactionId?: string;
  error?: string;
  fee?: number;
}

// Concrete Strategies
class CreditCardStrategy implements PaymentStrategy {
  constructor(
    private cardNumber: string,
    private cvv: string,
    private expiryDate: string
  ) {}

  validate(): boolean {
    const cardRegex = /^\d{16}$/;
    const cvvRegex = /^\d{3,4}$/;
    const expiryRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;
    
    return cardRegex.test(this.cardNumber.replace(/\s/g, '')) &&
           cvvRegex.test(this.cvv) &&
           expiryRegex.test(this.expiryDate);
  }

  async pay(amount: number): Promise<PaymentResult> {
    if (!this.validate()) {
      return { success: false, error: 'Invalid card details' };
    }

    // Simulate API call
    await this.delay(500);

    return {
      success: true,
      transactionId: `CC-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      fee: amount * 0.029 // 2.9% fee
    };
  }

  getMethodName(): string {
    return 'Credit Card';
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class PayPalStrategy implements PaymentStrategy {
  constructor(
    private email: string,
    private password: string
  ) {}

  validate(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(this.email) && this.password.length >= 8;
  }

  async pay(amount: number): Promise<PaymentResult> {
    if (!this.validate()) {
      return { success: false, error: 'Invalid PayPal credentials' };
    }

    await this.delay(300);

    return {
      success: true,
      transactionId: `PP-${Date.now()}`,
      fee: amount * 0.034 + 0.30 // 3.4% + $0.30
    };
  }

  getMethodName(): string {
    return 'PayPal';
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class CryptoStrategy implements PaymentStrategy {
  constructor(
    private walletAddress: string,
    private cryptocurrency: 'bitcoin' | 'ethereum'
  ) {}

  validate(): boolean {
    // Simplified validation
    return this.walletAddress.length >= 26;
  }

  async pay(amount: number): Promise<PaymentResult> {
    if (!this.validate()) {
      return { success: false, error: 'Invalid wallet address' };
    }

    await this.delay(2000); // Crypto takes longer

    return {
      success: true,
      transactionId: `${this.cryptocurrency.toUpperCase()}-${this.walletAddress.slice(0, 8)}`,
      fee: 0 // Crypto payments often have no processing fee
    };
  }

  getMethodName(): string {
    return `${this.cryptocurrency.charAt(0).toUpperCase() + this.cryptocurrency.slice(1)}`;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Context
class PaymentProcessor {
  private strategy?: PaymentStrategy;

  setStrategy(strategy: PaymentStrategy): void {
    this.strategy = strategy;
  }

  async processPayment(amount: number): Promise<PaymentResult> {
    if (!this.strategy) {
      return { success: false, error: 'No payment method selected' };
    }

    console.log(`Processing $${amount} via ${this.strategy.getMethodName()}`);
    return this.strategy.pay(amount);
  }
}

// Usage with Factory
class PaymentStrategyFactory {
  static createCreditCard(cardNumber: string, cvv: string, expiry: string): PaymentStrategy {
    return new CreditCardStrategy(cardNumber, cvv, expiry);
  }

  static createPayPal(email: string, password: string): PaymentStrategy {
    return new PayPalStrategy(email, password);
  }

  static createCrypto(address: string, crypto: 'bitcoin' | 'ethereum'): PaymentStrategy {
    return new CryptoStrategy(address, crypto);
  }
}
```

### Tests

```typescript
import { describe, it, expect } from 'vitest';

describe('Strategy Pattern - Payment Processing', () => {
  it('should validate credit card details', () => {
    const validCard = new CreditCardStrategy('1234567890123456', '123', '12/25');
    const invalidCard = new CreditCardStrategy('123', '1', 'invalid');
    
    expect(validCard.validate()).toBe(true);
    expect(invalidCard.validate()).toBe(false);
  });

  it('should validate PayPal credentials', () => {
    const validPaypal = new PayPalStrategy('test@example.com', 'password123');
    const invalidPaypal = new PayPalStrategy('invalid-email', 'short');
    
    expect(validPaypal.validate()).toBe(true);
    expect(invalidPaypal.validate()).toBe(false);
  });

  it('should process credit card payment', async () => {
    const strategy = new CreditCardStrategy('1234567890123456', '123', '12/25');
    const result = await strategy.pay(100);
    
    expect(result.success).toBe(true);
    expect(result.transactionId).toMatch(/^CC-/);
    expect(result.fee).toBeCloseTo(2.9, 1);
  });

  it('should process PayPal payment', async () => {
    const strategy = new PayPalStrategy('test@example.com', 'password123');
    const result = await strategy.pay(100);
    
    expect(result.success).toBe(true);
    expect(result.transactionId).toMatch(/^PP-/);
  });

  it('should switch between strategies', async () => {
    const processor = new PaymentProcessor();
    
    processor.setStrategy(new CreditCardStrategy('1234567890123456', '123', '12/25'));
    let result = await processor.processPayment(50);
    expect(result.success).toBe(true);
    
    processor.setStrategy(new PayPalStrategy('test@example.com', 'password123'));
    result = await processor.processPayment(50);
    expect(result.success).toBe(true);
  });

  it('should handle missing strategy', async () => {
    const processor = new PaymentProcessor();
    const result = await processor.processPayment(100);
    
    expect(result.success).toBe(false);
    expect(result.error).toContain('No payment method');
  });

  it('should handle invalid payment details', async () => {
    const strategy = new CreditCardStrategy('invalid', 'invalid', 'invalid');
    const result = await strategy.pay(100);
    
    expect(result.success).toBe(false);
    expect(result.error).toContain('Invalid');
  });

  it('should create strategies via factory', () => {
    const creditCard = PaymentStrategyFactory.createCreditCard('1234567890123456', '123', '12/25');
    const paypal = PaymentStrategyFactory.createPayPal('test@example.com', 'password123');
    const crypto = PaymentStrategyFactory.createCrypto('abc123', 'bitcoin');
    
    expect(creditCard.getMethodName()).toBe('Credit Card');
    expect(paypal.getMethodName()).toBe('PayPal');
    expect(crypto.getMethodName()).toBe('Bitcoin');
  });
});
```

### Analysis

**When to Use:**
- Multiple ways to do a specific task
- Need to switch algorithms at runtime
- Avoid complex conditional logic for selecting behaviors

**Pros:**
- Algorithms can vary independently from clients
- Easy to add new strategies
- Eliminates conditional statements

**Cons:**
- Clients must know about different strategies
- Increases number of objects

---

## Pattern 3: Observer Pattern with RxJS

### Problem Description
Implement reactive event streams with multiple observers.

### Solution

```typescript
// ============================================================
// Observer Pattern - Event Bus System
// ============================================================

import { Subject, Observable, Subscription, BehaviorSubject } from 'rxjs';
import { filter, map } from 'rxjs/operators';

// Event Types
interface BaseEvent {
  type: string;
  timestamp: Date;
  payload?: unknown;
}

interface UserEvent extends BaseEvent {
  type: 'user:login' | 'user:logout' | 'user:update';
  payload: {
    userId: string;
    username?: string;
    email?: string;
  };
}

interface OrderEvent extends BaseEvent {
  type: 'order:created' | 'order:shipped' | 'order:delivered';
  payload: {
    orderId: string;
    customerId: string;
    total: number;
  };
}

type AppEvent = UserEvent | OrderEvent;

// Event Bus
class EventBus {
  private subject = new Subject<AppEvent>();
  
  emit(event: AppEvent): void {
    this.subject.next(event);
  }

  on<T extends AppEvent>(
    eventType: T['type']
  ): Observable<T> {
    return this.subject.asObservable().pipe(
      filter((event): event is T => event.type === eventType)
    );
  }

  onAll(): Observable<AppEvent> {
    return this.subject.asObservable();
  }
}

// State Store with Observers
class ObservableStore<T> {
  private state$: BehaviorSubject<T>;
  
  constructor(initialState: T) {
    this.state$ = new BehaviorSubject(initialState);
  }

  getState(): T {
    return this.state$.getValue();
  }

  setState(newState: Partial<T>): void {
    this.state$.next({ ...this.getState(), ...newState });
  }

  subscribe(callback: (state: T) => void): Subscription {
    return this.state$.subscribe(callback);
  }

  select<R>(selector: (state: T) => R): Observable<R> {
    return this.state$.asObservable().pipe(map(selector));
  }
}

// User Store Implementation
interface UserState {
  isLoggedIn: boolean;
  userId: string | null;
  username: string | null;
}

class UserStore extends ObservableStore<UserState> {
  constructor() {
    super({
      isLoggedIn: false,
      userId: null,
      username: null
    });
  }

  login(userId: string, username: string): void {
    this.setState({
      isLoggedIn: true,
      userId,
      username
    });
  }

  logout(): void {
    this.setState({
      isLoggedIn: false,
      userId: null,
      username: null
    });
  }
}

// Logger Observer
class EventLogger {
  constructor(private eventBus: EventBus) {
    this.eventBus.onAll().subscribe(event => {
      console.log(`[${event.timestamp.toISOString()}] ${event.type}:`, event.payload);
    });
  }
}

// Analytics Observer
class AnalyticsService {
  private events: AppEvent[] = [];

  constructor(private eventBus: EventBus) {
    this.eventBus.onAll().subscribe(event => {
      this.events.push(event);
    });
  }

  getEventCount(): number {
    return this.events.length;
  }

  getEventsByType(type: string): AppEvent[] {
    return this.events.filter(e => e.type === type);
  }
}

// Notification Service
class NotificationService {
  constructor(private eventBus: EventBus) {
    // Subscribe to order events
    this.eventBus.on('order:created').subscribe(event => {
      this.sendNotification(
        `New order #${event.payload.orderId} created!`,
        event.payload.customerId
      );
    });

    this.eventBus.on('order:shipped').subscribe(event => {
      this.sendNotification(
        `Order #${event.payload.orderId} has been shipped!`,
        event.payload.customerId
      );
    });
  }

  private sendNotification(message: string, userId: string): void {
    console.log(`[Notification] To ${userId}: ${message}`);
  }
}
```

### Tests

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('Observer Pattern - Event System', () => {
  let eventBus: EventBus;

  beforeEach(() => {
    eventBus = new EventBus();
  });

  it('should emit and receive events', () => {
    const handler = vi.fn();
    eventBus.on('user:login').subscribe(handler);

    const event: UserEvent = {
      type: 'user:login',
      timestamp: new Date(),
      payload: { userId: '123', username: 'test' }
    };

    eventBus.emit(event);
    expect(handler).toHaveBeenCalledWith(event);
  });

  it('should filter events by type', () => {
    const userHandler = vi.fn();
    const orderHandler = vi.fn();

    eventBus.on('user:login').subscribe(userHandler);
    eventBus.on('order:created').subscribe(orderHandler);

    eventBus.emit({
      type: 'user:login',
      timestamp: new Date(),
      payload: { userId: '123' }
    });

    expect(userHandler).toHaveBeenCalled();
    expect(orderHandler).not.toHaveBeenCalled();
  });

  it('should manage observable store state', () => {
    const store = new UserStore();
    const callback = vi.fn();
    store.subscribe(callback);

    store.login('123', 'testuser');

    expect(store.getState().isLoggedIn).toBe(true);
    expect(store.getState().userId).toBe('123');
    expect(callback).toHaveBeenCalled();
  });

  it('should select specific state properties', (done) => {
    const store = new UserStore();
    
    store.select(state => state.isLoggedIn).subscribe(isLoggedIn => {
      if (isLoggedIn) {
        expect(isLoggedIn).toBe(true);
        done();
      }
    });

    store.login('123', 'testuser');
  });

  it('should track events in analytics service', () => {
    const analytics = new AnalyticsService(eventBus);

    eventBus.emit({
      type: 'order:created',
      timestamp: new Date(),
      payload: { orderId: 'ORD-001', customerId: 'CUST-001', total: 100 }
    });

    eventBus.emit({
      type: 'order:shipped',
      timestamp: new Date(),
      payload: { orderId: 'ORD-002', customerId: 'CUST-002', total: 200 }
    });

    expect(analytics.getEventCount()).toBe(2);
    expect(analytics.getEventsByType('order:created')).toHaveLength(1);
  });
});
```

### Analysis

**When to Use:**
- When objects need to be notified of state changes
- Broadcasting events to multiple listeners
- Decoupling event producers from consumers

**Pros:**
- Loose coupling between subjects and observers
- Dynamic subscription management
- Easy to add new observers

**Cons:**
- Unexpected updates if not careful
- Memory leaks if subscriptions not cleaned up
- Performance issues with many observers

---

## Summary

| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Abstract Factory | Create families of related objects | Medium |
| Strategy | Interchangeable algorithms | Low |
| Observer | Reactive event streams | Medium |

**Key Takeaways:**
- Use Abstract Factory for consistent product families
- Strategy pattern for runtime algorithm selection
- Observer with RxJS for reactive, composable event handling
