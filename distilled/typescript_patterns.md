# TypeScript/JavaScript 设计模式实现

本文档包含10个常用设计模式的完整TypeScript实现、使用示例和测试代码。

---

## 1. 单例模式 (Singleton Pattern)

### 概念
确保一个类只有一个实例，并提供全局访问点。

### TypeScript 实现

```typescript
class Singleton {
  private static instance: Singleton;
  private constructor(private value: string = "Default") {}
  
  public static getInstance(): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton();
    }
    return Singleton.instance;
  }
  
  public getValue(): string {
    return this.value;
  }
  
  public setValue(value: string): void {
    this.value = value;
  }
}

// 线程安全的单例（使用立即初始化）
class ThreadSafeSingleton {
  private static instance: ThreadSafeSingleton = new ThreadSafeSingleton();
  
  private constructor() {}
  
  public static getInstance(): ThreadSafeSingleton {
    return ThreadSafeSingleton.instance;
  }
}
```

### 使用示例

```typescript
// 获取单例实例
const instance1 = Singleton.getInstance();
const instance2 = Singleton.getInstance();

console.log(instance1 === instance2); // true
console.log(instance1.getValue()); // "Default"

instance1.setValue("New Value");
console.log(instance2.getValue()); // "New Value"
```

### 测试代码

```typescript
describe('Singleton Pattern', () => {
  test('should return same instance', () => {
    const instance1 = Singleton.getInstance();
    const instance2 = Singleton.getInstance();
    expect(instance1).toBe(instance2);
  });
  
  test('should share state across instances', () => {
    const instance1 = Singleton.getInstance();
    const instance2 = Singleton.getInstance();
    
    instance1.setValue("Test Value");
    expect(instance2.getValue()).toBe("Test Value");
  });
  
  test('should not allow direct instantiation', () => {
    // @ts-expect-error - Constructor is private
    expect(() => new Singleton()).toThrow();
  });
});
```

---

## 2. 工厂模式 (Factory Pattern)

### 概念
定义一个创建对象的接口，让子类决定实例化哪一个类。

### TypeScript 实现

```typescript
// 产品接口
interface Product {
  operation(): string;
}

// 具体产品A
class ConcreteProductA implements Product {
  public operation(): string {
    return "ConcreteProductA operation";
  }
}

// 具体产品B
class ConcreteProductB implements Product {
  public operation(): string {
    return "ConcreteProductB operation";
  }
}

// 工厂类
class Factory {
  public static createProduct(type: string): Product {
    switch (type) {
      case "A":
        return new ConcreteProductA();
      case "B":
        return new ConcreteProductB();
      default:
        throw new Error(`Unknown product type: ${type}`);
    }
  }
}

// 抽象工厂
interface AbstractFactory {
  createProduct(): Product;
}

class ConcreteFactoryA implements AbstractFactory {
  public createProduct(): Product {
    return new ConcreteProductA();
  }
}

class ConcreteFactoryB implements AbstractFactory {
  public createProduct(): Product {
    return new ConcreteProductB();
  }
}
```

### 使用示例

```typescript
// 使用简单工厂
const productA = Factory.createProduct("A");
console.log(productA.operation()); // "ConcreteProductA operation"

// 使用抽象工厂
const factoryA: AbstractFactory = new ConcreteFactoryA();
const product = factoryA.createProduct();
console.log(product.operation()); // "ConcreteProductA operation"
```

### 测试代码

```typescript
describe('Factory Pattern', () => {
  test('should create Product A', () => {
    const product = Factory.createProduct("A");
    expect(product).toBeInstanceOf(ConcreteProductA);
    expect(product.operation()).toBe("ConcreteProductA operation");
  });
  
  test('should create Product B', () => {
    const product = Factory.createProduct("B");
    expect(product).toBeInstanceOf(ConcreteProductB);
    expect(product.operation()).toBe("ConcreteProductB operation");
  });
  
  test('should throw error for unknown type', () => {
    expect(() => Factory.createProduct("C")).toThrow("Unknown product type: C");
  });
  
  test('abstract factory should work', () => {
    const factory: AbstractFactory = new ConcreteFactoryB();
    const product = factory.createProduct();
    expect(product.operation()).toBe("ConcreteProductB operation");
  });
});
```

---

## 3. 观察者模式 (Observer Pattern)

### 概念
定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会收到通知。

### TypeScript 实现

```typescript
// 观察者接口
interface Observer {
  update(data: any): void;
}

// 主题接口
interface Subject {
  attach(observer: Observer): void;
  detach(observer: Observer): void;
  notify(data: any): void;
}

// 具体主题
class ConcreteSubject implements Subject {
  private observers: Observer[] = [];
  private state: any;
  
  public attach(observer: Observer): void {
    const isExist = this.observers.includes(observer);
    if (isExist) {
      return console.log("Observer already attached");
    }
    this.observers.push(observer);
    console.log("Observer attached");
  }
  
  public detach(observer: Observer): void {
    const observerIndex = this.observers.indexOf(observer);
    if (observerIndex === -1) {
      return console.log("Observer not found");
    }
    this.observers.splice(observerIndex, 1);
    console.log("Observer detached");
  }
  
  public notify(data: any): void {
    console.log(`Notifying ${this.observers.length} observers`);
    for (const observer of this.observers) {
      observer.update(data);
    }
  }
  
  public setState(state: any): void {
    this.state = state;
    this.notify(state);
  }
  
  public getState(): any {
    return this.state;
  }
}

// 具体观察者
class ConcreteObserver implements Observer {
  constructor(private name: string) {}
  
  public update(data: any): void {
    console.log(`${this.name} received update: ${JSON.stringify(data)}`);
  }
  
  public getName(): string {
    return this.name;
  }
}
```

### 使用示例

```typescript
const subject = new ConcreteSubject();

const observer1 = new ConcreteObserver("Observer 1");
const observer2 = new ConcreteObserver("Observer 2");

subject.attach(observer1);
subject.attach(observer2);

subject.setState({ temperature: 25 }); // 两个观察者都会收到通知

subject.detach(observer1);

subject.setState({ temperature: 30 }); // 只有 Observer 2 收到通知
```

### 测试代码

```typescript
describe('Observer Pattern', () => {
  let subject: ConcreteSubject;
  let observer1: ConcreteObserver;
  let observer2: ConcreteObserver;
  
  beforeEach(() => {
    subject = new ConcreteSubject();
    observer1 = new ConcreteObserver("Observer 1");
    observer2 = new ConcreteObserver("Observer 2");
  });
  
  test('should attach observers', () => {
    const consoleSpy = jest.spyOn(console, 'log');
    subject.attach(observer1);
    expect(consoleSpy).toHaveBeenCalledWith("Observer attached");
  });
  
  test('should notify all observers', () => {
    subject.attach(observer1);
    subject.attach(observer2);
    
    const consoleSpy = jest.spyOn(console, 'log');
    subject.setState({ value: 42 });
    
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Observer 1 received update"));
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Observer 2 received update"));
  });
  
  test('should detach observers', () => {
    subject.attach(observer1);
    subject.detach(observer1);
    
    const consoleSpy = jest.spyOn(console, 'log');
    subject.setState({ value: 42 });
    
    expect(consoleSpy).not.toHaveBeenCalledWith(expect.stringContaining("Observer 1 received update"));
  });
});
```

---

## 4. 策略模式 (Strategy Pattern)

### 概念
定义一系列算法，把它们一个个封装起来，并且使它们可相互替换。

### TypeScript 实现

```typescript
// 策略接口
interface Strategy {
  execute(a: number, b: number): number;
}

// 具体策略：加法
class AddStrategy implements Strategy {
  public execute(a: number, b: number): number {
    return a + b;
  }
}

// 具体策略：减法
class SubtractStrategy implements Strategy {
  public execute(a: number, b: number): number {
    return a - b;
  }
}

// 具体策略：乘法
class MultiplyStrategy implements Strategy {
  public execute(a: number, b: number): number {
    return a * b;
  }
}

// 上下文
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

### 使用示例

```typescript
const context = new Context(new AddStrategy());
console.log(context.executeStrategy(5, 3)); // 8

context.setStrategy(new SubtractStrategy());
console.log(context.executeStrategy(5, 3)); // 2

context.setStrategy(new MultiplyStrategy());
console.log(context.executeStrategy(5, 3)); // 15
```

### 测试代码

```typescript
describe('Strategy Pattern', () => {
  let context: Context;
  
  beforeEach(() => {
    context = new Context(new AddStrategy());
  });
  
  test('should perform addition', () => {
    expect(context.executeStrategy(5, 3)).toBe(8);
  });
  
  test('should perform subtraction', () => {
    context.setStrategy(new SubtractStrategy());
    expect(context.executeStrategy(5, 3)).toBe(2);
  });
  
  test('should perform multiplication', () => {
    context.setStrategy(new MultiplyStrategy());
    expect(context.executeStrategy(5, 3)).toBe(15);
  });
  
  test('should switch strategies at runtime', () => {
    expect(context.executeStrategy(10, 5)).toBe(15); // add
    context.setStrategy(new SubtractStrategy());
    expect(context.executeStrategy(10, 5)).toBe(5);  // subtract
    context.setStrategy(new MultiplyStrategy());
    expect(context.executeStrategy(10, 5)).toBe(50); // multiply
  });
});
```

---

## 5. 装饰器模式 (Decorator Pattern)

### 概念
动态地给一个对象添加一些额外的职责，就增加功能来说，装饰器模式比生成子类更为灵活。

### TypeScript 实现

```typescript
// 组件接口
interface Component {
  operation(): string;
}

// 具体组件
class ConcreteComponent implements Component {
  public operation(): string {
    return "ConcreteComponent";
  }
}

// 装饰器基类
class Decorator implements Component {
  protected component: Component;
  
  constructor(component: Component) {
    this.component = component;
  }
  
  public operation(): string {
    return this.component.operation();
  }
}

// 具体装饰器A
class ConcreteDecoratorA extends Decorator {
  public operation(): string {
    return `ConcreteDecoratorA(${super.operation()})`;
  }
}

// 具体装饰器B
class ConcreteDecoratorB extends Decorator {
  public operation(): string {
    return `ConcreteDecoratorB(${super.operation()})`;
  }
  
  public addedBehavior(): string {
    return "Added behavior from B";
  }
}
```

### 使用示例

```typescript
let component: Component = new ConcreteComponent();
console.log(component.operation()); // "ConcreteComponent"

// 添加装饰器A
component = new ConcreteDecoratorA(component);
console.log(component.operation()); // "ConcreteDecoratorA(ConcreteComponent)"

// 再添加装饰器B
component = new ConcreteDecoratorB(component);
console.log(component.operation()); // "ConcreteDecoratorB(ConcreteDecoratorA(ConcreteComponent))"
```

### 测试代码

```typescript
describe('Decorator Pattern', () => {
  test('should use plain component', () => {
    const component = new ConcreteComponent();
    expect(component.operation()).toBe("ConcreteComponent");
  });
  
  test('should decorate with A', () => {
    const component = new ConcreteComponent();
    const decorated = new ConcreteDecoratorA(component);
    expect(decorated.operation()).toBe("ConcreteDecoratorA(ConcreteComponent)");
  });
  
  test('should decorate with multiple decorators', () => {
    const component = new ConcreteComponent();
    const decorated = new ConcreteDecoratorB(new ConcreteDecoratorA(component));
    expect(decorated.operation()).toBe("ConcreteDecoratorB(ConcreteDecoratorA(ConcreteComponent))");
  });
  
  test('decorator B should have added behavior', () => {
    const component = new ConcreteComponent();
    const decorated = new ConcreteDecoratorB(component);
    expect(decorated.addedBehavior()).toBe("Added behavior from B");
  });
});
```

---

## 6. 代理模式 (Proxy Pattern)

### 概念
为其他对象提供一种代理以控制对这个对象的访问。

### TypeScript 实现

```typescript
// 主题接口
interface Subject {
  request(): void;
}

// 真实主题
class RealSubject implements Subject {
  public request(): void {
    console.log("RealSubject: Handling request.");
  }
}

// 代理
class Proxy implements Subject {
  private realSubject: RealSubject;
  
  constructor(realSubject: RealSubject) {
    this.realSubject = realSubject;
  }
  
  public request(): void {
    if (this.checkAccess()) {
      this.realSubject.request();
      this.logAccess();
    }
  }
  
  private checkAccess(): boolean {
    console.log("Proxy: Checking access prior to firing a real request.");
    return true;
  }
  
  private logAccess(): void {
    console.log("Proxy: Logging the time of request.");
  }
}

// 虚拟代理示例（延迟加载）
class Image {
  constructor(private filename: string) {}
  
  public display(): void {
    console.log(`Displaying image: ${this.filename}`);
  }
}

class ImageProxy {
  private image: Image | null = null;
  
  constructor(private filename: string) {}
  
  public display(): void {
    if (!this.image) {
      this.image = new Image(this.filename);
      console.log("Loading image...");
    }
    this.image.display();
  }
}
```

### 使用示例

```typescript
console.log("=== Access Control Proxy ===");
const realSubject = new RealSubject();
const proxy = new Proxy(realSubject);
proxy.request();

console.log("\n=== Virtual Proxy ===");
const imageProxy = new ImageProxy("photo.jpg");
imageProxy.display(); // 首次调用会加载
imageProxy.display(); // 后续调用使用缓存
```

### 测试代码

```typescript
describe('Proxy Pattern', () => {
  test('should proxy requests', () => {
    const realSubject = new RealSubject();
    const proxy = new Proxy(realSubject);
    
    const consoleSpy = jest.spyOn(console, 'log');
    proxy.request();
    
    expect(consoleSpy).toHaveBeenCalledWith("Proxy: Checking access prior to firing a real request.");
    expect(consoleSpy).toHaveBeenCalledWith("RealSubject: Handling request.");
    expect(consoleSpy).toHaveBeenCalledWith("Proxy: Logging the time of request.");
  });
  
  test('should load image lazily', () => {
    const imageProxy = new ImageProxy("test.jpg");
    
    const consoleSpy = jest.spyOn(console, 'log');
    
    // First call - should load
    imageProxy.display();
    expect(consoleSpy).toHaveBeenCalledWith("Loading image...");
    expect(consoleSpy).toHaveBeenCalledWith("Displaying image: test.jpg");
    
    consoleSpy.mockClear();
    
    // Second call - should not load again
    imageProxy.display();
    expect(consoleSpy).not.toHaveBeenCalledWith("Loading image...");
    expect(consoleSpy).toHaveBeenCalledWith("Displaying image: test.jpg");
  });
});
```

---

## 7. 命令模式 (Command Pattern)

### 概念
将请求封装为对象，从而可用不同的请求对客户进行参数化、排队或记录请求日志，以及支持可撤销的操作。

### TypeScript 实现

```typescript
// 接收者
class Receiver {
  public doSomething(a: string): void {
    console.log(`Receiver: Working on ${a}.`);
  }
  
  public doSomethingElse(b: string): void {
    console.log(`Receiver: Also working on ${b}.`);
  }
}

// 命令接口
interface Command {
  execute(): void;
  undo(): void;
}

// 简单命令
class SimpleCommand implements Command {
  private payload: string;
  
  constructor(payload: string) {
    this.payload = payload;
  }
  
  public execute(): void {
    console.log(`SimpleCommand: See, I can do simple things like printing (${this.payload})`);
  }
  
  public undo(): void {
    console.log(`SimpleCommand: Undoing (${this.payload})`);
  }
}

// 复杂命令
class ComplexCommand implements Command {
  constructor(
    private receiver: Receiver,
    private a: string,
    private b: string
  ) {}
  
  public execute(): void {
    console.log("ComplexCommand: Complex stuff should be done by a receiver object.");
    this.receiver.doSomething(this.a);
    this.receiver.doSomethingElse(this.b);
  }
  
  public undo(): void {
    console.log("ComplexCommand: Undoing complex operations");
  }
}

// 调用者
class Invoker {
  private onStart: Command | null = null;
  private onFinish: Command | null = null;
  private history: Command[] = [];
  
  public setOnStart(command: Command): void {
    this.onStart = command;
  }
  
  public setOnFinish(command: Command): void {
    this.onFinish = command;
  }
  
  public doSomethingImportant(): void {
    console.log("Invoker: Does anybody want something done before I begin?");
    if (this.onStart) {
      this.onStart.execute();
      this.history.push(this.onStart);
    }
    
    console.log("Invoker: ...doing something really important...");
    
    console.log("Invoker: Does anybody want something done after I finish?");
    if (this.onFinish) {
      this.onFinish.execute();
      this.history.push(this.onFinish);
    }
  }
  
  public undoLast(): void {
    const command = this.history.pop();
    if (command) {
      command.undo();
    }
  }
}
```

### 使用示例

```typescript
const invoker = new Invoker();
const receiver = new Receiver();

invoker.setOnStart(new SimpleCommand("Say Hi!"));
invoker.setOnFinish(new ComplexCommand(receiver, "Send email", "Save report"));

invoker.doSomethingImportant();
invoker.undoLast();
```

### 测试代码

```typescript
describe('Command Pattern', () => {
  test('should execute simple command', () => {
    const command = new SimpleCommand("test");
    const consoleSpy = jest.spyOn(console, 'log');
    
    command.execute();
    
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("test"));
  });
  
  test('should execute complex command', () => {
    const receiver = new Receiver();
    const command = new ComplexCommand(receiver, "A", "B");
    const consoleSpy = jest.spyOn(console, 'log');
    
    command.execute();
    
    expect(consoleSpy).toHaveBeenCalledWith("Receiver: Working on A.");
    expect(consoleSpy).toHaveBeenCalledWith("Receiver: Also working on B.");
  });
  
  test('invoker should manage commands', () => {
    const invoker = new Invoker();
    const command1 = new SimpleCommand("Start");
    const command2 = new SimpleCommand("Finish");
    
    invoker.setOnStart(command1);
    invoker.setOnFinish(command2);
    
    const consoleSpy = jest.spyOn(console, 'log');
    invoker.doSomethingImportant();
    
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Start"));
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Finish"));
  });
  
  test('should support undo', () => {
    const invoker = new Invoker();
    const command = new SimpleCommand("test");
    invoker.setOnStart(command);
    
    const consoleSpy = jest.spyOn(console, 'log');
    invoker.doSomethingImportant();
    invoker.undoLast();
    
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("Undoing"));
  });
});
```

---

## 8. 状态模式 (State Pattern)

### 概念
允许一个对象在其内部状态改变时改变它的行为，对象看起来好像修改了它的类。

### TypeScript 实现

```typescript
// 状态接口
interface State {
  handle1(): void;
  handle2(): void;
}

// 上下文
class Context {
  private state: State;
  
  constructor(state: State) {
    this.transitionTo(state);
  }
  
  public transitionTo(state: State): void {
    console.log(`Context: Transition to ${(<any>state).constructor.name}.`);
    this.state = state;
    (<any>this.state).setContext(this);
  }
  
  public request1(): void {
    this.state.handle1();
  }
  
  public request2(): void {
    this.state.handle2();
  }
}

// 基础状态类
abstract class BaseState implements State {
  protected context: Context;
  
  public setContext(context: Context): void {
    this.context = context;
  }
  
  public abstract handle1(): void;
  public abstract handle2(): void;
}

// 具体状态A
class ConcreteStateA extends BaseState {
  public handle1(): void {
    console.log("ConcreteStateA handles request1.");
    console.log("ConcreteStateA wants to change the state of the context.");
    this.context.transitionTo(new ConcreteStateB());
  }
  
  public handle2(): void {
    console.log("ConcreteStateA handles request2.");
  }
}

// 具体状态B
class ConcreteStateB extends BaseState {
  public handle1(): void {
    console.log("ConcreteStateB handles request1.");
  }
  
  public handle2(): void {
    console.log("ConcreteStateB handles request2.");
    console.log("ConcreteStateB wants to change the state of the context.");
    this.context.transitionTo(new ConcreteStateA());
  }
}

// 实际示例：订单状态
interface OrderState {
  cancel(): void;
  confirm(): void;
  ship(): void;
  getStatus(): string;
}

class OrderContext {
  private state: OrderState;
  
  constructor(state: OrderState) {
    this.setState(state);
  }
  
  public setState(state: OrderState): void {
    this.state = state;
  }
  
  public cancel(): void {
    this.state.cancel();
  }
  
  public confirm(): void {
    this.state.confirm();
  }
  
  public ship(): void {
    this.state.ship();
  }
  
  public getStatus(): string {
    return this.state.getStatus();
  }
}

class NewOrderState implements OrderState {
  private context: OrderContext;
  
  constructor(context: OrderContext) {
    this.context = context;
  }
  
  public cancel(): void {
    console.log("Order cancelled");
    this.context.setState(new CancelledOrderState());
  }
  
  public confirm(): void {
    console.log("Order confirmed");
    this.context.setState(new ConfirmedOrderState(this.context));
  }
  
  public ship(): void {
    console.log("Cannot ship - order not confirmed");
  }
  
  public getStatus(): string {
    return "New";
  }
}

class ConfirmedOrderState implements OrderState {
  private context: OrderContext;
  
  constructor(context: OrderContext) {
    this.context = context;
  }
  
  public cancel(): void {
    console.log("Order cancelled");
    this.context.setState(new CancelledOrderState());
  }
  
  public confirm(): void {
    console.log("Order already confirmed");
  }
  
  public ship(): void {
    console.log("Order shipped");
    this.context.setState(new ShippedOrderState());
  }
  
  public getStatus(): string {
    return "Confirmed";
  }
}

class ShippedOrderState implements OrderState {
  public cancel(): void {
    console.log("Cannot cancel shipped order");
  }
  
  public confirm(): void {
    console.log("Order already confirmed");
  }
  
  public ship(): void {
    console.log("Order already shipped");
  }
  
  public getStatus(): string {
    return "Shipped";
  }
}

class CancelledOrderState implements OrderState {
  public cancel(): void {
    console.log("Order already cancelled");
  }
  
  public confirm(): void {
    console.log("Cannot confirm cancelled order");
  }
  
  public ship(): void {
    console.log("Cannot ship cancelled order");
  }
  
  public getStatus(): string {
    return "Cancelled";
  }
}
```

### 使用示例

```typescript
console.log("=== Basic State Pattern ===");
const context = new Context(new ConcreteStateA());
context.request1(); // 处理并切换到状态B
context.request2(); // 处理并切换回状态A

console.log("\n=== Order State Example ===");
const order = new OrderContext(null!);
order.setState(new NewOrderState(order));

console.log(`Status: ${order.getStatus()}`); // New
order.confirm();
console.log(`Status: ${order.getStatus()}`); // Confirmed
order.ship();
console.log(`Status: ${order.getStatus()}`); // Shipped
```

### 测试代码

```typescript
describe('State Pattern', () => {
  test('should transition between states', () => {
    const context = new Context(new ConcreteStateA());
    const consoleSpy = jest.spyOn(console, 'log');
    
    context.request1();
    expect(consoleSpy).toHaveBeenCalledWith("ConcreteStateA handles request1.");
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("ConcreteStateB"));
  });
  
  test('order should start as new', () => {
    const order = new OrderContext(null!);
    order.setState(new NewOrderState(order));
    expect(order.getStatus()).toBe("New");
  });
  
  test('new order can be confirmed', () => {
    const order = new OrderContext(null!);
    order.setState(new NewOrderState(order));
    
    const consoleSpy = jest.spyOn(console, 'log');
    order.confirm();
    
    expect(consoleSpy).toHaveBeenCalledWith("Order confirmed");
    expect(order.getStatus()).toBe("Confirmed");
  });
  
  test('new order cannot be shipped', () => {
    const order = new OrderContext(null!);
    order.setState(new NewOrderState(order));
    
    const consoleSpy = jest.spyOn(console, 'log');
    order.ship();
    
    expect(consoleSpy).toHaveBeenCalledWith("Cannot ship - order not confirmed");
    expect(order.getStatus()).toBe("New");
  });
  
  test('confirmed order can be shipped', () => {
    const order = new OrderContext(null!);
    order.setState(new NewOrderState(order));
    order.confirm();
    
    const consoleSpy = jest.spyOn(console, 'log');
    order.ship();
    
    expect(consoleSpy).toHaveBeenCalledWith("Order shipped");
    expect(order.getStatus()).toBe("Shipped");
  });
});
```

---

## 9. 中介者模式 (Mediator Pattern)

### 概念
用一个中介对象来封装一系列的对象交互，中介者使各对象不需要显式地相互引用，从而使其耦合松散，而且可以独立地改变它们之间的交互。

### TypeScript 实现

```typescript
// 中介者接口
interface Mediator {
  notify(sender: object, event: string): void;
}

// 具体中介者
class ConcreteMediator implements Mediator {
  private component1: Component1;
  private component2: Component2;
  
  constructor(c1: Component1, c2: Component2) {
    this.component1 = c1;
    this.component1.setMediator(this);
    this.component2 = c2;
    this.component2.setMediator(this);
  }
  
  public notify(sender: object, event: string): void {
    if (event === "A") {
      console.log("Mediator reacts on A and triggers following operations:");
      this.component2.doC();
    }
    
    if (event === "D") {
      console.log("Mediator reacts on D and triggers following operations:");
      this.component1.doB();
      this.component2.doC();
    }
  }
}

// 基础组件
class BaseComponent {
  protected mediator: Mediator;
  
  constructor(mediator: Mediator = null!) {
    this.mediator = mediator;
  }
  
  public setMediator(mediator: Mediator): void {
    this.mediator = mediator;
  }
}

// 组件1
class Component1 extends BaseComponent {
  public doA(): void {
    console.log("Component 1 does A.");
    this.mediator.notify(this, "A");
  }
  
  public doB(): void {
    console.log("Component 1 does B.");
    this.mediator.notify(this, "B");
  }
}

// 组件2
class Component2 extends BaseComponent {
  public doC(): void {
    console.log("Component 2 does C.");
    this.mediator.notify(this, "C");
  }
  
  public doD(): void {
    console.log("Component 2 does D.");
    this.mediator.notify(this, "D");
  }
}

// 聊天室示例
interface ChatMediator {
  sendMessage(message: string, user: User): void;
  addUser(user: User): void;
}

class ChatRoom implements ChatMediator {
  private users: User[] = [];
  
  public addUser(user: User): void {
    this.users.push(user);
  }
  
  public sendMessage(message: string, sender: User): void {
    for (const user of this.users) {
      // 不发送给自己
      if (user !== sender) {
        user.receive(message, sender.getName());
      }
    }
  }
}

class User {
  constructor(private name: string, private mediator: ChatMediator) {
    this.mediator.addUser(this);
  }
  
  public getName(): string {
    return this.name;
  }
  
  public send(message: string): void {
    console.log(`${this.name} sends: ${message}`);
    this.mediator.sendMessage(message, this);
  }
  
  public receive(message: string, from: string): void {
    console.log(`${this.name} received from ${from}: ${message}`);
  }
}
```

### 使用示例

```typescript
console.log("=== Basic Mediator ===");
const c1 = new Component1();
const c2 = new Component2();
const mediator = new ConcreteMediator(c1, c2);

c1.doA(); // 触发中介者，进而调用 c2.doC()

console.log("\n=== Chat Room ===");
const chatRoom = new ChatRoom();
const alice = new User("Alice", chatRoom);
const bob = new User("Bob", chatRoom);
const charlie = new User("Charlie", chatRoom);

alice.send("Hi everyone!");
```

### 测试代码

```typescript
describe('Mediator Pattern', () => {
  test('mediator should coordinate components', () => {
    const c1 = new Component1();
    const c2 = new Component2();
    const mediator = new ConcreteMediator(c1, c2);
    
    const consoleSpy = jest.spyOn(console, 'log');
    c1.doA();
    
    expect(consoleSpy).toHaveBeenCalledWith("Component 1 does A.");
    expect(consoleSpy).toHaveBeenCalledWith("Component 2 does C.");
  });
  
  test('chat room should broadcast messages', () => {
    const chatRoom = new ChatRoom();
    const alice = new User("Alice", chatRoom);
    const bob = new User("Bob", chatRoom);
    
    const consoleSpy = jest.spyOn(console, 'log');
    alice.send("Hello!");
    
    expect(consoleSpy).toHaveBeenCalledWith("Alice sends: Hello!");
    expect(consoleSpy).toHaveBeenCalledWith("Bob received from Alice: Hello!");
  });
  
  test('user should not receive own messages', () => {
    const chatRoom = new ChatRoom();
    const alice = new User("Alice", chatRoom);
    
    const consoleSpy = jest.spyOn(console, 'log');
    alice.send("Hello!");
    
    // Alice should send but not receive
    expect(consoleSpy).toHaveBeenCalledWith("Alice sends: Hello!");
    expect(consoleSpy).not.toHaveBeenCalledWith(expect.stringContaining("Alice received"));
  });
});
```

---

## 10. 责任链模式 (Chain of Responsibility Pattern)

### 概念
使多个对象都有机会处理请求，从而避免请求的发送者和接收者之间的耦合关系。将这些对象连成一条链，并沿着这条链传递该请求，直到有一个对象处理它为止。

### TypeScript 实现

```typescript
// 处理者接口
interface Handler {
  setNext(handler: Handler): Handler;
  handle(request: string): string | null;
}

// 抽象处理者
abstract class AbstractHandler implements Handler {
  private nextHandler: Handler | null = null;
  
  public setNext(handler: Handler): Handler {
    this.nextHandler = handler;
    return handler; // 返回handler以便链式调用
  }
  
  public handle(request: string): string | null {
    if (this.nextHandler) {
      return this.nextHandler.handle(request);
    }
    return null;
  }
}

// 具体处理者
class MonkeyHandler extends AbstractHandler {
  public handle(request: string): string | null {
    if (request === "Banana") {
      return `Monkey: I'll eat the ${request}.`;
    }
    return super.handle(request);
  }
}

class SquirrelHandler extends AbstractHandler {
  public handle(request: string): string | null {
    if (request === "Nut") {
      return `Squirrel: I'll eat the ${request}.`;
    }
    return super.handle(request);
  }
}

class DogHandler extends AbstractHandler {
  public handle(request: string): string | null {
    if (request === "MeatBall") {
      return `Dog: I'll eat the ${request}.`;
    }
    return super.handle(request);
  }
}

// 实际示例：中间件链
interface Middleware {
  setNext(middleware: Middleware): Middleware;
  handle(request: { user?: string; token?: string; role?: string }): boolean;
}

abstract class BaseMiddleware implements Middleware {
  private nextMiddleware: Middleware | null = null;
  
  public setNext(middleware: Middleware): Middleware {
    this.nextMiddleware = middleware;
    return middleware;
  }
  
  public handle(request: { user?: string; token?: string; role?: string }): boolean {
    if (this.nextMiddleware) {
      return this.nextMiddleware.handle(request);
    }
    return true;
  }
}

class AuthMiddleware extends BaseMiddleware {
  public handle(request: { user?: string; token?: string; role?: string }): boolean {
    if (!request.token) {
      console.log("Auth: No token provided");
      return false;
    }
    console.log("Auth: Token validated");
    return super.handle(request);
  }
}

class RoleMiddleware extends BaseMiddleware {
  private allowedRoles: string[];
  
  constructor(allowedRoles: string[]) {
    super();
    this.allowedRoles = allowedRoles;
  }
  
  public handle(request: { user?: string; token?: string; role?: string }): boolean {
    if (!request.role || !this.allowedRoles.includes(request.role)) {
      console.log("Role: Access denied");
      return false;
    }
    console.log("Role: Access granted");
    return super.handle(request);
  }
}

class LoggingMiddleware extends BaseMiddleware {
  public handle(request: { user?: string; token?: string; role?: string }): boolean {
    console.log(`Logging: User ${request.user} made a request`);
    return super.handle(request);
  }
}
```

### 使用示例

```typescript
console.log("=== Basic Chain ===");
const monkey = new MonkeyHandler();
const squirrel = new SquirrelHandler();
const dog = new DogHandler();

monkey.setNext(squirrel).setNext(dog);

console.log(monkey.handle("Nut"));     // Squirrel handles
console.log(monkey.handle("Banana"));  // Monkey handles
console.log(monkey.handle("MeatBall"));// Dog handles
console.log(monkey.handle("Coffee"));  // No one handles

console.log("\n=== Middleware Chain ===");
const auth = new AuthMiddleware();
const role = new RoleMiddleware(["admin", "editor"]);
const logging = new LoggingMiddleware();

auth.setNext(role).setNext(logging);

const validRequest = { user: "John", token: "abc123", role: "admin" };
const invalidRequest = { user: "Jane", role: "viewer" };

console.log("\nValid request:");
auth.handle(validRequest);

console.log("\nInvalid request:");
auth.handle(invalidRequest);
```

### 测试代码

```typescript
describe('Chain of Responsibility Pattern', () => {
  test('monkey should handle banana', () => {
    const monkey = new MonkeyHandler();
    expect(monkey.handle("Banana")).toBe("Monkey: I'll eat the Banana.");
  });
  
  test('squirrel should handle nut', () => {
    const squirrel = new SquirrelHandler();
    expect(squirrel.handle("Nut")).toBe("Squirrel: I'll eat the Nut.");
  });
  
  test('chain should pass request to next handler', () => {
    const monkey = new MonkeyHandler();
    const squirrel = new SquirrelHandler();
    monkey.setNext(squirrel);
    
    expect(monkey.handle("Nut")).toBe("Squirrel: I'll eat the Nut.");
  });
  
  test('chain should return null if no handler', () => {
    const monkey = new MonkeyHandler();
    expect(monkey.handle("Coffee")).toBeNull();
  });
  
  test('middleware should validate token', () => {
    const auth = new AuthMiddleware();
    const consoleSpy = jest.spyOn(console, 'log');
    
    const result = auth.handle({ token: "valid" });
    expect(result).toBe(true);
    expect(consoleSpy).toHaveBeenCalledWith("Auth: Token validated");
  });
  
  test('middleware should reject missing token', () => {
    const auth = new AuthMiddleware();
    const consoleSpy = jest.spyOn(console, 'log');
    
    const result = auth.handle({});
    expect(result).toBe(false);
    expect(consoleSpy).toHaveBeenCalledWith("Auth: No token provided");
  });
  
  test('middleware chain should work together', () => {
    const auth = new AuthMiddleware();
    const role = new RoleMiddleware(["admin"]);
    auth.setNext(role);
    
    const consoleSpy = jest.spyOn(console, 'log');
    
    // Valid request
    const validResult = auth.handle({ token: "abc", role: "admin" });
    expect(validResult).toBe(true);
    
    // Invalid role
    const invalidResult = auth.handle({ token: "abc", role: "user" });
    expect(invalidResult).toBe(false);
    expect(consoleSpy).toHaveBeenCalledWith("Role: Access denied");
  });
});
```

---

## 运行测试

要运行所有测试，需要安装 Jest:

```bash
npm install --save-dev jest @types/jest ts-jest typescript
```

创建 `jest.config.js`:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
};
```

运行测试:

```bash
npx jest typescript_patterns.test.ts
```

---

## 总结

| 模式 | 用途 | 优点 |
|------|------|------|
| 单例模式 | 确保只有一个实例 | 控制实例数量，全局访问 |
| 工厂模式 | 创建对象 | 解耦创建和使用 |
| 观察者模式 | 事件通知 | 一对多依赖管理 |
| 策略模式 | 算法选择 | 运行时切换算法 |
| 装饰器模式 | 动态添加功能 | 比继承更灵活 |
| 代理模式 | 控制对象访问 | 延迟加载、权限控制 |
| 命令模式 | 封装请求 | 支持撤销、队列 |
| 状态模式 | 状态管理 | 状态转换清晰 |
| 中介者模式 | 对象交互 | 降低耦合 |
| 责任链模式 | 请求处理 | 解耦发送者和接收者 |
