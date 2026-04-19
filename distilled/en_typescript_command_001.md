# Command Pattern in TypeScript

## Overview

The Command Pattern encapsulates a request as an object, thereby allowing for parameterization of clients with different requests, queuing of requests, and logging of operations. It decouples the object that invokes the operation from the one that knows how to perform it.

## Core Implementation

### Basic Command Structure

```typescript
// Command interface
interface Command {
    execute(): void;
    undo(): void;
    getDescription(): string;
}

// Receiver - knows how to perform the operations
class Light {
    private isOn: boolean = false;
    private location: string;
    
    constructor(location: string) {
        this.location = location;
    }
    
    turnOn(): void {
        this.isOn = true;
        console.log(`${this.location} light is ON`);
    }
    
    turnOff(): void {
        this.isOn = false;
        console.log(`${this.location} light is OFF`);
    }
    
    getState(): boolean {
        return this.isOn;
    }
}

// Concrete Command
class LightOnCommand implements Command {
    private light: Light;
    
    constructor(light: Light) {
        this.light = light;
    }
    
    execute(): void {
        this.light.turnOn();
    }
    
    undo(): void {
        this.light.turnOff();
    }
    
    getDescription(): string {
        return "Turn light ON";
    }
}

class LightOffCommand implements Command {
    private light: Light;
    
    constructor(light: Light) {
        this.light = light;
    }
    
    execute(): void {
        this.light.turnOff();
    }
    
    undo(): void {
        this.light.turnOn();
    }
    
    getDescription(): string {
        return "Turn light OFF";
    }
}
```

### Invoker - Remote Control

```typescript
class RemoteControl {
    private commands: Map<string, Command> = new Map();
    private undoStack: Command[] = [];
    private maxUndoLevel: number = 10;
    
    setCommand(slot: string, command: Command): void {
        this.commands.set(slot, command);
    }
    
    pressButton(slot: string): void {
        const command = this.commands.get(slot);
        if (command) {
            command.execute();
            this.addToUndoStack(command);
        } else {
            console.log(`No command assigned to slot: ${slot}`);
        }
    }
    
    undoLast(): void {
        const command = this.undoStack.pop();
        if (command) {
            command.undo();
        } else {
            console.log("Nothing to undo");
        }
    }
    
    private addToUndoStack(command: Command): void {
        this.undoStack.push(command);
        if (this.undoStack.length > this.maxUndoLevel) {
            this.undoStack.shift();
        }
    }
    
    showHistory(): void {
        console.log("\nCommand History:");
        this.undoStack.forEach((cmd, index) => {
            console.log(`${index + 1}. ${cmd.getDescription()}`);
        });
    }
}
```

## Advanced Patterns

### Macro Command (Composite)

```typescript
class MacroCommand implements Command {
    private commands: Command[] = [];
    private name: string;
    
    constructor(name: string) {
        this.name = name;
    }
    
    addCommand(command: Command): void {
        this.commands.push(command);
    }
    
    removeCommand(command: Command): void {
        const index = this.commands.indexOf(command);
        if (index > -1) {
            this.commands.splice(index, 1);
        }
    }
    
    execute(): void {
        console.log(`\nExecuting Macro: ${this.name}`);
        this.commands.forEach(cmd => cmd.execute());
    }
    
    undo(): void {
        console.log(`\nUndoing Macro: ${this.name}`);
        // Undo in reverse order
        [...this.commands].reverse().forEach(cmd => cmd.undo());
    }
    
    getDescription(): string {
        return `Macro: ${this.name} (${this.commands.length} commands)`;
    }
}
```

### Command with State Tracking

```typescript
interface CommandWithResult<T> extends Command {
    getResult(): T;
}

class Thermostat {
    private temperature: number = 20;
    
    setTemperature(temp: number): void {
        console.log(`Setting temperature to ${temp}°C`);
        this.temperature = temp;
    }
    
    getTemperature(): number {
        return this.temperature;
    }
}

class SetTemperatureCommand implements CommandWithResult<number> {
    private thermostat: Thermostat;
    private newTemp: number;
    private previousTemp: number | null = null;
    
    constructor(thermostat: Thermostat, temperature: number) {
        this.thermostat = thermostat;
        this.newTemp = temperature;
    }
    
    execute(): void {
        this.previousTemp = this.thermostat.getTemperature();
        this.thermostat.setTemperature(this.newTemp);
    }
    
    undo(): void {
        if (this.previousTemp !== null) {
            this.thermostat.setTemperature(this.previousTemp);
        }
    }
    
    getDescription(): string {
        return `Set temperature to ${this.newTemp}°C`;
    }
    
    getResult(): number {
        return this.thermostat.getTemperature();
    }
}
```

### Async Command Execution

```typescript
interface AsyncCommand {
    execute(): Promise<void>;
    undo(): Promise<void>;
    getDescription(): string;
}

class AsyncCommandQueue {
    private queue: AsyncCommand[] = [];
    private isProcessing: boolean = false;
    private processed: AsyncCommand[] = [];
    
    async enqueue(command: AsyncCommand): Promise<void> {
        this.queue.push(command);
        if (!this.isProcessing) {
            await this.processQueue();
        }
    }
    
    private async processQueue(): Promise<void> {
        this.isProcessing = true;
        
        while (this.queue.length > 0) {
            const command = this.queue.shift()!;
            console.log(`Executing: ${command.getDescription()}`);
            
            try {
                await command.execute();
                this.processed.push(command);
            } catch (error) {
                console.error(`Failed: ${command.getDescription()}`, error);
                // Continue with next command
            }
        }
        
        this.isProcessing = false;
    }
    
    async undoAll(): Promise<void> {
        while (this.processed.length > 0) {
            const command = this.processed.pop()!;
            await command.undo();
        }
    }
}

// Example async command
class DatabaseBackupCommand implements AsyncCommand {
    private dbName: string;
    
    constructor(dbName: string) {
        this.dbName = dbName;
    }
    
    async execute(): Promise<void> {
        console.log(`Starting backup of ${this.dbName}...`);
        await this.delay(1000); // Simulate backup
        console.log(`Backup of ${this.dbName} completed`);
    }
    
    async undo(): Promise<void> {
        console.log(`Restoring ${this.dbName} from backup...`);
        await this.delay(500);
        console.log(`Restore completed`);
    }
    
    getDescription(): string {
        return `Backup database: ${this.dbName}`;
    }
    
    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

## Practical Use Cases

### Text Editor with Undo/Redo

```typescript
class TextEditor {
    private content: string = "";
    private cursorPosition: number = 0;
    
    getText(): string {
        return this.content;
    }
    
    getCursorPosition(): number {
        return this.cursorPosition;
    }
    
    insertText(text: string, position: number): void {
        this.content = 
            this.content.slice(0, position) + 
            text + 
            this.content.slice(position);
        this.cursorPosition = position + text.length;
    }
    
    deleteText(start: number, end: number): string {
        const deleted = this.content.slice(start, end);
        this.content = this.content.slice(0, start) + this.content.slice(end);
        this.cursorPosition = start;
        return deleted;
    }
}

class InsertTextCommand implements Command {
    private editor: TextEditor;
    private text: string;
    private position: number;
    
    constructor(editor: TextEditor, text: string, position: number) {
        this.editor = editor;
        this.text = text;
        this.position = position;
    }
    
    execute(): void {
        this.editor.insertText(this.text, this.position);
    }
    
    undo(): void {
        this.editor.deleteText(
            this.position, 
            this.position + this.text.length
        );
    }
    
    getDescription(): string {
        return `Insert "${this.text}" at position ${this.position}`;
    }
}

class EditorInvoker {
    private undoStack: Command[] = [];
    private redoStack: Command[] = [];
    
    executeCommand(command: Command): void {
        command.execute();
        this.undoStack.push(command);
        this.redoStack = []; // Clear redo stack on new command
    }
    
    undo(): void {
        const command = this.undoStack.pop();
        if (command) {
            command.undo();
            this.redoStack.push(command);
        }
    }
    
    redo(): void {
        const command = this.redoStack.pop();
        if (command) {
            command.execute();
            this.undoStack.push(command);
        }
    }
}
```

## Benefits

1. **Decoupling**: Separates invoker from receiver
2. **Undo/Redo**: Easy to implement reversal operations
3. **Composable**: Commands can be combined into macros
4. **Queueable**: Commands can be scheduled and executed later
5. **Loggable**: Operations can be logged for audit trails
6. **Testable**: Each command is independently testable

## When to Use

- Need to parameterize objects with operations
- Need to queue, schedule, or execute operations at different times
- Need to support undo/redo functionality
- Need to log changes for recovery
- Need to support transactions with rollback
- Building systems with callbacks or event handling

## Best Practices

1. Keep commands focused on a single operation
2. Implement undo carefully to restore previous state
3. Consider using command pools for frequently used commands
4. Store command history for debugging and audit
5. Use macro commands for complex workflows
6. Consider async commands for I/O operations
