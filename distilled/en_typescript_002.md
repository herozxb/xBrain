# TypeScript Design Patterns - Part 2

## Pattern: Command Pattern

### Implementation

```typescript
// Command Interface
interface Command {
    execute(): void;
    undo(): void;
}

// Receiver - knows how to perform the operations
class TextEditor {
    private content: string = "";
    private history: string[] = [];

    write(text: string): void {
        this.history.push(this.content);
        this.content += text;
    }

    delete(length: number): void {
        this.history.push(this.content);
        this.content = this.content.slice(0, -length);
    }

    restore(state: string): void {
        this.content = state;
    }

    getContent(): string {
        return this.content;
    }

    getLastState(): string {
        return this.history[this.history.length - 1] || "";
    }
}

// Concrete Commands
class WriteCommand implements Command {
    private editor: TextEditor;
    private text: string;

    constructor(editor: TextEditor, text: string) {
        this.editor = editor;
        this.text = text;
    }

    execute(): void {
        this.editor.write(this.text);
    }

    undo(): void {
        this.editor.restore(this.editor.getLastState());
    }
}

class DeleteCommand implements Command {
    private editor: TextEditor;
    private length: number;
    private deletedText: string = "";

    constructor(editor: TextEditor, length: number) {
        this.editor = editor;
        this.length = length;
    }

    execute(): void {
        const content = this.editor.getContent();
        this.deletedText = content.slice(-this.length);
        this.editor.delete(this.length);
    }

    undo(): void {
        this.editor.write(this.deletedText);
    }
}

// Invoker
class EditorInvoker {
    private commands: Command[] = [];
    private undoneCommands: Command[] = [];

    executeCommand(command: Command): void {
        command.execute();
        this.commands.push(command);
        this.undoneCommands = [];
    }

    undo(): void {
        const command = this.commands.pop();
        if (command) {
            command.undo();
            this.undoneCommands.push(command);
        }
    }

    redo(): void {
        const command = this.undoneCommands.pop();
        if (command) {
            command.execute();
            this.commands.push(command);
        }
    }
}
```

### Usage

```typescript
const editor = new TextEditor();
const invoker = new EditorInvoker();

// Execute commands
invoker.executeCommand(new WriteCommand(editor, "Hello "));
invoker.executeCommand(new WriteCommand(editor, "World!"));
console.log(editor.getContent()); // "Hello World!"

// Undo last command
invoker.undo();
console.log(editor.getContent()); // "Hello "

// Redo
invoker.redo();
console.log(editor.getContent()); // "Hello World!"

// Delete command
invoker.executeCommand(new DeleteCommand(editor, 6));
console.log(editor.getContent()); // "Hello"

// Undo delete
invoker.undo();
console.log(editor.getContent()); // "Hello World!"
```

---

## Pattern: State Pattern

### Implementation

```typescript
// State Interface
interface TrafficLightState {
    handle(context: TrafficLight): void;
    getColor(): string;
}

// Concrete States
class RedLight implements TrafficLightState {
    handle(context: TrafficLight): void {
        console.log("Red light - STOP! Waiting for green...");
        context.setState(new GreenLight());
    }

    getColor(): string {
        return "RED";
    }
}

class GreenLight implements TrafficLightState {
    handle(context: TrafficLight): void {
        console.log("Green light - GO! Waiting for yellow...");
        context.setState(new YellowLight());
    }

    getColor(): string {
        return "GREEN";
    }
}

class YellowLight implements TrafficLightState {
    handle(context: TrafficLight): void {
        console.log("Yellow light - CAUTION! Preparing to stop...");
        context.setState(new RedLight());
    }

    getColor(): string {
        return "YELLOW";
    }
}

// Context
class TrafficLight {
    private state: TrafficLightState;

    constructor(initialState: TrafficLightState) {
        this.state = initialState;
    }

    setState(state: TrafficLightState): void {
        this.state = state;
    }

    change(): void {
        this.state.handle(this);
    }

    getCurrentColor(): string {
        return this.state.getColor();
    }
}

// Alternative: Vending Machine Example
interface VendingMachineState {
    insertMoney(amount: number): void;
    selectProduct(product: string): void;
    dispense(): void;
}

class NoMoneyState implements VendingMachineState {
    private machine: VendingMachine;

    constructor(machine: VendingMachine) {
        this.machine = machine;
    }

    insertMoney(amount: number): void {
        console.log(`Inserted $${amount}`);
        this.machine.setState(this.machine.getHasMoneyState());
    }

    selectProduct(product: string): void {
        console.log("Please insert money first");
    }

    dispense(): void {
        console.log("Please insert money first");
    }
}

class HasMoneyState implements VendingMachineState {
    private machine: VendingMachine;

    constructor(machine: VendingMachine) {
        this.machine = machine;
    }

    insertMoney(amount: number): void {
        console.log(`Added $${amount} more`);
    }

    selectProduct(product: string): void {
        console.log(`Selected: ${product}`);
        this.machine.setState(this.machine.getSoldState());
    }

    dispense(): void {
        console.log("Please select a product first");
    }
}

class SoldState implements VendingMachineState {
    private machine: VendingMachine;

    constructor(machine: VendingMachine) {
        this.machine = machine;
    }

    insertMoney(amount: number): void {
        console.log("Please wait, dispensing...");
    }

    selectProduct(product: string): void {
        console.log("Please wait, dispensing...");
    }

    dispense(): void {
        console.log("Product dispensed! Thank you!");
        this.machine.setState(this.machine.getNoMoneyState());
    }
}

class VendingMachine {
    private state: VendingMachineState;
    private noMoneyState: VendingMachineState;
    private hasMoneyState: VendingMachineState;
    private soldState: VendingMachineState;

    constructor() {
        this.noMoneyState = new NoMoneyState(this);
        this.hasMoneyState = new HasMoneyState(this);
        this.soldState = new SoldState(this);
        this.state = this.noMoneyState;
    }

    setState(state: VendingMachineState): void {
        this.state = state;
    }

    getNoMoneyState(): VendingMachineState { return this.noMoneyState; }
    getHasMoneyState(): VendingMachineState { return this.hasMoneyState; }
    getSoldState(): VendingMachineState { return this.soldState; }

    insertMoney(amount: number): void {
        this.state.insertMoney(amount);
    }

    selectProduct(product: string): void {
        this.state.selectProduct(product);
    }

    dispense(): void {
        this.state.dispense();
    }
}
```

### Usage

```typescript
// Traffic Light
const trafficLight = new TrafficLight(new RedLight());

console.log(`Current: ${trafficLight.getCurrentColor()}`); // RED
trafficLight.change(); // Red -> Green
console.log(`Current: ${trafficLight.getCurrentColor()}`); // GREEN

// Vending Machine
const vendingMachine = new VendingMachine();

vendingMachine.selectProduct("Soda"); // "Please insert money first"
vendingMachine.insertMoney(2);        // "Inserted $2"
vendingMachine.selectProduct("Soda"); // "Selected: Soda"
vendingMachine.dispense();            // "Product dispensed! Thank you!"
```

---

## Pattern: Mediator Pattern

### Implementation

```typescript
// Mediator Interface
interface ChatMediator {
    sendMessage(message: string, user: User): void;
    addUser(user: User): void;
}

// Colleague Interface
abstract class User {
    protected mediator: ChatMediator;
    protected name: string;

    constructor(mediator: ChatMediator, name: string) {
        this.mediator = mediator;
        this.name = name;
    }

    abstract send(message: string): void;
    abstract receive(message: string): void;

    getName(): string {
        return this.name;
    }
}

// Concrete Mediator
class ChatRoom implements ChatMediator {
    private users: User[] = [];

    addUser(user: User): void {
        this.users.push(user);
        console.log(`${user.getName()} joined the chat`);
    }

    sendMessage(message: string, sender: User): void {
        for (const user of this.users) {
            // Don't send message to the sender
            if (user !== sender) {
                user.receive(message);
            }
        }
    }
}

// Concrete Colleague
class ChatUser extends User {
    send(message: string): void {
        console.log(`${this.name} sends: ${message}`);
        this.mediator.sendMessage(message, this);
    }

    receive(message: string): void {
        console.log(`${this.name} received: ${message}`);
    }
}

// Air Traffic Control Example
interface AirTrafficControl {
    requestLanding(aircraft: Aircraft): void;
    requestTakeoff(aircraft: Aircraft): void;
    notifyRunwayAvailable(): void;
}

abstract class Aircraft {
    protected atc: AirTrafficControl;
    protected flightNumber: string;

    constructor(atc: AirTrafficControl, flightNumber: string) {
        this.atc = atc;
        this.flightNumber = flightNumber;
    }

    getFlightNumber(): string {
        return this.flightNumber;
    }

    abstract requestLanding(): void;
    abstract requestTakeoff(): void;
    abstract land(): void;
    abstract takeoff(): void;
}

class Airplane extends Aircraft {
    requestLanding(): void {
        console.log(`${this.flightNumber}: Requesting landing clearance`);
        this.atc.requestLanding(this);
    }

    requestTakeoff(): void {
        console.log(`${this.flightNumber}: Requesting takeoff clearance`);
        this.atc.requestTakeoff(this);
    }

    land(): void {
        console.log(`${this.flightNumber}: Landing now`);
    }

    takeoff(): void {
        console.log(`${this.flightNumber}: Taking off now`);
    }
}

class ControlTower implements AirTrafficControl {
    private runwayAvailable: boolean = true;
    private landingQueue: Aircraft[] = [];
    private takeoffQueue: Aircraft[] = [];

    requestLanding(aircraft: Aircraft): void {
        if (this.runwayAvailable) {
            this.runwayAvailable = false;
            console.log(`ATC: ${aircraft.getFlightNumber()}, cleared to land`);
            aircraft.land();
            setTimeout(() => this.notifyRunwayAvailable(), 100);
        } else {
            console.log(`ATC: ${aircraft.getFlightNumber()}, hold position`);
            this.landingQueue.push(aircraft);
        }
    }

    requestTakeoff(aircraft: Aircraft): void {
        if (this.runwayAvailable) {
            this.runwayAvailable = false;
            console.log(`ATC: ${aircraft.getFlightNumber()}, cleared for takeoff`);
            aircraft.takeoff();
            setTimeout(() => this.notifyRunwayAvailable(), 100);
        } else {
            console.log(`ATC: ${aircraft.getFlightNumber()}, hold short`);
            this.takeoffQueue.push(aircraft);
        }
    }

    notifyRunwayAvailable(): void {
        this.runwayAvailable = true;
        console.log("ATC: Runway now available");

        if (this.landingQueue.length > 0) {
            const next = this.landingQueue.shift()!;
            this.requestLanding(next);
        } else if (this.takeoffQueue.length > 0) {
            const next = this.takeoffQueue.shift()!;
            this.requestTakeoff(next);
        }
    }
}
```

### Usage

```typescript
// Chat Room
const chatRoom = new ChatRoom();

const alice = new ChatUser(chatRoom, "Alice");
const bob = new ChatUser(chatRoom, "Bob");
const charlie = new ChatUser(chatRoom, "Charlie");

chatRoom.addUser(alice);
chatRoom.addUser(bob);
chatRoom.addUser(charlie);

alice.send("Hi everyone!");
// Output:
// Alice sends: Hi everyone!
// Bob received: Hi everyone!
// Charlie received: Hi everyone!

// Air Traffic Control
const tower = new ControlTower();

const flight1 = new Airplane(tower, "AA123");
const flight2 = new Airplane(tower, "UA456");

flight1.requestLanding(); // Cleared to land
flight2.requestLanding(); // Hold position (queued)
```

---

## Pattern: Chain of Responsibility

### Implementation

```typescript
// Handler Interface
interface Handler {
    setNext(handler: Handler): Handler;
    handle(request: string): string | null;
}

// Abstract Handler
abstract class AbstractHandler implements Handler {
    private nextHandler: Handler | null = null;

    setNext(handler: Handler): Handler {
        this.nextHandler = handler;
        return handler;
    }

    getNext(): Handler | null {
        return this.nextHandler;
    }

    abstract handle(request: string): string | null;
}

// Concrete Handlers
class AuthHandler extends AbstractHandler {
    handle(request: string): string | null {
        if (request === "auth") {
            return "AuthHandler: Processing authentication";
        }
        return this.getNext()?.handle(request) || null;
    }
}

class LogHandler extends AbstractHandler {
    handle(request: string): string | null {
        if (request === "log") {
            return "LogHandler: Processing logs";
        }
        return this.getNext()?.handle(request) || null;
    }
}

class CacheHandler extends AbstractHandler {
    handle(request: string): string | null {
        if (request === "cache") {
            return "CacheHandler: Processing cache";
        }
        return this.getNext()?.handle(request) || null;
    }
}

// Purchase Approval Example
interface PurchaseApprover {
    setSuccessor(successor: PurchaseApprover): PurchaseApprover;
    approveRequest(amount: number): string;
}

abstract class AbstractApprover implements PurchaseApprover {
    protected successor: PurchaseApprover | null = null;
    protected name: string;
    protected limit: number;

    constructor(name: string, limit: number) {
        this.name = name;
        this.limit = limit;
    }

    setSuccessor(successor: PurchaseApprover): PurchaseApprover {
        this.successor = successor;
        return successor;
    }

    approveRequest(amount: number): string {
        if (amount <= this.limit) {
            return `${this.name} approved $${amount}`;
        } else if (this.successor) {
            return this.successor.approveRequest(amount);
        }
        return `Purchase of $${amount} requires executive approval`;
    }
}

class Manager extends AbstractApprover {
    constructor() {
        super("Manager", 1000);
    }
}

class Director extends AbstractApprover {
    constructor() {
        super("Director", 10000);
    }
}

class VicePresident extends AbstractApprover {
    constructor() {
        super("VP", 100000);
    }
}

// Middleware Example (Express-like)
type Middleware = (req: any, res: any, next: () => void) => void;

class MiddlewareChain {
    private middlewares: Middleware[] = [];
    private index: number = 0;

    use(middleware: Middleware): this {
        this.middlewares.push(middleware);
        return this;
    }

    handle(req: any, res: any): void {
        this.index = 0;
        this.next(req, res);
    }

    private next = (req: any, res: any): void => {
        if (this.index < this.middlewares.length) {
            const middleware = this.middlewares[this.index++];
            middleware(req, res, () => this.next(req, res));
        }
    };
}
```

### Usage

```typescript
// Basic Chain
const auth = new AuthHandler();
const log = new LogHandler();
const cache = new CacheHandler();

auth.setNext(log).setNext(cache);

console.log(auth.handle("auth"));   // "AuthHandler: Processing authentication"
console.log(auth.handle("log"));    // "LogHandler: Processing logs"
console.log(auth.handle("cache"));  // "CacheHandler: Processing cache"

// Purchase Approval Chain
const manager = new Manager();
const director = new Director();
const vp = new VicePresident();

manager.setSuccessor(director).setSuccessor(vp);

console.log(manager.approveRequest(500));    // "Manager approved $500"
console.log(manager.approveRequest(5000));   // "Director approved $5000"
console.log(manager.approveRequest(50000));  // "VP approved $50000"
console.log(manager.approveRequest(500000)); // "Purchase of $500000 requires executive approval"

// Middleware Chain
const chain = new MiddlewareChain();

chain
    .use((req, res, next) => {
        console.log("1. Logger");
        next();
    })
    .use((req, res, next) => {
        console.log("2. Auth check");
        req.user = { id: 1, name: "John" };
        next();
    })
    .use((req, res, next) => {
        console.log("3. Handler");
        res.data = `Hello, ${req.user.name}`;
    });

chain.handle({}, { data: "" });
// Output: 1. Logger, 2. Auth check, 3. Handler
```

---

## Pattern: Memento Pattern

### Implementation

```typescript
// Memento - stores the internal state
class EditorMemento {
    private readonly content: string;
    private readonly cursorPosition: number;
    private readonly timestamp: Date;

    constructor(content: string, cursorPosition: number) {
        this.content = content;
        this.cursorPosition = cursorPosition;
        this.timestamp = new Date();
    }

    getContent(): string {
        return this.content;
    }

    getCursorPosition(): number {
        return this.cursorPosition;
    }

    getTimestamp(): Date {
        return this.timestamp;
    }
}

// Originator - creates and restores from memento
class TextEditor {
    private content: string = "";
    private cursorPosition: number = 0;

    type(text: string): void {
        this.content = this.content.slice(0, this.cursorPosition) + 
                       text + 
                       this.content.slice(this.cursorPosition);
        this.cursorPosition += text.length;
    }

    delete(length: number): void {
        const start = Math.max(0, this.cursorPosition - length);
        this.content = this.content.slice(0, start) + this.content.slice(this.cursorPosition);
        this.cursorPosition = start;
    }

    moveCursor(position: number): void {
        this.cursorPosition = Math.max(0, Math.min(position, this.content.length));
    }

    getContent(): string {
        return this.content;
    }

    getCursorPosition(): number {
        return this.cursorPosition;
    }

    // Create memento
    save(): EditorMemento {
        return new EditorMemento(this.content, this.cursorPosition);
    }

    // Restore from memento
    restore(memento: EditorMemento): void {
        this.content = memento.getContent();
        this.cursorPosition = memento.getCursorPosition();
    }
}

// Caretaker - manages mementos
class EditorHistory {
    private history: EditorMemento[] = [];
    private maxSize: number;

    constructor(maxSize: number = 10) {
        this.maxSize = maxSize;
    }

    push(memento: EditorMemento): void {
        if (this.history.length >= this.maxSize) {
            this.history.shift();
        }
        this.history.push(memento);
    }

    pop(): EditorMemento | null {
        return this.history.pop() || null;
    }

    peek(): EditorMemento | null {
        return this.history[this.history.length - 1] || null;
    }

    size(): number {
        return this.history.length;
    }

    getHistory(): { content: string; timestamp: Date }[] {
        return this.history.map(m => ({
            content: m.getContent(),
            timestamp: m.getTimestamp()
        }));
    }
}

// Game State Example
class GameState {
    private level: number;
    private score: number;
    private health: number;
    private position: { x: number; y: number };

    constructor() {
        this.level = 1;
        this.score = 0;
        this.health = 100;
        this.position = { x: 0, y: 0 };
    }

    play(score: number, healthLoss: number): void {
        this.score += score;
        this.health = Math.max(0, this.health - healthLoss);
    }

    move(x: number, y: number): void {
        this.position = { x, y };
    }

    levelUp(): void {
        this.level++;
        this.health = 100;
    }

    getState(): { level: number; score: number; health: number; position: { x: number; y: number } } {
        return {
            level: this.level,
            score: this.score,
            health: this.health,
            position: { ...this.position }
        };
    }

    // Memento
    save(): GameMemento {
        return new GameMemento(this.level, this.score, this.health, this.position);
    }

    restore(memento: GameMemento): void {
        const state = memento.getState();
        this.level = state.level;
        this.score = state.score;
        this.health = state.health;
        this.position = { ...state.position };
    }
}

class GameMemento {
    private readonly state: {
        level: number;
        score: number;
        health: number;
        position: { x: number; y: number };
    };

    constructor(level: number, score: number, health: number, position: { x: number; y: number }) {
        this.state = { level, score, health, position: { ...position } };
    }

    getState(): typeof this.state {
        return { ...this.state, position: { ...this.state.position } };
    }
}

class GameSaveManager {
    private saves: Map<string, GameMemento> = new Map();
    private quickSave: GameMemento | null = null;

    saveGame(name: string, memento: GameMemento): void {
        this.saves.set(name, memento);
        console.log(`Game saved to slot: ${name}`);
    }

    loadGame(name: string): GameMemento | null {
        const save = this.saves.get(name);
        if (save) {
            console.log(`Game loaded from slot: ${name}`);
        } else {
            console.log(`Save slot not found: ${name}`);
        }
        return save || null;
    }

    quickSaveGame(memento: GameMemento): void {
        this.quickSave = memento;
        console.log("Quick save created");
    }

    quickLoad(): GameMemento | null {
        if (this.quickSave) {
            console.log("Quick save loaded");
        } else {
            console.log("No quick save available");
        }
        return this.quickSave;
    }

    listSaves(): string[] {
        return Array.from(this.saves.keys());
    }
}
```

### Usage

```typescript
// Text Editor with History
const editor = new TextEditor();
const history = new EditorHistory();

// Type some text and save states
editor.type("Hello");
history.push(editor.save());

editor.type(" World");
history.push(editor.save());

editor.type("!");
history.push(editor.save());

console.log(editor.getContent()); // "Hello World!"

// Undo
const lastState = history.pop();
if (lastState) {
    editor.restore(lastState);
}
console.log(editor.getContent()); // "Hello World"

// Game State Management
const game = new GameState();
const saveManager = new GameSaveManager();

// Play and save
game.play(100, 10);
game.move(50, 50);
saveManager.saveGame("slot1", game.save());

game.play(200, 30);
game.levelUp();
saveManager.saveGame("slot2", game.save());

console.log("Current game:", game.getState());

// Load earlier save
const slot1Save = saveManager.loadGame("slot1");
if (slot1Save) {
    game.restore(slot1Save);
}
console.log("Loaded game:", game.getState());

// Quick save/load
saveManager.quickSaveGame(game.save());
game.play(500, 50);
console.log("After playing:", game.getState());

saveManager.quickLoad() && game.restore(saveManager.quickLoad()!);
console.log("After quick load:", game.getState());
```
