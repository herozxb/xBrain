# State Pattern in TypeScript

## Overview

The State Pattern allows an object to alter its behavior when its internal state changes. The object will appear to change its class. This pattern is ideal for implementing finite state machines and managing complex state-dependent behavior.

## Core Implementation

### Basic State Machine

```typescript
// State interface
interface State {
    handle(context: Context): void;
    getName(): string;
}

// Context class
class Context {
    private state: State;
    private data: Map<string, any> = new Map();
    
    constructor(initialState: State) {
        this.state = initialState;
    }
    
    setState(state: State): void {
        console.log(`State changed: ${this.state.getName()} → ${state.getName()}`);
        this.state = state;
    }
    
    getState(): State {
        return this.state;
    }
    
    request(): void {
        this.state.handle(this);
    }
    
    setData(key: string, value: any): void {
        this.data.set(key, value);
    }
    
    getData<T>(key: string): T | undefined {
        return this.data.get(key);
    }
}
```

### Document Approval Workflow

```typescript
interface DocumentState extends State {
    submit(): void;
    approve(): void;
    reject(): void;
    review(): void;
}

class Document {
    private state: DocumentState;
    private content: string;
    private author: string;
    private reviewer: string | null = null;
    
    constructor(author: string, content: string) {
        this.author = author;
        this.content = content;
        this.state = new DraftState();
    }
    
    private setState(state: DocumentState): void {
        console.log(`[${this.state.getName()}] → [${state.getName()}]`);
        this.state = state;
    }
    
    submit(): void {
        try {
            this.state.submit();
            this.setState(new SubmittedState());
        } catch (error) {
            console.log(`Cannot submit: ${(error as Error).message}`);
        }
    }
    
    approve(): void {
        try {
            this.state.approve();
            this.setState(new ApprovedState());
        } catch (error) {
            console.log(`Cannot approve: ${(error as Error).message}`);
        }
    }
    
    reject(): void {
        try {
            this.state.reject();
            this.setState(new RejectedState());
        } catch (error) {
            console.log(`Cannot reject: ${(error as Error).message}`);
        }
    }
    
    review(): void {
        try {
            this.state.review();
            this.setState(new UnderReviewState());
        } catch (error) {
            console.log(`Cannot review: ${(error as Error).message}`);
        }
    }
    
    getAuthor(): string {
        return this.author;
    }
    
    setReviewer(reviewer: string): void {
        this.reviewer = reviewer;
    }
}

class DraftState implements DocumentState {
    getName(): string {
        return "Draft";
    }
    
    handle(context: Context): void {
        console.log("Document is in draft state");
    }
    
    submit(): void {
        console.log("Submitting document for review");
    }
    
    approve(): void {
        throw new Error("Cannot approve a draft");
    }
    
    reject(): void {
        throw new Error("Cannot reject a draft");
    }
    
    review(): void {
        throw new Error("Cannot review without submission");
    }
}

class SubmittedState implements DocumentState {
    getName(): string {
        return "Submitted";
    }
    
    handle(context: Context): void {
        console.log("Document has been submitted");
    }
    
    submit(): void {
        throw new Error("Already submitted");
    }
    
    approve(): void {
        throw new Error("Must be reviewed first");
    }
    
    reject(): void {
        throw new Error("Must be reviewed first");
    }
    
    review(): void {
        console.log("Starting review process");
    }
}

class UnderReviewState implements DocumentState {
    getName(): string {
        return "Under Review";
    }
    
    handle(context: Context): void {
        console.log("Document is being reviewed");
    }
    
    submit(): void {
        throw new Error("Already submitted");
    }
    
    approve(): void {
        console.log("Document approved");
    }
    
    reject(): void {
        console.log("Document rejected");
    }
    
    review(): void {
        throw new Error("Already under review");
    }
}

class ApprovedState implements DocumentState {
    getName(): string {
        return "Approved";
    }
    
    handle(context: Context): void {
        console.log("Document is approved");
    }
    
    submit(): void {
        throw new Error("Already approved");
    }
    
    approve(): void {
        throw new Error("Already approved");
    }
    
    reject(): void {
        console.log("Reopening document for review");
    }
    
    review(): void {
        throw new Error("Cannot review approved document");
    }
}

class RejectedState implements DocumentState {
    getName(): string {
        return "Rejected";
    }
    
    handle(context: Context): void {
        console.log("Document was rejected");
    }
    
    submit(): void {
        console.log("Resubmitting document");
    }
    
    approve(): void {
        throw new Error("Cannot approve rejected document");
    }
    
    reject(): void {
        throw new Error("Already rejected");
    }
    
    review(): void {
        throw new Error("Cannot review rejected document");
    }
}
```

## Advanced Patterns

### TCP Connection State Machine

```typescript
interface TCPState extends State {
    open(context: TCPConnection): void;
    close(context: TCPConnection): void;
    acknowledge(context: TCPConnection): void;
    sendData(context: TCPConnection, data: string): void;
}

class TCPConnection {
    private state: TCPState;
    private buffer: string[] = [];
    
    constructor() {
        this.state = new TCPClosedState();
    }
    
    private changeState(state: TCPState): void {
        this.state = state;
    }
    
    open(): void {
        this.state.open(this);
    }
    
    close(): void {
        this.state.close(this);
    }
    
    acknowledge(): void {
        this.state.acknowledge(this);
    }
    
    send(data: string): void {
        this.state.sendData(this, data);
    }
    
    addToBuffer(data: string): void {
        this.buffer.push(data);
    }
    
    flushBuffer(): string[] {
        const data = [...this.buffer];
        this.buffer = [];
        return data;
    }
}

class TCPClosedState implements TCPState {
    getName(): string {
        return "CLOSED";
    }
    
    handle(context: Context): void {
        console.log("Connection is closed");
    }
    
    open(context: TCPConnection): void {
        console.log("Opening connection... sending SYN");
        context.changeState(new TCPListenState());
    }
    
    close(context: TCPConnection): void {
        console.log("Already closed");
    }
    
    acknowledge(context: TCPConnection): void {
        console.log("Cannot acknowledge: connection closed");
    }
    
    sendData(context: TCPConnection, data: string): void {
        console.log("Cannot send: connection closed");
    }
}

class TCPListenState implements TCPState {
    getName(): string {
        return "LISTEN";
    }
    
    handle(context: Context): void {
        console.log("Waiting for connection");
    }
    
    open(context: TCPConnection): void {
        console.log("Already listening");
    }
    
    close(context: TCPConnection): void {
        console.log("Closing listener");
        context.changeState(new TCPClosedState());
    }
    
    acknowledge(context: TCPConnection): void {
        console.log("SYN received, sending SYN-ACK");
        context.changeState(new TCPEstablishedState());
    }
    
    sendData(context: TCPConnection, data: string): void {
        console.log("Cannot send: connection not established");
    }
}

class TCPEstablishedState implements TCPState {
    getName(): string {
        return "ESTABLISHED";
    }
    
    handle(context: Context): void {
        console.log("Connection is active");
    }
    
    open(context: TCPConnection): void {
        console.log("Connection already open");
    }
    
    close(context: TCPConnection): void {
        console.log("Sending FIN, closing connection");
        context.changeState(new TCPFinWaitState());
    }
    
    acknowledge(context: TCPConnection): void {
        console.log("ACK received");
    }
    
    sendData(context: TCPConnection, data: string): void {
        console.log(`Sending: ${data}`);
        context.addToBuffer(data);
    }
}

class TCPFinWaitState implements TCPState {
    getName(): string {
        return "FIN_WAIT";
    }
    
    handle(context: Context): void {
        console.log("Waiting for FIN-ACK");
    }
    
    open(context: TCPConnection): void {
        console.log("Cannot open: closing in progress");
    }
    
    close(context: TCPConnection): void {
        console.log("Already closing");
    }
    
    acknowledge(context: TCPConnection): void {
        console.log("FIN-ACK received, connection closed");
        context.changeState(new TCPClosedState());
    }
    
    sendData(context: TCPConnection, data: string): void {
        console.log("Cannot send: connection closing");
    }
}
```

### Vending Machine State

```typescript
interface VendingState extends State {
    insertCoin(amount: number): void;
    selectProduct(productId: string): void;
    dispense(): void;
    cancel(): void;
}

class VendingMachine {
    private state: VendingState;
    private balance: number = 0;
    private selectedProduct: string | null = null;
    private products: Map<string, { price: number; stock: number }> = new Map();
    
    constructor() {
        this.state = new IdleState();
        this.initializeProducts();
    }
    
    private initializeProducts(): void {
        this.products.set("A1", { price: 150, stock: 5 });
        this.products.set("A2", { price: 200, stock: 3 });
        this.products.set("B1", { price: 100, stock: 10 });
    }
    
    private setState(state: VendingState): void {
        this.state = state;
    }
    
    insertCoin(amount: number): void {
        this.state.insertCoin(amount);
    }
    
    selectProduct(productId: string): void {
        this.state.selectProduct(productId);
    }
    
    dispense(): void {
        this.state.dispense();
    }
    
    cancel(): void {
        this.state.cancel();
    }
    
    addBalance(amount: number): void {
        this.balance += amount;
        console.log(`Balance: $${(this.balance / 100).toFixed(2)}`);
    }
    
    refund(): number {
        const refund = this.balance;
        this.balance = 0;
        return refund;
    }
    
    getProductPrice(productId: string): number | undefined {
        return this.products.get(productId)?.price;
    }
    
    hasEnoughBalance(productId: string): boolean {
        const product = this.products.get(productId);
        return product ? this.balance >= product.price : false;
    }
    
    setSelectedProduct(productId: string): void {
        this.selectedProduct = productId;
    }
    
    dispenseProduct(): boolean {
        if (!this.selectedProduct) return false;
        
        const product = this.products.get(this.selectedProduct);
        if (!product || product.stock === 0) return false;
        
        product.stock--;
        this.balance -= product.price;
        console.log(`Dispensed: ${this.selectedProduct}`);
        
        if (this.balance > 0) {
            console.log(`Change: $${(this.balance / 100).toFixed(2)}`);
            this.balance = 0;
        }
        
        this.selectedProduct = null;
        return true;
    }
}

class IdleState implements VendingState {
    getName(): string {
        return "IDLE";
    }
    
    handle(context: Context): void {
        console.log("Vending machine is ready");
    }
    
    insertCoin(amount: number): void {
        console.log(`Inserting $${(amount / 100).toFixed(2)}`);
        // Transition to HasMoneyState
    }
    
    selectProduct(productId: string): void {
        console.log("Please insert coins first");
    }
    
    dispense(): void {
        console.log("No product selected");
    }
    
    cancel(): void {
        console.log("Nothing to cancel");
    }
}

class HasMoneyState implements VendingState {
    getName(): string {
        return "HAS_MONEY";
    }
    
    handle(context: Context): void {
        console.log("Customer has inserted money");
    }
    
    insertCoin(amount: number): void {
        console.log(`Adding $${(amount / 100).toFixed(2)}`);
    }
    
    selectProduct(productId: string): void {
        console.log(`Selecting product: ${productId}`);
        // Transition to ProductSelectedState
    }
    
    dispense(): void {
        console.log("Please select a product first");
    }
    
    cancel(): void {
        console.log("Cancelling transaction, returning money");
        // Transition to IdleState
    }
}

class ProductSelectedState implements VendingState {
    getName(): string {
        return "PRODUCT_SELECTED";
    }
    
    handle(context: Context): void {
        console.log("Product selected, ready to dispense");
    }
    
    insertCoin(amount: number): void {
        console.log("Cannot insert more coins after selection");
    }
    
    selectProduct(productId: string): void {
        console.log("Product already selected");
    }
    
    dispense(): void {
        console.log("Dispensing product...");
        // Transition to DispensingState
    }
    
    cancel(): void {
        console.log("Cancelling selection");
        // Transition to HasMoneyState
    }
}

class DispensingState implements VendingState {
    getName(): string {
        return "DISPENSING";
    }
    
    handle(context: Context): void {
        console.log("Product is being dispensed");
    }
    
    insertCoin(amount: number): void {
        console.log("Please wait for current transaction");
    }
    
    selectProduct(productId: string): void {
        console.log("Please wait for current transaction");
    }
    
    dispense(): void {
        console.log("Already dispensing");
    }
    
    cancel(): void {
        console.log("Cannot cancel during dispense");
    }
}
```

## Benefits

1. **Clean Code**: Eliminates complex conditional statements
2. **Open/Closed Principle**: Easy to add new states
3. **Single Responsibility**: Each state in its own class
4. **State Transitions**: Explicit state change logic
5. **Testability**: States can be tested independently
6. **Maintainability**: Clear separation of concerns

## When to Use

- Object behavior depends on its state
- Complex conditional logic based on state
- State transitions are well-defined
- Need to add new states without modifying existing code
- Implementing state machines or workflows
- Game development (character states, game states)

## Best Practices

1. Keep states immutable when possible
2. Use state factories for complex initialization
3. Consider state persistence for long-running processes
4. Log state transitions for debugging
5. Implement state validation
6. Use state machines for complex workflows
