# Python Algorithm Problems - Set 002

## Problem: Container With Most Water
### Solution
```python
def maxArea(height):
    """
    Given n non-negative integers representing the heights of vertical lines,
    find two lines that together with the x-axis form a container that holds
    the most water.
    """
    left, right = 0, len(height) - 1
    max_area = 0
    
    while left < right:
        # Calculate the area between two pointers
        current_area = min(height[left], height[right]) * (right - left)
        max_area = max(max_area, current_area)
        
        # Move the pointer with the smaller height
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area

# Example usage
heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]
print(maxArea(heights))  # Output: 49
```
### Complexity: O(n) time, O(1) space

---

## Problem: 3Sum
### Solution
```python
def threeSum(nums):
    """
    Given an array nums of n integers, find all unique triplets in the array
    which gives the sum of zero.
    """
    nums.sort()
    result = []
    n = len(nums)
    
    for i in range(n - 2):
        # Skip duplicate values for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        left, right = i + 1, n - 1
        
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates for second element
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicates for third element
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                
                left += 1
                right -= 1
    
    return result

# Example usage
nums = [-1, 0, 1, 2, -1, -4]
print(threeSum(nums))  # Output: [[-1, -1, 2], [-1, 0, 1]]
```
### Complexity: O(n²) time, O(1) space (excluding output)

---

## Problem: Longest Substring Without Repeating Characters
### Solution
```python
def lengthOfLongestSubstring(s):
    """
    Given a string s, find the length of the longest substring without
    repeating characters.
    """
    char_index = {}  # Maps character to its latest index
    left = 0
    max_length = 0
    
    for right, char in enumerate(s):
        # If character is seen and is in the current window
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        
        char_index[char] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length

# Example usage
s = "abcabcbb"
print(lengthOfLongestSubstring(s))  # Output: 3 ("abc")
```
### Complexity: O(n) time, O(min(m, n)) space where m is character set size

---

## Problem: Valid Sudoku
### Solution
```python
def isValidSudoku(board):
    """
    Determine if a 9 x 9 Sudoku board is valid by checking:
    - Each row contains 1-9 without repetition
    - Each column contains 1-9 without repetition
    - Each of the nine 3 x 3 sub-boxes contains 1-9 without repetition
    """
    # Check rows
    for row in board:
        seen = set()
        for num in row:
            if num != '.':
                if num in seen:
                    return False
                seen.add(num)
    
    # Check columns
    for col in range(9):
        seen = set()
        for row in range(9):
            num = board[row][col]
            if num != '.':
                if num in seen:
                    return False
                seen.add(num)
    
    # Check 3x3 sub-boxes
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            seen = set()
            for i in range(3):
                for j in range(3):
                    num = board[box_row + i][box_col + j]
                    if num != '.':
                        if num in seen:
                            return False
                        seen.add(num)
    
    return True

# Example usage
board = [
    ["5","3",".",".","7",".",".",".","."],
    ["6",".",".","1","9","5",".",".","."],
    [".","9","8",".",".",".",".","6","."],
    ["8",".",".",".","6",".",".",".","3"],
    ["4",".",".","8",".","3",".",".","1"],
    ["7",".",".",".","2",".",".",".","6"],
    [".","6",".",".",".",".","2","8","."],
    [".",".",".","4","1","9",".",".","5"],
    [".",".",".",".","8",".",".","7","9"]
]
print(isValidSudoku(board))  # Output: True
```
### Complexity: O(1) time (fixed 81 cells), O(1) space

---

## Problem: Group Anagrams
### Solution
```python
from collections import defaultdict

def groupAnagrams(strs):
    """
    Given an array of strings, group the anagrams together.
    Anagrams are strings that contain the same characters in different order.
    """
    anagram_groups = defaultdict(list)
    
    for s in strs:
        # Sort the string to create a key for anagrams
        key = ''.join(sorted(s))
        anagram_groups[key].append(s)
    
    return list(anagram_groups.values())

# Example usage
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
print(groupAnagrams(strs))
# Output: [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
```
### Complexity: O(n * k log k) time where n is number of strings, k is max length; O(n * k) space

---

## Problem: Subarray Sum Equals K
### Solution
```python
from collections import defaultdict

def subarraySum(nums, k):
    """
    Given an array of integers and an integer k, find the total number of
    continuous subarrays whose sum equals to k.
    """
    count = 0
    prefix_sum = 0
    sum_count = defaultdict(int)
    sum_count[0] = 1  # Empty subarray has sum 0
    
    for num in nums:
        prefix_sum += num
        
        # If (prefix_sum - k) exists in sum_count, we found subarrays
        if prefix_sum - k in sum_count:
            count += sum_count[prefix_sum - k]
        
        sum_count[prefix_sum] += 1
    
    return count

# Example usage
nums = [1, 1, 1]
k = 2
print(subarraySum(nums, k))  # Output: 2
```
### Complexity: O(n) time, O(n) space

---

## Problem: Top K Frequent Elements
### Solution
```python
from collections import Counter
import heapq

def topKFrequent(nums, k):
    """
    Given an integer array nums and an integer k, return the k most frequent
    elements.
    """
    # Count frequency of each number
    count = Counter(nums)
    
    # Use a min-heap of size k to keep top k frequent elements
    heap = []
    for num, freq in count.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)
    
    return [num for freq, num in heap]

# Alternative using bucket sort (more efficient for this specific problem)
def topKFrequentBucket(nums, k):
    count = Counter(nums)
    
    # Create buckets where index represents frequency
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)
    
    # Collect top k frequent elements
    result = []
    for i in range(len(buckets) - 1, -1, -1):
        for num in buckets[i]:
            result.append(num)
            if len(result) == k:
                return result
    
    return result

# Example usage
nums = [1, 1, 1, 2, 2, 3]
k = 2
print(topKFrequent(nums, k))  # Output: [1, 2]
```
### Complexity: O(n log k) for heap solution; O(n) for bucket sort solution; O(n) space

---

## Problem: Product of Array Except Self
### Solution
```python
def productExceptSelf(nums):
    """
    Given an integer array nums, return an array answer such that answer[i]
    is equal to the product of all the elements of nums except nums[i].
    Must run in O(n) time without using the division operation.
    """
    n = len(nums)
    answer = [1] * n
    
    # Calculate products of all elements to the left
    left_product = 1
    for i in range(n):
        answer[i] = left_product
        left_product *= nums[i]
    
    # Multiply by products of all elements to the right
    right_product = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= right_product
        right_product *= nums[i]
    
    return answer

# Example usage
nums = [1, 2, 3, 4]
print(productExceptSelf(nums))  # Output: [24, 12, 8, 6]
```
### Complexity: O(n) time, O(1) space (output array not counted as extra space)

---

## Problem: Find Minimum in Rotated Sorted Array
### Solution
```python
def findMin(nums):
    """
    Given the sorted rotated array nums of unique elements, return the
    minimum element of this array.
    """
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = left + (right - left) // 2
        
        # If middle element is greater than right element,
        # the minimum must be in the right half
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            # Otherwise, minimum is in left half (including mid)
            right = mid
    
    return nums[left]

# Example usage
nums = [3, 4, 5, 1, 2]
print(findMin(nums))  # Output: 1

nums2 = [4, 5, 6, 7, 0, 1, 2]
print(findMin(nums2))  # Output: 0
```
### Complexity: O(log n) time, O(1) space

---

## Problem: Word Search
### Solution
```python
def exist(board, word):
    """
    Given an m x n grid of characters board and a string word, return true
    if word exists in the grid. The word can be constructed from letters of
    sequentially adjacent cells (horizontally or vertically neighboring).
    """
    if not board or not board[0]:
        return False
    
    rows, cols = len(board), len(board[0])
    
    def dfs(row, col, index):
        # Found the complete word
        if index == len(word):
            return True
        
        # Out of bounds or character doesn't match
        if (row < 0 or row >= rows or 
            col < 0 or col >= cols or 
            board[row][col] != word[index]):
            return False
        
        # Mark as visited by temporarily changing the character
        temp = board[row][col]
        board[row][col] = '#'
        
        # Explore all four directions
        found = (dfs(row + 1, col, index + 1) or
                 dfs(row - 1, col, index + 1) or
                 dfs(row, col + 1, index + 1) or
                 dfs(row, col - 1, index + 1))
        
        # Restore the original character (backtrack)
        board[row][col] = temp
        
        return found
    
    # Try starting from each cell
    for i in range(rows):
        for j in range(cols):
            if dfs(i, j, 0):
                return True
    
    return False

# Example usage
board = [
    ['A', 'B', 'C', 'E'],
    ['S', 'F', 'C', 'S'],
    ['A', 'D', 'E', 'E']
]
word = "ABCCED"
print(exist(board, word))  # Output: True

word2 = "SEE"
print(exist(board, word2))  # Output: True

word3 = "ABCB"
print(exist(board, word3))  # Output: False
```
### Complexity: O(n * m * 4^L) time where L is word length; O(L) space for recursion
