# Python 数据结构实现

本文档包含5种核心数据结构的完整Python实现和测试代码。

---

## 1. 链表（单向/双向）

### 单向链表

```python
class ListNode:
    """单向链表节点"""
    def __init__(self, val=0):
        self.val = val
        self.next = None

class SinglyLinkedList:
    """单向链表实现"""
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, val):
        """在末尾添加节点"""
        new_node = ListNode(val)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
    
    def prepend(self, val):
        """在头部添加节点"""
        new_node = ListNode(val)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
    
    def insert(self, index, val):
        """在指定位置插入节点"""
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")
        if index == 0:
            self.prepend(val)
            return
        current = self.head
        for _ in range(index - 1):
            current = current.next
        new_node = ListNode(val)
        new_node.next = current.next
        current.next = new_node
        self.size += 1
    
    def delete(self, val):
        """删除第一个匹配的节点"""
        if not self.head:
            return False
        if self.head.val == val:
            self.head = self.head.next
            self.size -= 1
            return True
        current = self.head
        while current.next:
            if current.next.val == val:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False
    
    def find(self, val):
        """查找节点，返回索引"""
        current = self.head
        index = 0
        while current:
            if current.val == val:
                return index
            current = current.next
            index += 1
        return -1
    
    def to_list(self):
        """转换为Python列表"""
        result = []
        current = self.head
        while current:
            result.append(current.val)
            current = current.next
        return result

# 测试单向链表
def test_singly_linked_list():
    print("=== 单向链表测试 ===")
    ll = SinglyLinkedList()
    
    # 测试添加
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.prepend(0)
    assert ll.to_list() == [0, 1, 2, 3], f"Expected [0,1,2,3], got {ll.to_list()}"
    print("✓ 添加测试通过")
    
    # 测试插入
    ll.insert(2, 1.5)
    assert ll.to_list() == [0, 1, 1.5, 2, 3], f"插入失败: {ll.to_list()}"
    print("✓ 插入测试通过")
    
    # 测试查找
    assert ll.find(1.5) == 2, "查找失败"
    assert ll.find(100) == -1, "查找不存在的值应该返回-1"
    print("✓ 查找测试通过")
    
    # 测试删除
    ll.delete(1.5)
    assert ll.to_list() == [0, 1, 2, 3], "删除失败"
    print("✓ 删除测试通过")
    
    print(f"最终链表: {ll.to_list()}, 大小: {ll.size}\n")

test_singly_linked_list()
```

### 双向链表

```python
class DoublyListNode:
    """双向链表节点"""
    def __init__(self, val=0):
        self.val = val
        self.prev = None
        self.next = None

class DoublyLinkedList:
    """双向链表实现"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def append(self, val):
        """在末尾添加节点"""
        new_node = DoublyListNode(val)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1
    
    def prepend(self, val):
        """在头部添加节点"""
        new_node = DoublyListNode(val)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1
    
    def insert(self, index, val):
        """在指定位置插入节点"""
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")
        if index == 0:
            self.prepend(val)
        elif index == self.size:
            self.append(val)
        else:
            current = self.head
            for _ in range(index):
                current = current.next
            new_node = DoublyListNode(val)
            new_node.prev = current.prev
            new_node.next = current
            current.prev.next = new_node
            current.prev = new_node
            self.size += 1
    
    def delete(self, val):
        """删除第一个匹配的节点"""
        current = self.head
        while current:
            if current.val == val:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                self.size -= 1
                return True
            current = current.next
        return False
    
    def to_list(self, reverse=False):
        """转换为Python列表，reverse=True时从尾到头"""
        result = []
        if reverse:
            current = self.tail
            while current:
                result.append(current.val)
                current = current.prev
        else:
            current = self.head
            while current:
                result.append(current.val)
                current = current.next
        return result

# 测试双向链表
def test_doubly_linked_list():
    print("=== 双向链表测试 ===")
    dll = DoublyLinkedList()
    
    # 测试双向添加
    dll.append(2)
    dll.append(3)
    dll.prepend(1)
    assert dll.to_list() == [1, 2, 3], f"正向遍历失败: {dll.to_list()}"
    assert dll.to_list(reverse=True) == [3, 2, 1], f"反向遍历失败: {dll.to_list(reverse=True)}"
    print("✓ 双向遍历测试通过")
    
    # 测试插入
    dll.insert(1, 1.5)
    assert dll.to_list() == [1, 1.5, 2, 3], "插入失败"
    print("✓ 插入测试通过")
    
    # 测试删除头尾
    dll.delete(1)
    dll.delete(3)
    assert dll.to_list() == [1.5, 2], "删除头尾失败"
    print("✓ 删除测试通过")
    
    print(f"最终链表: {dll.to_list()}, 大小: {dll.size}\n")

test_doubly_linked_list()
```

---

## 2. 栈和队列

### 栈（Stack）

```python
class Stack:
    """栈实现（后进先出 LIFO）"""
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """压栈"""
        self.items.append(item)
    
    def pop(self):
        """弹栈"""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self.items.pop()
    
    def peek(self):
        """查看栈顶元素"""
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self.items[-1]
    
    def is_empty(self):
        """判断是否为空"""
        return len(self.items) == 0
    
    def size(self):
        """返回栈大小"""
        return len(self.items)

# 应用：括号匹配
def is_valid_parentheses(s):
    """检查括号是否匹配"""
    stack = Stack()
    mapping = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':
            stack.push(char)
        elif char in mapping:
            if stack.is_empty() or stack.pop() != mapping[char]:
                return False
    return stack.is_empty()

# 测试栈
def test_stack():
    print("=== 栈测试 ===")
    stack = Stack()
    
    # 基本操作
    stack.push(1)
    stack.push(2)
    stack.push(3)
    assert stack.peek() == 3, "peek失败"
    assert stack.pop() == 3, "pop失败"
    assert stack.size() == 2, "size失败"
    print("✓ 基本操作测试通过")
    
    # 括号匹配测试
    assert is_valid_parentheses("()[]{}") == True
    assert is_valid_parentheses("([)]") == False
    assert is_valid_parentheses("((()))") == True
    assert is_valid_parentheses("(()") == False
    print("✓ 括号匹配测试通过")
    print()

test_stack()
```

### 队列（Queue）

```python
from collections import deque

class Queue:
    """队列实现（先进先出 FIFO）"""
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        """入队"""
        self.items.append(item)
    
    def dequeue(self):
        """出队"""
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        return self.items.popleft()
    
    def front(self):
        """查看队首"""
        if self.is_empty():
            raise IndexError("Front from empty queue")
        return self.items[0]
    
    def is_empty(self):
        """判断是否为空"""
        return len(self.items) == 0
    
    def size(self):
        """返回队列大小"""
        return len(self.items)

# 循环队列
class CircularQueue:
    """循环队列实现"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front_idx = 0
        self.rear_idx = -1
        self.count = 0
    
    def enqueue(self, item):
        """入队"""
        if self.is_full():
            raise IndexError("Queue is full")
        self.rear_idx = (self.rear_idx + 1) % self.capacity
        self.queue[self.rear_idx] = item
        self.count += 1
    
    def dequeue(self):
        """出队"""
        if self.is_empty():
            raise IndexError("Queue is empty")
        item = self.queue[self.front_idx]
        self.front_idx = (self.front_idx + 1) % self.capacity
        self.count -= 1
        return item
    
    def front(self):
        """查看队首"""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue[self.front_idx]
    
    def is_empty(self):
        return self.count == 0
    
    def is_full(self):
        return self.count == self.capacity

# 测试队列
def test_queue():
    print("=== 队列测试 ===")
    queue = Queue()
    
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    assert queue.front() == 1, "front失败"
    assert queue.dequeue() == 1, "dequeue失败"
    assert queue.size() == 2, "size失败"
    print("✓ 基本队列测试通过")
    
    # 循环队列测试
    cq = CircularQueue(3)
    cq.enqueue(1)
    cq.enqueue(2)
    cq.enqueue(3)
    assert cq.is_full() == True, "循环队列应该已满"
    cq.dequeue()
    cq.enqueue(4)
    assert cq.front() == 2, "循环队列front失败"
    print("✓ 循环队列测试通过")
    print()

test_queue()
```

---

## 3. 二叉堆（Binary Heap）

```python
class BinaryHeap:
    """二叉堆实现（最小堆）"""
    def __init__(self, is_min_heap=True):
        self.heap = []
        self.is_min_heap = is_min_heap
    
    def _compare(self, a, b):
        """比较函数"""
        if self.is_min_heap:
            return a < b
        return a > b
    
    def _parent(self, i):
        return (i - 1) // 2
    
    def _left_child(self, i):
        return 2 * i + 1
    
    def _right_child(self, i):
        return 2 * i + 2
    
    def _heapify_up(self, i):
        """向上调整"""
        while i > 0 and self._compare(self.heap[i], self.heap[self._parent(i)]):
            parent = self._parent(i)
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            i = parent
    
    def _heapify_down(self, i):
        """向下调整"""
        size = len(self.heap)
        while True:
            smallest_or_largest = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            if left < size and self._compare(self.heap[left], self.heap[smallest_or_largest]):
                smallest_or_largest = left
            
            if right < size and self._compare(self.heap[right], self.heap[smallest_or_largest]):
                smallest_or_largest = right
            
            if smallest_or_largest != i:
                self.heap[i], self.heap[smallest_or_largest] = self.heap[smallest_or_largest], self.heap[i]
                i = smallest_or_largest
            else:
                break
    
    def insert(self, val):
        """插入元素"""
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)
    
    def extract(self):
        """提取堆顶元素"""
        if not self.heap:
            raise IndexError("Heap is empty")
        
        top = self.heap[0]
        last = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last
            self._heapify_down(0)
        
        return top
    
    def peek(self):
        """查看堆顶"""
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]
    
    def size(self):
        return len(self.heap)
    
    def is_empty(self):
        return len(self.heap) == 0
    
    @staticmethod
    def heapify(arr, is_min_heap=True):
        """从数组构建堆"""
        heap = BinaryHeap(is_min_heap)
        heap.heap = arr[:]
        for i in range(len(arr) // 2 - 1, -1, -1):
            heap._heapify_down(i)
        return heap

# 测试二叉堆
def test_binary_heap():
    print("=== 二叉堆测试 ===")
    
    # 最小堆测试
    min_heap = BinaryHeap(is_min_heap=True)
    for val in [5, 3, 7, 1, 9, 2]:
        min_heap.insert(val)
    
    assert min_heap.peek() == 1, "最小堆peek失败"
    result = []
    while not min_heap.is_empty():
        result.append(min_heap.extract())
    assert result == [1, 2, 3, 5, 7, 9], f"最小堆排序失败: {result}"
    print("✓ 最小堆测试通过")
    
    # 最大堆测试
    max_heap = BinaryHeap(is_min_heap=False)
    for val in [5, 3, 7, 1, 9, 2]:
        max_heap.insert(val)
    
    result = []
    while not max_heap.is_empty():
        result.append(max_heap.extract())
    assert result == [9, 7, 5, 3, 2, 1], f"最大堆排序失败: {result}"
    print("✓ 最大堆测试通过")
    
    # heapify测试
    heap = BinaryHeap.heapify([4, 1, 3, 2, 16, 9, 10])
    result = []
    while not heap.is_empty():
        result.append(heap.extract())
    assert result == [1, 2, 3, 4, 9, 10, 16], f"heapify失败: {result}"
    print("✓ heapify测试通过")
    print()

test_binary_heap()
```

---

## 4. 红黑树（Red-Black Tree）

```python
class RBNode:
    """红黑树节点"""
    def __init__(self, val, color='RED'):
        self.val = val
        self.color = color  # 'RED' or 'BLACK'
        self.left = None
        self.right = None
        self.parent = None

class RedBlackTree:
    """红黑树实现"""
    def __init__(self):
        self.NIL = RBNode(None, 'BLACK')  # 哨兵节点
        self.root = self.NIL
    
    def _left_rotate(self, x):
        """左旋"""
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
    
    def _right_rotate(self, y):
        """右旋"""
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent == self.NIL:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x
    
    def insert(self, val):
        """插入节点"""
        node = RBNode(val)
        node.left = self.NIL
        node.right = self.NIL
        
        y = self.NIL
        x = self.root
        
        while x != self.NIL:
            y = x
            if node.val < x.val:
                x = x.left
            else:
                x = x.right
        
        node.parent = y
        if y == self.NIL:
            self.root = node
        elif node.val < y.val:
            y.left = node
        else:
            y.right = node
        
        self._insert_fixup(node)
    
    def _insert_fixup(self, node):
        """插入修复"""
        while node.parent.color == 'RED':
            if node.parent == node.parent.parent.left:
                y = node.parent.parent.right
                if y.color == 'RED':
                    node.parent.color = 'BLACK'
                    y.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate(node)
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._right_rotate(node.parent.parent)
            else:
                y = node.parent.parent.left
                if y.color == 'RED':
                    node.parent.color = 'BLACK'
                    y.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate(node)
                    node.parent.color = 'BLACK'
                    node.parent.parent.color = 'RED'
                    self._left_rotate(node.parent.parent)
        self.root.color = 'BLACK'
    
    def search(self, val):
        """搜索节点"""
        node = self.root
        while node != self.NIL and val != node.val:
            if val < node.val:
                node = node.left
            else:
                node = node.right
        return node if node != self.NIL else None
    
    def inorder(self):
        """中序遍历"""
        result = []
        def _inorder(node):
            if node != self.NIL:
                _inorder(node.left)
                result.append((node.val, node.color))
                _inorder(node.right)
        _inorder(self.root)
        return result
    
    def _transplant(self, u, v):
        """替换子树"""
        if u.parent == self.NIL:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent
    
    def _minimum(self, node):
        """找最小节点"""
        while node.left != self.NIL:
            node = node.left
        return node
    
    def delete(self, val):
        """删除节点"""
        z = self.search(val)
        if not z:
            return False
        
        y = z
        y_original_color = y.color
        
        if z.left == self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        
        if y_original_color == 'BLACK':
            self._delete_fixup(x)
        return True
    
    def _delete_fixup(self, x):
        """删除修复"""
        while x != self.root and x.color == 'BLACK':
            if x == x.parent.left:
                w = x.parent.right
                if w.color == 'RED':
                    w.color = 'BLACK'
                    x.parent.color = 'RED'
                    self._left_rotate(x.parent)
                    w = x.parent.right
                if w.left.color == 'BLACK' and w.right.color == 'BLACK':
                    w.color = 'RED'
                    x = x.parent
                else:
                    if w.right.color == 'BLACK':
                        w.left.color = 'BLACK'
                        w.color = 'RED'
                        self._right_rotate(w)
                        w = x.parent.right
                    w.color = x.parent.color
                    x.parent.color = 'BLACK'
                    w.right.color = 'BLACK'
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == 'RED':
                    w.color = 'BLACK'
                    x.parent.color = 'RED'
                    self._right_rotate(x.parent)
                    w = x.parent.left
                if w.right.color == 'BLACK' and w.left.color == 'BLACK':
                    w.color = 'RED'
                    x = x.parent
                else:
                    if w.left.color == 'BLACK':
                        w.right.color = 'BLACK'
                        w.color = 'RED'
                        self._left_rotate(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = 'BLACK'
                    w.left.color = 'BLACK'
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = 'BLACK'

# 测试红黑树
def test_red_black_tree():
    print("=== 红黑树测试 ===")
    rbt = RedBlackTree()
    
    # 插入测试
    values = [7, 3, 18, 10, 22, 8, 11, 26]
    for val in values:
        rbt.insert(val)
    
    inorder_result = rbt.inorder()
    values_only = [v[0] for v in inorder_result]
    assert values_only == sorted(values), f"中序遍历应该有序: {values_only}"
    print(f"✓ 插入后中序遍历: {values_only}")
    
    # 搜索测试
    assert rbt.search(10) is not None, "应该找到10"
    assert rbt.search(100) is None, "不应该找到100"
    print("✓ 搜索测试通过")
    
    # 删除测试
    rbt.delete(18)
    inorder_result = rbt.inorder()
    values_only = [v[0] for v in inorder_result]
    expected = sorted([7, 3, 10, 22, 8, 11, 26])
    assert values_only == expected, f"删除18后失败: {values_only}"
    print(f"✓ 删除18后中序遍历: {values_only}")
    
    # 验证红黑树性质（简化：检查根是黑色）
    assert rbt.root.color == 'BLACK', "根节点应该是黑色"
    print("✓ 红黑树性质验证通过")
    print()

test_red_black_tree()
```

---

## 5. B树（B-Tree）

```python
class BTreeNode:
    """B树节点"""
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf

class BTree:
    """B树实现"""
    def __init__(self, t=3):
        """
        t: 最小度数
        - 每个节点最多有 2t-1 个关键字
        - 每个非根节点至少有 t-1 个关键字
        - 每个节点最多有 2t 个孩子
        - 每个非根节点至少有 t 个孩子
        """
        self.t = t
        self.root = BTreeNode(leaf=True)
    
    def search(self, key, node=None):
        """搜索关键字"""
        if node is None:
            node = self.root
        
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        elif node.leaf:
            return None
        else:
            return self.search(key, node.children[i])
    
    def insert(self, key):
        """插入关键字"""
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode()
            new_root.children.append(self.root)
            self.root = new_root
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key)
        else:
            self._insert_non_full(root, key)
    
    def _split_child(self, parent, index):
        """分裂子节点"""
        t = self.t
        y = parent.children[index]
        z = BTreeNode(leaf=y.leaf)
        
        # 将y的中间关键字提升到parent
        parent.keys.insert(index, y.keys[t - 1])
        
        # z获取y的后半部分关键字和孩子
        z.keys = y.keys[t:(2 * t - 1)]
        if not y.leaf:
            z.children = y.children[t:(2 * t)]
        
        # y只保留前半部分
        y.keys = y.keys[0:(t - 1)]
        if not y.leaf:
            y.children = y.children[0:t]
        
        parent.children.insert(index + 1, z)
    
    def _insert_non_full(self, node, key):
        """向非满节点插入关键字"""
        i = len(node.keys) - 1
        
        if node.leaf:
            # 找到插入位置并插入
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            # 找到合适的子节点
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # 如果子节点已满，先分裂
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key)
    
    def delete(self, key):
        """删除关键字"""
        self._delete(self.root, key)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
    
    def _delete(self, node, key):
        """删除辅助函数"""
        t = self.t
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if node.leaf:
            # 情况1：关键字在叶子节点中
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
                return True
            return False
        
        if i < len(node.keys) and node.keys[i] == key:
            # 情况2：关键字在内部节点中
            if len(node.children[i].keys) >= t:
                # 2a: 前驱
                pred = self._get_predecessor(node.children[i])
                node.keys[i] = pred
                self._delete(node.children[i], pred)
            elif len(node.children[i + 1].keys) >= t:
                # 2b: 后继
                succ = self._get_successor(node.children[i + 1])
                node.keys[i] = succ
                self._delete(node.children[i + 1], succ)
            else:
                # 2c: 合并
                self._merge(node, i)
                self._delete(node.children[i], key)
        else:
            # 情况3：关键字不在当前节点
            if len(node.children[i].keys) == t - 1:
                self._fill(node, i)
            if i > len(node.keys):
                self._delete(node.children[i - 1], key)
            else:
                self._delete(node.children[i], key)
    
    def _get_predecessor(self, node):
        """获取前驱"""
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]
    
    def _get_successor(self, node):
        """获取后继"""
        while not node.leaf:
            node = node.children[0]
        return node.keys[0]
    
    def _merge(self, parent, index):
        """合并子节点"""
        child = parent.children[index]
        sibling = parent.children[index + 1]
        
        # 将父节点的关键字下移
        child.keys.append(parent.keys[index])
        
        # 复制兄弟节点的关键字
        child.keys.extend(sibling.keys)
        
        # 复制兄弟节点的孩子
        if not child.leaf:
            child.children.extend(sibling.children)
        
        # 从父节点移除关键字和孩子指针
        parent.keys.pop(index)
        parent.children.pop(index + 1)
    
    def _fill(self, node, index):
        """确保子节点有足够的关键字"""
        t = self.t
        
        if index != 0 and len(node.children[index - 1].keys) >= t:
            self._borrow_from_prev(node, index)
        elif index != len(node.keys) and len(node.children[index + 1].keys) >= t:
            self._borrow_from_next(node, index)
        else:
            if index != len(node.keys):
                self._merge(node, index)
            else:
                self._merge(node, index - 1)
    
    def _borrow_from_prev(self, node, index):
        """从前一个兄弟借关键字"""
        child = node.children[index]
        sibling = node.children[index - 1]
        
        child.keys.insert(0, node.keys[index - 1])
        node.keys[index - 1] = sibling.keys.pop()
        
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
    
    def _borrow_from_next(self, node, index):
        """从后一个兄弟借关键字"""
        child = node.children[index]
        sibling = node.children[index + 1]
        
        child.keys.append(node.keys[index])
        node.keys[index] = sibling.keys.pop(0)
        
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
    
    def inorder(self):
        """中序遍历"""
        result = []
        def _inorder(node):
            i = 0
            while i < len(node.keys):
                if not node.leaf:
                    _inorder(node.children[i])
                result.append(node.keys[i])
                i += 1
            if not node.leaf:
                _inorder(node.children[i])
        _inorder(self.root)
        return result
    
    def traverse(self):
        """层序遍历"""
        result = []
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            result.append(node.keys[:])
            if not node.leaf:
                queue.extend(node.children)
        return result

# 测试B树
def test_btree():
    print("=== B树测试 ===")
    btree = BTree(t=3)  # 2-3-4树
    
    # 插入测试
    values = [10, 20, 5, 6, 12, 30, 7, 17]
    for val in values:
        btree.insert(val)
    
    inorder = btree.inorder()
    assert inorder == sorted(values), f"中序遍历应该有序: {inorder}"
    print(f"✓ 插入后中序遍历: {inorder}")
    print(f"  层序结构: {btree.traverse()}")
    
    # 搜索测试
    assert btree.search(6) is not None, "应该找到6"
    assert btree.search(100) is None, "不应该找到100"
    print("✓ 搜索测试通过")
    
    # 删除测试
    btree.delete(6)
    inorder = btree.inorder()
    expected = sorted([10, 20, 5, 12, 30, 7, 17])
    assert inorder == expected, f"删除6后失败: {inorder}"
    print(f"✓ 删除6后中序遍历: {inorder}")
    print(f"  层序结构: {btree.traverse()}")
    print()

test_btree()
```

---

## 总结

本文档实现了5种核心数据结构：

| 数据结构 | 时间复杂度（平均） | 空间复杂度 | 特点 |
|---------|------------------|-----------|------|
| 单向链表 | O(n) 查找/删除 | O(n) | 简单，单向遍历 |
| 双向链表 | O(n) 查找/删除 | O(n) | 双向遍历，更灵活 |
| 栈 | O(1) 压栈/弹栈 | O(n) | LIFO，递归、表达式求值 |
| 队列 | O(1) 入队/出队 | O(n) | FIFO，BFS、任务调度 |
| 二叉堆 | O(log n) 插入/提取 | O(n) | 优先队列，堆排序 |
| 红黑树 | O(log n) 增删查 | O(n) | 自平衡，高效查找 |
| B树 | O(log n) 增删查 | O(n) | 多路平衡，磁盘存储友好 |

所有实现都包含完整的操作方法和测试用例。
