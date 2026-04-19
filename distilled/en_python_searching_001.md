# Python Searching Algorithms - Complete Guide

## Overview

Searching algorithms are fundamental to computer science, enabling efficient location of elements within data structures. This guide covers various searching techniques from basic linear search to advanced algorithms with practical Python implementations.

---

## 1. Linear Search

### Basic Implementation
```python
def linear_search(arr, target):
    """
    Search for target in array sequentially.
    Time: O(n), Space: O(1)
    """
    for i, element in enumerate(arr):
        if element == target:
            return i
    return -1

# Example
data = [4, 2, 7, 1, 9, 5]
print(linear_search(data, 7))  # Output: 2
print(linear_search(data, 3))  # Output: -1
```

### Linear Search with Condition
```python
def linear_search_custom(arr, predicate):
    """Find first element matching predicate."""
    for i, element in enumerate(arr):
        if predicate(element):
            return i, element
    return None

# Find first even number
data = [1, 3, 5, 4, 7, 8]
result = linear_search_custom(data, lambda x: x % 2 == 0)
print(result)  # (3, 4)
```

---

## 2. Binary Search

### Iterative Implementation
```python
def binary_search(arr, target):
    """
    Search sorted array using divide and conquer.
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Example
sorted_data = [1, 2, 4, 5, 7, 8, 9]
print(binary_search(sorted_data, 5))  # Output: 3
print(binary_search(sorted_data, 6))  # Output: -1
```

### Recursive Implementation
```python
def binary_search_recursive(arr, target, left=0, right=None):
    """Recursive binary search implementation."""
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)
```

### Binary Search Variants

#### Find First Occurrence
```python
def find_first_occurrence(arr, target):
    """Find index of first occurrence of target."""
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

# Example with duplicates
data = [1, 2, 2, 2, 3, 4, 5]
print(find_first_occurrence(data, 2))  # Output: 1
```

#### Find Last Occurrence
```python
def find_last_occurrence(arr, target):
    """Find index of last occurrence of target."""
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            left = mid + 1  # Continue searching right
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

data = [1, 2, 2, 2, 3, 4, 5]
print(find_last_occurrence(data, 2))  # Output: 3
```

---

## 3. Jump Search

```python
import math

def jump_search(arr, target):
    """
    Search by jumping ahead by fixed steps.
    Time: O(√n), Space: O(1)
    """
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0
    
    # Find the block where element is present
    while arr[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1
    
    # Linear search in the found block
    while arr[prev] < target:
        prev += 1
        if prev == min(step, n):
            return -1
    
    if arr[prev] == target:
        return prev
    
    return -1

sorted_data = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
print(jump_search(sorted_data, 15))  # Output: 7
```

---

## 4. Interpolation Search

```python
def interpolation_search(arr, target):
    """
    Search using value-based position estimation.
    Best for uniformly distributed data.
    Average: O(log log n), Worst: O(n)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right and arr[left] <= target <= arr[right]:
        if left == right:
            if arr[left] == target:
                return left
            return -1
        
        # Estimate position
        pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            left = pos + 1
        else:
            right = pos - 1
    
    return -1

# Works best with uniform distribution
uniform_data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print(interpolation_search(uniform_data, 70))  # Output: 6
```

---

## 5. Exponential Search

```python
def exponential_search(arr, target):
    """
    Search by doubling range, then binary search.
    Time: O(log n), Space: O(1)
    Good for unbounded/infinite arrays.
    """
    n = len(arr)
    
    if arr[0] == target:
        return 0
    
    # Find range for binary search
    i = 1
    while i < n and arr[i] <= target:
        i *= 2
    
    # Binary search in found range
    return binary_search_range(arr, target, i // 2, min(i, n - 1))

def binary_search_range(arr, target, left, right):
    """Binary search within specific range."""
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

sorted_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
print(exponential_search(sorted_data, 10))  # Output: 9
```

---

## 6. Ternary Search

```python
def ternary_search(arr, target):
    """
    Divide array into three parts.
    Time: O(log₃ n), but more comparisons than binary search.
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid1 = left + (right - left) // 3
        mid2 = right - (right - left) // 3
        
        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2
        
        if target < arr[mid1]:
            right = mid1 - 1
        elif target > arr[mid2]:
            left = mid2 + 1
        else:
            left = mid1 + 1
            right = mid2 - 1
    
    return -1

sorted_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(ternary_search(sorted_data, 5))  # Output: 4
```

---

## 7. Search in Rotated Sorted Array

```python
def search_rotated(arr, target):
    """
    Search in rotated sorted array.
    Time: O(log n)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        
        # Left half is sorted
        if arr[left] <= arr[mid]:
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1

rotated = [4, 5, 6, 7, 0, 1, 2]
print(search_rotated(rotated, 0))  # Output: 4
print(search_rotated(rotated, 3))  # Output: -1
```

---

## 8. Fibonacci Search

```python
def fibonacci_search(arr, target):
    """
    Search using Fibonacci numbers for division.
    Time: O(log n), Space: O(1)
    """
    n = len(arr)
    
    # Find smallest Fibonacci number >= n
    fib2 = 0
    fib1 = 1
    fib = fib2 + fib1
    
    while fib < n:
        fib2 = fib1
        fib1 = fib
        fib = fib2 + fib1
    
    offset = -1
    
    while fib > 1:
        i = min(offset + fib2, n - 1)
        
        if arr[i] < target:
            fib = fib1
            fib1 = fib2
            fib2 = fib - fib1
            offset = i
        elif arr[i] > target:
            fib = fib2
            fib1 = fib1 - fib2
            fib2 = fib - fib1
        else:
            return i
    
    if fib1 and offset + 1 < n and arr[offset + 1] == target:
        return offset + 1
    
    return -1

sorted_data = [10, 22, 35, 40, 45, 50, 80, 82, 85, 90, 100]
print(fibonacci_search(sorted_data, 85))  # Output: 8
```

---

## 9. Hash-based Search

```python
class SearchIndex:
    """Build hash index for O(1) lookups."""
    
    def __init__(self, arr):
        self.index = {}
        for i, element in enumerate(arr):
            if element not in self.index:
                self.index[element] = []
            self.index[element].append(i)
    
    def search(self, target):
        """O(1) lookup."""
        return self.index.get(target, [])
    
    def exists(self, target):
        """Check existence."""
        return target in self.index

# Usage
data = [1, 2, 3, 2, 4, 2, 5]
search_idx = SearchIndex(data)

print(search_idx.search(2))     # [1, 3, 5] - all positions
print(search_idx.search(6))     # [] - not found
print(search_idx.exists(3))     # True
```

---

## 10. String Search Algorithms

### Naive String Search
```python
def naive_string_search(text, pattern):
    """Simple O(n*m) string search."""
    n, m = len(text), len(pattern)
    matches = []
    
    for i in range(n - m + 1):
        if text[i:i+m] == pattern:
            matches.append(i)
    
    return matches

text = "ABABABCABABABCABABABC"
pattern = "ABABC"
print(naive_string_search(text, pattern))  # [2, 9, 16]
```

### KMP Algorithm
```python
def kmp_search(text, pattern):
    """
    Knuth-Morris-Pratt algorithm.
    Time: O(n + m)
    """
    def compute_lps(pattern):
        """Compute Longest Proper Prefix which is also Suffix."""
        m = len(pattern)
        lps = [0] * m
        length = 0
        i = 1
        
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        
        return lps
    
    n, m = len(text), len(pattern)
    if m == 0:
        return []
    
    lps = compute_lps(pattern)
    matches = []
    i = j = 0
    
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            
            if j == m:
                matches.append(i - j)
                j = lps[j - 1]
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return matches

text = "ABABDABACDABABCABAB"
pattern = "ABABCABAB"
print(kmp_search(text, pattern))  # [10]
```

---

## 11. Search in 2D Matrix

```python
def search_2d_matrix(matrix, target):
    """
    Search in row-wise and column-wise sorted matrix.
    Time: O(m + n)
    """
    if not matrix or not matrix[0]:
        return False
    
    rows, cols = len(matrix), len(matrix[0])
    row, col = 0, cols - 1  # Start from top-right
    
    while row < rows and col >= 0:
        if matrix[row][col] == target:
            return (row, col)
        elif matrix[row][col] < target:
            row += 1
        else:
            col -= 1
    
    return None

matrix = [
    [1,  4,  7, 11],
    [2,  5,  8, 12],
    [3,  6,  9, 16],
    [10, 13, 14, 17]
]
print(search_2d_matrix(matrix, 5))  # (1, 1)
print(search_2d_matrix(matrix, 15))  # None
```

---

## 12. BST Search

```python
class TreeNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        """Insert value into BST."""
        if not self.root:
            self.root = TreeNode(val)
            return
        
        self._insert_recursive(self.root, val)
    
    def _insert_recursive(self, node, val):
        if val < node.val:
            if node.left is None:
                node.left = TreeNode(val)
            else:
                self._insert_recursive(node.left, val)
        else:
            if node.right is None:
                node.right = TreeNode(val)
            else:
                self._insert_recursive(node.right, val)
    
    def search(self, val):
        """Search for value in BST. O(log n) average, O(n) worst."""
        return self._search_recursive(self.root, val)
    
    def _search_recursive(self, node, val):
        if node is None:
            return False
        
        if val == node.val:
            return True
        elif val < node.val:
            return self._search_recursive(node.left, val)
        else:
            return self._search_recursive(node.right, val)

# Usage
bst = BST()
for val in [50, 30, 70, 20, 40, 60, 80]:
    bst.insert(val)

print(bst.search(40))  # True
print(bst.search(45))  # False
```

---

## 13. Performance Comparison

```python
import time
import random

def benchmark_search_algorithms(size=10000):
    """Compare search algorithm performance."""
    sorted_data = list(range(size))
    target = random.randint(0, size - 1)
    
    algorithms = [
        ("Linear Search", lambda: linear_search(sorted_data, target)),
        ("Binary Search", lambda: binary_search(sorted_data, target)),
        ("Jump Search", lambda: jump_search(sorted_data, target)),
        ("Interpolation Search", lambda: interpolation_search(sorted_data, target)),
        ("Exponential Search", lambda: exponential_search(sorted_data, target)),
    ]
    
    print(f"Searching for {target} in array of {size} elements:\n")
    print(f"{'Algorithm':<25} {'Time (ms)':<15} {'Found Index'}")
    print("-" * 55)
    
    for name, search_func in algorithms:
        start = time.perf_counter()
        result = search_func()
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{name:<25} {elapsed:<15.4f} {result}")

# Run benchmark
benchmark_search_algorithms()
```

---

## 14. Practical Applications

### Search in Dictionary
```python
class Dictionary:
    """Efficient dictionary word lookup."""
    
    def __init__(self, words):
        self.words = sorted(words)
        self.index = SearchIndex(self.words)
    
    def lookup(self, word):
        """Binary search for word."""
        return binary_search(self.words, word) != -1
    
    def prefix_search(self, prefix):
        """Find all words with given prefix."""
        matches = []
        for word in self.words:
            if word.startswith(prefix):
                matches.append(word)
        return matches
    
    def autocomplete(self, prefix, limit=10):
        """Autocomplete suggestions."""
        return self.prefix_search(prefix)[:limit]

words = ["apple", "banana", "cherry", "date", "grape", "orange"]
dictionary = Dictionary(words)
print(dictionary.lookup("cherry"))  # True
print(dictionary.autocomplete("a"))  # ['apple']
```

---

## 15. Summary Table

| Algorithm | Time (Best) | Time (Avg) | Time (Worst) | Space | Requirement |
|-----------|-------------|------------|--------------|-------|-------------|
| Linear Search | O(1) | O(n) | O(n) | O(1) | None |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) | Sorted |
| Jump Search | O(1) | O(√n) | O(√n) | O(1) | Sorted |
| Interpolation | O(1) | O(log log n) | O(n) | O(1) | Sorted + Uniform |
| Exponential | O(1) | O(log n) | O(log n) | O(1) | Sorted |
| Ternary | O(1) | O(log₃ n) | O(log₃ n) | O(1) | Sorted |
| Hash-based | O(1) | O(1) | O(n) | O(n) | None |
| KMP | O(m) | O(n+m) | O(n+m) | O(m) | None |

---

## Best Practices

1. **Choose based on data**: Use binary search for sorted data, linear for small unsorted arrays
2. **Consider preprocessing**: Build hash indices for frequent lookups
3. **Handle edge cases**: Empty arrays, single elements, duplicates
4. **Optimize for access patterns**: Cache-friendly algorithms for large datasets
5. **Profile in practice**: Real-world performance depends on data distribution
