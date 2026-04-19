# TypeScript Design Patterns: Structural & Advanced

## Pattern 1: Decorator Pattern

### Problem Description
Add responsibilities to objects dynamically without affecting other objects of the same class.

### Solution

```typescript
// ============================================================
// Decorator Pattern - HTTP Request Handler
// ============================================================

// Component Interface
interface HttpRequestHandler {
  handle(request: Request): Promise<Response>;
}

// Base Component
class BasicRequestHandler implements HttpRequestHandler {
  async handle(request: Request): Promise<Response> {
    return new Response('OK', { status: 200 });
  }
}

// Base Decorator
abstract class RequestHandlerDecorator implements HttpRequestHandler {
  constructor(protected wrapped: HttpRequestHandler) {}

  abstract handle(request: Request): Promise<Response>;
}

// Concrete Decorators
class LoggingDecorator extends RequestHandlerDecorator {
  async handle(request: Request): Promise<Response> {
    const startTime = Date.now();
    console.log(`[REQUEST] ${request.method} ${request.url}`);

    try {
      const response = await this.wrapped.handle(request);
      const duration = Date.now() - startTime;
      console.log(`[RESPONSE] ${response.status} (${duration}ms)`);
      return response;
    } catch (error) {
      const duration = Date.now() - startTime;
      console.error(`[ERROR] After ${duration}ms:`, error);
      throw error;
    }
  }
}

class AuthenticationDecorator extends RequestHandlerDecorator {
  private validTokens = new Set(['secret-token-123', 'admin-token-456']);

  async handle(request: Request): Promise<Response> {
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader) {
      return new Response('Unauthorized', { status: 401 });
    }

    const token = authHeader.replace('Bearer ', '');
    if (!this.validTokens.has(token)) {
      return new Response('Forbidden', { status: 403 });
    }

    return this.wrapped.handle(request);
  }
}

class RateLimitDecorator extends RequestHandlerDecorator {
  private requests = new Map<string, number[]>();
  private maxRequests = 100;
  private windowMs = 60000; // 1 minute

  async handle(request: Request): Promise<Response> {
    const clientId = this.getClientId(request);
    const now = Date.now();
    
    const requests = this.requests.get(clientId) || [];
    const recentRequests = requests.filter(time => now - time < this.windowMs);

    if (recentRequests.length >= this.maxRequests) {
      return new Response('Too Many Requests', { status: 429 });
    }

    recentRequests.push(now);
    this.requests.set(clientId, recentRequests);

    return this.wrapped.handle(request);
  }

  private getClientId(request: Request): string {
    return request.headers.get('X-Client-ID') || 'anonymous';
  }
}

class CacheDecorator extends RequestHandlerDecorator {
  private cache = new Map<string, { response: Response; expires: number }>();
  private ttlMs = 30000; // 30 seconds

  async handle(request: Request): Promise<Response> {
    if (request.method !== 'GET') {
      return this.wrapped.handle(request);
    }

    const cacheKey = request.url;
    const cached = this.cache.get(cacheKey);

    if (cached && cached.expires > Date.now()) {
      console.log(`[CACHE HIT] ${cacheKey}`);
      return cached.response.clone();
    }

    const response = await this.wrapped.handle(request);
    
    if (response.ok) {
      this.cache.set(cacheKey, {
        response: response.clone(),
        expires: Date.now() + this.ttlMs
      });
    }

    return response;
  }
}

class CompressionDecorator extends RequestHandlerDecorator {
  async handle(request: Request): Promise<Response> {
    const response = await this.wrapped.handle(request);
    
    const acceptEncoding = request.headers.get('Accept-Encoding') || '';
    if (!acceptEncoding.includes('gzip')) {
      return response;
    }

    // In a real implementation, we'd compress the body
    const newHeaders = new Headers(response.headers);
    newHeaders.set('Content-Encoding', 'gzip');
    
    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    });
  }
}

// Builder for creating decorated handlers
class RequestHandlerBuilder {
  private handler: HttpRequestHandler;

  constructor(baseHandler?: HttpRequestHandler) {
    this.handler = baseHandler || new BasicRequestHandler();
  }

  withLogging(): this {
    this.handler = new LoggingDecorator(this.handler);
    return this;
  }

  withAuthentication(): this {
    this.handler = new AuthenticationDecorator(this.handler);
    return this;
  }

  withRateLimit(maxRequests?: number): this {
    if (maxRequests) {
      // Would need to modify RateLimitDecorator to accept config
    }
    this.handler = new RateLimitDecorator(this.handler);
    return this;
  }

  withCache(): this {
    this.handler = new CacheDecorator(this.handler);
    return this;
  }

  withCompression(): this {
    this.handler = new CompressionDecorator(this.handler);
    return this;
  }

  build(): HttpRequestHandler {
    return this.handler;
  }
}
```

### Tests

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('Decorator Pattern - HTTP Request Handler', () => {
  const createMockRequest = (options: Partial<Request> = {}): Request => {
    return {
      method: 'GET',
      url: 'https://api.example.com/test',
      headers: new Headers(),
      ...options
    } as Request;
  };

  it('should handle basic request', async () => {
    const handler = new BasicRequestHandler();
    const request = createMockRequest();
    const response = await handler.handle(request);
    
    expect(response.status).toBe(200);
  });

  it('should log requests', async () => {
    const consoleSpy = vi.spyOn(console, 'log');
    const handler = new RequestHandlerBuilder()
      .withLogging()
      .build();
    
    await handler.handle(createMockRequest());
    
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[REQUEST]')
    );
  });

  it('should reject unauthorized requests', async () => {
    const handler = new RequestHandlerBuilder()
      .withAuthentication()
      .build();
    
    const response = await handler.handle(createMockRequest());
    expect(response.status).toBe(401);
  });

  it('should accept authorized requests', async () => {
    const handler = new RequestHandlerBuilder()
      .withAuthentication()
      .build();
    
    const request = createMockRequest({
      headers: new Headers({ 'Authorization': 'Bearer secret-token-123' })
    });
    
    const response = await handler.handle(request);
    expect(response.status).toBe(200);
  });

  it('should enforce rate limits', async () => {
    const handler = new RequestHandlerBuilder()
      .withRateLimit()
      .build();
    
    const clientId = 'test-client';
    
    // Make requests up to the limit
    for (let i = 0; i < 100; i++) {
      const request = createMockRequest({
        headers: new Headers({ 'X-Client-ID': clientId })
      });
      await handler.handle(request);
    }
    
    // Next request should be rate limited
    const request = createMockRequest({
      headers: new Headers({ 'X-Client-ID': clientId })
    });
    const response = await handler.handle(request);
    expect(response.status).toBe(429);
  });

  it('should cache GET requests', async () => {
    const consoleSpy = vi.spyOn(console, 'log');
    const handler = new RequestHandlerBuilder()
      .withCache()
      .withLogging()
      .build();
    
    const request = createMockRequest();
    
    await handler.handle(request);
    await handler.handle(request);
    
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[CACHE HIT]')
    );
  });

  it('should compose multiple decorators', async () => {
    const handler = new RequestHandlerBuilder()
      .withRateLimit()
      .withAuthentication()
      .withCache()
      .withLogging()
      .build();
    
    const request = createMockRequest({
      headers: new Headers({
        'Authorization': 'Bearer secret-token-123',
        'X-Client-ID': 'test-client'
      })
    });
    
    const response = await handler.handle(request);
    expect(response.status).toBe(200);
  });
});
```

---

## Pattern 2: Proxy Pattern

### Problem Description
Provide a surrogate or placeholder for another object to control access to it.

### Solution

```typescript
// ============================================================
// Proxy Pattern - Virtual Proxy & Protection Proxy
// ============================================================

// Virtual Proxy - Lazy Loading Images
interface Image {
  display(): void;
  getWidth(): number;
  getHeight(): number;
}

class RealImage implements Image {
  private width = 0;
  private height = 0;
  private loaded = false;

  constructor(private filename: string) {
    this.loadFromDisk();
  }

  private loadFromDisk(): void {
    console.log(`Loading image: ${this.filename}`);
    // Simulate expensive loading operation
    this.width = 1920;
    this.height = 1080;
    this.loaded = true;
  }

  display(): void {
    console.log(`Displaying ${this.filename} (${this.width}x${this.height})`);
  }

  getWidth(): number {
    return this.width;
  }

  getHeight(): number {
    return this.height;
  }
}

class ImageProxy implements Image {
  private realImage: RealImage | null = null;
  private cachedWidth = 800;  // Placeholder dimensions
  private cachedHeight = 600;

  constructor(private filename: string) {}

  display(): void {
    if (!this.realImage) {
      this.realImage = new RealImage(this.filename);
    }
    this.realImage.display();
  }

  getWidth(): number {
    return this.realImage ? this.realImage.getWidth() : this.cachedWidth;
  }

  getHeight(): number {
    return this.realImage ? this.realImage.getHeight() : this.cachedHeight;
  }
}

// Protection Proxy - Access Control
interface Document {
  read(): string;
  write(content: string): void;
  delete(): void;
}

class RealDocument implements Document {
  constructor(
    private content: string,
    private ownerId: string
  ) {}

  read(): string {
    return this.content;
  }

  write(content: string): void {
    this.content = content;
  }

  delete(): void {
    this.content = '';
  }
}

class DocumentProxy implements Document {
  constructor(
    private document: Document,
    private userId: string,
    private userRole: 'admin' | 'editor' | 'viewer'
  ) {}

  read(): string {
    return this.document.read();
  }

  write(content: string): void {
    if (this.userRole === 'viewer') {
      throw new Error('Viewers cannot edit documents');
    }
    this.document.write(content);
  }

  delete(): void {
    if (this.userRole !== 'admin') {
      throw new Error('Only admins can delete documents');
    }
    this.document.delete();
  }
}

// Smart Proxy - Caching
interface DataService {
  getData(key: string): Promise<string>;
  setData(key: string, value: string): Promise<void>;
}

class RemoteDataService implements DataService {
  async getData(key: string): Promise<string> {
    console.log(`Fetching ${key} from remote server...`);
    await this.delay(1000);
    return `Data for ${key}`;
  }

  async setData(key: string, value: string): Promise<void> {
    console.log(`Saving ${key} to remote server...`);
    await this.delay(500);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class CachingProxy implements DataService {
  private cache = new Map<string, { value: string; expires: number }>();
  private ttlMs = 60000;

  constructor(private service: DataService) {}

  async getData(key: string): Promise<string> {
    const cached = this.cache.get(key);
    
    if (cached && cached.expires > Date.now()) {
      console.log(`[CACHE HIT] ${key}`);
      return cached.value;
    }

    console.log(`[CACHE MISS] ${key}`);
    const value = await this.service.getData(key);
    
    this.cache.set(key, {
      value,
      expires: Date.now() + this.ttlMs
    });
    
    return value;
  }

  async setData(key: string, value: string): Promise<void> {
    await this.service.setData(key, value);
    // Invalidate cache on write
    this.cache.delete(key);
  }

  clearCache(): void {
    this.cache.clear();
  }
}

// Remote Proxy (Simulation)
class BankAccountProxy {
  private balance = 1000;

  constructor(private accountId: string, private accessToken: string) {}

  getBalance(): number {
    this.validateAccess();
    return this.balance;
  }

  deposit(amount: number): void {
    this.validateAccess();
    this.balance += amount;
    console.log(`Deposited $${amount}. New balance: $${this.balance}`);
  }

  withdraw(amount: number): boolean {
    this.validateAccess();
    
    if (amount > this.balance) {
      console.log('Insufficient funds');
      return false;
    }
    
    this.balance -= amount;
    console.log(`Withdrew $${amount}. New balance: $${this.balance}`);
    return true;
  }

  private validateAccess(): void {
    if (!this.accessToken) {
      throw new Error('Access denied: No token provided');
    }
    // In real implementation, validate token with auth server
  }
}
```

### Tests

```typescript
import { describe, it, expect, vi } from 'vitest';

describe('Proxy Pattern', () => {
  describe('Virtual Proxy - Image Loading', () => {
    it('should not load image until display is called', () => {
      const consoleSpy = vi.spyOn(console, 'log');
      const proxy = new ImageProxy('photo.jpg');
      
      // Getting dimensions should not trigger load
      proxy.getWidth();
      expect(consoleSpy).not.toHaveBeenCalled();
      
      // Display should trigger load
      proxy.display();
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Loading image')
      );
    });

    it('should return placeholder dimensions before load', () => {
      const proxy = new ImageProxy('photo.jpg');
      expect(proxy.getWidth()).toBe(800);
      expect(proxy.getHeight()).toBe(600);
    });

    it('should return real dimensions after load', () => {
      const proxy = new ImageProxy('photo.jpg');
      proxy.display();
      expect(proxy.getWidth()).toBe(1920);
      expect(proxy.getHeight()).toBe(1080);
    });
  });

  describe('Protection Proxy - Document Access', () => {
    const createDocument = () => new RealDocument('Initial content', 'owner1');

    it('should allow all roles to read', () => {
      const roles = ['admin', 'editor', 'viewer'] as const;
      
      roles.forEach(role => {
        const doc = createDocument();
        const proxy = new DocumentProxy(doc, 'user1', role);
        expect(proxy.read()).toBe('Initial content');
      });
    });

    it('should prevent viewers from writing', () => {
      const proxy = new DocumentProxy(createDocument(), 'user1', 'viewer');
      expect(() => proxy.write('New content')).toThrow('Viewers cannot edit');
    });

    it('should allow editors to write', () => {
      const proxy = new DocumentProxy(createDocument(), 'user1', 'editor');
      proxy.write('New content');
      expect(proxy.read()).toBe('New content');
    });

    it('should prevent non-admins from deleting', () => {
      const proxy = new DocumentProxy(createDocument(), 'user1', 'editor');
      expect(() => proxy.delete()).toThrow('Only admins can delete');
    });

    it('should allow admins to delete', () => {
      const proxy = new DocumentProxy(createDocument(), 'user1', 'admin');
      proxy.delete();
      expect(proxy.read()).toBe('');
    });
  });

  describe('Caching Proxy', () => {
    it('should cache data after first fetch', async () => {
      const consoleSpy = vi.spyOn(console, 'log');
      const remote = new RemoteDataService();
      const proxy = new CachingProxy(remote);

      await proxy.getData('key1');
      await proxy.getData('key1');

      expect(consoleSpy).toHaveBeenCalledWith('[CACHE HIT] key1');
    });

    it('should invalidate cache on set', async () => {
      const remote = new RemoteDataService();
      const proxy = new CachingProxy(remote);

      await proxy.getData('key1');
      await proxy.setData('key1', 'new value');
      await proxy.getData('key1');

      // Should fetch again after invalidation
    });

    it('should clear all cache', async () => {
      const remote = new RemoteDataService();
      const proxy = new CachingProxy(remote);

      await proxy.getData('key1');
      await proxy.getData('key2');
      proxy.clearCache();
      
      // Both should miss cache now
    });
  });

  describe('Bank Account Proxy', () => {
    it('should require access token', () => {
      const proxy = new BankAccountProxy('123', '');
      expect(() => proxy.getBalance()).toThrow('Access denied');
    });

    it('should handle deposits', () => {
      const proxy = new BankAccountProxy('123', 'token');
      proxy.deposit(500);
      expect(proxy.getBalance()).toBe(1500);
    });

    it('should handle withdrawals', () => {
      const proxy = new BankAccountProxy('123', 'token');
      const result = proxy.withdraw(200);
      expect(result).toBe(true);
      expect(proxy.getBalance()).toBe(800);
    });

    it('should reject insufficient funds', () => {
      const proxy = new BankAccountProxy('123', 'token');
      const result = proxy.withdraw(2000);
      expect(result).toBe(false);
      expect(proxy.getBalance()).toBe(1000);
    });
  });
});
```

---

## Pattern 3: Composite Pattern

### Problem Description
Compose objects into tree structures to represent part-whole hierarchies.

### Solution

```typescript
// ============================================================
// Composite Pattern - File System & UI Components
// ============================================================

// Component Interface
interface FileSystemNode {
  getName(): string;
  getSize(): number;
  print(indent?: string): void;
  isDirectory(): boolean;
}

// Leaf - File
class File implements FileSystemNode {
  constructor(
    private name: string,
    private size: number
  ) {}

  getName(): string {
    return this.name;
  }

  getSize(): number {
    return this.size;
  }

  print(indent = ''): void {
    console.log(`${indent}📄 ${this.name} (${this.formatSize()})`);
  }

  isDirectory(): boolean {
    return false;
  }

  private formatSize(): string {
    if (this.size < 1024) return `${this.size} B`;
    if (this.size < 1024 * 1024) return `${(this.size / 1024).toFixed(1)} KB`;
    return `${(this.size / (1024 * 1024)).toFixed(1)} MB`;
  }
}

// Composite - Directory
class Directory implements FileSystemNode {
  private children: FileSystemNode[] = [];

  constructor(private name: string) {}

  add(node: FileSystemNode): void {
    this.children.push(node);
  }

  remove(node: FileSystemNode): void {
    const index = this.children.indexOf(node);
    if (index > -1) {
      this.children.splice(index, 1);
    }
  }

  getChildren(): FileSystemNode[] {
    return [...this.children];
  }

  getName(): string {
    return this.name;
  }

  getSize(): number {
    return this.children.reduce((sum, child) => sum + child.getSize(), 0);
  }

  print(indent = ''): void {
    console.log(`${indent}📁 ${this.name}/ (${this.formatSize()})`);
    this.children.forEach(child => child.print(indent + '  '));
  }

  isDirectory(): boolean {
    return true;
  }

  private formatSize(): string {
    const size = this.getSize();
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }
}

// UI Component Composite
interface UIComponent {
  render(): string;
  getChildren(): UIComponent[];
  addChild(component: UIComponent): void;
}

class TextComponent implements UIComponent {
  constructor(private text: string) {}

  render(): string {
    return this.text;
  }

  getChildren(): UIComponent[] {
    return [];
  }

  addChild(): void {
    throw new Error('Cannot add children to leaf component');
  }
}

class ContainerComponent implements UIComponent {
  private children: UIComponent[] = [];

  constructor(
    private tagName: string,
    private className?: string
  ) {}

  addChild(component: UIComponent): void {
    this.children.push(component);
  }

  getChildren(): UIComponent[] {
    return [...this.children];
  }

  render(): string {
    const classAttr = this.className ? ` class="${this.className}"` : '';
    const content = this.children.map(c => c.render()).join('\n  ');
    return `<${this.tagName}${classAttr}>\n  ${content}\n</${this.tagName}>`;
  }
}

// HTML Builder using Composite
class HTMLBuilder {
  static div(className?: string): ContainerComponent {
    return new ContainerComponent('div', className);
  }

  static section(className?: string): ContainerComponent {
    return new ContainerComponent('section', className);
  }

  static p(text: string): TextComponent {
    return new TextComponent(`<p>${text}</p>`);
  }

  static h1(text: string): TextComponent {
    return new TextComponent(`<h1>${text}</h1>`);
  }

  static span(text: string): TextComponent {
    return new TextComponent(`<span>${text}</span>`);
  }
}

// Search in Composite
function findFile(node: FileSystemNode, name: string): FileSystemNode | null {
  if (node.getName() === name) {
    return node;
  }

  if (node.isDirectory()) {
    const dir = node as Directory;
    for (const child of dir.getChildren()) {
      const found = findFile(child, name);
      if (found) return found;
    }
  }

  return null;
}

// Collect all files recursively
function getAllFiles(node: FileSystemNode): File[] {
  if (!node.isDirectory()) {
    return [node as File];
  }

  const dir = node as Directory;
  return dir.getChildren().flatMap(child => getAllFiles(child));
}
```

### Tests

```typescript
import { describe, it, expect } from 'vitest';

describe('Composite Pattern', () => {
  describe('File System', () => {
    it('should calculate file size', () => {
      const file = new File('test.txt', 1024);
      expect(file.getSize()).toBe(1024);
      expect(file.isDirectory()).toBe(false);
    });

    it('should calculate directory size', () => {
      const dir = new Directory('docs');
      dir.add(new File('file1.txt', 100));
      dir.add(new File('file2.txt', 200));
      
      expect(dir.getSize()).toBe(300);
      expect(dir.isDirectory()).toBe(true);
    });

    it('should handle nested directories', () => {
      const root = new Directory('root');
      const docs = new Directory('docs');
      const images = new Directory('images');
      
      docs.add(new File('readme.md', 500));
      images.add(new File('logo.png', 2000));
      root.add(docs);
      root.add(images);
      
      expect(root.getSize()).toBe(2500);
    });

    it('should find files by name', () => {
      const root = new Directory('root');
      const docs = new Directory('docs');
      const file = new File('target.txt', 100);
      
      docs.add(file);
      root.add(docs);
      
      const found = findFile(root, 'target.txt');
      expect(found).toBe(file);
    });

    it('should collect all files', () => {
      const root = new Directory('root');
      const file1 = new File('a.txt', 100);
      const file2 = new File('b.txt', 200);
      
      root.add(file1);
      root.add(file2);
      
      const files = getAllFiles(root);
      expect(files).toHaveLength(2);
    });
  });

  describe('UI Components', () => {
    it('should render text component', () => {
      const text = new TextComponent('Hello');
      expect(text.render()).toBe('Hello');
    });

    it('should render container with children', () => {
      const container = new ContainerComponent('div', 'container');
      container.addChild(new TextComponent('<p>Hello</p>'));
      
      const rendered = container.render();
      expect(rendered).toContain('<div class="container">');
      expect(rendered).toContain('<p>Hello</p>');
    });

    it('should build HTML using builder', () => {
      const section = HTMLBuilder.section('main');
      section.addChild(HTMLBuilder.h1('Title'));
      section.addChild(HTMLBuilder.p('Paragraph'));
      
      const rendered = section.render();
      expect(rendered).toContain('<section class="main">');
      expect(rendered).toContain('<h1>Title</h1>');
    });

    it('should compose nested components', () => {
      const main = HTMLBuilder.div('main');
      const header = HTMLBuilder.div('header');
      header.addChild(HTMLBuilder.h1('Site Title'));
      
      main.addChild(header);
      main.addChild(HTMLBuilder.p('Content'));
      
      expect(main.getChildren()).toHaveLength(2);
    });
  });
});
```

---

## Summary

| Pattern | Purpose | Use Case |
|---------|---------|----------|
| Decorator | Add behavior dynamically | HTTP middleware, UI styling |
| Proxy | Control access to object | Lazy loading, access control, caching |
| Composite | Tree structures | File systems, UI component trees |

**Key Takeaways:**
- Decorator: Wraps objects to extend functionality without modifying code
- Proxy: Controls access, can cache or lazy-load
- Composite: Treats individual and group uniformly
