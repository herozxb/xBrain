# Python Heaps - Comprehensive Guide

## Overview

A heap is a specialized tree-based data structure that satisfies the heap property. In a max heap, parent nodes are always greater than children; in a min heap, parent nodes are always smaller. This guide covers heap implementations and applications in Python.

## 1. Heap Implementation from Scratch

```python
from typing import List, Optional, Any

class MinHeap:
    """Min heap implementation"""
    
    def __init__(self):
        self.heap: List[Any] = []
    
    def parent(self, i: int) -> int:
        """Get parent index"""
        return (i - 1) // 2
    
    def left_child(self, i: int) -> int:
        """Get left child index"""
        return 2 * i + 1
    
    def right_child(self, i: int) -> int:
        """Get right child index"""
        return 2 * i + 2
    
    def insert(self, val: Any) -> None:
        """Insert value into heap"""
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)
    
    def _heapify_up(self, i: int) -> None:
        """Restore heap property upward"""
        while i > 0 and self.heap[self.parent(i)] > self.heap[i]:
            self.heap[self.parent(i)], self.heap[i] = self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)
    
    def extract_min(self) -> Optional[Any]:
        """Remove and return minimum element"""
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        
        return min_val
    
    def _heapify_down(self, i: int) -> None:
        """Restore heap property downward"""
        smallest = i
        left = self.left_child(i)
        right = self.right_child(i)
        size = len(self.heap)
        
        if left < size and self.heap[left] < self.heap[smallest]:
            smallest = left
        
        if right < size and self.heap[right] < self.heap[smallest]:
            smallest = right
        
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self._heapify_down(smallest)
    
    def peek(self) -> Optional[Any]:
        """Get minimum without removing"""
        return self.heap[0] if self.heap else None
    
    def size(self) -> int:
        """Get heap size"""
        return len(self.heap)
    
    def is_empty(self) -> bool:
        """Check if heap is empty"""
        return len(self.heap) == 0

class MaxHeap:
    """Max heap implementation"""
    
    def __init__(self):
        self.heap: List[Any] = []
    
    def parent(self, i: int) -> int:
        return (i - 1) // 2
    
    def left_child(self, i: int) -> int:
        return 2 * i + 1
    
    def right_child(self, i: int) -> int:
        return 2 * i + 2
    
    def insert(self, val: Any) -> None:
        """Insert value into heap"""
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)
    
    def _heapify_up(self, i: int) -> None:
        """Restore heap property upward"""
        while i > 0 and self.heap[self.parent(i)] < self.heap[i]:
            self.heap[self.parent(i)], self.heap[i] = self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)
    
    def extract_max(self) -> Optional[Any]:
        """Remove and return maximum element"""
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        max_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        
        return max_val
    
    def _heapify_down(self, i: int) -> None:
        """Restore heap property downward"""
        largest = i
        left = self.left_child(i)
        right = self.right_child(i)
        size = len(self.heap)
        
        if left < size and self.heap[left] > self.heap[largest]:
            largest = left
        
        if right < size and self.heap[right] > self.heap[largest]:
            largest = right
        
        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self._heapify_down(largest)
    
    def peek(self) -> Optional[Any]:
        """Get maximum without removing"""
        return self.heap[0] if self.heap else None
```

## 2. Using Python's heapq Module

```python
import heapq
from typing import List, Tuple, Any

class HeapQWrapper:
    """Wrapper for heapq operations"""
    
    def __init__(self, data: List[Any] = None):
        """Initialize heap with optional data"""
        self.heap = data[:] if data else []
        if self.heap:
            heapq.heapify(self.heap)
    
    def push(self, item: Any) -> None:
        """Push item onto heap"""
        heapq.heappush(self.heap, item)
    
    def pop(self) -> Any:
        """Pop smallest item"""
        return heapq.heappop(self.heap)
    
    def pushpop(self, item: Any) -> Any:
        """Push item then pop smallest"""
        return heapq.heappushpop(self.heap, item)
    
    def replace(self, item: Any) -> Any:
        """Pop smallest then push item"""
        return heapq.heapreplace(self.heap, item)
    
    def peek(self) -> Any:
        """Get smallest without removing"""
        return self.heap[0] if self.heap else None
    
    def nlargest(self, n: int) -> List[Any]:
        """Get n largest elements"""
        return heapq.nlargest(n, self.heap)
    
    def nsmallest(self, n: int) -> List[Any]:
        """Get n smallest elements"""
        return heapq.nsmallest(n, self.heap)

# Max heap using heapq (negate values)
class MaxHeapQ:
    """Max heap using heapq with negated values"""
    
    def __init__(self):
        self.heap = []
    
    def push(self, val: Any) -> None:
        heapq.heappush(self.heap, -val)
    
    def pop(self) -> Any:
        return -heapq.heappop(self.heap)
    
    def peek(self) -> Any:
        return -self.heap[0] if self.heap else None
```

## 3. Heap Applications

### 3.1 Priority Queue

```python
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class Task:
    """Priority queue task"""
    priority: int
    item: Any = field(compare=False)

class PriorityQueue:
    """Priority queue using heap"""
    
    def __init__(self):
        self.heap: List[Task] = []
        self.counter = 0  # For FIFO on same priority
    
    def push(self, item: Any, priority: int) -> None:
        """Add item with priority"""
        heapq.heappush(self.heap, Task(priority, item))
        self.counter += 1
    
    def pop(self) -> Any:
        """Remove and return highest priority item"""
        return heapq.heappop(self.heap).item if self.heap else None
    
    def peek(self) -> Any:
        """Get highest priority item without removing"""
        return self.heap[0].item if self.heap else None
    
    def is_empty(self) -> bool:
        return len(self.heap) == 0
    
    def size(self) -> int:
        return len(self.heap)

# Usage
pq = PriorityQueue()
pq.push("Low priority task", 3)
pq.push("High priority task", 1)
pq.push("Medium priority task", 2)

print(pq.pop())  # High priority task
print(pq.pop())  # Medium priority task
print(pq.pop())  # Low priority task
```

### 3.2 Kth Largest/Smallest Element

```python
import heapq
from typing import List

class KthElementFinder:
    """Find kth largest/smallest elements using heaps"""
    
    @staticmethod
    def kth_largest(nums: List[int], k: int) -> int:
        """Find kth largest element"""
        # Min heap of size k
        heap = []
        for num in nums:
            heapq.heappush(heap, num)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0]
    
    @staticmethod
    def kth_smallest(nums: List[int], k: int) -> int:
        """Find kth smallest element"""
        # Max heap of size k (using negative values)
        heap = []
        for num in nums:
            heapq.heappush(heap, -num)
            if len(heap) > k:
                heapq.heappop(heap)
        return -heap[0]
    
    @staticmethod
    def top_k_largest(nums: List[int], k: int) -> List[int]:
        """Get top k largest elements"""
        return heapq.nlargest(k, nums)
    
    @staticmethod
    def top_k_smallest(nums: List[int], k: int) -> List[int]:
        """Get top k smallest elements"""
        return heapq.nsmallest(k, nums)

# Usage
finder = KthElementFinder()
nums = [3, 2, 1, 5, 6, 4, 7]
print(finder.kth_largest(nums, 2))  # 6
print(finder.kth_smallest(nums, 3))  # 3
print(finder.top_k_largest(nums, 3))  # [7, 6, 5]
```

### 3.3 Merge K Sorted Lists

```python
import heapq
from typing import List, Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class MergeKSorted:
    """Merge k sorted linked lists using heap"""
    
    @staticmethod
    def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        """Merge k sorted lists"""
        dummy = ListNode(0)
        current = dummy
        heap = []
        
        # Add first node of each list to heap
        for i, node in enumerate(lists):
            if node:
                heapq.heappush(heap, (node.val, i, node))
        
        while heap:
            val, i, node = heapq.heappop(heap)
            current.next = ListNode(val)
            current = current.next
            
            if node.next:
                heapq.heappush(heap, (node.next.val, i, node.next))
        
        return dummy.next
    
    @staticmethod
    def merge_k_arrays(arrays: List[List[int]]) -> List[int]:
        """Merge k sorted arrays"""
        result = []
        heap = []
        
        # Push first element of each array
        for i, arr in enumerate(arrays):
            if arr:
                heapq.heappush(heap, (arr[0], i, 0))
        
        while heap:
            val, arr_idx, elem_idx = heapq.heappop(heap)
            result.append(val)
            
            # Push next element from same array
            if elem_idx + 1 < len(arrays[arr_idx]):
                next_val = arrays[arr_idx][elem_idx + 1]
                heapq.heappush(heap, (next_val, arr_idx, elem_idx + 1))
        
        return result

# Usage
arrays = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
merged = MergeKSorted.merge_k_arrays(arrays)
print(merged)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### 3.4 Median Finder

```python
import heapq
from typing import List

class MedianFinder:
    """Find median of data stream using two heaps"""
    
    def __init__(self):
        # Max heap for lower half (negated for max heap behavior)
        self.lower = []  # Max heap
        # Min heap for upper half
        self.upper = []  # Min heap
    
    def add_num(self, num: int) -> None:
        """Add number to data structure"""
        # Add to lower (max heap)
        heapq.heappush(self.lower, -num)
        
        # Balance: move largest from lower to upper
        heapq.heappush(self.upper, -heapq.heappop(self.lower))
        
        # Maintain size: lower can have at most 1 more element than upper
        if len(self.upper) > len(self.lower):
            heapq.heappush(self.lower, -heapq.heappop(self.upper))
    
    def find_median(self) -> float:
        """Find current median"""
        if len(self.lower) > len(self.upper):
            return -self.lower[0]
        
        return (-self.lower[0] + self.upper[0]) / 2.0

# Usage
mf = MedianFinder()
for num in [1, 2, 3, 4, 5]:
    mf.add_num(num)
    print(f"Median after adding {num}: {mf.find_median()}")
# Median after adding 1: 1
# Median after adding 2: 1.5
# Median after adding 3: 2
# Median after adding 4: 2.5
# Median after adding 5: 3
```

### 3.5 Sliding Window Maximum

```python
import heapq
from typing import List, Tuple

class SlidingWindow:
    """Sliding window problems using heap"""
    
    @staticmethod
    def max_sliding_window(nums: List[int], k: int) -> List[int]:
        """Find max in each sliding window of size k"""
        if not nums or k == 0:
            return []
        
        # Max heap: (-value, index)
        heap: List[Tuple[int, int]] = []
        result = []
        
        for i in range(len(nums)):
            # Add current element
            heapq.heappush(heap, (-nums[i], i))
            
            # Remove elements outside window
            while heap[0][1] <= i - k:
                heapq.heappop(heap)
            
            # Add max to result once window is formed
            if i >= k - 1:
                result.append(-heap[0][0])
        
        return result

# Usage
sw = SlidingWindow()
nums = [1, 3, -1, -3, 5, 3, 6, 7]
print(sw.max_sliding_window(nums, 3))  # [3, 3, 5, 5, 6, 7]
```

### 3.6 Task Scheduler

```python
import heapq
from collections import Counter, deque
from typing import List

class TaskScheduler:
    """Schedule tasks with cooldown using heap"""
    
    @staticmethod
    def least_interval(tasks: List[str], n: int) -> int:
        """Find minimum time to complete all tasks with cooldown"""
        # Count task frequencies
        count = Counter(tasks)
        
        # Max heap of task counts
        max_heap = [-cnt for cnt in count.values()]
        heapq.heapify(max_heap)
        
        time = 0
        queue = deque()  # (count, ready_time)
        
        while max_heap or queue:
            time += 1
            
            if max_heap:
                cnt = heapq.heappop(max_heap) + 1  # Decrease count
                if cnt < 0:  # Still tasks remaining
                    queue.append((cnt, time + n))
            
            # Check if any task is ready to be added back
            if queue and queue[0][1] == time:
                heapq.heappush(max_heap, queue.popleft()[0])
        
        return time

# Usage
scheduler = TaskScheduler()
tasks = ["A", "A", "A", "B", "B", "B"]
cooldown = 2
print(scheduler.least_interval(tasks, cooldown))  # 8
# Order: A -> B -> idle -> A -> B -> idle -> A -> B
```

## 4. Heap Sort

```python
from typing import List

class HeapSort:
    """Heap sort implementation"""
    
    @staticmethod
    def heapify(arr: List[int], n: int, i: int) -> None:
        """Heapify subtree rooted at index i"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            HeapSort.heapify(arr, n, largest)
    
    @staticmethod
    def sort(arr: List[int]) -> List[int]:
        """Sort array using heap sort"""
        n = len(arr)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            HeapSort.heapify(arr, n, i)
        
        # Extract elements one by one
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            HeapSort.heapify(arr, i, 0)
        
        return arr

# Usage
arr = [12, 11, 13, 5, 6, 7]
sorted_arr = HeapSort.sort(arr[:])
print(sorted_arr)  # [5, 6, 7, 11, 12, 13]
```

## Usage Examples

```python
# Min Heap
min_heap = MinHeap()
for num in [3, 1, 4, 1, 5, 9, 2, 6]:
    min_heap.insert(num)

print("Min heap size:", min_heap.size())
print("Extract min:", min_heap.extract_min())  # 1
print("Peek min:", min_heap.peek())  # 1

# Priority Queue
pq = PriorityQueue()
pq.push("Task A", 3)
pq.push("Task B", 1)
pq.push("Task C", 2)

while not pq.is_empty():
    print(pq.pop())  # Task B, Task C, Task A (by priority)

# Median Finder
mf = MedianFinder()
data = [5, 15, 1, 3, 2, 8, 7, 9, 10, 6, 11, 4]
for num in data:
    mf.add_num(num)
print("Median:", mf.find_median())  # 6

# Kth Largest
finder = KthElementFinder()
nums = [3, 2, 1, 5, 6, 4, 7, 8, 9, 10]
print("3rd largest:", finder.kth_largest(nums, 3))  # 8
```

## Key Points

1. **Heap Property**: Parent nodes maintain order relative to children
2. **Binary Heap**: Complete binary tree with heap property
3. **Efficiency**: O(log n) for insert/delete, O(1) for peek
4. **Applications**: Priority queues, sorting, graph algorithms
5. **Python heapq**: Min heap by default; use negative values for max heap

## Time Complexities

| Operation | Min Heap | Max Heap | heapq |
|-----------|----------|----------|-------|
| Insert | O(log n) | O(log n) | O(log n) |
| Extract Min/Max | O(log n) | O(log n) | O(log n) |
| Peek | O(1) | O(1) | O(1) |
| Build Heap | O(n) | O(n) | O(n) |
| Heapify | O(log n) | O(log n) | O(log n) |
| Heap Sort | O(n log n) | O(n log n) | - |
