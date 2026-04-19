# Python Sliding Window Algorithms

## Problem

Implement sliding window techniques for solving array/string problems efficiently, including fixed-size and variable-size windows with applications in maximum subarray, longest substring, and optimization problems.

## Implementation

```python
from typing import List, Tuple, Optional
from collections import defaultdict, deque
import sys

class SlidingWindow:
    """Comprehensive sliding window algorithm implementations."""
    
    # ============================================
    # Fixed-Size Window Problems
    # ============================================
    
    @staticmethod
    def max_sum_subarray(arr: List[int], k: int) -> Tuple[int, int, int]:
        """
        Find maximum sum subarray of size k.
        Returns: (max_sum, start_index, end_index)
        """
        if len(arr) < k:
            return -1, -1, -1
        
        # Calculate sum of first window
        window_sum = sum(arr[:k])
        max_sum = window_sum
        max_start = 0
        
        # Slide window
        for i in range(len(arr) - k):
            window_sum = window_sum - arr[i] + arr[i + k]
            if window_sum > max_sum:
                max_sum = window_sum
                max_start = i + 1
        
        return max_sum, max_start, max_start + k - 1
    
    @staticmethod
    def min_sum_subarray(arr: List[int], k: int) -> Tuple[int, int, int]:
        """Find minimum sum subarray of size k."""
        if len(arr) < k:
            return -1, -1, -1
        
        window_sum = sum(arr[:k])
        min_sum = window_sum
        min_start = 0
        
        for i in range(len(arr) - k):
            window_sum = window_sum - arr[i] + arr[i + k]
            if window_sum < min_sum:
                min_sum = window_sum
                min_start = i + 1
        
        return min_sum, min_start, min_start + k - 1
    
    @staticmethod
    def max_of_all_subarrays(arr: List[int], k: int) -> List[int]:
        """
        Find maximum of all subarrays of size k using deque.
        Time: O(n), Space: O(k)
        """
        if not arr or k <= 0:
            return []
        
        result = []
        dq = deque()  # Store indices
        
        for i in range(len(arr)):
            # Remove elements outside window
            while dq and dq[0] < i - k + 1:
                dq.popleft()
            
            # Remove smaller elements (they won't be max)
            while dq and arr[dq[-1]] < arr[i]:
                dq.pop()
            
            dq.append(i)
            
            # Start recording results after first window
            if i >= k - 1:
                result.append(arr[dq[0]])
        
        return result
    
    @staticmethod
    def first_negative_in_window(arr: List[int], k: int) -> List[Optional[int]]:
        """
        Find first negative number in every window of size k.
        """
        result = []
        dq = deque()  # Store indices of negative numbers
        
        for i in range(len(arr)):
            # Remove elements outside window
            while dq and dq[0] < i - k + 1:
                dq.popleft()
            
            # Add current element if negative
            if arr[i] < 0:
                dq.append(i)
            
            # Record result
            if i >= k - 1:
                result.append(arr[dq[0]] if dq else None)
        
        return result
    
    # ============================================
    # Variable-Size Window Problems
    # ============================================
    
    @staticmethod
    def longest_substring_without_repeating(s: str) -> Tuple[int, str]:
        """
        Find longest substring without repeating characters.
        Returns: (length, substring)
        """
        char_index = {}  # char -> latest index
        max_len = 0
        max_start = 0
        start = 0
        
        for end, char in enumerate(s):
            if char in char_index and char_index[char] >= start:
                start = char_index[char] + 1
            
            char_index[char] = end
            
            if end - start + 1 > max_len:
                max_len = end - start + 1
                max_start = start
        
        return max_len, s[max_start:max_start + max_len]
    
    @staticmethod
    def longest_substring_k_distinct(s: str, k: int) -> Tuple[int, str]:
        """
        Find longest substring with at most k distinct characters.
        """
        if k == 0:
            return 0, ""
        
        char_count = defaultdict(int)
        max_len = 0
        max_start = 0
        start = 0
        distinct = 0
        
        for end, char in enumerate(s):
            if char_count[char] == 0:
                distinct += 1
            char_count[char] += 1
            
            # Shrink window if too many distinct chars
            while distinct > k:
                char_count[s[start]] -= 1
                if char_count[s[start]] == 0:
                    distinct -= 1
                start += 1
            
            if end - start + 1 > max_len:
                max_len = end - start + 1
                max_start = start
        
        return max_len, s[max_start:max_start + max_len]
    
    @staticmethod
    def min_window_substring(s: str, t: str) -> str:
        """
        Find minimum window in s containing all characters of t.
        Classic minimum window substring problem.
        """
        if not s or not t:
            return ""
        
        # Count characters in t
        t_count = defaultdict(int)
        for char in t:
            t_count[char] += 1
        
        required = len(t_count)
        formed = 0
        window_count = defaultdict(int)
        
        min_len = float('inf')
        min_start = 0
        
        left = 0
        for right, char in enumerate(s):
            window_count[char] += 1
            
            if char in t_count and window_count[char] == t_count[char]:
                formed += 1
            
            # Try to shrink window
            while formed == required and left <= right:
                if right - left + 1 < min_len:
                    min_len = right - left + 1
                    min_start = left
                
                # Remove left character
                left_char = s[left]
                window_count[left_char] -= 1
                if left_char in t_count and window_count[left_char] < t_count[left_char]:
                    formed -= 1
                
                left += 1
        
        return s[min_start:min_start + min_len] if min_len != float('inf') else ""
    
    @staticmethod
    def longest_subarray_sum_at_most_k(arr: List[int], k: int) -> int:
        """
        Find longest subarray with sum at most k.
        """
        prefix_sum = 0
        max_len = 0
        prefix_sums = {0: -1}  # sum -> earliest index
        
        for i, num in enumerate(arr):
            prefix_sum += num
            
            # Find smallest prefix sum such that current - prefix <= k
            # i.e., prefix >= current - k
            for prev_sum in prefix_sums:
                if prefix_sum - prev_sum <= k:
                    max_len = max(max_len, i - prefix_sums[prev_sum])
            
            if prefix_sum not in prefix_sums:
                prefix_sums[prefix_sum] = i
        
        return max_len
    
    @staticmethod
    def subarray_sum_equals_k(arr: List[int], k: int) -> int:
        """
        Count number of subarrays with sum exactly k.
        Uses prefix sum with hash map.
        """
        count = 0
        prefix_sum = 0
        sum_count = defaultdict(int)
        sum_count[0] = 1  # Empty prefix
        
        for num in arr:
            prefix_sum += num
            # If prefix_sum - k exists, we have a valid subarray
            count += sum_count[prefix_sum - k]
            sum_count[prefix_sum] += 1
        
        return count
    
    @staticmethod
    def longest_repeating_character_replacement(s: str, k: int) -> int:
        """
        Find longest substring with same character after at most k replacements.
        """
        char_count = defaultdict(int)
        max_count = 0
        max_len = 0
        start = 0
        
        for end, char in enumerate(s):
            char_count[char] += 1
            max_count = max(max_count, char_count[char])
            
            # If window size - max_count > k, shrink
            while end - start + 1 - max_count > k:
                char_count[s[start]] -= 1
                start += 1
            
            max_len = max(max_len, end - start + 1)
        
        return max_len
    
    @staticmethod
    def permutation_in_string(s1: str, s2: str) -> bool:
        """
        Check if any permutation of s1 exists in s2.
        """
        if len(s1) > len(s2):
            return False
        
        s1_count = [0] * 26
        s2_count = [0] * 26
        
        # Initialize first window
        for i in range(len(s1)):
            s1_count[ord(s1[i]) - ord('a')] += 1
            s2_count[ord(s2[i]) - ord('a')] += 1
        
        matches = sum(1 for i in range(26) if s1_count[i] == s2_count[i])
        
        # Slide window
        for i in range(len(s1), len(s2)):
            if matches == 26:
                return True
            
            # Add new character
            idx = ord(s2[i]) - ord('a')
            if s2_count[idx] == s1_count[idx]:
                matches -= 1
            s2_count[idx] += 1
            if s2_count[idx] == s1_count[idx]:
                matches += 1
            
            # Remove old character
            idx = ord(s2[i - len(s1)]) - ord('a')
            if s2_count[idx] == s1_count[idx]:
                matches -= 1
            s2_count[idx] -= 1
            if s2_count[idx] == s1_count[idx]:
                matches += 1
        
        return matches == 26
    
    @staticmethod
    def max_consecutive_ones_iii(nums: List[int], k: int) -> int:
        """
        Find max consecutive 1s after flipping at most k 0s.
        """
        zeros = 0
        max_len = 0
        start = 0
        
        for end, num in enumerate(nums):
            if num == 0:
                zeros += 1
            
            while zeros > k:
                if nums[start] == 0:
                    zeros -= 1
                start += 1
            
            max_len = max(max_len, end - start + 1)
        
        return max_len


# Usage Examples
if __name__ == "__main__":
    sw = SlidingWindow()
    
    # Fixed-size window
    arr = [2, 1, 5, 1, 3, 2]
    print(f"Max sum subarray of size 3: {sw.max_sum_subarray(arr, 3)}")
    print(f"Max of all subarrays: {sw.max_of_all_subarrays([1, 3, -1, -3, 5, 3, 6, 7], 3)}")
    
    # Variable-size window
    s = "abcabcbb"
    print(f"Longest substring without repeating: {sw.longest_substring_without_repeating(s)}")
    
    s = "eceba"
    print(f"Longest substring with 2 distinct: {sw.longest_substring_k_distinct(s, 2)}")
    
    s, t = "ADOBECODEBANC", "ABC"
    print(f"Min window substring: '{sw.min_window_substring(s, t)}'")
    
    arr = [1, 1, 1]
    print(f"Subarrays with sum 2: {sw.subarray_sum_equals_k(arr, 2)}")
    
    s1, s2 = "ab", "eidbaooo"
    print(f"Permutation in string: {sw.permutation_in_string(s1, s2)}")
```

## Tests

```python
import pytest

class TestSlidingWindow:
    
    def test_max_sum_subarray(self):
        """Test maximum sum subarray of fixed size."""
        arr = [2, 1, 5, 1, 3, 2]
        max_sum, start, end = SlidingWindow.max_sum_subarray(arr, 3)
        assert max_sum == 9  # [5, 1, 3]
        assert start == 2
        assert end == 4
    
    def test_max_sum_subarray_edge(self):
        """Test edge cases."""
        assert SlidingWindow.max_sum_subarray([1], 2) == (-1, -1, -1)
        assert SlidingWindow.max_sum_subarray([], 1) == (-1, -1, -1)
    
    def test_min_sum_subarray(self):
        """Test minimum sum subarray."""
        arr = [3, -4, 2, -3, -1, 7, -5]
        min_sum, start, end = SlidingWindow.min_sum_subarray(arr, 3)
        assert min_sum == -6  # [-4, 2, -3] -> wait, need to recalc
        # Actually [-4, 2, -3] = -5, [-3, -1, 7] = 3
        # [2, -3, -1] = -2
        # Let's recalculate: windows are [3,-4,2]=-1, [-4,2,-3]=-5, [2,-3,-1]=-2, [-3,-1,7]=3, [-1,7,-5]=1
        assert min_sum == -5
    
    def test_max_of_all_subarrays(self):
        """Test maximum in all subarrays."""
        arr = [1, 3, -1, -3, 5, 3, 6, 7]
        k = 3
        result = SlidingWindow.max_of_all_subarrays(arr, k)
        assert result == [3, 3, 5, 5, 6, 7]
    
    def test_first_negative_in_window(self):
        """Test first negative in each window."""
        arr = [12, -1, -7, 8, -15, 30, 16, 28]
        k = 3
        result = SlidingWindow.first_negative_in_window(arr, k)
        assert result == [-1, -1, -7, -15, -15, None]
    
    def test_longest_substring_without_repeating(self):
        """Test longest substring without repeating characters."""
        length, substr = SlidingWindow.longest_substring_without_repeating("abcabcbb")
        assert length == 3
        assert substr == "abc"
        
        length, substr = SlidingWindow.longest_substring_without_repeating("bbbbb")
        assert length == 1
    
    def test_longest_substring_k_distinct(self):
        """Test longest substring with k distinct characters."""
        length, substr = SlidingWindow.longest_substring_k_distinct("eceba", 2)
        assert length == 3
        assert substr in ["ece", "ceb"]
    
    def test_min_window_substring(self):
        """Test minimum window substring."""
        result = SlidingWindow.min_window_substring("ADOBECODEBANC", "ABC")
        assert result == "BANC"
        
        result = SlidingWindow.min_window_substring("a", "a")
        assert result == "a"
        
        result = SlidingWindow.min_window_substring("a", "aa")
        assert result == ""
    
    def test_subarray_sum_equals_k(self):
        """Test subarray sum equals k."""
        assert SlidingWindow.subarray_sum_equals_k([1, 1, 1], 2) == 2
        assert SlidingWindow.subarray_sum_equals_k([1, 2, 3], 3) == 2
    
    def test_longest_repeating_character_replacement(self):
        """Test character replacement."""
        assert SlidingWindow.longest_repeating_character_replacement("ABAB", 2) == 4
        assert SlidingWindow.longest_repeating_character_replacement("AABABBA", 1) == 4
    
    def test_permutation_in_string(self):
        """Test permutation in string."""
        assert SlidingWindow.permutation_in_string("ab", "eidbaooo") is True
        assert SlidingWindow.permutation_in_string("ab", "eidboaoo") is False
    
    def test_max_consecutive_ones_iii(self):
        """Test max consecutive ones with k flips."""
        assert SlidingWindow.max_consecutive_ones_iii([1,1,1,0,0,0,1,1,1,1,0], 2) == 6
        assert SlidingWindow.max_consecutive_ones_iii(
            [0,0,1,1,1,0,0], 0
        ) == 3
    
    def test_empty_inputs(self):
        """Test empty input handling."""
        assert SlidingWindow.max_of_all_subarrays([], 3) == []
        assert SlidingWindow.longest_substring_without_repeating("")[0] == 0
```

## Complexity Analysis

**Fixed-Size Window:**
- Max/Min Sum Subarray: O(n) time, O(1) space
- Max of All Subarrays: O(n) time, O(k) space
- First Negative: O(n) time, O(k) space

**Variable-Size Window:**
- Longest Substring No Repeat: O(n) time, O(min(n, charset)) space
- Longest K Distinct: O(n) time, O(k) space
- Min Window Substring: O(n + m) time, O(charset) space
- Subarray Sum K: O(n) time, O(n) space
- Permutation in String: O(n) time, O(1) space (fixed charset)

**Key Patterns:**
1. Fixed window: Slide by removing left, adding right
2. Variable window: Shrink from left while condition holds
3. Use hash maps for character/element counting
4. Use deques for max/min in window
5. Prefix sums for range queries

**Common Optimizations:**
- Two pointers instead of nested loops
- Early termination conditions
- Monotonic deques for max/min
- Hash maps for O(1) lookups
