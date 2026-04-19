# LeetCode Medium Problems - Set 002

## Problem: Add Two Numbers (Linked List)

You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

**Example:**
```
Input: l1 = [2,4,3], l2 = [5,6,4]
Output: [7,0,8]
Explanation: 342 + 465 = 807
```

### Solution
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummy = ListNode(0)
        curr = dummy
        carry = 0
        
        while l1 or l2 or carry:
            # Get values from both lists (or 0 if None)
            val1 = l1.val if l1 else 0
            val2 = l2.val if l2 else 0
            
            # Calculate sum and carry
            total = val1 + val2 + carry
            carry = total // 10
            digit = total % 10
            
            # Create new node
            curr.next = ListNode(digit)
            curr = curr.next
            
            # Move to next nodes
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
        
        return dummy.next
```

### Complexity: O(max(m, n))
- Time: O(max(m, n)) where m and n are lengths of the two lists
- Space: O(max(m, n)) for the result list

---

## Problem: Longest Palindromic Substring

Given a string `s`, return the longest palindromic substring in `s`.

**Example:**
```
Input: s = "babad"
Output: "bab"
Explanation: "aba" is also a valid answer
```

### Solution
```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        if not s or len(s) == 1:
            return s
        
        start, max_len = 0, 1
        
        def expand_around_center(left: int, right: int) -> int:
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            return right - left - 1
        
        for i in range(len(s)):
            # Odd length palindrome
            len1 = expand_around_center(i, i)
            # Even length palindrome
            len2 = expand_around_center(i, i + 1)
            
            curr_len = max(len1, len2)
            
            if curr_len > max_len:
                max_len = curr_len
                start = i - (curr_len - 1) // 2
        
        return s[start:start + max_len]
```

### Complexity: O(n²)
- Time: O(n²) where n is the string length
- Space: O(1) for constant extra space

---

## Problem: Generate Parentheses

Given `n` pairs of parentheses, write a function to generate all combinations of well-formed parentheses.

**Example:**
```
Input: n = 3
Output: ["((()))","(()())","(())()","()(())","()()()"]
```

### Solution
```python
class Solution:
    def generateParenthesis(self, n: int) -> list[str]:
        result = []
        
        def backtrack(current: str, open_count: int, close_count: int):
            if len(current) == 2 * n:
                result.append(current)
                return
            
            # Add opening parenthesis if we have remaining
            if open_count < n:
                backtrack(current + '(', open_count + 1, close_count)
            
            # Add closing parenthesis if it won't create invalid sequence
            if close_count < open_count:
                backtrack(current + ')', open_count, close_count + 1)
        
        backtrack("", 0, 0)
        return result
```

### Complexity: O(4ⁿ/√n)
- Time: O(4ⁿ/√n) - related to the nth Catalan number
- Space: O(4ⁿ/√n) for storing all valid combinations

---

## Problem: Merge Intervals

Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

**Example:**
```
Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6]
```

### Solution
```python
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        if not intervals:
            return []
        
        # Sort intervals by start time
        intervals.sort(key=lambda x: x[0])
        
        merged = [intervals[0]]
        
        for current in intervals[1:]:
            last = merged[-1]
            
            # If current interval overlaps with the last merged interval
            if current[0] <= last[1]:
                # Merge by extending the end
                last[1] = max(last[1], current[1])
            else:
                # No overlap, add current interval
                merged.append(current)
        
        return merged
```

### Complexity: O(n log n)
- Time: O(n log n) for sorting
- Space: O(n) for the merged intervals (or O(log n) for sorting in-place)

---

## Problem: Spiral Matrix

Given an `m x n` matrix, return all elements of the matrix in spiral order.

**Example:**
```
Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
Output: [1,2,3,6,9,8,7,4,5]
```

### Solution
```python
class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        if not matrix or not matrix[0]:
            return []
        
        result = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1
        
        while top <= bottom and left <= right:
            # Traverse right
            for col in range(left, right + 1):
                result.append(matrix[top][col])
            top += 1
            
            # Traverse down
            for row in range(top, bottom + 1):
                result.append(matrix[row][right])
            right -= 1
            
            # Traverse left (if still valid)
            if top <= bottom:
                for col in range(right, left - 1, -1):
                    result.append(matrix[bottom][col])
                bottom -= 1
            
            # Traverse up (if still valid)
            if left <= right:
                for row in range(bottom, top - 1, -1):
                    result.append(matrix[row][left])
                left += 1
        
        return result
```

### Complexity: O(m × n)
- Time: O(m × n) where m and n are matrix dimensions
- Space: O(1) extra space (O(m × n) for output)

---

## Summary

| Problem | Technique | Time | Space |
|---------|-----------|------|-------|
| Add Two Numbers | Linked List + Carry | O(max(m,n)) | O(max(m,n)) |
| Longest Palindromic Substring | Expand Around Center | O(n²) | O(1) |
| Generate Parentheses | Backtracking | O(4ⁿ/√n) | O(4ⁿ/√n) |
| Merge Intervals | Sorting + Greedy | O(n log n) | O(n) |
| Spiral Matrix | Boundary Traversal | O(m × n) | O(1) |
