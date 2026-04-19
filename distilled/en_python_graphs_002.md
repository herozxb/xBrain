# Python Graph Algorithms: Advanced Techniques

## Problem 1: Union-Find (Disjoint Set Union)

### Problem Description
Implement a Union-Find data structure with path compression and union by rank for efficient connectivity queries.

### Solution

```python
from typing import Dict, List, Set

class UnionFind:
    """
    Union-Find with path compression and union by rank.
    
    Time Complexity:
    - Find: O(α(n)) amortized, where α is inverse Ackermann
    - Union: O(α(n)) amortized
    - Space: O(n)
    """
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n
    
    def find(self, x: int) -> int:
        """Find root with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """
        Union two sets. Returns True if merged, False if already connected.
        """
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        self.components -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        """Check if two elements are in the same set."""
        return self.find(x) == self.find(y)
    
    def get_components(self) -> Dict[int, List[int]]:
        """Get all components as a dictionary."""
        components = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)
        return components


def count_provinces(n: int, connections: List[tuple]) -> int:
    """
    Count number of provinces (connected components) in a graph.
    """
    uf = UnionFind(n)
    for a, b in connections:
        uf.union(a, b)
    return uf.components


def detect_cycle_undirected(n: int, edges: List[tuple]) -> bool:
    """
    Detect cycle in undirected graph using Union-Find.
    """
    uf = UnionFind(n)
    for u, v in edges:
        if uf.connected(u, v):
            return True
        uf.union(u, v)
    return False
```

### Tests

```python
import pytest

class TestUnionFind:
    def test_basic_union_find(self):
        uf = UnionFind(5)
        assert uf.components == 5
        assert not uf.connected(0, 1)
        
        uf.union(0, 1)
        assert uf.connected(0, 1)
        assert uf.components == 4
    
    def test_transitive_connection(self):
        uf = UnionFind(5)
        uf.union(0, 1)
        uf.union(1, 2)
        assert uf.connected(0, 2)
    
    def test_no_double_union(self):
        uf = UnionFind(3)
        assert uf.union(0, 1) == True
        assert uf.union(0, 1) == False  # Already connected
    
    def test_count_provinces(self):
        n = 5
        connections = [(0, 1), (1, 2), (3, 4)]
        assert count_provinces(n, connections) == 2
    
    def test_cycle_detection(self):
        # No cycle
        assert not detect_cycle_undirected(3, [(0, 1), (1, 2)])
        # Has cycle
        assert detect_cycle_undirected(3, [(0, 1), (1, 2), (2, 0)])
    
    def test_get_components(self):
        uf = UnionFind(4)
        uf.union(0, 1)
        uf.union(2, 3)
        components = uf.get_components()
        assert len(components) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Problem 2: Bellman-Ford Algorithm

### Problem Description
Find shortest paths from a source vertex to all vertices, handling negative weights and detecting negative cycles.

### Solution

```python
from typing import List, Tuple, Optional
import math

def bellman_ford(n: int, edges: List[Tuple[int, int, int]], 
                  source: int) -> Tuple[List[float], bool]:
    """
    Bellman-Ford algorithm for single-source shortest paths.
    
    Returns: (distances, has_negative_cycle)
    
    Time Complexity: O(V * E)
    Space Complexity: O(V)
    """
    dist = [math.inf] * n
    dist[source] = 0
    
    # Relax all edges V-1 times
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break
    
    # Check for negative cycles
    has_negative_cycle = False
    for u, v, w in edges:
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break
    
    return dist, has_negative_cycle


def find_negative_cycle(n: int, edges: List[Tuple[int, int, int]]) -> Optional[List[int]]:
    """
    Find a negative cycle if it exists.
    Returns the cycle as a list of vertices, or None.
    """
    dist = [0] * n  # Start with 0 for all vertices
    parent = [-1] * n
    
    # Relax all edges V times
    last_updated = -1
    for i in range(n):
        last_updated = -1
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                last_updated = v
    
    if last_updated == -1:
        return None
    
    # Find cycle
    visited = set()
    cycle_start = last_updated
    for _ in range(n):
        cycle_start = parent[cycle_start]
    
    # Reconstruct cycle
    cycle = [cycle_start]
    current = parent[cycle_start]
    while current != cycle_start:
        cycle.append(current)
        current = parent[current]
    cycle.append(cycle_start)
    
    return list(reversed(cycle))


def arbitrage_detection(rates: List[List[float]]) -> bool:
    """
    Detect if arbitrage is possible given currency exchange rates.
    
    rates[i][j] = amount of currency j obtained for 1 unit of currency i
    """
    n = len(rates)
    # Convert to log space: log(a*b) = log(a) + log(b)
    # Arbitrage exists if sum of logs < 0 (product > 1)
    edges = []
    for i in range(n):
        for j in range(n):
            if i != j and rates[i][j] > 0:
                edges.append((i, j, -math.log(rates[i][j])))
    
    _, has_negative_cycle = bellman_ford(n, edges, 0)
    return has_negative_cycle
```

### Tests

```python
class TestBellmanFord:
    def test_simple_graph(self):
        n = 5
        edges = [(0, 1, 4), (0, 2, 2), (1, 2, 3), (2, 1, 1), 
                 (1, 3, 2), (1, 4, 3), (2, 3, 4), (2, 4, 5)]
        dist, has_cycle = bellman_ford(n, edges, 0)
        assert not has_cycle
        assert dist[0] == 0
        assert dist[1] == 3  # 0 -> 2 -> 1
        assert dist[2] == 2
    
    def test_negative_weights(self):
        n = 3
        edges = [(0, 1, 1), (1, 2, -2), (0, 2, 4)]
        dist, has_cycle = bellman_ford(n, edges, 0)
        assert not has_cycle
        assert dist[2] == -1  # 0 -> 1 -> 2
    
    def test_negative_cycle_detection(self):
        n = 3
        edges = [(0, 1, 1), (1, 2, -3), (2, 0, 1)]
        _, has_cycle = bellman_ford(n, edges, 0)
        assert has_cycle
    
    def test_unreachable_vertices(self):
        n = 4
        edges = [(0, 1, 1)]
        dist, has_cycle = bellman_ford(n, edges, 0)
        assert not has_cycle
        assert dist[3] == math.inf
    
    def test_arbitrage_detection(self):
        # No arbitrage
        rates1 = [
            [1, 2, 0.5],
            [0.5, 1, 0.25],
            [2, 4, 1]
        ]
        assert not arbitrage_detection(rates1)
        
        # Has arbitrage (cycle: 0 -> 1 -> 2 -> 0 gives > 1)
        rates2 = [
            [1, 2, 0.5],
            [0.5, 1, 4],
            [2, 0.25, 1]
        ]
        assert arbitrage_detection(rates2)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Problem 3: Topological Sort with Cycle Detection

### Problem Description
Perform topological sorting on a directed graph with cycle detection.

### Solution

```python
from collections import deque, defaultdict

def topological_sort_kahn(n: int, edges: List[Tuple[int, int]]) -> Tuple[List[int], bool]:
    """
    Kahn's algorithm for topological sort.
    
    Returns: (sorted_order, is_dag)
    """
    graph = defaultdict(list)
    in_degree = [0] * n
    
    for u, v in edges:
        graph[u].append(v)
        in_degree[v] += 1
    
    # Start with nodes having no incoming edges
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If not all nodes processed, there's a cycle
    is_dag = len(result) == n
    return result, is_dag


def topological_sort_dfs(n: int, edges: List[Tuple[int, int]]) -> Tuple[List[int], bool]:
    """
    DFS-based topological sort with cycle detection.
    """
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
    
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    result = []
    has_cycle = False
    
    def dfs(node: int) -> bool:
        nonlocal has_cycle
        if has_cycle:
            return False
        
        color[node] = GRAY
        
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:  # Back edge = cycle
                has_cycle = True
                return False
            if color[neighbor] == WHITE:
                if not dfs(neighbor):
                    return False
        
        color[node] = BLACK
        result.append(node)
        return True
    
    for i in range(n):
        if color[i] == WHITE:
            dfs(i)
    
    return list(reversed(result)), not has_cycle


def course_schedule(num_courses: int, prerequisites: List[Tuple[int, int]]) -> List[int]:
    """
    Return a valid course order, or empty list if impossible.
    """
    order, is_dag = topological_sort_kahn(num_courses, prerequisites)
    return order if is_dag else []


def parallel_course_schedule(n: int, relations: List[Tuple[int, int]], 
                             time: List[int]) -> int:
    """
    Minimum time to finish all courses if you can take any number 
    of courses in parallel (as long as prerequisites are met).
    """
    graph = defaultdict(list)
    in_degree = [0] * n
    
    for u, v in relations:
        graph[u].append(v)
        in_degree[v] += 1
    
    # dp[i] = minimum time to complete course i
    dp = [0] * n
    queue = deque()
    
    for i in range(n):
        if in_degree[i] == 0:
            queue.append(i)
            dp[i] = time[i]
    
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            dp[neighbor] = max(dp[neighbor], dp[node] + time[neighbor])
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return max(dp)
```

### Tests

```python
class TestTopologicalSort:
    def test_simple_dag(self):
        n = 4
        edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
        order, is_dag = topological_sort_kahn(n, edges)
        assert is_dag
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(3)
        assert order.index(2) < order.index(3)
    
    def test_cycle_detection(self):
        n = 3
        edges = [(0, 1), (1, 2), (2, 0)]
        order, is_dag = topological_sort_kahn(n, edges)
        assert not is_dag
    
    def test_dfs_vs_kahn(self):
        n = 5
        edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
        kahn_result, _ = topological_sort_kahn(n, edges)
        dfs_result, _ = topological_sort_dfs(n, edges)
        # Both should be valid topological orders
        assert len(kahn_result) == n
        assert len(dfs_result) == n
    
    def test_course_schedule(self):
        num_courses = 4
        prerequisites = [(1, 0), (2, 0), (3, 1), (3, 2)]
        order = course_schedule(num_courses, prerequisites)
        assert len(order) == 4
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
    
    def test_parallel_courses(self):
        n = 3
        relations = [(0, 1), (0, 2)]
        time = [1, 2, 3]
        result = parallel_course_schedule(n, relations, time)
        # Course 0 takes 1, then courses 1 and 2 in parallel
        assert result == 4  # max(1+2, 1+3)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Summary

| Algorithm | Use Case | Time | Space |
|-----------|----------|------|-------|
| Union-Find | Connectivity, MST | O(α(n)) | O(n) |
| Bellman-Ford | Negative weights | O(V×E) | O(V) |
| Topological Sort | DAG ordering | O(V+E) | O(V+E) |

**Key Patterns:**
- **Union-Find**: Path compression + rank = near-constant time
- **Bellman-Ford**: V-1 relaxations + one check for negative cycle
- **Topological Sort**: Kahn's (BFS) vs DFS approach
