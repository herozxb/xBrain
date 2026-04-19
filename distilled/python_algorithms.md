# Python 算法问题完整解决方案

## 目录
1. [快排/归并排序](#1-快排归并排序)
2. [二叉树遍历](#2-二叉树遍历)
3. [动态规划（背包问题）](#3-动态规划背包问题)
4. [图的 BFS/DFS](#4-图的-bfsdfs)
5. [最短路径（Dijkstra）](#5-最短路径dijkstra)
6. [滑动窗口](#6-滑动窗口)
7. [前缀和](#7-前缀和)
8. [单调栈](#8-单调栈)
9. [并查集](#9-并查集)
10. [线段树](#10-线段树)

---

## 1. 快排/归并排序

### 1.1 快速排序 (Quick Sort)

```python
def quick_sort(arr):
    """
    快速排序 - 分治思想
    选择基准值，将数组分为小于和大于基准的两部分，递归排序
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def quick_sort_inplace(arr, low=0, high=None):
    """
    原地快速排序 - 空间优化版本
    """
    if high is None:
        high = len(arr) - 1
    
    def partition(low, high):
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
        quick_sort_inplace(arr, low, pi - 1)
        quick_sort_inplace(arr, pi + 1, high)
    
    return arr


# 测试
def test_quick_sort():
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 4, 6, 1, 3],
        [1],
        [],
        [3, 3, 3, 3],
        [9, 8, 7, 6, 5, 4, 3, 2, 1]
    ]
    
    for arr in test_cases:
        sorted_arr = quick_sort(arr.copy())
        assert sorted_arr == sorted(arr), f"Failed: {arr}"
    
    print("✓ 快速排序测试通过!")


# 复杂度分析:
# - 时间复杂度: 平均 O(n log n), 最坏 O(n²) (当数组已排序时)
# - 空间复杂度: O(log n) 递归栈空间 (平均), O(n) 最坏
# - 不稳定排序
```

### 1.2 归并排序 (Merge Sort)

```python
def merge_sort(arr):
    """
    归并排序 - 分治思想
    将数组分成两半，递归排序后合并
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left, right):
    """合并两个有序数组"""
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


# 测试
def test_merge_sort():
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 4, 6, 1, 3],
        [1],
        [],
        [3, 3, 3, 3],
        [9, 8, 7, 6, 5, 4, 3, 2, 1]
    ]
    
    for arr in test_cases:
        sorted_arr = merge_sort(arr)
        assert sorted_arr == sorted(arr), f"Failed: {arr}"
    
    print("✓ 归并排序测试通过!")


# 复杂度分析:
# - 时间复杂度: O(n log n) - 稳定
# - 空间复杂度: O(n) - 需要额外空间存储临时数组
# - 稳定排序
```

---

## 2. 二叉树遍历

```python
from collections import deque
from typing import Optional, List

class TreeNode:
    """二叉树节点"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class BinaryTreeTraversal:
    """二叉树遍历方法集合"""
    
    # ========== 深度优先遍历 (DFS) ==========
    
    @staticmethod
    def preorder_recursive(root: Optional[TreeNode]) -> List[int]:
        """前序遍历 - 递归 (根->左->右)"""
        result = []
        
        def dfs(node):
            if node:
                result.append(node.val)
                dfs(node.left)
                dfs(node.right)
        
        dfs(root)
        return result
    
    @staticmethod
    def preorder_iterative(root: Optional[TreeNode]) -> List[int]:
        """前序遍历 - 迭代"""
        if not root:
            return []
        
        result, stack = [], [root]
        while stack:
            node = stack.pop()
            result.append(node.val)
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)
        
        return result
    
    @staticmethod
    def inorder_recursive(root: Optional[TreeNode]) -> List[int]:
        """中序遍历 - 递归 (左->根->右)"""
        result = []
        
        def dfs(node):
            if node:
                dfs(node.left)
                result.append(node.val)
                dfs(node.right)
        
        dfs(root)
        return result
    
    @staticmethod
    def inorder_iterative(root: Optional[TreeNode]) -> List[int]:
        """中序遍历 - 迭代"""
        result, stack, current = [], [], root
        
        while current or stack:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current.val)
            current = current.right
        
        return result
    
    @staticmethod
    def postorder_recursive(root: Optional[TreeNode]) -> List[int]:
        """后序遍历 - 递归 (左->右->根)"""
        result = []
        
        def dfs(node):
            if node:
                dfs(node.left)
                dfs(node.right)
                result.append(node.val)
        
        dfs(root)
        return result
    
    @staticmethod
    def postorder_iterative(root: Optional[TreeNode]) -> List[int]:
        """后序遍历 - 迭代"""
        if not root:
            return []
        
        result, stack = [], [(root, False)]
        
        while stack:
            node, visited = stack.pop()
            if visited:
                result.append(node.val)
            else:
                stack.append((node, True))
                if node.right:
                    stack.append((node.right, False))
                if node.left:
                    stack.append((node.left, False))
        
        return result
    
    # ========== 广度优先遍历 (BFS) ==========
    
    @staticmethod
    def level_order(root: Optional[TreeNode]) -> List[List[int]]:
        """层序遍历 (BFS)"""
        if not root:
            return []
        
        result, queue = [], deque([root])
        
        while queue:
            level = []
            for _ in range(len(queue)):
                node = queue.popleft()
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            result.append(level)
        
        return result


# 测试
def test_tree_traversal():
    """
    构建测试树:
         1
        / \
       2   3
      / \
     4   5
    """
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    
    # 前序: 1, 2, 4, 5, 3
    assert BinaryTreeTraversal.preorder_recursive(root) == [1, 2, 4, 5, 3]
    assert BinaryTreeTraversal.preorder_iterative(root) == [1, 2, 4, 5, 3]
    
    # 中序: 4, 2, 5, 1, 3
    assert BinaryTreeTraversal.inorder_recursive(root) == [4, 2, 5, 1, 3]
    assert BinaryTreeTraversal.inorder_iterative(root) == [4, 2, 5, 1, 3]
    
    # 后序: 4, 5, 2, 3, 1
    assert BinaryTreeTraversal.postorder_recursive(root) == [4, 5, 2, 3, 1]
    assert BinaryTreeTraversal.postorder_iterative(root) == [4, 5, 2, 3, 1]
    
    # 层序: [[1], [2, 3], [4, 5]]
    assert BinaryTreeTraversal.level_order(root) == [[1], [2, 3], [4, 5]]
    
    print("✓ 二叉树遍历测试通过!")


# 复杂度分析:
# - 时间复杂度: O(n) - 每个节点访问一次
# - 空间复杂度: 
#   - 递归: O(h) 栈空间, h为树高
#   - 迭代: O(h) 显式栈
#   - 层序: O(w) w为最大宽度
# - 最坏空间复杂度: O(n) (斜树)
```

---

## 3. 动态规划（背包问题）

```python
class Knapsack:
    """背包问题集合"""
    
    @staticmethod
    def zero_one_knapsack(weights, values, capacity):
        """
        0-1 背包问题
        每个物品只能选择一次
        
        Args:
            weights: 物品重量列表
            values: 物品价值列表
            capacity: 背包容量
        
        Returns:
            最大价值
        """
        n = len(weights)
        # dp[i][w] 表示前i个物品，容量为w时的最大价值
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(1, capacity + 1):
                if weights[i-1] <= w:
                    # 选择当前物品或不选择
                    dp[i][w] = max(
                        dp[i-1][w],  # 不选
                        dp[i-1][w - weights[i-1]] + values[i-1]  # 选
                    )
                else:
                    dp[i][w] = dp[i-1][w]
        
        return dp[n][capacity]
    
    @staticmethod
    def zero_one_knapsack_optimized(weights, values, capacity):
        """0-1 背包 - 空间优化版本"""
        n = len(weights)
        dp = [0] * (capacity + 1)
        
        for i in range(n):
            # 从后向前遍历，避免重复选择
            for w in range(capacity, weights[i] - 1, -1):
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
        
        return dp[capacity]
    
    @staticmethod
    def complete_knapsack(weights, values, capacity):
        """
        完全背包问题
        每个物品可以选择无限次
        """
        n = len(weights)
        dp = [0] * (capacity + 1)
        
        for i in range(n):
            # 从前向后遍历，允许重复选择
            for w in range(weights[i], capacity + 1):
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
        
        return dp[capacity]
    
    @staticmethod
    def get_selected_items(weights, values, capacity):
        """获取选中的物品索引"""
        n = len(weights)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(1, capacity + 1):
                if weights[i-1] <= w:
                    dp[i][w] = max(
                        dp[i-1][w],
                        dp[i-1][w - weights[i-1]] + values[i-1]
                    )
                else:
                    dp[i][w] = dp[i-1][w]
        
        # 回溯找选中物品
        selected = []
        w = capacity
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected.append(i - 1)
                w -= weights[i - 1]
        
        return selected[::-1]


# 测试
def test_knapsack():
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8
    
    # 0-1背包: 最大价值应为 10 (选择物品0和物品3)
    assert Knapsack.zero_one_knapsack(weights, values, capacity) == 10
    assert Knapsack.zero_one_knapsack_optimized(weights, values, capacity) == 10
    
    # 验证选中物品
    selected = Knapsack.get_selected_items(weights, values, capacity)
    total_weight = sum(weights[i] for i in selected)
    total_value = sum(values[i] for i in selected)
    assert total_weight <= capacity
    assert total_value == 10
    
    # 完全背包测试
    weights2 = [1, 3, 4, 5]
    values2 = [1, 4, 5, 7]
    capacity2 = 7
    # 最优: 选择物品1两次 (3+3=6, 价值4+4=8) 或 物品3+物品0 (5+1=6, 价值7+1=8)
    assert Knapsack.complete_knapsack(weights2, values2, capacity2) == 9
    
    print("✓ 背包问题测试通过!")


# 复杂度分析:
# 0-1背包:
# - 时间复杂度: O(n * W), n为物品数, W为容量
# - 空间复杂度: O(n * W) 或 O(W) 优化版
# 
# 完全背包:
# - 时间复杂度: O(n * W)
# - 空间复杂度: O(W)
```

---

## 4. 图的 BFS/DFS

```python
from collections import deque, defaultdict
from typing import Dict, List, Set

class GraphTraversal:
    """图的遍历方法"""
    
    @staticmethod
    def dfs_recursive(graph: Dict[int, List[int]], start: int) -> List[int]:
        """
        DFS 递归实现
        """
        visited = set()
        result = []
        
        def dfs(node):
            visited.add(node)
            result.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(start)
        return result
    
    @staticmethod
    def dfs_iterative(graph: Dict[int, List[int]], start: int) -> List[int]:
        """
        DFS 迭代实现
        """
        visited = set()
        result = []
        stack = [start]
        
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                result.append(node)
                # 逆序添加以保持和递归相同的顺序
                for neighbor in reversed(graph.get(node, [])):
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return result
    
    @staticmethod
    def bfs(graph: Dict[int, List[int]], start: int) -> List[int]:
        """
        BFS 实现
        """
        visited = set([start])
        result = []
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    @staticmethod
    def bfs_shortest_path(graph: Dict[int, List[int]], start: int, end: int) -> List[int]:
        """
        BFS 寻找最短路径 (无权图)
        """
        if start == end:
            return [start]
        
        visited = set([start])
        queue = deque([(start, [start])])
        
        while queue:
            node, path = queue.popleft()
            
            for neighbor in graph.get(node, []):
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # 没有路径
    
    @staticmethod
    def has_cycle_undirected(graph: Dict[int, List[int]]) -> bool:
        """检测无向图是否有环"""
        visited = set()
        
        def dfs(node, parent):
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, node):
                        return True
                elif neighbor != parent:
                    return True
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node, -1):
                    return True
        return False


# 测试
def test_graph_traversal():
    """
    构建测试图:
      0 --- 1
      |     |
      2 --- 3 --- 4
    """
    graph = {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3],
        3: [1, 2, 4],
        4: [3]
    }
    
    # DFS测试
    dfs_result = GraphTraversal.dfs_recursive(graph, 0)
    assert len(dfs_result) == 5
    assert set(dfs_result) == {0, 1, 2, 3, 4}
    
    # BFS测试
    bfs_result = GraphTraversal.bfs(graph, 0)
    assert len(bfs_result) == 5
    assert set(bfs_result) == {0, 1, 2, 3, 4}
    
    # 最短路径测试
    shortest = GraphTraversal.bfs_shortest_path(graph, 0, 4)
    assert shortest == [0, 1, 3, 4] or shortest == [0, 2, 3, 4]
    
    # 环检测
    assert GraphTraversal.has_cycle_undirected(graph) == True
    
    # 无环图测试
    tree = {0: [1, 2], 1: [0], 2: [0]}
    assert GraphTraversal.has_cycle_undirected(tree) == False
    
    print("✓ 图遍历测试通过!")


# 复杂度分析:
# - 时间复杂度: O(V + E), V为顶点数, E为边数
# - 空间复杂度: O(V) - visited集合和递归栈/队列
```

---

## 5. 最短路径（Dijkstra）

```python
import heapq
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class Dijkstra:
    """Dijkstra 最短路径算法"""
    
    @staticmethod
    def shortest_path(graph: Dict[int, List[Tuple[int, int]]], 
                      start: int, 
                      end: int) -> Tuple[int, List[int]]:
        """
        Dijkstra 算法 - 寻找最短路径
        
        Args:
            graph: 邻接表，graph[u] = [(v, weight), ...]
            start: 起点
            end: 终点
        
        Returns:
            (最短距离, 路径列表)
        """
        # 初始化距离和前驱节点
        distances = defaultdict(lambda: float('inf'))
        distances[start] = 0
        predecessors = {}
        
        # 优先队列: (距离, 节点)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            dist, node = heapq.heappop(pq)
            
            if node in visited:
                continue
            visited.add(node)
            
            if node == end:
                break
            
            for neighbor, weight in graph.get(node, []):
                if neighbor in visited:
                    continue
                
                new_dist = dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = node
                    heapq.heappush(pq, (new_dist, neighbor))
        
        # 重建路径
        if end not in predecessors and start != end:
            return float('inf'), []
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        path.reverse()
        
        return distances[end], path
    
    @staticmethod
    def all_shortest_paths(graph: Dict[int, List[Tuple[int, int]]], 
                          start: int) -> Dict[int, int]:
        """
        从起点到所有节点的最短距离
        
        Returns:
            每个节点到起点的最短距离字典
        """
        distances = defaultdict(lambda: float('inf'))
        distances[start] = 0
        pq = [(0, start)]
        visited = set()
        
        while pq:
            dist, node = heapq.heappop(pq)
            
            if node in visited:
                continue
            visited.add(node)
            
            for neighbor, weight in graph.get(node, []):
                if neighbor in visited:
                    continue
                
                new_dist = dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
        
        return dict(distances)


# 测试
def test_dijkstra():
    """
    构建测试图:
          4
      0 ----> 1
      |       |
     2|       |3
      v       v
      2 ----> 3
          1
    """
    graph = {
        0: [(1, 4), (2, 2)],
        1: [(3, 3)],
        2: [(3, 1)],
        3: []
    }
    
    # 最短路径测试
    distance, path = Dijkstra.shortest_path(graph, 0, 3)
    assert distance == 3, f"Expected 3, got {distance}"
    assert path == [0, 2, 3], f"Expected [0, 2, 3], got {path}"
    
    # 到所有节点的最短距离
    all_dist = Dijkstra.all_shortest_paths(graph, 0)
    assert all_dist[0] == 0
    assert all_dist[1] == 4
    assert all_dist[2] == 2
    assert all_dist[3] == 3
    
    print("✓ Dijkstra 最短路径测试通过!")


# 复杂度分析:
# - 时间复杂度: O((V + E) log V) - 使用优先队列
# - 空间复杂度: O(V) - 存储距离和优先队列
# - 注意: 只适用于非负权边
```

---

## 6. 滑动窗口

```python
from typing import List
from collections import defaultdict

class SlidingWindow:
    """滑动窗口算法集合"""
    
    @staticmethod
    def max_sum_subarray(nums: List[int], k: int) -> int:
        """
        固定窗口 - 长度为k的子数组最大和
        """
        if len(nums) < k:
            return 0
        
        window_sum = sum(nums[:k])
        max_sum = window_sum
        
        for i in range(k, len(nums)):
            window_sum += nums[i] - nums[i - k]
            max_sum = max(max_sum, window_sum)
        
        return max_sum
    
    @staticmethod
    def min_window_substring(s: str, t: str) -> str:
        """
        最小窗口子串 - 包含t所有字符的最小窗口
        LeetCode 76
        """
        if not s or not t:
            return ""
        
        need = defaultdict(int)
        for c in t:
            need[c] += 1
        
        left = 0
        need_count = len(need)
        have_count = 0
        window = defaultdict(int)
        min_len = float('inf')
        result = ""
        
        for right, char in enumerate(s):
            window[char] += 1
            
            if char in need and window[char] == need[char]:
                have_count += 1
            
            while have_count == need_count:
                if right - left + 1 < min_len:
                    min_len = right - left + 1
                    result = s[left:right + 1]
                
                left_char = s[left]
                window[left_char] -= 1
                if left_char in need and window[left_char] < need[left_char]:
                    have_count -= 1
                left += 1
        
        return result
    
    @staticmethod
    def longest_substring_without_repeating(s: str) -> int:
        """
        无重复字符的最长子串
        LeetCode 3
        """
        char_index = {}
        left = 0
        max_len = 0
        
        for right, char in enumerate(s):
            if char in char_index and char_index[char] >= left:
                left = char_index[char] + 1
            char_index[char] = right
            max_len = max(max_len, right - left + 1)
        
        return max_len
    
    @staticmethod
    def length_of_longest_substring_k_distinct(s: str, k: int) -> int:
        """
        最多包含k个不同字符的最长子串
        """
        if k == 0:
            return 0
        
        char_count = defaultdict(int)
        left = 0
        max_len = 0
        
        for right, char in enumerate(s):
            char_count[char] += 1
            
            while len(char_count) > k:
                left_char = s[left]
                char_count[left_char] -= 1
                if char_count[left_char] == 0:
                    del char_count[left_char]
                left += 1
            
            max_len = max(max_len, right - left + 1)
        
        return max_len


# 测试
def test_sliding_window():
    # 固定窗口最大和
    assert SlidingWindow.max_sum_subarray([1, 4, 2, 10, 23, 3, 1, 0, 20], 4) == 39
    
    # 最小窗口子串
    assert SlidingWindow.min_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert SlidingWindow.min_window_substring("a", "a") == "a"
    
    # 无重复字符最长子串
    assert SlidingWindow.longest_substring_without_repeating("abcabcbb") == 3
    assert SlidingWindow.longest_substring_without_repeating("bbbbb") == 1
    assert SlidingWindow.longest_substring_without_repeating("pwwkew") == 3
    
    # k个不同字符最长子串
    assert SlidingWindow.length_of_longest_substring_k_distinct("eceba", 2) == 3
    
    print("✓ 滑动窗口测试通过!")


# 复杂度分析:
# - 时间复杂度: O(n) - 每个元素最多访问两次
# - 空间复杂度: O(k) - k为字符集大小或窗口大小
```

---

## 7. 前缀和

```python
from typing import List

class PrefixSum:
    """前缀和算法集合"""
    
    @staticmethod
    def build_prefix_sum(arr: List[int]) -> List[int]:
        """构建前缀和数组"""
        n = len(arr)
        prefix = [0] * (n + 1)
        for i in range(n):
            prefix[i + 1] = prefix[i] + arr[i]
        return prefix
    
    @staticmethod
    def range_sum(prefix: List[int], left: int, right: int) -> int:
        """计算区间 [left, right] 的和"""
        return prefix[right + 1] - prefix[left]
    
    @staticmethod
    def subarray_sum(nums: List[int], k: int) -> int:
        """
        和为k的子数组个数
        LeetCode 560
        """
        from collections import defaultdict
        
        count = 0
        prefix_sum = 0
        sum_count = defaultdict(int)
        sum_count[0] = 1  # 空前缀
        
        for num in nums:
            prefix_sum += num
            # 如果存在 prefix_sum - k，说明有子数组和为k
            count += sum_count[prefix_sum - k]
            sum_count[prefix_sum] += 1
        
        return count
    
    @staticmethod
    def find_max_length_binary(nums: List[int]) -> int:
        """
        二进制数组中0和1数量相等的最长子数组
        LeetCode 525
        """
        from collections import defaultdict
        
        # 将0视为-1，问题转化为和为0的最长子数组
        sum_index = defaultdict(int)
        sum_index[0] = -1
        prefix_sum = 0
        max_len = 0
        
        for i, num in enumerate(nums):
            prefix_sum += 1 if num == 1 else -1
            
            if prefix_sum in sum_index:
                max_len = max(max_len, i - sum_index[prefix_sum])
            else:
                sum_index[prefix_sum] = i
        
        return max_len
    
    @staticmethod
    def two_d_prefix_sum(matrix: List[List[int]]) -> List[List[int]]:
        """二维前缀和"""
        if not matrix or not matrix[0]:
            return []
        
        m, n = len(matrix), len(matrix[0])
        prefix = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                prefix[i][j] = (prefix[i-1][j] + prefix[i][j-1] 
                               - prefix[i-1][j-1] + matrix[i-1][j-1])
        
        return prefix
    
    @staticmethod
    def range_sum_2d(prefix: List[List[int]], 
                     r1: int, c1: int, r2: int, c2: int) -> int:
        """计算二维矩阵区间和"""
        return (prefix[r2+1][c2+1] - prefix[r1][c2+1] 
                - prefix[r2+1][c1] + prefix[r1][c1])


# 测试
def test_prefix_sum():
    # 一维前缀和
    arr = [1, 2, 3, 4, 5]
    prefix = PrefixSum.build_prefix_sum(arr)
    assert prefix == [0, 1, 3, 6, 10, 15]
    assert PrefixSum.range_sum(prefix, 1, 3) == 9  # 2+3+4
    
    # 和为k的子数组
    assert PrefixSum.subarray_sum([1, 1, 1], 2) == 2
    assert PrefixSum.subarray_sum([1, 2, 3], 3) == 2
    
    # 0和1相等的最长子数组
    assert PrefixSum.find_max_length_binary([0, 1]) == 2
    assert PrefixSum.find_max_length_binary([0, 1, 0]) == 2
    
    # 二维前缀和
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    prefix_2d = PrefixSum.two_d_prefix_sum(matrix)
    assert PrefixSum.range_sum_2d(prefix_2d, 0, 0, 1, 1) == 12  # 1+2+4+5
    
    print("✓ 前缀和测试通过!")


# 复杂度分析:
# 构建前缀和:
# - 时间复杂度: O(n)
# - 空间复杂度: O(n)
# 
# 区间查询:
# - 时间复杂度: O(1)
# - 空间复杂度: O(1)
```

---

## 8. 单调栈

```python
from typing import List

class MonotonicStack:
    """单调栈算法集合"""
    
    @staticmethod
    def next_greater_element(nums: List[int]) -> List[int]:
        """
        下一个更大元素
        LeetCode 496
        """
        n = len(nums)
        result = [-1] * n
        stack = []  # 单调递减栈
        
        for i in range(n):
            while stack and nums[stack[-1]] < nums[i]:
                result[stack.pop()] = nums[i]
            stack.append(i)
        
        return result
    
    @staticmethod
    def next_greater_element_circular(nums: List[int]) -> List[int]:
        """
        循环数组的下一个更大元素
        LeetCode 503
        """
        n = len(nums)
        result = [-1] * n
        stack = []
        
        # 遍历两遍
        for i in range(2 * n):
            idx = i % n
            while stack and nums[stack[-1]] < nums[idx]:
                result[stack.pop()] = nums[idx]
            if i < n:
                stack.append(idx)
        
        return result
    
    @staticmethod
    def largest_rectangle_in_histogram(heights: List[int]) -> int:
        """
        柱状图中最大的矩形
        LeetCode 84
        """
        heights = heights + [0]  # 添加哨兵
        stack = [-1]  # 单调递增栈
        max_area = 0
        
        for i in range(len(heights)):
            while stack[-1] != -1 and heights[stack[-1]] > heights[i]:
                h = heights[stack.pop()]
                w = i - stack[-1] - 1
                max_area = max(max_area, h * w)
            stack.append(i)
        
        return max_area
    
    @staticmethod
    def daily_temperatures(temperatures: List[int]) -> List[int]:
        """
        每日温度 - 等待多少天才能有更高温度
        LeetCode 739
        """
        n = len(temperatures)
        result = [0] * n
        stack = []  # 存储索引
        
        for i in range(n):
            while stack and temperatures[stack[-1]] < temperatures[i]:
                prev_idx = stack.pop()
                result[prev_idx] = i - prev_idx
            stack.append(i)
        
        return result
    
    @staticmethod
    def trapping_rain_water(height: List[int]) -> int:
        """
        接雨水
        LeetCode 42
        """
        if not height:
            return 0
        
        stack = []
        water = 0
        
        for i, h in enumerate(height):
            while stack and height[stack[-1]] < h:
                mid = stack.pop()
                if not stack:
                    break
                left = stack[-1]
                # 计算当前位置能接的水
                min_height = min(height[left], h)
                water += (min_height - height[mid]) * (i - left - 1)
            stack.append(i)
        
        return water


# 测试
def test_monotonic_stack():
    # 下一个更大元素
    assert MonotonicStack.next_greater_element([4, 5, 2, 25]) == [5, 25, 25, -1]
    
    # 循环数组下一个更大元素
    assert MonotonicStack.next_greater_element_circular([1, 2, 1]) == [2, -1, 2]
    
    # 最大矩形
    assert MonotonicStack.largest_rectangle_in_histogram([2, 1, 5, 6, 2, 3]) == 10
    
    # 每日温度
    assert MonotonicStack.daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == \
           [1, 1, 4, 2, 1, 1, 0, 0]
    
    # 接雨水
    assert MonotonicStack.trapping_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    
    print("✓ 单调栈测试通过!")


# 复杂度分析:
# - 时间复杂度: O(n) - 每个元素最多入栈出栈一次
# - 空间复杂度: O(n) - 栈的空间
```

---

## 9. 并查集

```python
from typing import List, Dict

class UnionFind:
    """并查集 (Union-Find / Disjoint Set)"""
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # 连通分量数
    
    def find(self, x: int) -> int:
        """查找根节点 - 路径压缩"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """
        合并两个集合 - 按秩合并
        返回是否成功合并（如果已在同一集合则返回False）
        """
        px, py = self.find(x), self.find(y)
        
        if px == py:
            return False
        
        # 按秩合并
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        self.count -= 1
        return True
    
    def connected(self, x: int, y: int) -> bool:
        """判断两个节点是否连通"""
        return self.find(x) == self.find(y)
    
    def get_count(self) -> int:
        """获取连通分量数"""
        return self.count


class UnionFindApplications:
    """并查集应用"""
    
    @staticmethod
    def find_redundant_connection(edges: List[List[int]]) -> List[int]:
        """
        冗余连接 - 找出导致环的边
        LeetCode 684
        """
        n = len(edges)
        uf = UnionFind(n + 1)
        
        for u, v in edges:
            if not uf.union(u, v):
                return [u, v]
        
        return []
    
    @staticmethod
    def num_islands(grid: List[List[str]]) -> int:
        """
        岛屿数量
        LeetCode 200
        """
        if not grid or not grid[0]:
            return 0
        
        m, n = len(grid), len(grid[0])
        uf = UnionFind(m * n)
        water_count = 0
        
        directions = [(0, 1), (1, 0)]
        
        for i in range(m):
            for j in range(n):
                if grid[i][j] == '0':
                    water_count += 1
                    continue
                
                # 只检查右和下，避免重复
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] == '1':
                        uf.union(i * n + j, ni * n + nj)
        
        return uf.get_count() - water_count
    
    @staticmethod
    def accounts_merge(accounts: List[List[str]]) -> List[List[str]]:
        """
        账户合并
        LeetCode 721
        """
        email_to_id = {}
        email_to_name = {}
        id_counter = 0
        
        # 给每个邮箱分配ID
        for account in accounts:
            name = account[0]
            for email in account[1:]:
                if email not in email_to_id:
                    email_to_id[email] = id_counter
                    email_to_name[email] = name
                    id_counter += 1
        
        uf = UnionFind(id_counter)
        
        # 合并同一账户的邮箱
        for account in accounts:
            first_id = email_to_id[account[1]]
            for email in account[2:]:
                uf.union(first_id, email_to_id[email])
        
        # 收集结果
        root_to_emails = {}
        for email, id_ in email_to_id.items():
            root = uf.find(id_)
            if root not in root_to_emails:
                root_to_emails[root] = []
            root_to_emails[root].append(email)
        
        # 排序并添加名字
        result = []
        for emails in root_to_emails.values():
            emails.sort()
            result.append([email_to_name[emails[0]]] + emails)
        
        return result


# 测试
def test_union_find():
    # 基本功能测试
    uf = UnionFind(5)
    assert uf.get_count() == 5
    uf.union(0, 1)
    assert uf.connected(0, 1)
    assert uf.get_count() == 4
    uf.union(2, 3)
    uf.union(1, 2)
    assert uf.connected(0, 3)
    assert uf.get_count() == 2
    
    # 冗余连接
    assert UnionFindApplications.find_redundant_connection([[1,2],[1,3],[2,3]]) == [2, 3]
    
    # 岛屿数量
    grid = [
        ["1","1","0","0","0"],
        ["1","1","0","0","0"],
        ["0","0","1","0","0"],
        ["0","0","0","1","1"]
    ]
    assert UnionFindApplications.num_islands(grid) == 3
    
    print("✓ 并查集测试通过!")


# 复杂度分析:
# - 时间复杂度: 
#   - find: O(α(n)) ≈ O(1), α为阿克曼函数的反函数
#   - union: O(α(n)) ≈ O(1)
# - 空间复杂度: O(n)
# - 近乎常数时间操作
```

---

## 10. 线段树

```python
from typing import List, Optional

class SegmentTree:
    """线段树 - 支持区间查询和单点更新"""
    
    def __init__(self, data: List[int]):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(data, 1, 0, self.n - 1)
    
    def _build(self, data: List[int], node: int, start: int, end: int):
        """构建线段树"""
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self._build(data, 2 * node, start, mid)
            self._build(data, 2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
    
    def update(self, index: int, value: int):
        """单点更新"""
        self._update(1, 0, self.n - 1, index, value)
    
    def _update(self, node: int, start: int, end: int, index: int, value: int):
        if start == end:
            self.tree[node] = value
        else:
            mid = (start + end) // 2
            if index <= mid:
                self._update(2 * node, start, mid, index, value)
            else:
                self._update(2 * node + 1, mid + 1, end, index, value)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
    
    def query(self, left: int, right: int) -> int:
        """区间查询"""
        return self._query(1, 0, self.n - 1, left, right)
    
    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        if right < start or left > end:
            return 0
        if left <= start and end <= right:
            return self.tree[node]
        
        mid = (start + end) // 2
        left_sum = self._query(2 * node, start, mid, left, right)
        right_sum = self._query(2 * node + 1, mid + 1, end, left, right)
        return left_sum + right_sum


class SegmentTreeLazy:
    """线段树 - 支持区间更新（懒惰传播）"""
    
    def __init__(self, data: List[int]):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        if self.n > 0:
            self._build(data, 1, 0, self.n - 1)
    
    def _build(self, data: List[int], node: int, start: int, end: int):
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self._build(data, 2 * node, start, mid)
            self._build(data, 2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
    
    def _push_down(self, node: int, start: int, end: int):
        """下推懒惰标记"""
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            left_len = mid - start + 1
            right_len = end - mid
            
            self.tree[2 * node] += self.lazy[node] * left_len
            self.tree[2 * node + 1] += self.lazy[node] * right_len
            self.lazy[2 * node] += self.lazy[node]
            self.lazy[2 * node + 1] += self.lazy[node]
            self.lazy[node] = 0
    
    def update_range(self, left: int, right: int, value: int):
        """区间更新"""
        self._update_range(1, 0, self.n - 1, left, right, value)
    
    def _update_range(self, node: int, start: int, end: int, 
                      left: int, right: int, value: int):
        if left > end or right < start:
            return
        
        if left <= start and end <= right:
            self.tree[node] += value * (end - start + 1)
            self.lazy[node] += value
            return
        
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self._update_range(2 * node, start, mid, left, right, value)
        self._update_range(2 * node + 1, mid + 1, end, left, right, value)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
    
    def query(self, left: int, right: int) -> int:
        """区间查询"""
        return self._query(1, 0, self.n - 1, left, right)
    
    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        if left > end or right < start:
            return 0
        
        if left <= start and end <= right:
            return self.tree[node]
        
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return (self._query(2 * node, start, mid, left, right) +
                self._query(2 * node + 1, mid + 1, end, left, right))


class SegmentTreeMax:
    """线段树 - 区间最大值查询"""
    
    def __init__(self, data: List[int]):
        self.n = len(data)
        self.tree = [float('-inf')] * (4 * self.n)
        if self.n > 0:
            self._build(data, 1, 0, self.n - 1)
    
    def _build(self, data: List[int], node: int, start: int, end: int):
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self._build(data, 2 * node, start, mid)
            self._build(data, 2 * node + 1, mid + 1, end)
            self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])
    
    def update(self, index: int, value: int):
        self._update(1, 0, self.n - 1, index, value)
    
    def _update(self, node: int, start: int, end: int, index: int, value: int):
        if start == end:
            self.tree[node] = value
        else:
            mid = (start + end) // 2
            if index <= mid:
                self._update(2 * node, start, mid, index, value)
            else:
                self._update(2 * node + 1, mid + 1, end, index, value)
            self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])
    
    def query(self, left: int, right: int) -> int:
        return self._query(1, 0, self.n - 1, left, right)
    
    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        if right < start or left > end:
            return float('-inf')
        if left <= start and end <= right:
            return self.tree[node]
        
        mid = (start + end) // 2
        return max(
            self._query(2 * node, start, mid, left, right),
            self._query(2 * node + 1, mid + 1, end, left, right)
        )


# 测试
def test_segment_tree():
    # 基本线段树测试
    data = [1, 3, 5, 7, 9, 11]
    st = SegmentTree(data)
    
    assert st.query(0, 2) == 9  # 1+3+5
    assert st.query(1, 4) == 24  # 3+5+7+9
    
    st.update(2, 10)
    assert st.query(0, 2) == 14  # 1+3+10
    
    # 懒惰传播线段树测试
    data2 = [1, 2, 3, 4, 5]
    st_lazy = SegmentTreeLazy(data2)
    
    assert st_lazy.query(0, 4) == 15
    
    st_lazy.update_range(1, 3, 2)  # [1,4,5,6,5]
    assert st_lazy.query(1, 3) == 15  # 4+5+6
    
    # 区间最大值线段树测试
    data3 = [1, 5, 3, 7, 2, 8]
    st_max = SegmentTreeMax(data3)
    
    assert st_max.query(0, 3) == 7
    assert st_max.query(2, 5) == 8
    
    st_max.update(2, 10)
    assert st_max.query(0, 3) == 10
    
    print("✓ 线段树测试通过!")


# 复杂度分析:
# 构建线段树:
# - 时间复杂度: O(n)
# - 空间复杂度: O(n)
# 
# 单点更新:
# - 时间复杂度: O(log n)
# 
# 区间查询:
# - 时间复杂度: O(log n)
# 
# 区间更新（懒惰传播）:
# - 时间复杂度: O(log n)
```

---

## 综合测试

```python
def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始运行所有算法测试...")
    print("=" * 50 + "\n")
    
    test_quick_sort()
    test_merge_sort()
    test_tree_traversal()
    test_knapsack()
    test_graph_traversal()
    test_dijkstra()
    test_sliding_window()
    test_prefix_sum()
    test_monotonic_stack()
    test_union_find()
    test_segment_tree()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
```

---

## 复杂度总结表

| 算法 | 时间复杂度 | 空间复杂度 | 稳定性 |
|------|-----------|-----------|--------|
| 快速排序 | O(n log n) 平均 | O(log n) | 不稳定 |
| 归并排序 | O(n log n) | O(n) | 稳定 |
| 二叉树遍历 | O(n) | O(h) | - |
| 0-1背包 | O(nW) | O(nW) | - |
| 图BFS/DFS | O(V+E) | O(V) | - |
| Dijkstra | O((V+E)logV) | O(V) | - |
| 滑动窗口 | O(n) | O(k) | - |
| 前缀和 | O(n)构建/O(1)查询 | O(n) | - |
| 单调栈 | O(n) | O(n) | - |
| 并查集 | O(α(n)) ≈ O(1) | O(n) | - |
| 线段树 | O(log n) | O(n) | - |

---

*文档生成时间: 2026-02-18*
*作者: OpenClaw AI Assistant*
