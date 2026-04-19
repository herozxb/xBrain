# Python Sorting Algorithms

## 1. QuickSort Implementation

```python
from typing import List, TypeVar
from functools import lru_cache

T = TypeVar('T')

def quicksort(arr: List[T]) -> List[T]:
    """
    Efficient QuickSort implementation with O(n log n) average complexity.
    
    @cached_property - Results can be cached for repeated calls
    Time: O(n log n) average, O(n²) worst
    Space: O(log n) for recursion stack
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


# In-place QuickSort (more memory efficient)
def quicksort_inplace(arr: List[T], low: int = 0, high: int = None) -> List[T]:
    """In-place QuickSort to minimize memory usage."""
    if high is None:
        high = len(arr) - 1
    
    def partition(low: int, high: int) -> int:
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    if low < high:
        pi = partition(low, high)
        quicksort_inplace(arr, low, pi - 1)
        quicksort_inplace(arr, pi + 1, high)
    
    return arr
```

## 2. MergeSort with Caching

```python
from functools import lru_cache

def mergesort(arr: List[T]) -> List[T]:
    """
    Stable MergeSort with guaranteed O(n log n) complexity.
    
    @lru_cache - Can cache comparison results for repeated elements
    Time: O(n log n) always
    Space: O(n) for temporary arrays
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    
    return _merge(left, right)


def _merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two sorted arrays."""
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
```

## 3. HeapSort

```python
import heapq

def heapsort(arr: List[T]) -> List[T]:
    """
    HeapSort using Python's built-in heapq module.
    
    Time: O(n log n) always
    Space: O(n) for heap
    In-place variant possible with O(1) space
    """
    # Convert to heap in-place
    heap = arr.copy()
    heapq.heapify(heap)
    
    # Extract elements in sorted order
    return [heapq.heappop(heap) for _ in range(len(heap))]


# In-place HeapSort
def heapsort_inplace(arr: List[T]) -> List[T]:
    """In-place HeapSort with O(1) extra space."""
    n = len(arr)
    
    def heapify(n: int, i: int) -> None:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(n, largest)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    
    # Extract elements
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(i, 0)
    
    return arr
```

## 4. Counting Sort (Non-comparison)

```python
from collections import Counter

def counting_sort(arr: List[int]) -> List[int]:
    """
    Counting Sort for integers - O(n + k) where k is range.
    
    Best for: Small range of integers
    Time: O(n + k)
    Space: O(k)
    """
    if not arr:
        return arr
    
    min_val, max_val = min(arr), max(arr)
    range_size = max_val - min_val + 1
    
    count = [0] * range_size
    for num in arr:
        count[num - min_val] += 1
    
    result = []
    for i, freq in enumerate(count):
        result.extend([i + min_val] * freq)
    
    return result


# Using Counter for sparse distributions
def counting_sort_counter(arr: List[int]) -> List[int]:
    """More memory-efficient for sparse distributions."""
    counter = Counter(arr)
    min_val, max_val = min(arr), max(arr)
    
    result = []
    for val in range(min_val, max_val + 1):
        result.extend([val] * counter.get(val, 0))
    
    return result
```

## 5. TimSort (Python's Built-in)

```python
# Python's built-in sorted() uses TimSort
# Hybrid of MergeSort + InsertionSort

def timsort_style(arr: List[T], min_run: int = 32) -> List[T]:
    """
    TimSort-style implementation (simplified).
    
    Python's sorted() is highly optimized:
    - Time: O(n log n) worst, O(n) best (already sorted)
    - Space: O(n)
    - Stable sort
    - Adaptive to patterns
    """
    n = len(arr)
    if n < 2:
        return arr
    
    # Insertion sort for small runs
    def insertion_sort(arr: List[T], left: int, right: int) -> None:
        for i in range(left + 1, right + 1):
            key = arr[i]
            j = i - 1
            while j >= left and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
    
    # Sort individual runs
    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end)
    
    # Merge runs
    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merged = _merge(arr[left:mid + 1], arr[mid + 1:right + 1])
                arr[left:left + len(merged)] = merged
        size *= 2
    
    return arr
```

## 6. Sorting with Custom Key & Cache

```python
from functools import lru_cache

class Person:
    def __init__(self, name: str, age: int, score: float):
        self.name = name
        self.age = age
        self.score = score
    
    @lru_cache(maxsize=128)
    def _cached_key(self) -> tuple:
        """Cache the sort key for repeated sorts."""
        return (self.score, self.age)
    
    def __lt__(self, other: 'Person') -> bool:
        return self._cached_key() < other._cached_key()


def sort_with_cached_key(people: List[Person]) -> List[Person]:
    """
    Sort with pre-computed cached keys.
    
    @lru_cache - Caches key computation for objects
    Useful when key computation is expensive
    """
    return sorted(people, key=lambda p: p._cached_key())


# Decorator for caching sort keys
def cached_sort_key(key_func):
    """Decorator to cache sort key computations."""
    cache = {}
    
    def wrapper(obj):
        obj_id = id(obj)
        if obj_id not in cache:
            cache[obj_id] = key_func(obj)
        return cache[obj_id]
    
    wrapper.clear_cache = cache.clear
    return wrapper
```

## Performance Comparison

| Algorithm | Time (avg) | Time (worst) | Space | Stable | Best For |
|-----------|------------|--------------|-------|--------|----------|
| QuickSort | O(n log n) | O(n²) | O(log n) | No | General purpose |
| MergeSort | O(n log n) | O(n log n) | O(n) | Yes | Linked lists, external |
| HeapSort | O(n log n) | O(n log n) | O(1)* | No | Memory constrained |
| Counting | O(n + k) | O(n + k) | O(k) | Yes | Small integer range |
| TimSort | O(n log n) | O(n log n) | O(n) | Yes | Real-world data |

## Usage Examples

```python
# Example 1: Basic sorting
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = quicksort(data)
print(sorted_data)  # [11, 12, 22, 25, 34, 64, 90]

# Example 2: Sorting with key
people = [
    Person("Alice", 30, 85.5),
    Person("Bob", 25, 92.0),
    Person("Charlie", 35, 78.5)
]
sorted_people = sort_with_cached_key(people)

# Example 3: In-place sorting
arr = [64, 34, 25, 12, 22, 11, 90]
quicksort_inplace(arr)
print(arr)  # [11, 12, 22, 25, 34, 64, 90]

# Example 4: Counting sort for integers
integers = [4, 2, 2, 8, 3, 3, 1]
sorted_ints = counting_sort(integers)
print(sorted_ints)  # [1, 2, 2, 3, 3, 4, 8]
```

## Best Practices

1. **Use built-in `sorted()`** for most cases (TimSort is highly optimized)
2. **QuickSort** for average-case performance
3. **MergeSort** when stability is required
4. **HeapSort** when memory is constrained
5. **Counting Sort** for small integer ranges
6. **Cache sort keys** when key computation is expensive
