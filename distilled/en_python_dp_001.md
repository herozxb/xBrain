# Python Dynamic Programming: Classic Problems

## Problem 1: Longest Common Subsequence (LCS)

### Problem Description
Given two strings, find the length of their longest common subsequence.

### Solution

```python
def longest_common_subsequence(text1: str, text2: str) -> int:
    """
    Find the length of the longest common subsequence between two strings.
    
    Time Complexity: O(m * n)
    Space Complexity: O(min(m, n)) with space optimization
    """
    if len(text1) < len(text2):
        text1, text2 = text2, text1
    
    m, n = len(text1), len(text2)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev, curr = curr, prev
    
    return prev[n]

def lcs_with_path(text1: str, text2: str) -> tuple[int, str]:
    """
    Return both the length and the actual LCS string.
    
    Time Complexity: O(m * n)
    Space Complexity: O(m * n)
    """
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Build DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Reconstruct the LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if text1[i-1] == text2[j-1]:
            lcs.append(text1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return dp[m][n], ''.join(reversed(lcs))
```

### Tests

```python
import pytest

class TestLCS:
    def test_basic_cases(self):
        assert longest_common_subsequence("abcde", "ace") == 3
        assert longest_common_subsequence("abc", "abc") == 3
        assert longest_common_subsequence("abc", "def") == 0
    
    def test_empty_strings(self):
        assert longest_common_subsequence("", "abc") == 0
        assert longest_common_subsequence("abc", "") == 0
        assert longest_common_subsequence("", "") == 0
    
    def test_single_character(self):
        assert longest_common_subsequence("a", "a") == 1
        assert longest_common_subsequence("a", "b") == 0
    
    def test_with_path(self):
        length, path = lcs_with_path("abcde", "ace")
        assert length == 3
        assert path == "ace"
    
    def test_longer_strings(self):
        text1 = "abcdefghijklmnop"
        text2 = "acegikmo"
        assert longest_common_subsequence(text1, text2) == 8
    
    def test_repeated_characters(self):
        assert longest_common_subsequence("aaa", "aa") == 2
        assert longest_common_subsequence("abab", "baba") == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Complexity Analysis

| Approach | Time | Space |
|----------|------|-------|
| Standard DP | O(m×n) | O(m×n) |
| Space Optimized | O(m×n) | O(min(m,n)) |

**Key Insights:**
- DP recurrence: `dp[i][j] = dp[i-1][j-1] + 1` if match, else `max(dp[i-1][j], dp[i][j-1])`
- Space optimization uses two rows instead of full matrix
- Path reconstruction requires storing full DP table

---

## Problem 2: Edit Distance (Levenshtein Distance)

### Problem Description
Given two strings, find the minimum number of operations (insert, delete, replace) to transform one string into another.

### Solution

```python
def edit_distance(word1: str, word2: str) -> int:
    """
    Calculate minimum edit distance between two strings.
    
    Operations: insert, delete, replace (each costs 1)
    
    Time Complexity: O(m * n)
    Space Complexity: O(min(m, n))
    """
    if len(word1) < len(word2):
        word1, word2 = word2, word1
    
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))
    
    for i in range(1, m + 1):
        curr = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                curr[j] = prev[j-1]
            else:
                curr[j] = 1 + min(
                    prev[j],      # delete
                    curr[j-1],    # insert
                    prev[j-1]     # replace
                )
        prev = curr
    
    return prev[n]

def edit_distance_with_operations(word1: str, word2: str) -> tuple[int, list[str]]:
    """
    Return edit distance and the list of operations.
    """
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    # Backtrack to find operations
    operations = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and word1[i-1] == word2[j-1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            operations.append(f"Replace '{word1[i-1]}' with '{word2[j-1]}'")
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
            operations.append(f"Insert '{word2[j-1]}'")
            j -= 1
        else:
            operations.append(f"Delete '{word1[i-1]}'")
            i -= 1
    
    return dp[m][n], list(reversed(operations))
```

### Tests

```python
class TestEditDistance:
    def test_basic_cases(self):
        assert edit_distance("horse", "ros") == 3
        assert edit_distance("intention", "execution") == 5
    
    def test_identical_strings(self):
        assert edit_distance("hello", "hello") == 0
    
    def test_empty_strings(self):
        assert edit_distance("", "abc") == 3
        assert edit_distance("abc", "") == 3
        assert edit_distance("", "") == 0
    
    def test_single_operations(self):
        # Single insert
        assert edit_distance("a", "ab") == 1
        # Single delete
        assert edit_distance("ab", "a") == 1
        # Single replace
        assert edit_distance("a", "b") == 1
    
    def test_with_operations(self):
        dist, ops = edit_distance_with_operations("cat", "bat")
        assert dist == 1
        assert "Replace" in ops[0]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Complexity Analysis

| Metric | Value |
|--------|-------|
| Time | O(m × n) |
| Space | O(min(m, n)) optimized |

**DP State Transition:**
```
dp[i][j] = dp[i-1][j-1]           if word1[i-1] == word2[j-1]
dp[i][j] = 1 + min(
    dp[i-1][j],    # delete from word1
    dp[i][j-1],    # insert into word1
    dp[i-1][j-1]   # replace in word1
)                  otherwise
```

---

## Problem 3: Knapsack Problem (0/1)

### Problem Description
Given weights and values of n items, put them in a knapsack of capacity W to maximize total value.

### Solution

```python
from typing import List

def knapsack_01(weights: List[int], values: List[int], capacity: int) -> int:
    """
    0/1 Knapsack - each item can be taken at most once.
    
    Time Complexity: O(n * W)
    Space Complexity: O(W) with optimization
    """
    n = len(weights)
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # Traverse backwards to avoid using same item twice
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]

def knapsack_with_items(weights: List[int], values: List[int], 
                        capacity: int) -> tuple[int, List[int]]:
    """
    Return max value and indices of selected items.
    """
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    # Build DP table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(
                    dp[i-1][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )
            else:
                dp[i][w] = dp[i-1][w]
    
    # Find selected items
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(i - 1)
            w -= weights[i-1]
    
    return dp[n][capacity], list(reversed(selected))

def unbounded_knapsack(weights: List[int], values: List[int], 
                       capacity: int) -> int:
    """
    Unbounded Knapsack - items can be taken multiple times.
    
    Time Complexity: O(n * W)
    Space Complexity: O(W)
    """
    dp = [0] * (capacity + 1)
    
    for w in range(capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= w:
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]
```

### Tests

```python
class TestKnapsack:
    def test_basic_case(self):
        weights = [1, 3, 4, 5]
        values = [1, 4, 5, 7]
        capacity = 7
        assert knapsack_01(weights, values, capacity) == 9
    
    def test_zero_capacity(self):
        assert knapsack_01([1, 2, 3], [10, 20, 30], 0) == 0
    
    def test_single_item_fits(self):
        assert knapsack_01([5], [10], 5) == 10
        assert knapsack_01([5], [10], 4) == 0
    
    def test_with_items(self):
        weights = [2, 3, 4, 5]
        values = [3, 4, 5, 6]
        capacity = 5
        value, items = knapsack_with_items(weights, values, capacity)
        assert value == 7
        assert len(items) == 2
    
    def test_unbounded(self):
        weights = [1, 2, 3]
        values = [1, 4, 6]
        capacity = 3
        # Best: take weight 2 twice (value 8) or weight 1 three times
        assert unbounded_knapsack(weights, values, capacity) == 8

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Complexity Analysis

| Variant | Time | Space |
|---------|------|-------|
| 0/1 Knapsack | O(n×W) | O(W) |
| With Item Tracking | O(n×W) | O(n×W) |
| Unbounded | O(n×W) | O(W) |

**Key Differences:**
- **0/1**: Iterate weights backwards to prevent reuse
- **Unbounded**: Iterate forwards, allow item reuse
- **Tracking items**: Requires full DP table for backtracking

---

## Summary

| Problem | Pattern | Time | Space |
|---------|---------|------|-------|
| LCS | 2D DP | O(m×n) | O(min(m,n)) |
| Edit Distance | 2D DP | O(m×n) | O(min(m,n)) |
| Knapsack 0/1 | 1D DP | O(n×W) | O(W) |

**Common DP Optimization Techniques:**
1. Space optimization using rolling arrays
2. State compression
3. Early termination when possible
4. Using the smaller dimension for space efficiency
