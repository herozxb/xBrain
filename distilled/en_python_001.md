# Python Algorithm Implementations

---

## Problem: Binary Search

### Solution

```python
def binary_search_iterative(arr, target):
    """
    Iterative binary search implementation.
    Returns the index of target if found, -1 otherwise.
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def binary_search_recursive(arr, target, left=0, right=None):
    """
    Recursive binary search implementation.
    Returns the index of target if found, -1 otherwise.
    """
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = left + (right - left) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)
```

### Tests

```python
import unittest

class TestBinarySearch(unittest.TestCase):
    def setUp(self):
        self.sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
    
    def test_iterative_found(self):
        self.assertEqual(binary_search_iterative(self.sorted_arr, 7), 3)
        self.assertEqual(binary_search_iterative(self.sorted_arr, 1), 0)
        self.assertEqual(binary_search_iterative(self.sorted_arr, 15), 7)
    
    def test_iterative_not_found(self):
        self.assertEqual(binary_search_iterative(self.sorted_arr, 4), -1)
        self.assertEqual(binary_search_iterative(self.sorted_arr, 0), -1)
        self.assertEqual(binary_search_iterative(self.sorted_arr, 20), -1)
    
    def test_recursive_found(self):
        self.assertEqual(binary_search_recursive(self.sorted_arr, 7), 3)
        self.assertEqual(binary_search_recursive(self.sorted_arr, 1), 0)
        self.assertEqual(binary_search_recursive(self.sorted_arr, 15), 7)
    
    def test_recursive_not_found(self):
        self.assertEqual(binary_search_recursive(self.sorted_arr, 4), -1)
        self.assertEqual(binary_search_recursive(self.sorted_arr, 0), -1)
        self.assertEqual(binary_search_recursive(self.sorted_arr, 20), -1)
    
    def test_empty_array(self):
        self.assertEqual(binary_search_iterative([], 5), -1)
        self.assertEqual(binary_search_recursive([], 5), -1)
    
    def test_single_element(self):
        self.assertEqual(binary_search_iterative([5], 5), 0)
        self.assertEqual(binary_search_iterative([5], 3), -1)

if __name__ == '__main__':
    unittest.main()
```

### Complexity: Time O(log n), Space O(1) iterative / O(log n) recursive

---

## Problem: Merge Sort

### Solution

```python
def merge_sort(arr):
    """
    Merge sort implementation using divide and conquer.
    Returns a new sorted array.
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left, right):
    """
    Helper function to merge two sorted arrays.
    """
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result


def merge_sort_inplace(arr):
    """
    In-place merge sort implementation.
    """
    if len(arr) <= 1:
        return arr
    
    _merge_sort_helper(arr, 0, len(arr) - 1)
    return arr


def _merge_sort_helper(arr, left, right):
    if left < right:
        mid = left + (right - left) // 2
        _merge_sort_helper(arr, left, mid)
        _merge_sort_helper(arr, mid + 1, right)
        _merge(arr, left, mid, right)


def _merge(arr, left, mid, right):
    left_arr = arr[left:mid + 1]
    right_arr = arr[mid + 1:right + 1]
    
    i = j = 0
    k = left
    
    while i < len(left_arr) and j < len(right_arr):
        if left_arr[i] <= right_arr[j]:
            arr[k] = left_arr[i]
            i += 1
        else:
            arr[k] = right_arr[j]
            j += 1
        k += 1
    
    while i < len(left_arr):
        arr[k] = left_arr[i]
        i += 1
        k += 1
    
    while j < len(right_arr):
        arr[k] = right_arr[j]
        j += 1
        k += 1
```

### Tests

```python
import unittest
import random

class TestMergeSort(unittest.TestCase):
    def test_basic_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        sorted_arr = merge_sort(arr)
        self.assertEqual(sorted_arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_already_sorted(self):
        arr = [1, 2, 3, 4, 5]
        sorted_arr = merge_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_reverse_sorted(self):
        arr = [5, 4, 3, 2, 1]
        sorted_arr = merge_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_duplicates(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        sorted_arr = merge_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])
    
    def test_empty_array(self):
        self.assertEqual(merge_sort([]), [])
    
    def test_single_element(self):
        self.assertEqual(merge_sort([42]), [42])
    
    def test_negative_numbers(self):
        arr = [-3, -1, -7, -5, -2]
        sorted_arr = merge_sort(arr)
        self.assertEqual(sorted_arr, [-7, -5, -3, -2, -1])
    
    def test_mixed_numbers(self):
        arr = [0, -5, 3, -2, 8, -1]
        sorted_arr = merge_sort(arr)
        self.assertEqual(sorted_arr, [-5, -2, -1, 0, 3, 8])
    
    def test_inplace_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        merge_sort_inplace(arr)
        self.assertEqual(arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_random_arrays(self):
        for _ in range(10):
            arr = [random.randint(-100, 100) for _ in range(random.randint(0, 50))]
            sorted_arr = merge_sort(arr)
            self.assertEqual(sorted_arr, sorted(arr))

if __name__ == '__main__':
    unittest.main()
```

### Complexity: Time O(n log n), Space O(n)

---

## Problem: Quick Sort

### Solution

```python
def quick_sort(arr):
    """
    Quick sort implementation using Lomuto partition scheme.
    Returns a new sorted array.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    result = arr.copy()
    _quick_sort_helper(result, 0, len(result) - 1)
    return result


def _quick_sort_helper(arr, low, high):
    if low < high:
        pivot_index = partition(arr, low, high)
        _quick_sort_helper(arr, low, pivot_index - 1)
        _quick_sort_helper(arr, pivot_index + 1, high)


def partition(arr, low, high):
    """
    Lomuto partition scheme.
    """
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quick_sort_hoare(arr):
    """
    Quick sort using Hoare partition scheme.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    result = arr.copy()
    _quick_sort_hoare_helper(result, 0, len(result) - 1)
    return result


def _quick_sort_hoare_helper(arr, low, high):
    if low < high:
        pivot_index = partition_hoare(arr, low, high)
        _quick_sort_hoare_helper(arr, low, pivot_index)
        _quick_sort_hoare_helper(arr, pivot_index + 1, high)


def partition_hoare(arr, low, high):
    """
    Hoare partition scheme.
    """
    pivot = arr[low + (high - low) // 2]
    i = low - 1
    j = high + 1
    
    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        
        j -= 1
        while arr[j] > pivot:
            j -= 1
        
        if i >= j:
            return j
        
        arr[i], arr[j] = arr[j], arr[i]


def quick_sort_randomized(arr):
    """
    Quick sort with randomized pivot selection.
    """
    import random
    
    if len(arr) <= 1:
        return arr.copy()
    
    result = arr.copy()
    _quick_sort_randomized_helper(result, 0, len(result) - 1)
    return result


def _quick_sort_randomized_helper(arr, low, high):
    import random
    
    if low < high:
        # Randomize pivot
        random_index = random.randint(low, high)
        arr[random_index], arr[high] = arr[high], arr[random_index]
        
        pivot_index = partition(arr, low, high)
        _quick_sort_randomized_helper(arr, low, pivot_index - 1)
        _quick_sort_randomized_helper(arr, pivot_index + 1, high)
```

### Tests

```python
import unittest
import random

class TestQuickSort(unittest.TestCase):
    def test_basic_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        sorted_arr = quick_sort(arr)
        self.assertEqual(sorted_arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_already_sorted(self):
        arr = [1, 2, 3, 4, 5]
        sorted_arr = quick_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_reverse_sorted(self):
        arr = [5, 4, 3, 2, 1]
        sorted_arr = quick_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_duplicates(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        sorted_arr = quick_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])
    
    def test_empty_array(self):
        self.assertEqual(quick_sort([]), [])
    
    def test_single_element(self):
        self.assertEqual(quick_sort([42]), [42])
    
    def test_negative_numbers(self):
        arr = [-3, -1, -7, -5, -2]
        sorted_arr = quick_sort(arr)
        self.assertEqual(sorted_arr, [-7, -5, -3, -2, -1])
    
    def test_hoare_partition(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        sorted_arr = quick_sort_hoare(arr)
        self.assertEqual(sorted_arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_randomized_quick_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        sorted_arr = quick_sort_randomized(arr)
        self.assertEqual(sorted_arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_random_arrays(self):
        for _ in range(10):
            arr = [random.randint(-100, 100) for _ in range(random.randint(0, 50))]
            sorted_arr = quick_sort(arr)
            self.assertEqual(sorted_arr, sorted(arr))
    
    def test_original_unchanged(self):
        arr = [3, 1, 2]
        original = arr.copy()
        quick_sort(arr)
        self.assertEqual(arr, original)

if __name__ == '__main__':
    unittest.main()
```

### Complexity: Time O(n log n) average, O(n^2) worst case; Space O(log n) average

---

## Problem: Heap Sort

### Solution

```python
def heap_sort(arr):
    """
    Heap sort implementation using max-heap.
    Returns a new sorted array.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    result = arr.copy()
    n = len(result)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(result, n, i)
    
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        heapify(result, i, 0)
    
    return result


def heapify(arr, n, i):
    """
    Heapify subtree rooted at index i.
    n is the size of the heap.
    """
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    
    if left < n and arr[left] > arr[largest]:
        largest = left
    
    if right < n and arr[right] > arr[largest]:
        largest = right
    
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heap_sort_iterative(arr):
    """
    Heap sort with iterative heapify.
    """
    if len(arr) <= 1:
        return arr.copy()
    
    result = arr.copy()
    n = len(result)
    
    # Build max heap iteratively
    for i in range(n // 2 - 1, -1, -1):
        heapify_iterative(result, n, i)
    
    # Extract elements
    for i in range(n - 1, 0, -1):
        result[0], result[i] = result[i], result[0]
        heapify_iterative(result, i, 0)
    
    return result


def heapify_iterative(arr, n, i):
    """
    Iterative version of heapify.
    """
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest == i:
            break
        
        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest


class MinHeap:
    """
    Min-heap implementation for educational purposes.
    """
    
    def __init__(self):
        self.heap = []
    
    def insert(self, val):
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)
    
    def extract_min(self):
        if not self.heap:
            return None
        
        min_val = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heap.pop()
        
        if self.heap:
            self._sift_down(0)
        
        return min_val
    
    def _sift_up(self, i):
        parent = (i - 1) // 2
        while i > 0 and self.heap[i] < self.heap[parent]:
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            i = parent
            parent = (i - 1) // 2
    
    def _sift_down(self, i):
        n = len(self.heap)
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < n and self.heap[left] < self.heap[smallest]:
                smallest = left
            
            if right < n and self.heap[right] < self.heap[smallest]:
                smallest = right
            
            if smallest == i:
                break
            
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest
    
    def peek(self):
        return self.heap[0] if self.heap else None
    
    def size(self):
        return len(self.heap)
```

### Tests

```python
import unittest
import random

class TestHeapSort(unittest.TestCase):
    def test_basic_sort(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        sorted_arr = heap_sort(arr)
        self.assertEqual(sorted_arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_already_sorted(self):
        arr = [1, 2, 3, 4, 5]
        sorted_arr = heap_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_reverse_sorted(self):
        arr = [5, 4, 3, 2, 1]
        sorted_arr = heap_sort(arr)
        self.assertEqual(sorted_arr, [1, 2, 3, 4, 5])
    
    def test_duplicates(self):
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        sorted_arr = heap_sort(arr)
        self.assertEqual(sorted_arr, [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])
    
    def test_empty_array(self):
        self.assertEqual(heap_sort([]), [])
    
    def test_single_element(self):
        self.assertEqual(heap_sort([42]), [42])
    
    def test_negative_numbers(self):
        arr = [-3, -1, -7, -5, -2]
        sorted_arr = heap_sort(arr)
        self.assertEqual(sorted_arr, [-7, -5, -3, -2, -1])
    
    def test_iterative_version(self):
        arr = [64, 34, 25, 12, 22, 11, 90]
        sorted_arr = heap_sort_iterative(arr)
        self.assertEqual(sorted_arr, [11, 12, 22, 25, 34, 64, 90])
    
    def test_random_arrays(self):
        for _ in range(10):
            arr = [random.randint(-100, 100) for _ in range(random.randint(0, 50))]
            sorted_arr = heap_sort(arr)
            self.assertEqual(sorted_arr, sorted(arr))
    
    def test_original_unchanged(self):
        arr = [3, 1, 2]
        original = arr.copy()
        heap_sort(arr)
        self.assertEqual(arr, original)


class TestMinHeap(unittest.TestCase):
    def setUp(self):
        self.heap = MinHeap()
    
    def test_insert_extract(self):
        values = [5, 3, 7, 1, 9]
        for v in values:
            self.heap.insert(v)
        
        result = []
        while self.heap.size() > 0:
            result.append(self.heap.extract_min())
        
        self.assertEqual(result, [1, 3, 5, 7, 9])
    
    def test_peek(self):
        self.heap.insert(5)
        self.assertEqual(self.heap.peek(), 5)
        self.assertEqual(self.heap.size(), 1)
    
    def test_empty_heap(self):
        self.assertEqual(self.heap.extract_min(), None)
        self.assertEqual(self.heap.peek(), None)
    
    def test_single_element(self):
        self.heap.insert(42)
        self.assertEqual(self.heap.extract_min(), 42)
        self.assertEqual(self.heap.size(), 0)

if __name__ == '__main__':
    unittest.main()
```

### Complexity: Time O(n log n), Space O(1)

---

## Problem: Graph BFS and DFS

### Solution

```python
from collections import deque

def bfs(graph, start):
    """
    Breadth-First Search traversal.
    Returns list of nodes in BFS order.
    """
    if start not in graph:
        return []
    
    visited = set()
    result = []
    queue = deque([start])
    
    while queue:
        node = queue.popleft()
        
        if node not in visited:
            visited.add(node)
            result.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
    
    return result


def dfs(graph, start):
    """
    Depth-First Search traversal (iterative).
    Returns list of nodes in DFS order.
    """
    if start not in graph:
        return []
    
    visited = set()
    result = []
    stack = [start]
    
    while stack:
        node = stack.pop()
        
        if node not in visited:
            visited.add(node)
            result.append(node)
            
            # Add neighbors in reverse order for correct traversal
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return result


def dfs_recursive(graph, start, visited=None):
    """
    Depth-First Search traversal (recursive).
    Returns list of nodes in DFS order.
    """
    if start not in graph:
        return []
    
    if visited is None:
        visited = set()
    
    visited.add(start)
    result = [start]
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            result.extend(dfs_recursive(graph, neighbor, visited))
    
    return result


def bfs_shortest_path(graph, start, end):
    """
    Find shortest path using BFS.
    Returns the path as a list, or None if no path exists.
    """
    if start not in graph or end not in graph:
        return None
    
    if start == end:
        return [start]
    
    visited = {start}
    queue = deque([(start, [start])])
    
    while queue:
        node, path = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None


def dfs_has_path(graph, start, end, visited=None):
    """
    Check if path exists using DFS.
    """
    if start not in graph or end not in graph:
        return False
    
    if start == end:
        return True
    
    if visited is None:
        visited = set()
    
    visited.add(start)
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            if dfs_has_path(graph, neighbor, end, visited):
                return True
    
    return False


def bfs_level_order(graph, start):
    """
    BFS returning nodes grouped by level.
    """
    if start not in graph:
        return []
    
    visited = {start}
    queue = deque([start])
    levels = []
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        levels.append(current_level)
    
    return levels


def find_connected_components(graph):
    """
    Find all connected components using DFS.
    """
    visited = set()
    components = []
    
    for node in graph:
        if node not in visited:
            component = []
            stack = [node]
            
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    component.append(current)
                    stack.extend(graph[current])
            
            components.append(component)
    
    return components


def detect_cycle_dfs(graph):
    """
    Detect cycle in directed graph using DFS.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    
    def dfs_visit(node):
        color[node] = GRAY
        
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True
            if color[neighbor] == WHITE and dfs_visit(neighbor):
                return True
        
        color[node] = BLACK
        return False
    
    for node in graph:
        if color[node] == WHITE:
            if dfs_visit(node):
                return True
    
    return False
```

### Tests

```python
import unittest

class TestGraphTraversal(unittest.TestCase):
    def setUp(self):
        self.graph = {
            'A': ['B', 'C'],
            'B': ['A', 'D', 'E'],
            'C': ['A', 'F'],
            'D': ['B'],
            'E': ['B', 'F'],
            'F': ['C', 'E']
        }
        
        self.tree = {
            1: [2, 3],
            2: [1, 4, 5],
            3: [1, 6, 7],
            4: [2],
            5: [2],
            6: [3],
            7: [3]
        }
    
    def test_bfs_basic(self):
        result = bfs(self.graph, 'A')
        self.assertEqual(result[0], 'A')
        self.assertIn('B', result)
        self.assertIn('C', result)
        self.assertEqual(len(result), 6)
    
    def test_dfs_basic(self):
        result = dfs(self.graph, 'A')
        self.assertEqual(result[0], 'A')
        self.assertEqual(len(result), 6)
    
    def test_dfs_recursive(self):
        result = dfs_recursive(self.graph, 'A')
        self.assertEqual(result[0], 'A')
        self.assertEqual(len(result), 6)
    
    def test_bfs_tree(self):
        result = bfs(self.tree, 1)
        self.assertEqual(result[:3], [1, 2, 3])
    
    def test_bfs_shortest_path(self):
        path = bfs_shortest_path(self.graph, 'A', 'F')
        self.assertEqual(len(path), 3)  # A -> C -> F or A -> B -> E -> F
        self.assertEqual(path[0], 'A')
        self.assertEqual(path[-1], 'F')
    
    def test_bfs_no_path(self):
        disconnected = {
            'A': ['B'],
            'B': ['A'],
            'C': ['D'],
            'D': ['C']
        }
        self.assertIsNone(bfs_shortest_path(disconnected, 'A', 'C'))
    
    def test_dfs_has_path(self):
        self.assertTrue(dfs_has_path(self.graph, 'A', 'F'))
        self.assertFalse(dfs_has_path(self.graph, 'A', 'Z'))
    
    def test_bfs_level_order(self):
        levels = bfs_level_order(self.tree, 1)
        self.assertEqual(len(levels), 3)
        self.assertEqual(levels[0], [1])
        self.assertEqual(set(levels[1]), {2, 3})
    
    def test_connected_components(self):
        disconnected = {
            'A': ['B'],
            'B': ['A'],
            'C': ['D'],
            'D': ['C']
        }
        components = find_connected_components(disconnected)
        self.assertEqual(len(components), 2)
    
    def test_detect_cycle_no_cycle(self):
        dag = {
            'A': ['B', 'C'],
            'B': ['D'],
            'C': ['D'],
            'D': []
        }
        self.assertFalse(detect_cycle_dfs(dag))
    
    def test_detect_cycle_with_cycle(self):
        cyclic = {
            'A': ['B'],
            'B': ['C'],
            'C': ['A']
        }
        self.assertTrue(detect_cycle_dfs(cyclic))
    
    def test_single_node(self):
        single = {'A': []}
        self.assertEqual(bfs(single, 'A'), ['A'])
        self.assertEqual(dfs(single, 'A'), ['A'])
    
    def test_node_not_in_graph(self):
        self.assertEqual(bfs(self.graph, 'Z'), [])
        self.assertEqual(dfs(self.graph, 'Z'), [])
        self.assertIsNone(bfs_shortest_path(self.graph, 'Z', 'A'))

if __name__ == '__main__':
    unittest.main()
```

### Complexity: 
- **BFS/DFS Traversal:** Time O(V + E), Space O(V)
- **BFS Shortest Path:** Time O(V + E), Space O(V)
- **Cycle Detection:** Time O(V + E), Space O(V)
- **Connected Components:** Time O(V + E), Space O(V)

Where V = number of vertices, E = number of edges.

---

## Summary Table

| Algorithm | Time Complexity (Average) | Time Complexity (Worst) | Space Complexity |
|-----------|---------------------------|-------------------------|------------------|
| Binary Search | O(log n) | O(log n) | O(1) iterative, O(log n) recursive |
| Merge Sort | O(n log n) | O(n log n) | O(n) |
| Quick Sort | O(n log n) | O(n^2) | O(log n) |
| Heap Sort | O(n log n) | O(n log n) | O(1) |
| BFS/DFS | O(V + E) | O(V + E) | O(V) |
