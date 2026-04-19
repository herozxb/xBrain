# ALGORITHMS - High-Quality Code Data
**Date:** February 18, 2026
**Category:** Algorithms (Sorting, Searching, Graphs, Dynamic Programming)
**Total Items:** 6

---

## Problem: Merge Sort Implementation

```python
# PROBLEM: Sort an array of integers in ascending order using divide-and-conquer
# APPROACH: Recursively divide array into halves, sort each half, then merge sorted halves
# TIME: O(n log n)  SPACE: O(n)
# EDGE CASES: Empty array, single element, already sorted, reverse sorted, duplicates

def merge_sort(arr):
    # Step 1: Base case - arrays with 0 or 1 element are already sorted
    if len(arr) <= 1:
        return arr
    
    # Step 2: Divide - find middle point and split into two halves
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    # Step 3: Conquer - recursively sort both halves
    left_sorted = merge_sort(left_half)
    right_sorted = merge_sort(right_half)
    
    # Step 4: Combine - merge the two sorted halves
    return merge(left_sorted, right_sorted)

def merge(left, right):
    # Initialize result array and pointers for both arrays
    result = []
    i = j = 0
    
    # Compare elements from both arrays and add smaller one to result
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements from left array (if any)
    result.extend(left[i:])
    # Add remaining elements from right array (if any)
    result.extend(right[j:])
    
    return result
```

**Explanation**: Merge sort is a stable, comparison-based sorting algorithm that guarantees O(n log n) time complexity in all cases. It works by recursively dividing the input array into smaller subarrays until each contains at most one element, then merging these subarrays back together in sorted order. The merge operation is the key to efficiency, combining two sorted arrays in linear time by comparing the smallest remaining elements from each.

**When to Use**: Use merge sort when you need guaranteed O(n log n) performance regardless of input distribution, when sorting linked lists (no random access needed), or when stable sorting is required (preserves relative order of equal elements). It's ideal for external sorting where data doesn't fit in memory.

**Trade-offs**: 
- **Pros:** Guaranteed O(n log n) time, stable sort, parallelizable, works well with linked lists
- **Cons:** Requires O(n) additional space, not in-place, slower for small arrays due to recursion overhead, not cache-friendly

---

## Problem: Binary Search

```python
# PROBLEM: Find the index of a target value in a sorted array efficiently
# APPROACH: Repeatedly divide search interval in half by comparing target with middle element
# TIME: O(log n)  SPACE: O(1)
# EDGE CASES: Empty array, target not found, target at boundaries, duplicate targets, single element

def binary_search(arr, target):
    # Step 1: Initialize search boundaries
    left, right = 0, len(arr) - 1
    
    # Step 2: Continue while search space is valid
    while left <= right:
        # Calculate middle index (avoid overflow with this formula)
        mid = left + (right - left) // 2
        
        # Step 3: Check if target is found at mid
        if arr[mid] == target:
            return mid
        
        # Step 4: Narrow search to appropriate half
        elif arr[mid] < target:
            # Target is in right half, adjust left boundary
            left = mid + 1
        else:
            # Target is in left half, adjust right boundary
            right = mid - 1
    
    # Target not found in array
    return -1

def binary_search_recursive(arr, target, left=0, right=None):
    # Initialize right boundary on first call
    if right is None:
        right = len(arr) - 1
    
    # Base case: search space exhausted
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

**Explanation**: Binary search is an efficient algorithm for finding elements in sorted arrays, achieving O(log n) time complexity by eliminating half of the remaining elements with each comparison. The algorithm maintains a search range and progressively narrows it down until the target is found or the range becomes empty. It's fundamental to many advanced algorithms and data structures like binary search trees.

**When to Use**: Use binary search when working with sorted arrays or when you can maintain sorted order, when you need to perform repeated searches on the same dataset, or when implementing search functionality in large datasets. Common in databases, file systems, and game development.

**Trade-offs**:
- **Pros:** Extremely efficient O(log n) time, minimal space O(1), simple implementation
- **Cons:** Requires sorted input, not suitable for frequently changing data, random access required (doesn't work with linked lists)

---

## Problem: Depth-First Search (DFS)

```python
# PROBLEM: Traverse all nodes in a graph/tree, visiting each node exactly once
# APPROACH: Explore as far as possible along each branch before backtracking
# TIME: O(V + E) where V=vertices, E=edges  SPACE: O(V)
# EDGE CASES: Empty graph, single node, disconnected graph, graph with cycles, self-loops

def dfs_recursive(graph, start, visited=None):
    # Initialize visited set on first call
    if visited is None:
        visited = set()
    
    # Mark current node as visited
    visited.add(start)
    print(f"Visiting: {start}")
    
    # Recursively visit all unvisited neighbors
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    
    return visited

def dfs_iterative(graph, start):
    # Use stack for iterative implementation
    visited = set()
    stack = [start]
    
    while stack:
        # Pop the top node from stack
        node = stack.pop()
        
        # Skip if already visited (handles cycles)
        if node in visited:
            continue
        
        # Mark as visited and process
        visited.add(node)
        print(f"Visiting: {node}")
        
        # Add unvisited neighbors to stack
        # Reverse to maintain same order as recursive version
        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(neighbor)
    
    return visited

def dfs_path_exists(graph, start, end):
    """Check if path exists between start and end nodes."""
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        
        if node == end:
            return True
        
        if node not in visited:
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return False
```

**Explanation**: Depth-First Search explores a graph by going as deep as possible before backtracking, using either recursion (implicit stack) or an explicit stack data structure. It's excellent for problems requiring exhaustive exploration of paths, cycle detection, and topological sorting. The algorithm naturally implements backtracking for constraint satisfaction problems.

**When to Use**: Use DFS for finding paths in mazes, detecting cycles in graphs, topological sorting, finding connected components, solving puzzles with backtracking (N-Queens, Sudoku), or when you need to explore all possible paths before finding the shortest one.

**Trade-offs**:
- **Pros:** Simple implementation, memory-efficient for certain problems, naturally suited for backtracking
- **Cons:** May get stuck in infinite loops with cycles (need visited tracking), doesn't guarantee shortest path, recursive version can cause stack overflow on deep graphs

---

## Problem: Breadth-First Search (BFS)

```python
# PROBLEM: Traverse graph level by level, finding shortest path in unweighted graphs
# APPROACH: Explore all neighbors at current depth before moving to next depth level
# TIME: O(V + E) where V=vertices, E=edges  SPACE: O(V)
# EDGE CASES: Empty graph, single node, disconnected components, target not found, cycles

from collections import deque

def bfs(graph, start):
    # Use deque for O(1) popleft operation
    visited = set([start])
    queue = deque([start])
    traversal_order = []
    
    while queue:
        # Dequeue the front node
        node = queue.popleft()
        traversal_order.append(node)
        
        # Enqueue all unvisited neighbors
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return traversal_order

def bfs_shortest_path(graph, start, end):
    """Find shortest path between start and end in unweighted graph."""
    if start == end:
        return [start]
    
    visited = set([start])
    queue = deque([(start, [start])])  # (node, path)
    
    while queue:
        node, path = queue.popleft()
        
        for neighbor in graph.get(node, []):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path exists

def bfs_level_order(tree_root):
    """Perform level-order traversal of binary tree."""
    if not tree_root:
        return []
    
    result = []
    queue = deque([tree_root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
    
    return result
```

**Explanation**: Breadth-First Search explores a graph level by level using a queue, guaranteeing the shortest path in unweighted graphs. It processes all nodes at the current depth before moving deeper, making it ideal for finding nearest neighbors or minimum steps to reach a goal. The level-order traversal variant is commonly used in tree problems.

**When to Use**: Use BFS for finding shortest paths in unweighted graphs, level-order traversal of trees, finding all nodes within K distance, web crawling (processing pages by depth), social network analysis (finding connections), or when you need the closest solution.

**Trade-offs**:
- **Pros:** Guarantees shortest path in unweighted graphs, explores nodes systematically by distance
- **Cons:** Uses more memory than DFS (stores entire level), not suitable for deep graphs with limited memory, slower than DFS for some pathfinding where shortest isn't required

---

## Problem: Dynamic Programming - Longest Common Subsequence

```python
# PROBLEM: Find the length of longest common subsequence between two strings
# APPROACH: Build DP table where dp[i][j] represents LCS length of first i and j characters
# TIME: O(m * n)  SPACE: O(m * n) or O(min(m,n)) with optimization
# EDGE CASES: Empty strings, identical strings, no common characters, one string is substring

def longest_common_subsequence(text1, text2):
    # Get lengths of both strings
    m, n = len(text1), len(text2)
    
    # Step 1: Create DP table with (m+1) x (n+1) dimensions
    # dp[i][j] = LCS length of text1[0:i] and text2[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Step 2: Fill DP table bottom-up
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # If characters match, extend LCS by 1
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                # Take maximum of excluding either character
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]

def lcs_with_path(text1, text2):
    """Return both the length and actual LCS string."""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Build DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    # Backtrack to find actual LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            lcs.append(text1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    
    return dp[m][n], ''.join(reversed(lcs))

def lcs_space_optimized(text1, text2):
    """Space-optimized version using only 2 rows."""
    if len(text1) < len(text2):
        text1, text2 = text2, text1
    
    n = len(text2)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    
    for i in range(1, len(text1) + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, [0] * (n + 1)
    
    return prev[n]
```

**Explanation**: The Longest Common Subsequence problem is a classic dynamic programming challenge that finds the longest sequence of characters appearing in both strings in the same relative order (not necessarily contiguous). The solution builds a 2D table where each cell represents the LCS length for substrings, using the optimal substructure property. It's fundamental to diff tools, bioinformatics, and version control systems.

**When to Use**: Use LCS for comparing file differences (diff tools), DNA sequence alignment in bioinformatics, plagiarism detection, version control merge algorithms, or any scenario requiring similarity measurement between sequences.

**Trade-offs**:
- **Pros:** Polynomial time solution to otherwise exponential problem, finds optimal solution, can be space-optimized
- **Cons:** O(mn) time and space can be prohibitive for very long strings, doesn't handle weighted or fuzzy matching

---

## Problem: Dijkstra's Shortest Path Algorithm

```python
# PROBLEM: Find shortest path from source to all nodes in weighted graph with non-negative edges
# APPROACH: Use greedy approach with priority queue, always process closest unvisited node
# TIME: O((V + E) log V) with min-heap  SPACE: O(V)
# EDGE CASES: Disconnected graph, single node, source equals destination, negative weights (invalid)

import heapq
from collections import defaultdict

def dijkstra(graph, start):
    # Initialize distances with infinity for all nodes except start
    distances = defaultdict(lambda: float('infinity'))
    distances[start] = 0
    
    # Priority queue: (distance, node)
    pq = [(0, start)]
    visited = set()
    
    while pq:
        # Get node with minimum distance
        current_dist, current = heapq.heappop(pq)
        
        # Skip if already processed
        if current in visited:
            continue
        
        visited.add(current)
        
        # Update distances to neighbors
        for neighbor, weight in graph.get(current, []):
            if neighbor in visited:
                continue
            
            new_dist = current_dist + weight
            
            # Found shorter path to neighbor
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    
    return dict(distances)

def dijkstra_with_path(graph, start, end):
    """Find shortest path and distance between start and end."""
    distances = defaultdict(lambda: float('infinity'))
    distances[start] = 0
    previous = {}  # Track path
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current == end:
            # Reconstruct path
            path = []
            while current in previous:
                path.append(current)
                current = previous[current]
            path.append(start)
            return distances[end], path[::-1]
        
        if current_dist > distances[current]:
            continue
        
        for neighbor, weight in graph.get(current, []):
            new_dist = current_dist + weight
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    return float('infinity'), []  # No path exists

class DijkstraGrid:
    """Dijkstra for 2D grid with obstacles."""
    def shortest_path(self, grid, start, end):
        rows, cols = len(grid), len(grid[0])
        sr, sc = start
        er, ec = end
        
        distances = defaultdict(lambda: float('infinity'))
        distances[(sr, sc)] = 0
        pq = [(0, sr, sc)]
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while pq:
            dist, r, c = heapq.heappop(pq)
            
            if (r, c) == (er, ec):
                return dist
            
            if dist > distances[(r, c)]:
                continue
            
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                    new_dist = dist + 1  # Unit weight
                    
                    if new_dist < distances[(nr, nc)]:
                        distances[(nr, nc)] = new_dist
                        heapq.heappush(pq, (new_dist, nr, nc))
        
        return -1  # No path
```

**Explanation**: Dijkstra's algorithm finds the shortest path from a source node to all other nodes in a graph with non-negative edge weights. It uses a greedy approach, always processing the closest unvisited node first, which guarantees optimality. The priority queue (min-heap) efficiently selects the next node to process, achieving O((V+E) log V) time complexity.

**When to Use**: Use Dijkstra for GPS navigation systems, network routing protocols, finding shortest paths in road networks, game AI pathfinding, or any weighted graph shortest path problem with non-negative edges.

**Trade-offs**:
- **Pros:** Guarantees optimal solution, efficient with priority queue, works for any non-negative weighted graph
- **Cons:** Cannot handle negative weights (use Bellman-Ford), slower than BFS for unweighted graphs, may be overkill for single-target search

---

**End of ALGORITHMS Category**
