# Robust Python Algorithm Collection
# Generated: 2026-02-19 01:19

---

## Binary Search
```python
# PROBLEM: Find target in sorted array
# TIME: O(log n) SPACE: O(1)
def binary_search(arr, target):
    left, right = 0, len(arr)-1
    while left <= right:
        mid = (left+right)//2
        if arr[mid]==target: return mid
        elif arr[mid]<target: left=mid+1
        else: right=mid-1
    return -1
```

---

## Two Sum
```python
# PROBLEM: Find two numbers that add up to target
# TIME: O(n) SPACE: O(n)
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

---

## Reverse Linked List
```python
# PROBLEM: Reverse a singly linked list
# TIME: O(n) SPACE: O(1)
def reverse_list(head):
    prev = None
    curr = head
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    return prev
```

---

## Valid Parentheses
```python
# PROBLEM: Check if parentheses string is valid
# TIME: O(n) SPACE: O(n)
def is_valid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)
    return not stack
```

---

## Maximum Depth of Binary Tree
```python
# PROBLEM: Find max depth of binary tree
# TIME: O(n) SPACE: O(h)
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

---

## Merge Two Sorted Lists
```python
# PROBLEM: Merge two sorted linked lists
# TIME: O(n+m) SPACE: O(1)
def merge_two_lists(l1, l2):
    dummy = ListNode(0)
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

---

## Best Time to Buy and Sell Stock
```python
# PROBLEM: Max profit from single buy/sell
# TIME: O(n) SPACE: O(1)
def max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit
```

---

## Contains Duplicate
```python
# PROBLEM: Check if array has duplicates
# TIME: O(n) SPACE: O(n)
def contains_duplicate(nums):
    return len(nums) != len(set(nums))
```

---

## Maximum Subarray
```python
# PROBLEM: Find contiguous subarray with largest sum
# TIME: O(n) SPACE: O(1)
def max_subarray(nums):
    max_sum = curr_sum = nums[0]
    for num in nums[1:]:
        curr_sum = max(num, curr_sum + num)
        max_sum = max(max_sum, curr_sum)
    return max_sum
```

---

## Climbing Stairs
```python
# PROBLEM: Count ways to climb n stairs (1 or 2 steps)
# TIME: O(n) SPACE: O(1)
def climb_stairs(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n+1):
        a, b = b, a + b
    return b
```

---

## Binary Tree Level Order Traversal
```python
# PROBLEM: Traverse tree level by level
# TIME: O(n) SPACE: O(n)
def level_order(root):
    if not root:
        return []
    result, queue = [], [root]
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

---

## Validate Binary Search Tree
```python
# PROBLEM: Check if tree is valid BST
# TIME: O(n) SPACE: O(h)
def is_valid_bst(root, low=float('-inf'), high=float('inf')):
    if not root:
        return True
    if not (low < root.val < high):
        return False
    return (is_valid_bst(root.left, low, root.val) and
            is_valid_bst(root.right, root.val, high))
```

---

## Symmetric Tree
```python
# PROBLEM: Check if tree is mirror of itself
# TIME: O(n) SPACE: O(h)
def is_symmetric(root):
    def mirror(t1, t2):
        if not t1 and not t2:
            return True
        if not t1 or not t2:
            return False
        return (t1.val == t2.val and
                mirror(t1.left, t2.right) and
                mirror(t1.right, t2.left))
    return mirror(root, root)
```

---

## Palindrome Number
```python
# PROBLEM: Check if integer is palindrome
# TIME: O(log n) SPACE: O(1)
def is_palindrome(x):
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    reversed_half = 0
    while x > reversed_half:
        reversed_half = reversed_half * 10 + x % 10
        x //= 10
    return x == reversed_half or x == reversed_half // 10
```

---

## Longest Common Prefix
```python
# PROBLEM: Find longest common prefix string
# TIME: O(S) SPACE: O(1)
def longest_common_prefix(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
```

---

## Plus One
```python
# PROBLEM: Add one to large integer represented as array
# TIME: O(n) SPACE: O(1)
def plus_one(digits):
    for i in range(len(digits)-1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    return [1] + digits
```

---

## Remove Duplicates from Sorted Array
```python
# PROBLEM: Remove duplicates in-place, return new length
# TIME: O(n) SPACE: O(1)
def remove_duplicates(nums):
    if not nums:
        return 0
    j = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[i-1]:
            nums[j] = nums[i]
            j += 1
    return j
```

---

## Search Insert Position
```python
# PROBLEM: Find insert position for target in sorted array
# TIME: O(log n) SPACE: O(1)
def search_insert(nums, target):
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

---

## First Bad Version
```python
# PROBLEM: Find first bad version in series
# TIME: O(log n) SPACE: O(1)
def first_bad_version(n):
    left, right = 1, n
    while left < right:
        mid = (left + right) // 2
        if isBadVersion(mid):
            right = mid
        else:
            left = mid + 1
    return left
```

---

## Intersection of Two Arrays
```python
# PROBLEM: Find common elements between two arrays
# TIME: O(n+m) SPACE: O(min(n,m))
def intersection(nums1, nums2):
    set1 = set(nums1)
    return list(set(num for num in nums2 if num in set1))
```

---
