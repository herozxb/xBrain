# Python Algorithm: Dijkstra's Shortest Path Algorithm

## Problem Statement
Implement Dijkstra's algorithm to find the shortest path from a source node to all other nodes in a weighted graph with non-negative edges.

## Solution Code

```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import heapq
from collections import defaultdict

@dataclass
class Edge:
    """Represents a weighted edge in the graph."""
    to: str
    weight: float

class Graph:
    """Weighted graph implementation using adjacency list."""
    
    def __init__(self):
        self.adjacency: Dict[str, List[Edge]] = defaultdict(list)
        self.nodes: set = set()
    
    def add_edge(self, from_node: str, to_node: str, weight: float) -> None:
        """Add a directed edge to the graph."""
        if weight < 0:
            raise ValueError("Dijkstra's algorithm doesn't support negative weights")
        self.adjacency[from_node].append(Edge(to_node, weight))
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def add_bidirectional_edge(self, node1: str, node2: str, weight: float) -> None:
        """Add an undirected edge (both directions)."""
        self.add_edge(node1, node2, weight)
        self.add_edge(node2, node1, weight)

class Dijkstra:
    """Dijkstra's shortest path algorithm implementation."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def find_shortest_paths(self, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
        """
        Find shortest paths from source to all other nodes.
        
        Returns:
            distances: Dict mapping node -> shortest distance from source
            predecessors: Dict mapping node -> previous node in shortest path
        """
        if source not in self.graph.nodes:
            raise ValueError(f"Source node '{source}' not in graph")
        
        # Initialize distances with infinity, source has distance 0
        distances: Dict[str, float] = {node: float('inf') for node in self.graph.nodes}
        distances[source] = 0
        
        # Track the path
        predecessors: Dict[str, Optional[str]] = {node: None for node in self.graph.nodes}
        
        # Priority queue: (distance, node)
        # Using counter to break ties (heapq doesn't handle node comparison)
        pq: List[Tuple[float, int, str]] = []
        counter = 0
        heapq.heappush(pq, (0, counter, source))
        
        # Track visited nodes
        visited: set = set()
        
        while pq:
            current_dist, _, current_node = heapq.heappop(pq)
            
            # Skip if already processed
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Explore neighbors
            for edge in self.graph.adjacency[current_node]:
                if edge.to in visited:
                    continue
                
                new_dist = current_dist + edge.weight
                
                # Found shorter path
                if new_dist < distances[edge.to]:
                    distances[edge.to] = new_dist
                    predecessors[edge.to] = current_node
                    counter += 1
                    heapq.heappush(pq, (new_dist, counter, edge.to))
        
        return distances, predecessors
    
    def get_path(self, source: str, target: str) -> Optional[List[str]]:
        """Get the shortest path from source to target."""
        distances, predecessors = self.find_shortest_paths(source)
        
        if distances[target] == float('inf'):
            return None  # No path exists
        
        # Reconstruct path
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        return path[::-1]  # Reverse to get source -> target

# Usage Example
if __name__ == "__main__":
    graph = Graph()
    graph.add_bidirectional_edge("A", "B", 4)
    graph.add_bidirectional_edge("A", "C", 2)
    graph.add_bidirectional_edge("B", "C", 1)
    graph.add_bidirectional_edge("B", "D", 5)
    graph.add_bidirectional_edge("C", "D", 8)
    graph.add_bidirectional_edge("C", "E", 10)
    graph.add_bidirectional_edge("D", "E", 2)
    
    dijkstra = Dijkstra(graph)
    distances, _ = dijkstra.find_shortest_paths("A")
    
    print("Shortest distances from A:")
    for node, dist in sorted(distances.items()):
        print(f"  {node}: {dist}")
    
    print("\nPath from A to E:", " -> ".join(dijkstra.get_path("A", "E")))
```

## Unit Tests

```python
import pytest
from python_graph_dijkstra import Graph, Dijkstra

class TestGraph:
    def test_add_edge(self):
        g = Graph()
        g.add_edge("A", "B", 5)
        assert "A" in g.nodes
        assert "B" in g.nodes
        assert len(g.adjacency["A"]) == 1
        assert g.adjacency["A"][0].to == "B"
        assert g.adjacency["A"][0].weight == 5
    
    def test_negative_weight_raises(self):
        g = Graph()
        with pytest.raises(ValueError, match="negative weights"):
            g.add_edge("A", "B", -1)
    
    def test_bidirectional_edge(self):
        g = Graph()
        g.add_bidirectional_edge("A", "B", 3)
        assert len(g.adjacency["A"]) == 1
        assert len(g.adjacency["B"]) == 1

class TestDijkstra:
    @pytest.fixture
    def simple_graph(self):
        g = Graph()
        g.add_bidirectional_edge("A", "B", 1)
        g.add_bidirectional_edge("B", "C", 2)
        g.add_bidirectional_edge("A", "C", 5)
        return g
    
    @pytest.fixture
    def complex_graph(self):
        g = Graph()
        g.add_bidirectional_edge("A", "B", 4)
        g.add_bidirectional_edge("A", "C", 2)
        g.add_bidirectional_edge("B", "C", 1)
        g.add_bidirectional_edge("B", "D", 5)
        g.add_bidirectional_edge("C", "D", 8)
        g.add_bidirectional_edge("D", "E", 2)
        return g
    
    def test_single_node(self):
        g = Graph()
        g.nodes.add("A")
        d = Dijkstra(g)
        distances, _ = d.find_shortest_paths("A")
        assert distances["A"] == 0
    
    def test_simple_path(self, simple_graph):
        d = Dijkstra(simple_graph)
        distances, _ = d.find_shortest_paths("A")
        assert distances["A"] == 0
        assert distances["B"] == 1
        assert distances["C"] == 3  # A -> B -> C is shorter than A -> C
    
    def test_unreachable_node(self):
        g = Graph()
        g.add_edge("A", "B", 1)
        g.nodes.add("C")  # Isolated node
        d = Dijkstra(g)
        distances, _ = d.find_shortest_paths("A")
        assert distances["C"] == float('inf')
    
    def test_path_reconstruction(self, complex_graph):
        d = Dijkstra(complex_graph)
        path = d.get_path("A", "D")
        assert path == ["A", "C", "B", "D"]
    
    def test_no_path_exists(self):
        g = Graph()
        g.add_edge("A", "B", 1)
        g.nodes.add("C")
        d = Dijkstra(g)
        path = d.get_path("A", "C")
        assert path is None
    
    def test_invalid_source(self):
        g = Graph()
        g.nodes.add("A")
        d = Dijkstra(g)
        with pytest.raises(ValueError, match="not in graph"):
            d.find_shortest_paths("Z")

# Run tests with: pytest python_graph_dijkstra.py -v
```

## Analysis

### Time Complexity
- **O((V + E) log V)** where V = vertices, E = edges
- Each vertex is added to the heap once: O(V log V)
- Each edge causes at most one heap operation: O(E log V)
- Total: O((V + E) log V)

### Space Complexity
- **O(V + E)** for the adjacency list
- **O(V)** for distances, predecessors, and priority queue

### Key Design Decisions

1. **Dataclass for Edges**: Using `@dataclass` provides clean, immutable edge representation with automatic `__init__`.

2. **Priority Queue with Counter**: Python's `heapq` compares elements fully. Adding a counter ensures stable ordering when distances are equal.

3. **Separation of Concerns**: 
   - `Graph` class handles graph structure
   - `Dijkstra` class handles algorithm logic
   - This allows different algorithms on the same graph structure

4. **Lazy Deletion**: Using a `visited` set instead of decreasing keys in the heap is simpler and equally efficient for sparse graphs.

### When to Use Dijkstra

✅ **Good for:**
- Non-negative edge weights
- Single-source shortest path
- GPS navigation systems
- Network routing protocols

❌ **Not suitable for:**
- Negative edge weights (use Bellman-Ford)
- All-pairs shortest paths (use Floyd-Warshall)
- Unweighted graphs (use BFS)

### Alternative Approaches

| Algorithm | Weights | Time | Best For |
|-----------|---------|------|----------|
| BFS | Unweighted | O(V+E) | Unweighted graphs |
| Dijkstra | Non-negative | O((V+E)log V) | Single source |
| Bellman-Ford | Any | O(VE) | Negative weights |
| Floyd-Warshall | Any | O(V³) | All pairs |
| A* | Non-negative | O(E) typical | With heuristic |

### Production Considerations

1. **Large Graphs**: Consider using `numpy` arrays for distances instead of dicts
2. **Dynamic Graphs**: Implement edge weight updates with decrease-key operations
3. **Parallel Processing**: Partition graph for distributed computation
4. **Memory Optimization**: Use adjacency matrix for dense graphs
