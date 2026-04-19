# Code Interview Practice Problems - Batch 1

## Problem: Two Sum

```python
# PROBLEM: Find two numbers in array that add up to target
# APPROACH: Use hash map to store complements, single pass
# TIME: O(n)  SPACE: O(n)

def two_sum(nums, target):
    # Step 1: Create hash map to store number -> index
    seen = {}
    # Step 2: For each number, check if complement exists
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Explanation**: We iterate through the array once, storing each number's index in a hash map. For each number, we calculate its complement (target - num). If the complement already exists in our map, we've found our pair. This achieves O(n) time complexity by trading space for time.

---

## Problem: Merge Sorted Arrays

```python
# PROBLEM: Merge two sorted arrays into one sorted array
# APPROACH: Two-pointer technique, compare and merge
# TIME: O(m + n)  SPACE: O(m + n)

def merge_sorted(arr1, arr2):
    # Step 1: Initialize pointers and result array
    i, j = 0, 0
    result = []
    # Step 2: Compare elements and add smaller one
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1
    # Step 3: Add remaining elements
    result.extend(arr1[i:])
    result.extend(arr2[j:])
    return result
```

**Explanation**: Using two pointers, we compare the current elements of both arrays and always take the smaller one. This maintains sorted order. Once one array is exhausted, we append all remaining elements from the other array since they're already sorted.

---

## Problem: Binary Search

```python
# PROBLEM: Find target in sorted array efficiently
# APPROACH: Divide and conquer, halve search space each step
# TIME: O(log n)  SPACE: O(1)

def binary_search(arr, target):
    # Step 1: Initialize left and right boundaries
    left, right = 0, len(arr) - 1
    # Step 2: While search space exists
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Explanation**: Binary search works by repeatedly dividing the search interval in half. We compare the target with the middle element and eliminate half the search space each time. This logarithmic time complexity makes it extremely efficient for large sorted datasets.

---

## Problem: Maximum Subarray (Kadane's Algorithm)

```python
# PROBLEM: Find contiguous subarray with largest sum
# APPROACH: Dynamic programming, track current and global max
# TIME: O(n)  SPACE: O(1)

def max_subarray(nums):
    # Step 1: Initialize with first element
    current_max = global_max = nums[0]
    # Step 2: For each element, decide to extend or start fresh
    for num in nums[1:]:
        current_max = max(num, current_max + num)
        global_max = max(global_max, current_max)
    return global_max
```

**Explanation**: Kadane's algorithm maintains two values: the maximum sum ending at the current position, and the overall maximum. For each element, we either extend the previous subarray or start a new one from the current element, whichever gives a larger sum.

---

## Problem: Valid Parentheses

```python
# PROBLEM: Check if parentheses string is valid (balanced)
# APPROACH: Use stack to track opening brackets
# TIME: O(n)  SPACE: O(n)

def is_valid_parentheses(s):
    # Step 1: Create mapping of closing to opening brackets
    mapping = {')': '(', ']': '[', '}': '{'}
    stack = []
    # Step 2: For each char, push or pop from stack
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)
    return len(stack) == 0
```

**Explanation**: We use a stack to keep track of opening brackets. When we encounter a closing bracket, it must match the most recent opening bracket (top of stack). If the stack is empty at the end, all brackets were properly matched.

---

## Problem: Reverse Linked List

```python
# PROBLEM: Reverse a singly linked list
# APPROACH: Iterative three-pointer technique
# TIME: O(n)  SPACE: O(1)

def reverse_list(head):
    # Step 1: Initialize previous, current pointers
    prev = None
    current = head
    # Step 2: Reverse links one by one
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    return prev
```

**Explanation**: We maintain three pointers: prev, current, and next_temp. At each step, we reverse the link from current to point to prev, then advance all pointers. The key is storing next_temp before breaking the link.

---

## Problem: BFS Graph Traversal

```python
# PROBLEM: Traverse graph level by level from starting node
# APPROACH: Use queue for breadth-first exploration
# TIME: O(V + E)  SPACE: O(V)

from collections import deque

def bfs(graph, start):
    # Step 1: Initialize queue and visited set
    visited = set()
    queue = deque([start])
    result = []
    # Step 2: Process nodes level by level
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            result.append(node)
            queue.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
    return result
```

**Explanation**: BFS explores a graph level by level using a queue. We mark nodes as visited to avoid cycles and process neighbors in FIFO order, ensuring we visit all nodes at distance k before any nodes at distance k+1.

---

## Problem: DFS Graph Traversal

```python
# PROBLEM: Traverse graph depth-first from starting node
# APPROACH: Recursive exploration with visited tracking
# TIME: O(V + E)  SPACE: O(V)

def dfs(graph, node, visited=None):
    # Step 1: Initialize visited set on first call
    if visited is None:
        visited = set()
    # Step 2: Mark current node and recurse on neighbors
    visited.add(node)
    result = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))
    return result
```

**Explanation**: DFS explores as deep as possible before backtracking. We recursively visit unvisited neighbors, which naturally implements a stack-based traversal. This is useful for pathfinding, cycle detection, and topological sorting.

---

## Problem: Climbing Stairs

```python
# PROBLEM: Count ways to climb n stairs (1 or 2 steps at a time)
# APPROACH: Dynamic programming, Fibonacci-like pattern
# TIME: O(n)  SPACE: O(1)

def climb_stairs(n):
    # Step 1: Handle base cases
    if n <= 2:
        return n
    # Step 2: Use rolling variables for Fibonacci sequence
    prev1, prev2 = 2, 1
    for i in range(3, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    return prev1
```

**Explanation**: This is essentially the Fibonacci sequence. To reach step n, you either came from step n-1 (one step) or step n-2 (two steps). So the total ways is the sum of ways to reach those two previous steps.

---

## Problem: Best Time to Buy and Sell Stock

```python
# PROBLEM: Find maximum profit from single buy/sell transaction
# APPROACH: Track minimum price and maximum profit
# TIME: O(n)  SPACE: O(1)

def max_profit(prices):
    # Step 1: Initialize min price and max profit
    min_price = float('inf')
    max_profit = 0
    # Step 2: Update min price and calculate potential profit
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit
```

**Explanation**: We track the minimum price seen so far and calculate the profit if we sold at the current price. The maximum of all these potential profits is our answer. We must buy before selling, hence tracking minimum from the past.

---

## Problem: Contains Duplicate

```python
# PROBLEM: Check if array contains any duplicates
# APPROACH: Use hash set for O(1) lookups
# TIME: O(n)  SPACE: O(n)

def contains_duplicate(nums):
    # Step 1: Create set to track seen numbers
    seen = set()
    # Step 2: Check each number against set
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

**Explanation**: A set provides O(1) average-time lookups and insertions. By adding each element to a set and checking if it already exists, we can detect duplicates in a single pass through the array.

---

## Problem: Invert Binary Tree

```python
# PROBLEM: Mirror/flip a binary tree
# APPROACH: Recursive swap of left and right children
# TIME: O(n)  SPACE: O(h) where h is height

def invert_tree(root):
    # Step 1: Base case - empty node
    if not root:
        return None
    # Step 2: Swap children and recurse
    root.left, root.right = root.right, root.left
    invert_tree(root.left)
    invert_tree(root.right)
    return root
```

**Explanation**: We recursively swap the left and right children of each node. The base case handles empty nodes. This classic problem demonstrates tree recursion and in-place modification.

---

## Problem: Maximum Depth of Binary Tree

```python
# PROBLEM: Find the maximum depth/height of binary tree
# APPROACH: Recursive depth calculation
# TIME: O(n)  SPACE: O(h)

def max_depth(root):
    # Step 1: Base case - empty tree has depth 0
    if not root:
        return 0
    # Step 2: Return 1 + max of left and right depths
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

**Explanation**: The depth of a tree is the length of the longest path from root to leaf. For each node, we recursively find the maximum depth of its subtrees and add 1 for the current node.

---

## Problem: Valid Anagram

```python
# PROBLEM: Check if two strings are anagrams
# APPROACH: Compare character frequency counts
# TIME: O(n)  SPACE: O(1) - fixed alphabet size

from collections import Counter

def is_anagram(s, t):
    # Step 1: Check length first
    if len(s) != len(t):
        return False
    # Step 2: Compare character counts
    return Counter(s) == Counter(t)
```

**Explanation**: Anagrams have the same characters with the same frequencies. Using Counter creates frequency dictionaries for both strings, and comparing them tells us if they're anagrams. The space is O(1) since the alphabet size is fixed.

---

## Problem: Longest Palindrome

```python
# PROBLEM: Find length of longest palindrome that can be built
# APPROACH: Count character frequencies, use pairs
# TIME: O(n)  SPACE: O(1)

def longest_palindrome(s):
    # Step 1: Count character frequencies
    char_counts = {}
    for char in s:
        char_counts[char] = char_counts.get(char, 0) + 1
    # Step 2: Calculate length using pairs and optional center
    length = 0
    odd_found = False
    for count in char_counts.values():
        length += count // 2 * 2
        if count % 2 == 1:
            odd_found = True
    return length + 1 if odd_found else length
```

**Explanation**: A palindrome reads the same forwards and backwards. We can use all pairs of characters, and at most one odd-count character can go in the center. We count pairs and add 1 if any odd count exists.

---

## Problem: Move Zeroes

```python
# PROBLEM: Move all zeros to end while maintaining order
# APPROACH: Two-pointer technique with swap
# TIME: O(n)  SPACE: O(1)

def move_zeroes(nums):
    # Step 1: Initialize position for non-zero elements
    pos = 0
    # Step 2: Move non-zero elements to front
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[pos], nums[i] = nums[i], nums[pos]
            pos += 1
```

**Explanation**: We maintain a pointer for where the next non-zero element should go. When we encounter a non-zero, we swap it to that position and increment the pointer. This maintains relative order of non-zero elements.

---

## Problem: First Unique Character

```python
# PROBLEM: Find index of first non-repeating character
# APPROACH: Count frequencies, then find first with count 1
# TIME: O(n)  SPACE: O(1)

def first_unique_char(s):
    # Step 1: Count character frequencies
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    # Step 2: Find first character with count 1
    for i, char in enumerate(s):
        if counts[char] == 1:
            return i
    return -1
```

**Explanation**: We first count all character frequencies in one pass, then scan again to find the first character with a count of 1. Two passes give us O(n) time with O(1) space for the fixed alphabet.

---

## Problem: Intersection of Two Arrays

```python
# PROBLEM: Find common elements between two arrays
# APPROACH: Use set intersection
# TIME: O(n + m)  SPACE: O(min(n, m))

def intersection(nums1, nums2):
    # Step 1: Convert smaller array to set
    set1 = set(nums1)
    set2 = set(nums2)
    # Step 2: Return intersection
    return list(set1 & set2)
```

**Explanation**: Converting arrays to sets removes duplicates and enables O(1) lookups. The set intersection operator & finds elements common to both sets efficiently.

---

## Problem: FizzBuzz

```python
# PROBLEM: Print Fizz for multiples of 3, Buzz for 5, FizzBuzz for both
# APPROACH: Check divisibility conditions in order
# TIME: O(n)  SPACE: O(n)

def fizzbuzz(n):
    # Step 1: Initialize result list
    result = []
    # Step 2: Check conditions and append appropriate string
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
```

**Explanation**: We check for divisibility by 15 first (both 3 and 5), then by 3, then by 5. The order matters - checking 3 and 5 separately before 15 would give incorrect results for numbers divisible by both.

---

## Problem: Rotate Array

```python
# PROBLEM: Rotate array to the right by k steps
# APPROACH: Triple reverse technique
# TIME: O(n)  SPACE: O(1)

def rotate(nums, k):
    # Step 1: Handle edge cases
    n = len(nums)
    k = k % n
    if k == 0:
        return
    # Step 2: Reverse entire array
    nums.reverse()
    # Step 3: Reverse first k and remaining elements
    nums[:k] = reversed(nums[:k])
    nums[k:] = reversed(nums[k:])
```

**Explanation**: The triple reverse technique: reverse the entire array, then reverse the first k elements, then reverse the remaining elements. This achieves in-place rotation with O(1) extra space.

---

## Problem: Single Number

```python
# PROBLEM: Find element that appears only once (others appear twice)
# APPROACH: XOR all numbers - duplicates cancel out
# TIME: O(n)  SPACE: O(1)

def single_number(nums):
    # Step 1: XOR all numbers
    result = 0
    for num in nums:
        result ^= num
    return result
```

**Explanation**: XOR has properties: a ^ a = 0 and a ^ 0 = a. When we XOR all numbers together, pairs cancel out to 0, leaving only the single number. This elegant solution uses constant space.

---

## Problem: Happy Number

```python
# PROBLEM: Determine if number is happy (sum of squares of digits reaches 1)
# APPROACH: Floyd's cycle detection or set tracking
# TIME: O(log n)  SPACE: O(1) with Floyd's

def is_happy(n):
    # Step 1: Helper to calculate sum of squares of digits
    def get_next(num):
        total = 0
        while num > 0:
            digit = num % 10
            total += digit * digit
            num //= 10
        return total
    # Step 2: Floyd's cycle detection
    slow = fast = n
    while fast != 1 and get_next(fast) != 1:
        slow = get_next(slow)
        fast = get_next(get_next(fast))
        if slow == fast:
            return False
    return True
```

**Explanation**: A happy number eventually reaches 1 when repeatedly summing squares of digits. Non-happy numbers enter a cycle. Floyd's cycle detection (tortoise and hare) finds cycles with O(1) space.

---

## Problem: Pascal's Triangle

```python
# PROBLEM: Generate first n rows of Pascal's triangle
# APPROACH: Each element is sum of two elements above it
# TIME: O(n^2)  SPACE: O(n^2)

def generate_pascal(n):
    # Step 1: Handle base case
    if n <= 0:
        return []
    # Step 2: Build triangle row by row
    triangle = [[1]]
    for i in range(1, n):
        prev_row = triangle[-1]
        new_row = [1]
        for j in range(1, i):
            new_row.append(prev_row[j-1] + prev_row[j])
        new_row.append(1)
        triangle.append(new_row)
    return triangle
```

**Explanation**: Each row of Pascal's triangle starts and ends with 1. Inner elements are the sum of two elements from the previous row. We build iteratively, using the previous row to construct each new row.

---

## Problem: Plus One

```python
# PROBLEM: Add one to number represented as digit array
# APPROACH: Handle carry from least significant digit
# TIME: O(n)  SPACE: O(1)

def plus_one(digits):
    # Step 1: Add from rightmost digit
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    # Step 2: If all digits were 9, prepend 1
    return [1] + digits
```

**Explanation**: We traverse from right to left. If a digit is less than 9, we can add 1 and return. If it's 9, it becomes 0 with a carry. If all digits were 9, we need an extra digit at the front.

---

## Problem: Majority Element

```python
# PROBLEM: Find element appearing more than n/2 times
# APPROACH: Boyer-Moore voting algorithm
# TIME: O(n)  SPACE: O(1)

def majority_element(nums):
    # Step 1: Find candidate using voting
    count = 0
    candidate = None
    for num in nums:
        if count == 0:
            candidate = num
        count += 1 if num == candidate else -1
    return candidate
```

**Explanation**: Boyer-Moore voting maintains a candidate and count. When count is 0, we pick a new candidate. If we see the candidate, count++; otherwise count--. The majority element survives because it appears more than half the time.

---

## Problem: Find Missing Number

```python
# PROBLEM: Find missing number in range [0, n] from array of size n
# APPROACH: XOR or mathematical sum formula
# TIME: O(n)  SPACE: O(1)

def missing_number(nums):
    # Step 1: XOR all indices and values
    missing = len(nums)
    for i, num in enumerate(nums):
        missing ^= i ^ num
    return missing
```

**Explanation**: XORing all indices (0 to n-1) with all array values leaves only the missing number. This works because XOR is commutative and a ^ a = 0. We start with n to include it in the XOR chain.

---

## Problem: Island Perimeter

```python
# PROBLEM: Calculate perimeter of island (1s) in grid
# APPROACH: Count cell contributions, subtract shared edges
# TIME: O(m*n)  SPACE: O(1)

def island_perimeter(grid):
    # Step 1: Initialize perimeter counter
    perimeter = 0
    # Step 2: For each land cell, add 4 - number of neighbors
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 1:
                perimeter += 4
                if i > 0 and grid[i-1][j] == 1:
                    perimeter -= 2
                if j > 0 and grid[i][j-1] == 1:
                    perimeter -= 2
    return perimeter
```

**Explanation**: Each land cell contributes 4 to the perimeter. When two cells are adjacent, they share an edge, reducing perimeter by 2. We only check up and left neighbors to avoid double-counting.

---

## Problem: Hamming Distance

```python
# PROBLEM: Count positions where bits differ between two numbers
# APPROACH: XOR and count set bits
# TIME: O(1) - at most 32 bits  SPACE: O(1)

def hamming_distance(x, y):
    # Step 1: XOR to find differing bits
    xor = x ^ y
    # Step 2: Count set bits (Brian Kernighan's algorithm)
    distance = 0
    while xor:
        distance += 1
        xor &= xor - 1  # Clear least significant bit
    return distance
```

**Explanation**: XOR produces 1s where bits differ. Brian Kernighan's algorithm efficiently counts set bits by repeatedly clearing the least significant set bit. This runs in O(number of set bits) time.

---

## Problem: Reverse Bits

```python
# PROBLEM: Reverse bits of 32-bit unsigned integer
# APPROACH: Bit manipulation, build result bit by bit
# TIME: O(1) - always 32 bits  SPACE: O(1)

def reverse_bits(n):
    # Step 1: Initialize result
    result = 0
    # Step 2: Extract and place each bit
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
```

**Explanation**: We extract the least significant bit of n (n & 1) and add it to result. Result is shifted left each iteration to make room. After 32 iterations, all bits are reversed.

---

## Problem: Number of 1 Bits

```python
# PROBLEM: Count number of set bits (Hamming weight)
# APPROACH: Brian Kernighan's algorithm
# TIME: O(k) where k is number of set bits  SPACE: O(1)

def hamming_weight(n):
    # Step 1: Initialize counter
    count = 0
    # Step 2: Clear least significant bit until n is 0
    while n:
        count += 1
        n &= n - 1
    return count
```

**Explanation**: The operation n & (n-1) clears the least significant set bit. This means we iterate exactly as many times as there are set bits, making it more efficient than checking all 32 bits.

---

## Problem: Valid Palindrome

```python
# PROBLEM: Check if string is palindrome (ignoring non-alphanumeric)
# APPROACH: Two-pointer technique from both ends
# TIME: O(n)  SPACE: O(1)

def is_palindrome(s):
    # Step 1: Initialize pointers
    left, right = 0, len(s) - 1
    # Step 2: Compare alphanumeric characters
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

**Explanation**: We use two pointers moving inward, skipping non-alphanumeric characters. We compare characters case-insensitively. If all pairs match, it's a palindrome. This handles edge cases like empty strings and strings with only non-alphanumeric characters.
