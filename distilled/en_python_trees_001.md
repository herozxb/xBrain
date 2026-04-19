# Python Trees - Comprehensive Guide

## Overview

Trees are hierarchical data structures consisting of nodes connected by edges, with a single root node at the top. This guide covers various tree types and operations in Python.

## 1. Binary Tree Implementation

```python
from typing import Optional, List, Any
from collections import deque

class TreeNode:
    """Binary tree node"""
    def __init__(self, val: Any = 0, left: Optional['TreeNode'] = None, right: Optional['TreeNode'] = None):
        self.val = val
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"TreeNode({self.val})"

class BinaryTree:
    """Binary tree with common operations"""
    
    def __init__(self, root: Optional[TreeNode] = None):
        self.root = root
    
    # Traversals
    def inorder(self, node: Optional[TreeNode] = None) -> List[Any]:
        """Left -> Root -> Right"""
        result = []
        node = node or self.root
        
        def _inorder(n):
            if n:
                _inorder(n.left)
                result.append(n.val)
                _inorder(n.right)
        
        _inorder(node)
        return result
    
    def preorder(self, node: Optional[TreeNode] = None) -> List[Any]:
        """Root -> Left -> Right"""
        result = []
        node = node or self.root
        
        def _preorder(n):
            if n:
                result.append(n.val)
                _preorder(n.left)
                _preorder(n.right)
        
        _preorder(node)
        return result
    
    def postorder(self, node: Optional[TreeNode] = None) -> List[Any]:
        """Left -> Right -> Root"""
        result = []
        node = node or self.root
        
        def _postorder(n):
            if n:
                _postorder(n.left)
                _postorder(n.right)
                result.append(n.val)
        
        _postorder(node)
        return result
    
    def level_order(self) -> List[List[Any]]:
        """BFS traversal level by level"""
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            level = []
            size = len(queue)
            
            for _ in range(size):
                node = queue.popleft()
                level.append(node.val)
                
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            
            result.append(level)
        
        return result
    
    # Tree Properties
    def height(self, node: Optional[TreeNode] = None) -> int:
        """Calculate tree height"""
        node = node or self.root
        if not node:
            return -1
        return 1 + max(self.height(node.left), self.height(node.right))
    
    def size(self, node: Optional[TreeNode] = None) -> int:
        """Count total nodes"""
        node = node or self.root
        if not node:
            return 0
        return 1 + self.size(node.left) + self.size(node.right)
    
    def is_balanced(self, node: Optional[TreeNode] = None) -> bool:
        """Check if tree is height-balanced"""
        node = node or self.root
        
        def _check(n):
            if not n:
                return 0, True
            
            left_height, left_balanced = _check(n.left)
            right_height, right_balanced = _check(n.right)
            
            balanced = (left_balanced and right_balanced and 
                       abs(left_height - right_height) <= 1)
            
            return max(left_height, right_height) + 1, balanced
        
        _, balanced = _check(node)
        return balanced
```

## 2. Binary Search Tree (BST)

```python
class BST(TreeNode):
    """Binary Search Tree with search, insert, delete operations"""
    
    def __init__(self, val: Any = None):
        super().__init__(val)
    
    def search(self, val: Any) -> Optional['BST']:
        """Search for a value in BST"""
        if not self.val or val == self.val:
            return self if self.val == val else None
        
        if val < self.val:
            return self.left.search(val) if self.left else None
        else:
            return self.right.search(val) if self.right else None
    
    def insert(self, val: Any) -> None:
        """Insert value maintaining BST property"""
        if not self.val:
            self.val = val
            return
        
        if val < self.val:
            if self.left:
                self.left.insert(val)
            else:
                self.left = BST(val)
        elif val > self.val:
            if self.right:
                self.right.insert(val)
            else:
                self.right = BST(val)
    
    def delete(self, val: Any) -> Optional['BST']:
        """Delete node and return new root"""
        if not self.val:
            return None
        
        if val < self.val:
            if self.left:
                self.left = self.left.delete(val)
        elif val > self.val:
            if self.right:
                self.right = self.right.delete(val)
        else:
            # Node found
            if not self.left:
                return self.right
            if not self.right:
                return self.left
            
            # Node with two children: get inorder successor
            min_node = self._find_min(self.right)
            self.val = min_node.val
            self.right = self.right.delete(min_node.val)
        
        return self
    
    def _find_min(self, node: 'BST') -> 'BST':
        """Find minimum value node"""
        current = node
        while current.left:
            current = current.left
        return current
    
    def validate(self) -> bool:
        """Check if tree is valid BST"""
        def _validate(node, min_val, max_val):
            if not node:
                return True
            if min_val is not None and node.val <= min_val:
                return False
            if max_val is not None and node.val >= max_val:
                return False
            return (_validate(node.left, min_val, node.val) and
                   _validate(node.right, node.val, max_val))
        
        return _validate(self, None, None)
```

## 3. AVL Tree (Self-Balancing BST)

```python
class AVLNode:
    """AVL tree node with height tracking"""
    def __init__(self, val: Any):
        self.val = val
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height = 1

class AVLTree:
    """Self-balancing AVL tree"""
    
    def __init__(self):
        self.root: Optional[AVLNode] = None
    
    def get_height(self, node: Optional[AVLNode]) -> int:
        """Get node height"""
        return node.height if node else 0
    
    def get_balance(self, node: Optional[AVLNode]) -> int:
        """Get balance factor"""
        return self.get_height(node.left) - self.get_height(node.right) if node else 0
    
    def update_height(self, node: AVLNode) -> None:
        """Update node height"""
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
    
    def rotate_right(self, y: AVLNode) -> AVLNode:
        """Right rotation"""
        x = y.left
        T2 = x.right
        
        x.right = y
        y.left = T2
        
        self.update_height(y)
        self.update_height(x)
        
        return x
    
    def rotate_left(self, x: AVLNode) -> AVLNode:
        """Left rotation"""
        y = x.right
        T2 = y.left
        
        y.left = x
        x.right = T2
        
        self.update_height(x)
        self.update_height(y)
        
        return y
    
    def insert(self, val: Any) -> None:
        """Insert value with automatic balancing"""
        self.root = self._insert(self.root, val)
    
    def _insert(self, node: Optional[AVLNode], val: Any) -> AVLNode:
        # Standard BST insert
        if not node:
            return AVLNode(val)
        
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        else:
            return node  # Duplicates not allowed
        
        # Update height
        self.update_height(node)
        
        # Get balance factor
        balance = self.get_balance(node)
        
        # Left Left Case
        if balance > 1 and val < node.left.val:
            return self.rotate_right(node)
        
        # Right Right Case
        if balance < -1 and val > node.right.val:
            return self.rotate_left(node)
        
        # Left Right Case
        if balance > 1 and val > node.left.val:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        
        # Right Left Case
        if balance < -1 and val < node.right.val:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        
        return node
```

## 4. N-ary Tree (General Tree)

```python
from typing import List

class NaryNode:
    """N-ary tree node"""
    def __init__(self, val: Any = None, children: List['NaryNode'] = None):
        self.val = val
        self.children = children if children is not None else []

class NaryTree:
    """General tree with unlimited children"""
    
    def __init__(self, root: Optional[NaryNode] = None):
        self.root = root
    
    def preorder(self) -> List[Any]:
        """Preorder traversal: Root -> Children"""
        result = []
        
        def _traverse(node):
            if node:
                result.append(node.val)
                for child in node.children:
                    _traverse(child)
        
        _traverse(self.root)
        return result
    
    def postorder(self) -> List[Any]:
        """Postorder traversal: Children -> Root"""
        result = []
        
        def _traverse(node):
            if node:
                for child in node.children:
                    _traverse(child)
                result.append(node.val)
        
        _traverse(self.root)
        return result
    
    def level_order(self) -> List[List[Any]]:
        """Level order traversal"""
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            level = []
            size = len(queue)
            
            for _ in range(size):
                node = queue.popleft()
                level.append(node.val)
                queue.extend(node.children)
            
            result.append(level)
        
        return result
    
    def max_depth(self) -> int:
        """Calculate maximum depth"""
        def _depth(node):
            if not node:
                return 0
            if not node.children:
                return 1
            return 1 + max(_depth(child) for child in node.children)
        
        return _depth(self.root)
```

## 5. Trie (Prefix Tree)

```python
class TrieNode:
    """Trie node"""
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    """Prefix tree for string operations"""
    
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        """Insert word into trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word: str) -> bool:
        """Check if word exists"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    
    def starts_with(self, prefix: str) -> bool:
        """Check if prefix exists"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
    
    def get_words_with_prefix(self, prefix: str) -> List[str]:
        """Get all words starting with prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        words = []
        self._collect_words(node, prefix, words)
        return words
    
    def _collect_words(self, node: TrieNode, prefix: str, words: List[str]) -> None:
        """Helper to collect all words from node"""
        if node.is_end:
            words.append(prefix)
        
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, words)
```

## 6. Segment Tree (Range Queries)

```python
class SegmentTree:
    """Segment tree for range sum queries"""
    
    def __init__(self, data: List[int]):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.build(data, 0, 0, self.n - 1)
    
    def build(self, data: List[int], node: int, start: int, end: int) -> None:
        """Build segment tree"""
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self.build(data, 2 * node + 1, start, mid)
            self.build(data, 2 * node + 2, mid + 1, end)
            self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]
    
    def update(self, idx: int, val: int) -> None:
        """Update value at index"""
        self._update(0, 0, self.n - 1, idx, val)
    
    def _update(self, node: int, start: int, end: int, idx: int, val: int) -> None:
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self._update(2 * node + 1, start, mid, idx, val)
            else:
                self._update(2 * node + 2, mid + 1, end, idx, val)
            self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]
    
    def query(self, l: int, r: int) -> int:
        """Range sum query [l, r]"""
        return self._query(0, 0, self.n - 1, l, r)
    
    def _query(self, node: int, start: int, end: int, l: int, r: int) -> int:
        if r < start or end < l:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        
        mid = (start + end) // 2
        left_sum = self._query(2 * node + 1, start, mid, l, r)
        right_sum = self._query(2 * node + 2, mid + 1, end, l, r)
        return left_sum + right_sum
```

## Usage Examples

```python
# Binary Tree
bt = BinaryTree()
bt.root = TreeNode(1)
bt.root.left = TreeNode(2)
bt.root.right = TreeNode(3)
bt.root.left.left = TreeNode(4)
bt.root.left.right = TreeNode(5)

print("Inorder:", bt.inorder())  # [4, 2, 5, 1, 3]
print("Level order:", bt.level_order())  # [[1], [2, 3], [4, 5]]
print("Height:", bt.height())  # 2

# BST
bst = BST(10)
bst.insert(5)
bst.insert(15)
bst.insert(3)
bst.insert(7)
print("Search 7:", bst.search(7))  # Found
print("Is valid BST:", bst.validate())  # True

# Trie
trie = Trie()
trie.insert("apple")
trie.insert("app")
print("Search 'app':", trie.search("app"))  # True
print("Starts with 'ap':", trie.starts_with("ap"))  # True
print("Words with prefix 'app':", trie.get_words_with_prefix("app"))  # ['app', 'apple']

# Segment Tree
data = [1, 3, 5, 7, 9, 11]
st = SegmentTree(data)
print("Sum [1, 3]:", st.query(1, 3))  # 15 (3+5+7)
st.update(1, 10)
print("Sum [1, 3] after update:", st.query(1, 3))  # 22 (10+5+7)
```

## Key Points

1. **Binary Trees**: Basic hierarchical structure with left/right children
2. **BST**: Ordered binary tree enabling O(log n) search/insert/delete
3. **AVL Tree**: Self-balancing BST maintaining O(log n) operations
4. **N-ary Tree**: General tree with unlimited children per node
5. **Trie**: Efficient for prefix-based string searches
6. **Segment Tree**: Enables O(log n) range queries and updates

## Time Complexities

| Operation | Binary Tree | BST (balanced) | Trie | Segment Tree |
|-----------|-------------|----------------|------|--------------|
| Search | O(n) | O(log n) | O(m) | O(log n) |
| Insert | O(n) | O(log n) | O(m) | O(log n) |
| Delete | O(n) | O(log n) | O(m) | O(log n) |
| Traversal | O(n) | O(n) | O(n) | - |
| Range Query | - | - | - | O(log n) |

*m = length of string/key*
