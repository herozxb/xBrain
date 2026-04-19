# Data Structures: Advanced Collections in Python

## Problem
Implement production-ready, optimized data structures with proper time complexity analysis and thread safety.

## Solution

### 1. LRU Cache with O(1) Operations

```python
# data_structures/lru_cache.py
from __future__ import annotations
from typing import Generic, TypeVar, Optional, Hashable
from dataclasses import dataclass
import threading

K = TypeVar('K', bound=Hashable)
V = TypeVar('V')

@dataclass
class Node(Generic[K, V]):
    """Doubly linked list node for LRU cache."""
    key: K
    value: V
    prev: Optional[Node[K, V]] = None
    next: Optional[Node[K, V]] = None


class LRUCache(Generic[K, V]):
    """
    Thread-safe LRU Cache with O(1) get and put operations.
    
    Time Complexity:
        - get: O(1)
        - put: O(1)
        - evict: O(1)
    
    Space Complexity: O(capacity)
    """
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self._capacity = capacity
        self._cache: dict[K, Node[K, V]] = {}
        self._lock = threading.RLock()
        
        # Sentinel nodes for doubly linked list
        self._head = Node(None, None)  # Most recently used
        self._tail = Node(None, None)  # Least recently used
        self._head.next = self._tail
        self._tail.prev = self._head
    
    def get(self, key: K) -> Optional[V]:
        """Get value by key, moving it to most recently used."""
        with self._lock:
            node = self._cache.get(key)
            if node is None:
                return None
            
            self._move_to_head(node)
            return node.value
    
    def put(self, key: K, value: V) -> Optional[V]:
        """
        Put key-value pair, returning evicted value if any.
        """
        with self._lock:
            node = self._cache.get(key)
            
            if node is not None:
                old_value = node.value
                node.value = value
                self._move_to_head(node)
                return old_value
            
            # Create new node
            new_node = Node(key, value)
            self._cache[key] = new_node
            self._add_to_head(new_node)
            
            # Evict if over capacity
            evicted_value = None
            if len(self._cache) > self._capacity:
                evicted = self._remove_tail()
                if evicted:
                    del self._cache[evicted.key]
                    evicted_value = evicted.value
            
            return evicted_value
    
    def delete(self, key: K) -> bool:
        """Delete key from cache. Returns True if key existed."""
        with self._lock:
            node = self._cache.pop(key, None)
            if node is None:
                return False
            
            self._remove_node(node)
            return True
    
    def _move_to_head(self, node: Node[K, V]) -> None:
        """Move existing node to head (most recently used)."""
        self._remove_node(node)
        self._add_to_head(node)
    
    def _add_to_head(self, node: Node[K, V]) -> None:
        """Add node right after head."""
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node
    
    def _remove_node(self, node: Node[K, V]) -> None:
        """Remove node from linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _remove_tail(self) -> Optional[Node[K, V]]:
        """Remove and return the least recently used node."""
        if self._tail.prev is self._head:
            return None
        
        lru = self._tail.prev
        self._remove_node(lru)
        return lru
    
    def __len__(self) -> int:
        return len(self._cache)
    
    def __contains__(self, key: K) -> bool:
        return key in self._cache
    
    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
            self._head.next = self._tail
            self._tail.prev = self._head
    
    def keys(self) -> list[K]:
        """Return keys from most to least recently used."""
        with self._lock:
            result = []
            current = self._head.next
            while current is not self._tail:
                result.append(current.key)
                current = current.next
            return result
```

### 2. Priority Queue with Decrease Key

```python
# data_structures/priority_queue.py
from __future__ import annotations
from typing import Generic, TypeVar, Optional, Callable
import heapq
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass(order=True)
class PriorityItem(Generic[T]):
    """Heap item with priority and unique ID for updates."""
    priority: float
    insertion_order: int  # Break ties, maintain FIFO for equal priorities
    item: T = field(compare=False)
    valid: bool = field(default=True, compare=False)


class PriorityQueue(Generic[T]):
    """
    Min-heap based priority queue with support for updates and deletion.
    
    Time Complexity:
        - push: O(log n)
        - pop: O(log n) amortized (lazy deletion)
        - update: O(log n)
        - delete: O(1) (lazy deletion)
    
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self._heap: list[PriorityItem[T]] = []
        self._item_map: dict[T, PriorityItem[T]] = {}
        self._insertion_counter = 0
        self._invalid_count = 0
    
    def push(self, item: T, priority: float = 0.0) -> bool:
        """
        Add or update item priority.
        Returns True if item was updated, False if new.
        """
        if item in self._item_map:
            self.update(item, priority)
            return True
        
        entry = PriorityItem(
            priority=priority,
            insertion_order=self._insertion_counter,
            item=item
        )
        self._insertion_counter += 1
        
        self._item_map[item] = entry
        heapq.heappush(self._heap, entry)
        return False
    
    def pop(self) -> Optional[T]:
        """Remove and return highest priority item."""
        while self._heap:
            entry = heapq.heappop(self._heap)
            if entry.valid:
                del self._item_map[entry.item]
                return entry.item
            else:
                self._invalid_count -= 1
        
        return None
    
    def peek(self) -> Optional[T]:
        """Return highest priority item without removing."""
        self._clean_invalid()
        
        if self._heap:
            return self._heap[0].item
        return None
    
    def update(self, item: T, new_priority: float) -> bool:
        """Update priority of existing item. Returns False if not found."""
        if item not in self._item_map:
            return False
        
        # Mark old entry as invalid
        old_entry = self._item_map[item]
        old_entry.valid = False
        self._invalid_count += 1
        
        # Create new entry
        new_entry = PriorityItem(
            priority=new_priority,
            insertion_order=self._insertion_counter,
            item=item
        )
        self._insertion_counter += 1
        
        self._item_map[item] = new_entry
        heapq.heappush(self._heap, new_entry)
        return True
    
    def delete(self, item: T) -> bool:
        """Mark item for deletion (lazy deletion)."""
        if item not in self._item_map:
            return False
        
        entry = self._item_map[item]
        if entry.valid:
            entry.valid = False
            self._invalid_count += 1
            del self._item_map[item]
        return True
    
    def _clean_invalid(self) -> None:
        """Remove invalid entries from heap."""
        if self._invalid_count > len(self._heap) // 2:
            # Rebuild heap if too many invalid entries
            self._heap = [e for e in self._heap if e.valid]
            heapq.heapify(self._heap)
            self._invalid_count = 0
    
    def __len__(self) -> int:
        return len(self._item_map)
    
    def __contains__(self, item: T) -> bool:
        return item in self._item_map and self._item_map[item].valid
    
    def clear(self) -> None:
        """Remove all items."""
        self._heap.clear()
        self._item_map.clear()
        self._invalid_count = 0
```

### 3. Trie (Prefix Tree) for Autocomplete

```python
# data_structures/trie.py
from __future__ import annotations
from typing import Optional, Iterator
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TrieNode:
    """Trie node with children and metadata."""
    children: dict[str, TrieNode] = field(default_factory=dict)
    is_end: bool = False
    count: int = 0  # Number of words passing through
    word_count: int = 0  # Number of complete words ending here


class Trie:
    """
    Trie (Prefix Tree) for efficient string operations.
    
    Time Complexity:
        - insert: O(m) where m is word length
        - search: O(m)
        - starts_with: O(m)
        - autocomplete: O(m + k) where k is number of results
    
    Space Complexity: O(alphabet_size * average_word_length * number_of_words)
    """
    
    def __init__(self):
        self._root = TrieNode()
        self._size = 0
    
    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self._root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.count += 1
        
        node.is_end = True
        node.word_count += 1
        self._size += 1
    
    def search(self, word: str) -> bool:
        """Check if exact word exists in trie."""
        node = self._find_node(word)
        return node is not None and node.is_end
    
    def starts_with(self, prefix: str) -> bool:
        """Check if any word starts with prefix."""
        return self._find_node(prefix) is not None
    
    def count_prefix(self, prefix: str) -> int:
        """Count words with given prefix."""
        node = self._find_node(prefix)
        return node.count if node else 0
    
    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        """Return words starting with prefix."""
        node = self._find_node(prefix)
        if node is None:
            return []
        
        results = []
        self._collect_words(node, prefix, results, limit)
        return results
    
    def delete(self, word: str) -> bool:
        """Delete word from trie. Returns True if word existed."""
        if not word:
            return False
        
        # Track path for cleanup
        path = [self._root]
        for char in word:
            if char not in path[-1].children:
                return False
            path.append(path[-1].children[char])
        
        last_node = path[-1]
        if not last_node.is_end:
            return False
        
        # Mark as not end
        last_node.is_end = False
        last_node.word_count -= 1
        self._size -= 1
        
        # Clean up nodes with no children
        for i in range(len(path) - 1, 0, -1):
            node = path[i]
            node.count -= 1
            
            if node.count == 0 and not node.is_end:
                parent = path[i - 1]
                del parent.children[word[i - 1]]
            else:
                break
        
        return True
    
    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find node at end of prefix."""
        node = self._root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def _collect_words(self, node: TrieNode, prefix: str, 
                       results: list[str], limit: int) -> None:
        """Collect all words from node using DFS."""
        if len(results) >= limit:
            return
        
        if node.is_end:
            for _ in range(node.word_count):
                results.append(prefix)
                if len(results) >= limit:
                    return
        
        for char, child in sorted(node.children.items()):
            self._collect_words(child, prefix + char, results, limit)
            if len(results) >= limit:
                return
    
    def __len__(self) -> int:
        return self._size
    
    def __contains__(self, word: str) -> bool:
        return self.search(word)
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over all words in the trie."""
        results = []
        self._collect_words(self._root, "", results, float('inf'))
        return iter(results)
```

### 4. Bloom Filter for Set Membership

```python
# data_structures/bloom_filter.py
import math
import mmh3  # MurmurHash3
from typing import Iterator
from bitarray import bitarray


class BloomFilter:
    """
    Space-efficient probabilistic data structure for set membership.
    
    False positives possible, false negatives not possible.
    
    Time Complexity:
        - add: O(k) where k is number of hash functions
        - contains: O(k)
    
    Space Complexity: O(m) bits where m is filter size
    """
    
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        """
        Initialize bloom filter with optimal size and hash count.
        
        Args:
            expected_items: Expected number of items to store
            false_positive_rate: Desired false positive probability
        """
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be between 0 and 1")
        
        # Calculate optimal size and hash count
        self._size = self._calculate_size(expected_items, false_positive_rate)
        self._hash_count = self._calculate_hash_count(self._size, expected_items)
        
        self._bitarray = bitarray(self._size)
        self._bitarray.setall(False)
        self._count = 0
    
    @staticmethod
    def _calculate_size(n: int, p: float) -> int:
        """Calculate optimal bit array size: m = -(n * ln(p)) / (ln(2)^2)"""
        return int(-n * math.log(p) / (math.log(2) ** 2))
    
    @staticmethod
    def _calculate_hash_count(m: int, n: int) -> int:
        """Calculate optimal number of hash functions: k = (m/n) * ln(2)"""
        return int(m / n * math.log(2))
    
    def add(self, item: str) -> None:
        """Add item to filter."""
        for seed in range(self._hash_count):
            index = mmh3.hash(str(item), seed) % self._size
            self._bitarray[index] = True
        self._count += 1
    
    def contains(self, item: str) -> bool:
        """Check if item might be in filter (may have false positives)."""
        for seed in range(self._hash_count):
            index = mmh3.hash(str(item), seed) % self._size
            if not self._bitarray[index]:
                return False
        return True
    
    def __contains__(self, item: str) -> bool:
        return self.contains(item)
    
    def __len__(self) -> int:
        return self._count
    
    def false_positive_probability(self) -> float:
        """Calculate current false positive probability."""
        if self._count == 0:
            return 0.0
        
        # p = (1 - e^(-kn/m))^k
        exponent = -self._hash_count * self._count / self._size
        return (1 - math.exp(exponent)) ** self._hash_count
    
    def clear(self) -> None:
        """Clear all items."""
        self._bitarray.setall(False)
        self._count = 0
```

## Tests

```python
# tests/test_data_structures.py
import pytest
import threading
import random
from data_structures.lru_cache import LRUCache
from data_structures.priority_queue import PriorityQueue
from data_structures.trie import Trie
from data_structures.bloom_filter import BloomFilter


class TestLRUCache:
    """Test suite for LRU Cache."""
    
    def test_basic_operations(self):
        cache = LRUCache[str, int](capacity=3)
        
        assert cache.get("a") is None
        assert len(cache) == 0
        
        cache.put("a", 1)
        assert cache.get("a") == 1
        assert len(cache) == 1
    
    def test_eviction_policy(self):
        cache = LRUCache[str, int](capacity=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict "a"
        
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
    
    def test_access_updates_recency(self):
        cache = LRUCache[str, int](capacity=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # Access "a", making "b" LRU
        cache.put("c", 3)  # Should evict "b"
        
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3
    
    def test_update_existing_key(self):
        cache = LRUCache[str, int](capacity=2)
        
        cache.put("a", 1)
        old_value = cache.put("a", 10)
        
        assert old_value == 1
        assert cache.get("a") == 10
        assert len(cache) == 1
    
    def test_thread_safety(self):
        cache = LRUCache[int, int](capacity=100)
        errors = []
        
        def writer(start):
            try:
                for i in range(100):
                    cache.put(start + i, i)
            except Exception as e:
                errors.append(e)
        
        def reader(start):
            try:
                for i in range(100):
                    cache.get(start + i)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=writer, args=(0,)),
            threading.Thread(target=writer, args=(100,)),
            threading.Thread(target=reader, args=(0,)),
            threading.Thread(target=reader, args=(100,)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_delete(self):
        cache = LRUCache[str, int](capacity=2)
        
        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None
        assert cache.delete("nonexistent") is False
    
    def test_keys_order(self):
        cache = LRUCache[str, int](capacity=3)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # Keys should be in order: c, b, a (most to least recent)
        assert cache.keys() == ["c", "b", "a"]
        
        cache.get("a")  # Access "a"
        assert cache.keys() == ["a", "c", "b"]


class TestPriorityQueue:
    """Test suite for Priority Queue."""
    
    def test_basic_operations(self):
        pq = PriorityQueue[str]()
        
        assert pq.pop() is None
        assert len(pq) == 0
        
        pq.push("task1", priority=2)
        pq.push("task2", priority=1)
        pq.push("task3", priority=3)
        
        assert pq.pop() == "task2"  # Lowest priority first
        assert pq.pop() == "task1"
        assert pq.pop() == "task3"
    
    def test_update_priority(self):
        pq = PriorityQueue[str]()
        
        pq.push("a", priority=3)
        pq.push("b", priority=2)
        pq.update("a", priority=0)  # Now "a" should be first
        
        assert pq.pop() == "a"
        assert pq.pop() == "b"
    
    def test_delete(self):
        pq = PriorityQueue[str]()
        
        pq.push("a", priority=1)
        pq.push("b", priority=2)
        pq.delete("a")
        
        assert pq.pop() == "b"
        assert pq.pop() is None
    
    def test_peek(self):
        pq = PriorityQueue[str]()
        
        pq.push("a", priority=2)
        pq.push("b", priority=1)
        
        assert pq.peek() == "b"
        assert len(pq) == 2  # Peek shouldn't remove
    
    def test_fifo_for_equal_priorities(self):
        pq = PriorityQueue[str]()
        
        pq.push("first", priority=1)
        pq.push("second", priority=1)
        pq.push("third", priority=1)
        
        assert pq.pop() == "first"
        assert pq.pop() == "second"
        assert pq.pop() == "third"


class TestTrie:
    """Test suite for Trie."""
    
    def test_basic_operations(self):
        trie = Trie()
        
        assert "hello" not in trie
        assert trie.search("hello") is False
        
        trie.insert("hello")
        assert "hello" in trie
        assert trie.search("hello") is True
    
    def test_prefix_search(self):
        trie = Trie()
        
        trie.insert("hello")
        trie.insert("help")
        trie.insert("helicopter")
        
        assert trie.starts_with("hel") is True
        assert trie.starts_with("wor") is False
        assert trie.count_prefix("hel") == 3
    
    def test_autocomplete(self):
        trie = Trie()
        
        words = ["apple", "application", "apply", "appreciate", "banana"]
        for word in words:
            trie.insert(word)
        
        results = trie.autocomplete("app", limit=3)
        assert len(results) == 3
        assert all(w.startswith("app") for w in results)
    
    def test_delete(self):
        trie = Trie()
        
        trie.insert("hello")
        trie.insert("help")
        
        assert trie.delete("hello") is True
        assert "hello" not in trie
        assert "help" in trie  # Other words unaffected
    
    def test_iteration(self):
        trie = Trie()
        
        words = ["cat", "car", "card", "care", "careful"]
        for word in words:
            trie.insert(word)
        
        result = list(trie)
        assert set(result) == set(words)
    
    def test_duplicate_insertions(self):
        trie = Trie()
        
        trie.insert("hello")
        trie.insert("hello")
        trie.insert("hello")
        
        assert len(trie) == 3  # Count duplicates
        assert trie.delete("hello")
        assert len(trie) == 2


class TestBloomFilter:
    """Test suite for Bloom Filter."""
    
    def test_basic_operations(self):
        bf = BloomFilter(expected_items=100, false_positive_rate=0.01)
        
        bf.add("item1")
        bf.add("item2")
        
        assert "item1" in bf
        assert "item2" in bf
        assert len(bf) == 2
    
    def test_no_false_negatives(self):
        """Items that were added must always be found."""
        bf = BloomFilter(expected_items=1000, false_positive_rate=0.01)
        
        items = [f"item_{i}" for i in range(100)]
        for item in items:
            bf.add(item)
        
        # All added items must be found
        for item in items:
            assert item in bf, f"False negative for {item}"
    
    def test_false_positive_rate(self):
        """False positive rate should be within expected bounds."""
        expected_items = 1000
        fp_rate = 0.05
        bf = BloomFilter(expected_items=expected_items, false_positive_rate=fp_rate)
        
        # Add items
        for i in range(expected_items):
            bf.add(f"item_{i}")
        
        # Test for items not in filter
        false_positives = 0
        test_count = 10000
        for i in range(expected_items, expected_items + test_count):
            if f"item_{i}" in bf:
                false_positives += 1
        
        actual_fp_rate = false_positives / test_count
        # Allow some variance (factor of 2)
        assert actual_fp_rate < fp_rate * 2, f"FP rate too high: {actual_fp_rate}"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Key Features

1. **LRU Cache** - O(1) operations with doubly linked list + hash map
2. **Thread Safety** - Proper locking for concurrent access
3. **Priority Queue** - Decrease-key with lazy deletion
4. **Trie** - Autocomplete with prefix search
5. **Bloom Filter** - Space-efficient membership testing
6. **Time/Space Analysis** - Big-O documented for all operations
7. **Comprehensive Tests** - Edge cases, thread safety, correctness
8. **Type Hints** - Full generic type support
9. **Pythonic API** - Support for `in`, `len`, iteration
