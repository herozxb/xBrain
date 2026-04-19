# DATA STRUCTURES - High-Quality Code Data
**Date:** February 18, 2026
**Category:** Data Structures (Arrays, Linked Lists, Trees, Stacks, Queues)
**Total Items:** 6

---

## Problem: Dynamic Array Implementation

```python
# PROBLEM: Implement a dynamic array that automatically resizes when capacity is reached
# APPROACH: Use underlying static array, double capacity when full, halve when quarter full
# TIME: O(1) amortized for append, O(n) worst case for resize  SPACE: O(n)
# EDGE CASES: Empty array, single element, capacity overflow, negative indices

class DynamicArray:
    def __init__(self, capacity=10):
        # Initialize with given capacity or default
        self.capacity = max(1, capacity)
        self.size = 0
        self.array = [None] * self.capacity
    
    def __len__(self):
        return self.size
    
    def __getitem__(self, index):
        # Support negative indexing like Python lists
        if index < 0:
            index = self.size + index
        
        if not 0 <= index < self.size:
            raise IndexError("Index out of bounds")
        return self.array[index]
    
    def __setitem__(self, index, value):
        if index < 0:
            index = self.size + index
        
        if not 0 <= index < self.size:
            raise IndexError("Index out of bounds")
        self.array[index] = value
    
    def append(self, value):
        # Resize if capacity is reached
        if self.size == self.capacity:
            self._resize(2 * self.capacity)
        
        self.array[self.size] = value
        self.size += 1
    
    def insert(self, index, value):
        # Validate index
        if index < 0:
            index = self.size + index
        
        if not 0 <= index <= self.size:
            raise IndexError("Index out of bounds")
        
        # Resize if necessary
        if self.size == self.capacity:
            self._resize(2 * self.capacity)
        
        # Shift elements right to make space
        for i in range(self.size, index, -1):
            self.array[i] = self.array[i - 1]
        
        self.array[index] = value
        self.size += 1
    
    def remove(self, index):
        if index < 0:
            index = self.size + index
        
        if not 0 <= index < self.size:
            raise IndexError("Index out of bounds")
        
        # Store value to return
        value = self.array[index]
        
        # Shift elements left to fill gap
        for i in range(index, self.size - 1):
            self.array[i] = self.array[i + 1]
        
        self.size -= 1
        self.array[self.size] = None  # Clear reference
        
        # Shrink if too empty (quarter of capacity)
        if self.size > 0 and self.size == self.capacity // 4:
            self._resize(self.capacity // 2)
        
        return value
    
    def _resize(self, new_capacity):
        # Create new array and copy elements
        new_array = [None] * new_capacity
        for i in range(self.size):
            new_array[i] = self.array[i]
        
        self.array = new_array
        self.capacity = new_capacity
    
    def __repr__(self):
        return f"DynamicArray({self.array[:self.size]})"
```

**Explanation**: A dynamic array provides the convenience of automatic resizing while maintaining O(1) random access time. When the underlying static array reaches capacity, it creates a new larger array (typically double) and copies all elements. The amortized analysis shows that despite occasional O(n) resize operations, the average cost per operation remains O(1).

**When to Use**: Use dynamic arrays when you need random access to elements, don't know the exact size upfront, need cache-friendly contiguous memory, or want efficient append operations. They're the foundation for most high-level language list implementations.

**Trade-offs**:
- **Pros:** O(1) random access, cache-friendly, efficient amortized append, simple interface
- **Cons:** O(n) worst-case for insert/delete in middle, wasted space when not full, resize operation is expensive

---

## Problem: Singly Linked List

```python
# PROBLEM: Implement a singly linked list with common operations
# APPROACH: Use node objects with value and next pointer, maintain head and tail references
# TIME: O(1) prepend/append, O(n) search/delete by value  SPACE: O(n)
# EDGE CASES: Empty list, single node, delete head/tail, value not found

class ListNode:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def __len__(self):
        return self.size
    
    def is_empty(self):
        return self.size == 0
    
    def prepend(self, value):
        # Add node at beginning - O(1)
        new_node = ListNode(value)
        
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        
        self.size += 1
    
    def append(self, value):
        # Add node at end - O(1) with tail pointer
        new_node = ListNode(value)
        
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
    
    def insert_after(self, node, value):
        # Insert after given node - O(1)
        if node is None:
            self.prepend(value)
            return
        
        new_node = ListNode(value)
        new_node.next = node.next
        node.next = new_node
        
        if node == self.tail:
            self.tail = new_node
        
        self.size += 1
    
    def delete_head(self):
        if self.is_empty():
            raise Exception("List is empty")
        
        value = self.head.value
        self.head = self.head.next
        
        if self.head is None:
            self.tail = None
        
        self.size -= 1
        return value
    
    def delete_by_value(self, value):
        # Find and delete first occurrence - O(n)
        if self.is_empty():
            return False
        
        # Special case: delete head
        if self.head.value == value:
            self.delete_head()
            return True
        
        # Search for node to delete
        current = self.head
        while current.next:
            if current.next.value == value:
                # Skip over node to delete
                current.next = current.next.next
                
                if current.next is None:
                    self.tail = current
                
                self.size -= 1
                return True
            current = current.next
        
        return False  # Value not found
    
    def find(self, value):
        # Search for value - O(n)
        current = self.head
        index = 0
        
        while current:
            if current.value == value:
                return index
            current = current.next
            index += 1
        
        return -1  # Not found
    
    def reverse(self):
        # Reverse entire list in-place - O(n)
        prev = None
        current = self.head
        self.tail = current  # Old head becomes new tail
        
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        
        self.head = prev
    
    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result
    
    def __repr__(self):
        return f"LinkedList({self.to_list()})"
```

**Explanation**: A singly linked list consists of nodes where each node contains a value and a pointer to the next node. This structure allows O(1) insertion and deletion at known positions but requires O(n) time for searching. The lack of contiguous memory allocation makes it less cache-friendly than arrays but enables efficient insertions without resizing.

**When to Use**: Use linked lists when you need frequent insertions/deletions at arbitrary positions, don't need random access, have unpredictable size growth, or are implementing stacks, queues, or hash table chaining. They're ideal for LRU caches and polynomial arithmetic.

**Trade-offs**:
- **Pros:** O(1) insert/delete at known positions, dynamic size, no wasted space, no resize overhead
- **Cons:** No random access O(n) search, extra memory for pointers, poor cache locality, more complex than arrays

---

## Problem: Binary Search Tree

```python
# PROBLEM: Implement a binary search tree with insert, search, and delete operations
# APPROACH: Maintain BST property: left child < parent < right child
# TIME: O(log n) average, O(n) worst case  SPACE: O(n)
# EDGE CASES: Empty tree, duplicate values, deleting root, single child deletions

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1  # For AVL balancing

class BinarySearchTree:
    def __init__(self):
        self.root = None
        self.size = 0
    
    def insert(self, value):
        self.root = self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        # Base case: create new node
        if node is None:
            self.size += 1
            return TreeNode(value)
        
        # Recursively insert in appropriate subtree
        if value < node.value:
            node.left = self._insert_recursive(node.left, value)
        elif value > node.value:
            node.right = self._insert_recursive(node.right, value)
        # Duplicate values are ignored
        
        return node
    
    def search(self, value):
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        # Base cases: not found or found
        if node is None:
            return False
        if value == node.value:
            return True
        
        # Search in appropriate subtree
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)
    
    def delete(self, value):
        if self.search(value):
            self.root = self._delete_recursive(self.root, value)
            self.size -= 1
            return True
        return False
    
    def _delete_recursive(self, node, value):
        if node is None:
            return None
        
        # Find node to delete
        if value < node.value:
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            node.right = self._delete_recursive(node.right, value)
        else:
            # Node found - handle three cases
            
            # Case 1: No children (leaf)
            if node.left is None and node.right is None:
                return None
            
            # Case 2: One child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            
            # Case 3: Two children - find inorder successor
            successor = self._find_min(node.right)
            node.value = successor.value
            node.right = self._delete_recursive(node.right, successor.value)
        
        return node
    
    def _find_min(self, node):
        # Leftmost node is minimum
        while node.left:
            node = node.left
        return node
    
    def _find_max(self, node):
        # Rightmost node is maximum
        while node.right:
            node = node.right
        return node
    
    def inorder_traversal(self):
        # Returns sorted list of values
        result = []
        self._inorder_helper(self.root, result)
        return result
    
    def _inorder_helper(self, node, result):
        if node:
            self._inorder_helper(node.left, result)
            result.append(node.value)
            self._inorder_helper(node.right, result)
    
    def get_height(self):
        return self._height_helper(self.root)
    
    def _height_helper(self, node):
        if node is None:
            return 0
        return 1 + max(self._height_helper(node.left), 
                       self._height_helper(node.right))
    
    def is_balanced(self):
        return self._check_balance(self.root) != -1
    
    def _check_balance(self, node):
        if node is None:
            return 0
        
        left_height = self._check_balance(node.left)
        if left_height == -1:
            return -1
        
        right_height = self._check_balance(node.right)
        if right_height == -1:
            return -1
        
        if abs(left_height - right_height) > 1:
            return -1
        
        return 1 + max(left_height, right_height)
```

**Explanation**: A binary search tree maintains sorted data enabling efficient search, insertion, and deletion operations. Each node has at most two children, with all left descendants being smaller and right descendants being larger. Performance depends on tree balance—ideally O(log n), but can degrade to O(n) if the tree becomes skewed like a linked list.

**When to Use**: Use BSTs when you need to maintain sorted data with dynamic insertions and deletions, implement symbol tables or dictionaries, support range queries, or build expression parsers. They're fundamental to database indexing and file systems.

**Trade-offs**:
- **Pros:** O(log n) average case operations, maintains sorted order, supports range queries, no resizing needed
- **Cons:** Can become unbalanced leading to O(n) operations, more complex than arrays, no O(1) random access

---

## Problem: Stack Implementation

```python
# PROBLEM: Implement a LIFO (Last-In-First-Out) stack with common operations
# APPROACH: Use list or linked list to store elements, maintain top pointer
# TIME: O(1) for push, pop, peek  SPACE: O(n)
# EDGE CASES: Empty stack pop, stack overflow (if capacity limited), None values

class Stack:
    def __init__(self, capacity=None):
        self.items = []
        self.capacity = capacity
    
    def push(self, item):
        # Add item to top of stack
        if self.capacity and len(self.items) >= self.capacity:
            raise Exception("Stack Overflow")
        self.items.append(item)
    
    def pop(self):
        # Remove and return top item
        if self.is_empty():
            raise Exception("Stack Underflow")
        return self.items.pop()
    
    def peek(self):
        # Return top item without removing
        if self.is_empty():
            raise Exception("Stack is empty")
        return self.items[-1]
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
    
    def __repr__(self):
        return f"Stack({self.items})"

class StackWithMin:
    """Stack that supports O(1) minimum retrieval."""
    def __init__(self):
        self.stack = []
        self.min_stack = []  # Track minimums
    
    def push(self, value):
        self.stack.append(value)
        
        # Push to min_stack if empty or new minimum
        if not self.min_stack or value <= self.min_stack[-1]:
            self.min_stack.append(value)
    
    def pop(self):
        if not self.stack:
            raise Exception("Stack is empty")
        
        value = self.stack.pop()
        
        # Pop from min_stack if it's the minimum
        if value == self.min_stack[-1]:
            self.min_stack.pop()
        
        return value
    
    def get_min(self):
        if not self.min_stack:
            raise Exception("Stack is empty")
        return self.min_stack[-1]

def is_valid_parentheses(s):
    """Check if parentheses string is balanced using stack."""
    stack = Stack()
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.push(char)
        elif char in ')}]':
            if stack.is_empty() or stack.pop() != mapping[char]:
                return False
    
    return stack.is_empty()

def evaluate_postfix(expression):
    """Evaluate postfix notation using stack."""
    stack = Stack()
    operators = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b
    }
    
    tokens = expression.split()
    
    for token in tokens:
        if token in operators:
            b = stack.pop()
            a = stack.pop()
            stack.push(operators[token](a, b))
        else:
            stack.push(float(token))
    
    return stack.pop()

def reverse_string(s):
    """Reverse string using stack."""
    stack = Stack()
    for char in s:
        stack.push(char)
    
    result = []
    while not stack.is_empty():
        result.append(stack.pop())
    
    return ''.join(result)
```

**Explanation**: A stack is a linear data structure following LIFO (Last-In-First-Out) principle, where the last element added is the first to be removed. It supports three primary operations: push (add), pop (remove), and peek (view top). Stacks are crucial for function call management, undo operations, and expression evaluation.

**When to Use**: Use stacks for function call management (call stack), undo/redo functionality, expression evaluation (postfix, prefix), bracket matching, depth-first search, or any scenario where you need to reverse order or track history.

**Trade-offs**:
- **Pros:** O(1) operations, simple implementation, natural for recursive problems
- **Cons:** Limited access (only top element), no random access, fixed capacity if array-based

---

## Problem: Queue Implementation

```python
# PROBLEM: Implement a FIFO (First-In-First-Out) queue with common operations
# APPROACH: Use deque or linked list for O(1) enqueue/dequeue at different ends
# TIME: O(1) for enqueue, dequeue, peek  SPACE: O(n)
# EDGE CASES: Empty queue dequeue, queue overflow, priority duplicates

from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        # Add item to back of queue
        self.items.append(item)
    
    def dequeue(self):
        # Remove and return front item
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.items.popleft()
    
    def peek(self):
        # Return front item without removing
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.items[0]
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
    
    def __repr__(self):
        return f"Queue({list(self.items)})"

class CircularQueue:
    """Fixed-size circular queue using array."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = -1
        self.size = 0
    
    def enqueue(self, item):
        if self.is_full():
            raise Exception("Queue is full")
        
        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = item
        self.size += 1
    
    def dequeue(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        
        item = self.queue[self.front]
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item
    
    def is_empty(self):
        return self.size == 0
    
    def is_full(self):
        return self.size == self.capacity

class PriorityQueue:
    """Min-heap based priority queue."""
    def __init__(self):
        self.heap = []
    
    def enqueue(self, item, priority):
        # Insert as tuple (priority, item)
        heapq.heappush(self.heap, (priority, item))
    
    def dequeue(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        return heapq.heappop(self.heap)[1]
    
    def peek(self):
        if self.is_empty():
            raise Exception("Queue is empty")
        return self.heap[0][1]
    
    def is_empty(self):
        return len(self.heap) == 0

import heapq

class Deque:
    """Double-ended queue implementation."""
    def __init__(self):
        self.items = deque()
    
    def add_front(self, item):
        self.items.appendleft(item)
    
    def add_rear(self, item):
        self.items.append(item)
    
    def remove_front(self):
        if self.is_empty():
            raise Exception("Deque is empty")
        return self.items.popleft()
    
    def remove_rear(self):
        if self.is_empty():
            raise Exception("Deque is empty")
        return self.items.pop()
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

def breadth_first_search_queue(graph, start):
    """BFS using explicit queue."""
    visited = set([start])
    queue = Queue()
    queue.enqueue(start)
    result = []
    
    while not queue.is_empty():
        node = queue.dequeue()
        result.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.enqueue(neighbor)
    
    return result
```

**Explanation**: A queue follows the FIFO (First-In-First-Out) principle where elements are added at the rear and removed from the front. Variants include circular queues (efficient memory use), priority queues (elements have priorities), and deques (double-ended). Queues are essential for BFS, scheduling, and buffer management.

**When to Use**: Use queues for task scheduling, breadth-first search, printer job spooling, message passing between processes, handling requests in web servers, or any scenario requiring first-come-first-served processing.

**Trade-offs**:
- **Pros:** O(1) enqueue/dequeue, fair ordering, simple concept
- **Cons:** No random access, limited to sequential processing, array-based may need resizing

---

## Problem: Hash Table Implementation

```python
# PROBLEM: Implement a hash table with collision handling using chaining
# APPROACH: Use array of linked lists, hash function maps keys to indices
# TIME: O(1) average for insert/delete/search, O(n) worst case  SPACE: O(n)
# EDGE CASES: Hash collisions, null keys, resize threshold, load factor

class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable:
    def __init__(self, capacity=16, load_factor=0.75):
        self.capacity = capacity
        self.size = 0
        self.load_factor = load_factor
        self.buckets = [None] * capacity
    
    def _hash(self, key):
        # Custom hash function
        hash_value = 0
        key_str = str(key)
        
        for char in key_str:
            hash_value = (hash_value * 31 + ord(char)) % self.capacity
        
        return hash_value
    
    def put(self, key, value):
        # Check if resize needed
        if self.size >= self.capacity * self.load_factor:
            self._resize()
        
        index = self._hash(key)
        
        # Check if key already exists
        current = self.buckets[index]
        while current:
            if current.key == key:
                current.value = value  # Update existing
                return
            current = current.next
        
        # Add new node at head of chain
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1
    
    def get(self, key):
        index = self._hash(key)
        current = self.buckets[index]
        
        while current:
            if current.key == key:
                return current.value
            current = current.next
        
        return None  # Key not found
    
    def remove(self, key):
        index = self._hash(key)
        current = self.buckets[index]
        prev = None
        
        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.buckets[index] = current.next
                self.size -= 1
                return current.value
            prev = current
            current = current.next
        
        return None  # Key not found
    
    def contains_key(self, key):
        return self.get(key) is not None
    
    def _resize(self):
        # Double capacity and rehash all entries
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        self.size = 0
        
        for head in old_buckets:
            current = head
            while current:
                self.put(current.key, current.value)
                current = current.next
    
    def keys(self):
        result = []
        for head in self.buckets:
            current = head
            while current:
                result.append(current.key)
                current = current.next
        return result
    
    def values(self):
        result = []
        for head in self.buckets:
            current = head
            while current:
                result.append(current.value)
                current = current.next
        return result
    
    def items(self):
        result = []
        for head in self.buckets:
            current = head
            while current:
                result.append((current.key, current.value))
                current = current.next
        return result
    
    def __setitem__(self, key, value):
        self.put(key, value)
    
    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __contains__(self, key):
        return self.contains_key(key)
    
    def __len__(self):
        return self.size

class LRUCache:
    """LRU Cache using hash table + doubly linked list."""
    class Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.head = self.Node(None, None)  # Dummy head
        self.tail = self.Node(None, None)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def get(self, key):
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._remove_node(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove_node(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Remove LRU (tail)
                lru = self.tail.prev
                self._remove_node(lru)
                del self.cache[lru.key]
            
            new_node = self.Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
```

**Explanation**: A hash table provides O(1) average-case lookup, insertion, and deletion by using a hash function to map keys to array indices. Collision handling via chaining (linked lists) or open addressing ensures correctness even when different keys hash to the same index. Load factor management and resizing maintain performance as the table grows.

**When to Use**: Use hash tables for implementing dictionaries/caches, counting occurrences, finding duplicates, two-sum problems, or any scenario requiring fast key-value lookups. They're ubiquitous in database indexing, caching systems, and symbol tables.

**Trade-offs**:
- **Pros:** O(1) average operations, flexible key types, efficient memory usage
- **Cons:** O(n) worst case, no ordering, extra memory for collision handling, hash function quality matters

---

**End of DATA STRUCTURES Category**
