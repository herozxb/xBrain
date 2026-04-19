# TypeScript Design Patterns

A collection of essential design patterns implemented in TypeScript.

## Pattern: Singleton

### Implementation

```typescript
class Singleton {
  private static instance: Singleton;
  private constructor() {
    // Private constructor prevents direct instantiation
  }

  public static getInstance(): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton();
    }
    return Singleton.instance;
  }

  public someBusinessLogic(): void {
    console.log("Executing business logic...");
  }
}
```

### Usage Example

```typescript
const instance1 = Singleton.getInstance();
const instance2 = Singleton.getInstance();

console.log(instance1 === instance2); // true

instance1.someBusinessLogic(); // "Executing business logic..."
```

---

## Pattern: Factory

### Implementation

```typescript
interface Product {
  operation(): string;
}

class ConcreteProductA implements Product {
  operation(): string {
    return "Result of ConcreteProductA";
  }
}

class ConcreteProductB implements Product {
  operation(): string {
    return "Result of ConcreteProductB";
  }
}

abstract class Creator {
  public abstract factoryMethod(): Product;

  public someOperation(): string {
    const product = this.factoryMethod();
    return `Creator: Working with ${product.operation()}`;
  }
}

class ConcreteCreatorA extends Creator {
  public factoryMethod(): Product {
    return new ConcreteProductA();
  }
}

class ConcreteCreatorB extends Creator {
  public factoryMethod(): Product {
    return new ConcreteProductB();
  }
}
```

### Usage Example

```typescript
function clientCode(creator: Creator): void {
  console.log(creator.someOperation());
}

clientCode(new ConcreteCreatorA());
// "Creator: Working with Result of ConcreteProductA"

clientCode(new ConcreteCreatorB());
// "Creator: Working with Result of ConcreteProductB"
```

---

## Pattern: Observer

### Implementation

```typescript
interface Observer {
  update(subject: Subject): void;
}

interface Subject {
  attach(observer: Observer): void;
  detach(observer: Observer): void;
  notify(): void;
}

class ConcreteSubject implements Subject {
  private observers: Observer[] = [];
  public state: number = 0;

  public attach(observer: Observer): void {
    const isExist = this.observers.includes(observer);
    if (isExist) {
      return console.log("Observer already attached.");
    }
    this.observers.push(observer);
    console.log("Attached an observer.");
  }

  public detach(observer: Observer): void {
    const observerIndex = this.observers.indexOf(observer);
    if (observerIndex === -1) {
      return console.log("Nonexistent observer.");
    }
    this.observers.splice(observerIndex, 1);
    console.log("Detached an observer.");
  }

  public notify(): void {
    console.log("Notifying observers...");
    for (const observer of this.observers) {
      observer.update(this);
    }
  }

  public someBusinessLogic(): void {
    console.log("Updating state...");
    this.state = Math.floor(Math.random() * 10);
    this.notify();
  }
}

class ConcreteObserverA implements Observer {
  public update(subject: Subject): void {
    if (subject instanceof ConcreteSubject && subject.state < 3) {
      console.log("ConcreteObserverA: Reacted to the event.");
    }
  }
}

class ConcreteObserverB implements Observer {
  public update(subject: Subject): void {
    if (subject instanceof ConcreteSubject && (subject.state === 0 || subject.state >= 2)) {
      console.log("ConcreteObserverB: Reacted to the event.");
    }
  }
}
```

### Usage Example

```typescript
const subject = new ConcreteSubject();

const observer1 = new ConcreteObserverA();
subject.attach(observer1);

const observer2 = new ConcreteObserverB();
subject.attach(observer2);

subject.someBusinessLogic();
// "Updating state..."
// "Notifying observers..."
// Possible: "ConcreteObserverA: Reacted to the event."
// Possible: "ConcreteObserverB: Reacted to the event."

subject.detach(observer1);
// "Detached an observer."
```

---

## Pattern: Strategy

### Implementation

```typescript
interface Strategy {
  execute(a: number, b: number): number;
}

class ConcreteStrategyAdd implements Strategy {
  execute(a: number, b: number): number {
    return a + b;
  }
}

class ConcreteStrategySubtract implements Strategy {
  execute(a: number, b: number): number {
    return a - b;
  }
}

class ConcreteStrategyMultiply implements Strategy {
  execute(a: number, b: number): number {
    return a * b;
  }
}

class Context {
  private strategy: Strategy;

  constructor(strategy: Strategy) {
    this.strategy = strategy;
  }

  public setStrategy(strategy: Strategy): void {
    this.strategy = strategy;
  }

  public executeStrategy(a: number, b: number): number {
    return this.strategy.execute(a, b);
  }
}
```

### Usage Example

```typescript
const context = new Context(new ConcreteStrategyAdd());
console.log(context.executeStrategy(5, 3)); // 8

context.setStrategy(new ConcreteStrategySubtract());
console.log(context.executeStrategy(5, 3)); // 2

context.setStrategy(new ConcreteStrategyMultiply());
console.log(context.executeStrategy(5, 3)); // 15
```

---

## Pattern: Decorator

### Implementation

```typescript
interface Component {
  operation(): string;
}

class ConcreteComponent implements Component {
  operation(): string {
    return "ConcreteComponent";
  }
}

class Decorator implements Component {
  protected component: Component;

  constructor(component: Component) {
    this.component = component;
  }

  operation(): string {
    return this.component.operation();
  }
}

class ConcreteDecoratorA extends Decorator {
  operation(): string {
    return `ConcreteDecoratorA(${super.operation()})`;
  }
}

class ConcreteDecoratorB extends Decorator {
  operation(): string {
    return `ConcreteDecoratorB(${super.operation()})`;
  }
}
```

### Usage Example

```typescript
const simple = new ConcreteComponent();
console.log(simple.operation()); // "ConcreteComponent"

const decorator1 = new ConcreteDecoratorA(simple);
console.log(decorator1.operation()); // "ConcreteDecoratorA(ConcreteComponent)"

const decorator2 = new ConcreteDecoratorB(decorator1);
console.log(decorator2.operation()); // "ConcreteDecoratorB(ConcreteDecoratorA(ConcreteComponent))"

// Stacking multiple decorators
const decorator3 = new ConcreteDecoratorA(decorator2);
console.log(decorator3.operation());
// "ConcreteDecoratorA(ConcreteDecoratorB(ConcreteDecoratorA(ConcreteComponent)))"
```

---

## Summary

| Pattern | Intent |
|---------|--------|
| Singleton | Ensure a class has only one instance |
| Factory | Create objects without specifying exact class |
| Observer | Define subscription mechanism for events |
| Strategy | Define family of algorithms, make them interchangeable |
| Decorator | Add responsibilities to objects dynamically |
