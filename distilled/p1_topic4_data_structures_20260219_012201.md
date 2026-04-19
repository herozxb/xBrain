# Python3 - Data Structures

## Lists - Advanced Operations
```python
# PROBLEM: Advanced list operations
# APPROACH: Use built-in methods and slicing
# TIME: O(n) SPACE: O(n)

# Slicing
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
first_three = nums[:3]      # [0, 1, 2]
last_three = nums[-3:]      # [7, 8, 9]
every_other = nums[::2]     # [0, 2, 4, 6, 8]
reversed_list = nums[::-1]  # [9, 8, 7, ...]
middle = nums[3:7]          # [3, 4, 5, 6]

# List methods
nums.append(10)             # Add to end
nums.extend([11, 12])       # Add multiple
nums.insert(0, -1)          # Insert at index
nums.pop()                  # Remove last
nums.pop(0)                 # Remove first
nums.remove(5)              # Remove by value
nums.clear()                # Remove all

# Sorting
nums = [3, 1, 4, 1, 5, 9, 2, 6]
nums.sort()                 # In-place sort
nums.sort(reverse=True)     # Descending
nums.sort(key=lambda x: -x) # Custom key

# Searching
index = nums.index(5)       # Find index
count = nums.count(1)       # Count occurrences
exists = 5 in nums          # Membership test
```

**Explanation**: Lists support rich operations including slicing, sorting, and searching.
---

## Dictionaries - Advanced Operations
```python
# PROBLEM: Advanced dictionary operations
# APPROACH: Use dict methods and comprehensions
# TIME: O(1) average SPACE: O(n)

# Create dictionaries
d1 = dict(a=1, b=2, c=3)
d2 = dict(zip(['x', 'y', 'z'], [10, 20, 30]))
d3 = {k: v**2 for k, v in d1.items()}

# Merge dictionaries (Python 3.9+)
merged = d1 | d2
d1 |= d2  # In-place merge

# Default values
from collections import defaultdict
word_count = defaultdict(int)
for word in ['apple', 'banana', 'apple']:
    word_count[word] += 1

# OrderedDict (maintains insertion order)
from collections import OrderedDict
ordered = OrderedDict([('a', 1), ('b', 2)])

# Counter
from collections import Counter
freq = Counter('mississippi')
# Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

# ChainMap
from collections import ChainMap
defaults = {'theme': 'dark', 'lang': 'en'}
user = {'lang': 'es'}
config = ChainMap(user, defaults)
# config['lang'] -> 'es', config['theme'] -> 'dark'
```

**Explanation**: Python provides defaultdict, Counter, OrderedDict, ChainMap for specialized dict needs.
---

## Sets - Mathematical Operations
```python
# PROBLEM: Set operations for uniqueness and membership
# APPROACH: Use set methods and operators
# TIME: O(1) average SPACE: O(n)

# Create sets
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# Set operations
union = a | b              # {1, 2, 3, 4, 5, 6, 7, 8}
union = a.union(b)         # Same result
intersection = a & b       # {4, 5}
intersection = a.intersection(b)
difference = a - b         # {1, 2, 3}
symmetric_diff = a ^ b     # {1, 2, 3, 6, 7, 8}

# Subset/superset tests
c = {1, 2}
c.issubset(a)              # True
a.issuperset(c)            # True
a.isdisjoint({10, 11})     # True (no common elements)

# Frozen set (immutable)
frozen = frozenset([1, 2, 3])
# Can be used as dict key or set element
```

**Explanation**: Sets support mathematical operations. frozenset is immutable version.
---

## Queues and Stacks
```python
# PROBLEM: Implement queue and stack data structures
# APPROACH: Use collections.deque for efficiency
# TIME: O(1) for append/pop SPACE: O(n)

from collections import deque

# Stack (LIFO)
stack = deque()
stack.append(1)
stack.append(2)
stack.append(3)
top = stack.pop()          # 3

# Queue (FIFO)
queue = deque()
queue.append(1)
queue.append(2)
queue.append(3)
first = queue.popleft()    # 1

# Double-ended queue operations
d = deque([1, 2, 3])
d.appendleft(0)            # Add to front
d.append(4)                # Add to back
left = d.popleft()         # Remove from front
right = d.pop()            # Remove from back

# Bounded queue
bounded = deque(maxlen=3)
bounded.extend([1, 2, 3, 4])  # Only [2, 3, 4] kept

# Priority Queue
import heapq
pq = []
heapq.heappush(pq, (3, 'low'))
heapq.heappush(pq, (1, 'high'))
heapq.heappush(pq, (2, 'medium'))
priority, task = heapq.heappop(pq)  # (1, 'high')
```

**Explanation**: Use deque for efficient O(1) operations at both ends. heapq for priority queue.
---

## Arrays (Fixed Type)
```python
# PROBLEM: Store homogeneous numeric data efficiently
# APPROACH: Use array module or numpy
# TIME: O(1) for access SPACE: O(n) but smaller than list

from array import array

# Create arrays
int_array = array('i', [1, 2, 3, 4, 5])  # Signed int
float_array = array('f', [1.0, 2.0, 3.0])  # Float

# Type codes: 'i' int, 'f' float, 'd' double, 'b' signed char

# Operations
int_array.append(6)
int_array.extend([7, 8])
int_array.insert(0, 0)
value = int_array[2]

# Bytes conversion
bytes_data = int_array.tobytes()
restored = array('i', bytes_data)

# NumPy (better for numeric computing)
import numpy as np
np_array = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))
range_arr = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]
```

**Explanation**: array module provides efficient storage for numeric data. NumPy is better for computations.
