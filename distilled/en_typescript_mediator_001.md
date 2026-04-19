# Mediator Pattern in TypeScript

## Overview

The Mediator Pattern defines an object that encapsulates how a set of objects interact. It promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently.

## Core Implementation

### Basic Mediator Structure

```typescript
// Mediator interface
interface Mediator {
    notify(sender: object, event: string): void;
    register(component: Colleague): void;
}

// Colleague interface
abstract class Colleague {
    protected mediator: Mediator;
    
    constructor(mediator: Mediator) {
        this.mediator = mediator;
    }
    
    abstract send(event: string): void;
    abstract receive(event: string): void;
}
```

### Chat Room Example

```typescript
interface ChatMediator extends Mediator {
    sendMessage(user: User, message: string): void;
    sendPrivateMessage(from: User, to: User, message: string): void;
    broadcast(message: string): void;
    addUser(user: User): void;
    removeUser(user: User): void;
}

class User {
    private name: string;
    private mediator: ChatMediator;
    private messages: Array<{ from: string; message: string; timestamp: Date }> = [];
    
    constructor(name: string, mediator: ChatMediator) {
        this.name = name;
        this.mediator = mediator;
        this.mediator.addUser(this);
    }
    
    send(message: string): void {
        console.log(`\n${this.name} sends: "${message}"`);
        this.mediator.sendMessage(this, message);
    }
    
    sendPrivate(recipient: User, message: string): void {
        console.log(`\n${this.name} sends private to ${recipient.name}: "${message}"`);
        this.mediator.sendPrivateMessage(this, recipient, message);
    }
    
    receive(from: string, message: string): void {
        const msg = {
            from,
            message,
            timestamp: new Date()
        };
        this.messages.push(msg);
        console.log(`${this.name} received from ${from}: "${message}"`);
    }
    
    getMessages(): Array<{ from: string; message: string; timestamp: Date }> {
        return this.messages;
    }
    
    getName(): string {
        return this.name;
    }
}

class ChatRoom implements ChatMediator {
    private users: Map<string, User> = new Map();
    private messageLog: Array<{ from: string; to: string; message: string; timestamp: Date }> = [];
    
    addUser(user: User): void {
        this.users.set(user.getName(), user);
        console.log(`${user.getName()} joined the chat`);
    }
    
    removeUser(user: User): void {
        this.users.delete(user.getName());
        console.log(`${user.getName()} left the chat`);
    }
    
    sendMessage(sender: User, message: string): void {
        this.users.forEach((user, name) => {
            if (name !== sender.getName()) {
                user.receive(sender.getName(), message);
            }
        });
        
        this.logMessage(sender.getName(), 'all', message);
    }
    
    sendPrivateMessage(from: User, to: User, message: string): void {
        to.receive(from.getName(), message);
        this.logMessage(from.getName(), to.getName(), message);
    }
    
    broadcast(message: string): void {
        this.users.forEach(user => {
            user.receive('System', message);
        });
        this.logMessage('System', 'all', message);
    }
    
    notify(sender: object, event: string): void {
        console.log(`Event: ${event} from ${sender.constructor.name}`);
    }
    
    register(component: Colleague): void {
        // Register colleague
    }
    
    private logMessage(from: string, to: string, message: string): void {
        this.messageLog.push({
            from,
            to,
            message,
            timestamp: new Date()
        });
    }
    
    getMessageLog(): Array<{ from: string; to: string; message: string; timestamp: Date }> {
        return this.messageLog;
    }
}
```

## Advanced Patterns

### Air Traffic Control System

```typescript
interface AircraftMediator extends Mediator {
    requestTakeoff(aircraft: Aircraft): boolean;
    requestLanding(aircraft: Aircraft): boolean;
    reportPosition(aircraft: Aircraft, position: Position): void;
    declareEmergency(aircraft: Aircraft): void;
}

interface Position {
    lat: number;
    lon: number;
    altitude: number;
}

class Aircraft {
    private id: string;
    private type: string;
    private position: Position;
    private mediator: AircraftMediator;
    private status: 'grounded' | 'taxiing' | 'airborne' | 'landing' = 'grounded';
    
    constructor(id: string, type: string, mediator: AircraftMediator) {
        this.id = id;
        this.type = type;
        this.mediator = mediator;
        this.position = { lat: 0, lon: 0, altitude: 0 };
    }
    
    requestTakeoff(): void {
        console.log(`\n${this.id}: Requesting takeoff clearance`);
        if (this.mediator.requestTakeoff(this)) {
            this.status = 'airborne';
            console.log(`${this.id}: Takeoff approved, now airborne`);
        } else {
            console.log(`${this.id}: Takeoff denied, must wait`);
        }
    }
    
    requestLanding(): void {
        console.log(`\n${this.id}: Requesting landing clearance`);
        if (this.mediator.requestLanding(this)) {
            this.status = 'landing';
            console.log(`${this.id}: Landing approved`);
        } else {
            console.log(`${this.id}: Landing denied, holding pattern`);
        }
    }
    
    updatePosition(position: Position): void {
        this.position = position;
        this.mediator.reportPosition(this, position);
    }
    
    declareEmergency(): void {
        console.log(`\n${this.id}: MAYDAY MAYDAY MAYDAY`);
        this.mediator.declareEmergency(this);
    }
    
    getId(): string {
        return this.id;
    }
    
    getType(): string {
        return this.type;
    }
    
    getStatus(): string {
        return this.status;
    }
    
    setPosition(pos: Position): void {
        this.position = pos;
    }
}

class AirTrafficControl implements AircraftMediator {
    private runways: Map<number, { occupied: boolean; aircraft?: Aircraft }> = new Map();
    private aircraftRegistry: Map<string, Aircraft> = new Map();
    private emergencies: Set<string> = new Set();
    
    constructor() {
        // Initialize 2 runways
        this.runways.set(1, { occupied: false });
        this.runways.set(2, { occupied: false });
    }
    
    requestTakeoff(aircraft: Aircraft): boolean {
        // Priority to emergency aircraft
        if (this.emergencies.size > 0 && !this.emergencies.has(aircraft.getId())) {
            return false;
        }
        
        // Find available runway
        for (const [runwayNum, runway] of this.runways) {
            if (!runway.occupied) {
                runway.occupied = true;
                runway.aircraft = aircraft;
                console.log(`ATC: ${aircraft.getId()} cleared for takeoff on runway ${runwayNum}`);
                return true;
            }
        }
        
        return false;
    }
    
    requestLanding(aircraft: Aircraft): boolean {
        // Emergency aircraft gets priority
        if (this.emergencies.has(aircraft.getId())) {
            for (const [runwayNum, runway] of this.runways) {
                if (runway.occupied && !this.emergencies.has(runway.aircraft?.getId() || '')) {
                    console.log(`ATC: ${runway.aircraft?.getId()} vacate runway immediately, emergency landing`);
                }
                runway.occupied = true;
                runway.aircraft = aircraft;
                console.log(`ATC: ${aircraft.getId()} EMERGENCY landing on runway ${runwayNum}`);
                return true;
            }
        }
        
        // Normal landing request
        for (const [runwayNum, runway] of this.runways) {
            if (!runway.occupied) {
                runway.occupied = true;
                runway.aircraft = aircraft;
                console.log(`ATC: ${aircraft.getId()} cleared to land on runway ${runwayNum}`);
                return true;
            }
        }
        
        return false;
    }
    
    reportPosition(aircraft: Aircraft, position: Position): void {
        this.aircraftRegistry.set(aircraft.getId(), aircraft);
        // In real system, would check for conflicts
    }
    
    declareEmergency(aircraft: Aircraft): void {
        this.emergencies.add(aircraft.getId());
        console.log(`ATC: Emergency declared by ${aircraft.getId()}. All aircraft give way.`);
        
        // Clear all runways for emergency
        this.runways.forEach((runway, num) => {
            if (runway.occupied && runway.aircraft?.getId() !== aircraft.getId()) {
                console.log(`ATC: ${runway.aircraft?.getId()} abort takeoff, emergency in progress`);
            }
        });
    }
    
    notify(sender: object, event: string): void {
        console.log(`ATC Event: ${event}`);
    }
    
    register(component: Colleague): void {
        // Register aircraft
    }
    
    clearRunway(runwayNum: number): void {
        const runway = this.runways.get(runwayNum);
        if (runway) {
            console.log(`ATC: Runway ${runwayNum} cleared`);
            runway.occupied = false;
            runway.aircraft = undefined;
        }
    }
}
```

### UI Dialog Coordinator

```typescript
interface DialogMediator extends Mediator {
    onButtonClick(button: string): void;
    onTextChange(field: string, value: string): void;
    onCheckboxChange(checkbox: string, checked: boolean): void;
    validateForm(): boolean;
    submitForm(): void;
}

abstract class UIControl {
    protected mediator: DialogMediator;
    protected enabled: boolean = true;
    
    constructor(mediator: DialogMediator) {
        this.mediator = mediator;
    }
    
    enable(): void {
        this.enabled = true;
    }
    
    disable(): void {
        this.enabled = false;
    }
    
    isEnabled(): boolean {
        return this.enabled;
    }
}

class Button extends UIControl {
    private label: string;
    private id: string;
    
    constructor(id: string, label: string, mediator: DialogMediator) {
        super(mediator);
        this.id = id;
        this.label = label;
    }
    
    click(): void {
        if (this.enabled) {
            this.mediator.onButtonClick(this.id);
        }
    }
    
    getLabel(): string {
        return this.label;
    }
}

class TextBox extends UIControl {
    private id: string;
    private value: string = '';
    private placeholder: string;
    
    constructor(id: string, placeholder: string, mediator: DialogMediator) {
        super(mediator);
        this.id = id;
        this.placeholder = placeholder;
    }
    
    setValue(value: string): void {
        this.value = value;
        this.mediator.onTextChange(this.id, value);
    }
    
    getValue(): string {
        return this.value;
    }
    
    clear(): void {
        this.value = '';
    }
}

class Checkbox extends UIControl {
    private id: string;
    private checked: boolean = false;
    private label: string;
    
    constructor(id: string, label: string, mediator: DialogMediator) {
        super(mediator);
        this.id = id;
        this.label = label;
    }
    
    toggle(): void {
        this.checked = !this.checked;
        this.mediator.onCheckboxChange(this.id, this.checked);
    }
    
    isChecked(): boolean {
        return this.checked;
    }
    
    setChecked(checked: boolean): void {
        this.checked = checked;
    }
}

class RegistrationDialog implements DialogMediator {
    private usernameTextBox: TextBox;
    private emailTextBox: TextBox;
    private passwordTextBox: TextBox;
    private confirmPasswordTextBox: TextBox;
    private termsCheckbox: Checkbox;
    private submitButton: Button;
    private cancelButton: Button;
    
    constructor() {
        this.usernameTextBox = new TextBox('username', 'Enter username', this);
        this.emailTextBox = new TextBox('email', 'Enter email', this);
        this.passwordTextBox = new TextBox('password', 'Enter password', this);
        this.confirmPasswordTextBox = new TextBox('confirmPassword', 'Confirm password', this);
        this.termsCheckbox = new Checkbox('terms', 'I agree to terms', this);
        this.submitButton = new Button('submit', 'Register', this);
        this.cancelButton = new Button('cancel', 'Cancel', this);
        
        this.submitButton.disable(); // Initially disabled
    }
    
    onButtonClick(button: string): void {
        switch (button) {
            case 'submit':
                this.submitForm();
                break;
            case 'cancel':
                this.resetForm();
                break;
        }
    }
    
    onTextChange(field: string, value: string): void {
        console.log(`${field} changed: ${value}`);
        this.validateForm();
    }
    
    onCheckboxChange(checkbox: string, checked: boolean): void {
        console.log(`${checkbox} ${checked ? 'checked' : 'unchecked'}`);
        this.validateForm();
    }
    
    validateForm(): boolean {
        const username = this.usernameTextBox.getValue();
        const email = this.emailTextBox.getValue();
        const password = this.passwordTextBox.getValue();
        const confirmPassword = this.confirmPasswordTextBox.getValue();
        const termsAccepted = this.termsCheckbox.isChecked();
        
        const isValid = 
            username.length >= 3 &&
            email.includes('@') &&
            password.length >= 8 &&
            password === confirmPassword &&
            termsAccepted;
        
        if (isValid) {
            this.submitButton.enable();
        } else {
            this.submitButton.disable();
        }
        
        return isValid;
    }
    
    submitForm(): void {
        if (this.validateForm()) {
            const formData = {
                username: this.usernameTextBox.getValue(),
                email: this.emailTextBox.getValue(),
                password: this.passwordTextBox.getValue()
            };
            
            console.log('Form submitted:', formData);
            // API call would go here
        }
    }
    
    notify(sender: object, event: string): void {
        console.log(`Dialog event: ${event}`);
    }
    
    register(component: Colleague): void {
        // Register UI component
    }
    
    private resetForm(): void {
        this.usernameTextBox.clear();
        this.emailTextBox.clear();
        this.passwordTextBox.clear();
        this.confirmPasswordTextBox.clear();
        this.termsCheckbox.setChecked(false);
        this.submitButton.disable();
    }
}
```

### Stock Exchange Mediator

```typescript
interface StockMediator extends Mediator {
    placeBuyOrder(trader: Trader, symbol: string, quantity: number, price: number): void;
    placeSellOrder(trader: Trader, symbol: string, quantity: number, price: number): void;
    getStockPrice(symbol: string): number;
}

interface Order {
    trader: Trader;
    symbol: string;
    quantity: number;
    price: number;
    timestamp: Date;
}

class Trader {
    private id: string;
    private name: string;
    private mediator: StockMediator;
    private portfolio: Map<string, number> = new Map();
    private balance: number = 100000; // Starting balance
    
    constructor(id: string, name: string, mediator: StockMediator) {
        this.id = id;
        this.name = name;
        this.mediator = mediator;
    }
    
    buy(symbol: string, quantity: number, maxPrice: number): void {
        const currentPrice = this.mediator.getStockPrice(symbol);
        if (currentPrice <= maxPrice && this.balance >= currentPrice * quantity) {
            console.log(`\n${this.name} buying ${quantity} ${symbol} @ $${maxPrice}`);
            this.mediator.placeBuyOrder(this, symbol, quantity, maxPrice);
        } else {
            console.log(`${this.name}: Cannot buy ${symbol} - insufficient funds or price too high`);
        }
    }
    
    sell(symbol: string, quantity: number, minPrice: number): void {
        const held = this.portfolio.get(symbol) || 0;
        if (held >= quantity) {
            console.log(`\n${this.name} selling ${quantity} ${symbol} @ $${minPrice}`);
            this.mediator.placeSellOrder(this, symbol, quantity, minPrice);
        } else {
            console.log(`${this.name}: Cannot sell ${symbol} - insufficient holdings`);
        }
    }
    
    receiveBuyConfirmation(symbol: string, quantity: number, price: number): void {
        this.balance -= price * quantity;
        const current = this.portfolio.get(symbol) || 0;
        this.portfolio.set(symbol, current + quantity);
        console.log(`${this.name} bought ${quantity} ${symbol} @ $${price}`);
        console.log(`${this.name} balance: $${this.balance.toFixed(2)}`);
    }
    
    receiveSellConfirmation(symbol: string, quantity: number, price: number): void {
        this.balance += price * quantity;
        const current = this.portfolio.get(symbol) || 0;
        this.portfolio.set(symbol, current - quantity);
        console.log(`${this.name} sold ${quantity} ${symbol} @ $${price}`);
        console.log(`${this.name} balance: $${this.balance.toFixed(2)}`);
    }
    
    getId(): string {
        return this.id;
    }
    
    getName(): string {
        return this.name;
    }
}

class StockExchange implements StockMediator {
    private buyOrders: Map<string, Order[]> = new Map();
    private sellOrders: Map<string, Order[]> = new Map();
    private stockPrices: Map<string, number> = new Map();
    
    constructor() {
        // Initialize stock prices
        this.stockPrices.set('AAPL', 175);
        this.stockPrices.set('GOOGL', 140);
        this.stockPrices.set('MSFT', 380);
    }
    
    placeBuyOrder(trader: Trader, symbol: string, quantity: number, price: number): void {
        const order: Order = {
            trader,
            symbol,
            quantity,
            price,
            timestamp: new Date()
        };
        
        // Try to match with existing sell orders
        const sellOrders = this.sellOrders.get(symbol) || [];
        let remainingQty = quantity;
        
        for (let i = sellOrders.length - 1; i >= 0; i--) {
            const sellOrder = sellOrders[i];
            
            if (sellOrder.price <= price) {
                const matchedQty = Math.min(remainingQty, sellOrder.quantity);
                const matchedPrice = (price + sellOrder.price) / 2;
                
                // Execute trade
                trader.receiveBuyConfirmation(symbol, matchedQty, matchedPrice);
                sellOrder.trader.receiveSellConfirmation(symbol, matchedQty, matchedPrice);
                
                remainingQty -= matchedQty;
                sellOrder.quantity -= matchedQty;
                
                if (sellOrder.quantity === 0) {
                    sellOrders.splice(i, 1);
                }
                
                this.updateStockPrice(symbol, matchedPrice);
            }
        }
        
        // Add remaining to buy order book
        if (remainingQty > 0) {
            order.quantity = remainingQty;
            const orders = this.buyOrders.get(symbol) || [];
            orders.push(order);
            this.buyOrders.set(symbol, orders);
        }
    }
    
    placeSellOrder(trader: Trader, symbol: string, quantity: number, price: number): void {
        const order: Order = {
            trader,
            symbol,
            quantity,
            price,
            timestamp: new Date()
        };
        
        // Try to match with existing buy orders
        const buyOrders = this.buyOrders.get(symbol) || [];
        let remainingQty = quantity;
        
        for (let i = buyOrders.length - 1; i >= 0; i--) {
            const buyOrder = buyOrders[i];
            
            if (buyOrder.price >= price) {
                const matchedQty = Math.min(remainingQty, buyOrder.quantity);
                const matchedPrice = (price + buyOrder.price) / 2;
                
                // Execute trade
                trader.receiveSellConfirmation(symbol, matchedQty, matchedPrice);
                buyOrder.trader.receiveBuyConfirmation(symbol, matchedQty, matchedPrice);
                
                remainingQty -= matchedQty;
                buyOrder.quantity -= matchedQty;
                
                if (buyOrder.quantity === 0) {
                    buyOrders.splice(i, 1);
                }
                
                this.updateStockPrice(symbol, matchedPrice);
            }
        }
        
        // Add remaining to sell order book
        if (remainingQty > 0) {
            order.quantity = remainingQty;
            const orders = this.sellOrders.get(symbol) || [];
            orders.push(order);
            this.sellOrders.set(symbol, orders);
        }
    }
    
    getStockPrice(symbol: string): number {
        return this.stockPrices.get(symbol) || 0;
    }
    
    notify(sender: object, event: string): void {
        console.log(`Exchange event: ${event}`);
    }
    
    register(component: Colleague): void {
        // Register trader
    }
    
    private updateStockPrice(symbol: string, price: number): void {
        this.stockPrices.set(symbol, price);
    }
}
```

## Benefits

1. **Decoupling**: Reduces direct connections between components
2. **Simplified Communication**: Central point for coordination
3. **Reusability**: Components can be reused in different contexts
4. **Maintainability**: Changes to interaction logic in one place
5. **Testability**: Easier to test mediator logic independently

## When to Use

- Set of objects communicate in complex ways
- Reusing an object is difficult because it references other objects
- Behavior distributed across several classes should be customizable
- Many-to-many relationships between objects
- Complex coordination logic
- UI frameworks with many interdependent components

## Best Practices

1. Keep mediator focused on coordination, not business logic
2. Use clear interfaces for colleagues
3. Avoid making mediator a "god object"
4. Consider event-driven architecture for complex scenarios
5. Document communication protocols
6. Use type safety for events and messages
