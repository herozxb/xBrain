# Python Trie Data Structure

## Problem

Implement a Trie (prefix tree) data structure supporting efficient insert, search, delete, and prefix-based operations with applications in autocomplete, spell checking, and IP routing.

## Implementation

```python
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import heapq

@dataclass
class TrieNode:
    """Trie node with character children and metadata."""
    children: Dict[str, 'TrieNode'] = field(default_factory=dict)
    is_end: bool = False
    count: int = 0  # Number of words passing through
    word_count: int = 0  # Number of complete words ending here
    metadata: dict = field(default_factory=dict)  # Optional word metadata


class Trie:
    """
    Trie (Prefix Tree) implementation with comprehensive operations.
    
    Time Complexities:
    - Insert: O(m) where m is word length
    - Search: O(m)
    - Delete: O(m)
    - Prefix search: O(m + k) where k is number of results
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.total_words = 0
    
    def insert(self, word: str, metadata: dict = None) -> None:
        """Insert a word into the trie with optional metadata."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.count += 1
        
        node.is_end = True
        node.word_count += 1
        node.metadata = metadata or {}
        self.total_words += 1
    
    def search(self, word: str) -> Tuple[bool, dict]:
        """Check if word exists and return its metadata."""
        node = self._find_node(word)
        if node and node.is_end:
            return True, node.metadata
        return False, {}
    
    def starts_with(self, prefix: str) -> bool:
        """Check if any word starts with prefix."""
        return self._find_node(prefix) is not None
    
    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find node corresponding to prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def delete(self, word: str) -> bool:
        """Delete word from trie. Returns True if word existed."""
        if not word:
            return False
        
        # Find nodes along path
        path = [self.root]
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
            path.append(node)
        
        if not node.is_end:
            return False
        
        # Mark as not end
        node.is_end = False
        node.word_count -= 1
        self.total_words -= 1
        
        # Remove unused nodes (backwards)
        for i in range(len(path) - 1, 0, -1):
            current = path[i]
            parent = path[i - 1]
            char = word[i - 1]
            
            current.count -= 1
            if current.count == 0 and not current.is_end:
                del parent.children[char]
        
        return True
    
    def get_words_with_prefix(self, prefix: str, limit: int = None) -> List[str]:
        """Get all words starting with prefix."""
        start_node = self._find_node(prefix)
        if not start_node:
            return []
        
        results = []
        self._collect_words(start_node, prefix, results, limit)
        return results
    
    def _collect_words(
        self, 
        node: TrieNode, 
        current: str, 
        results: List[str], 
        limit: int = None
    ) -> None:
        """Collect all words from node using DFS."""
        if limit and len(results) >= limit:
            return
        
        if node.is_end:
            # Add word multiple times if it was inserted multiple times
            for _ in range(node.word_count):
                results.append(current)
                if limit and len(results) >= limit:
                    return
        
        for char, child in sorted(node.children.items()):
            self._collect_words(child, current + char, results, limit)
    
    def count_words_with_prefix(self, prefix: str) -> int:
        """Count words starting with prefix without enumerating."""
        node = self._find_node(prefix)
        if not node:
            return 0
        
        total = node.word_count
        for child in node.children.values():
            # Sum word_count of all descendant end nodes
            total += self._count_end_words(child)
        return total
    
    def _count_end_words(self, node: TrieNode) -> int:
        """Recursively count end words from node."""
        count = node.word_count
        for child in node.children.values():
            count += self._count_end_words(child)
        return count
    
    def longest_common_prefix(self) -> str:
        """Find longest common prefix of all words."""
        if self.total_words == 0:
            return ""
        
        prefix = []
        node = self.root
        
        while len(node.children) == 1 and not node.is_end:
            char = next(iter(node.children))
            prefix.append(char)
            node = node.children[char]
        
        return "".join(prefix)


class AutocompleteSystem:
    """Autocomplete system using Trie with frequency-based ranking."""
    
    def __init__(self, sentences: List[str], times: List[int]):
        self.trie = Trie()
        self.current_input = ""
        
        # Build trie with frequencies
        for sentence, freq in zip(sentences, times):
            self.trie.insert(sentence.lower(), {'frequency': freq})
    
    def input(self, c: str) -> List[str]:
        """Process input character and return top 3 suggestions."""
        if c == '#':
            # Save current input
            if self.current_input:
                exists, metadata = self.trie.search(self.current_input)
                freq = metadata.get('frequency', 0) + 1
                self.trie.insert(self.current_input, {'frequency': freq})
            self.current_input = ""
            return []
        
        self.current_input += c
        
        # Get candidates
        words = self.trie.get_words_with_prefix(self.current_input)
        
        # Sort by frequency (descending), then alphabetically
        scored = []
        for word in words:
            _, meta = self.trie.search(word)
            freq = meta.get('frequency', 0)
            scored.append((-freq, word, word))
        
        scored.sort()
        return [w for _, _, w in scored[:3]]


class WordDictionary:
    """Trie-based dictionary supporting wildcard search with '.' pattern."""
    
    def __init__(self):
        self.trie = Trie()
    
    def add_word(self, word: str) -> None:
        self.trie.insert(word)
    
    def search(self, word: str) -> bool:
        return self._search_with_wildcard(self.trie.root, word, 0)
    
    def _search_with_wildcard(self, node: TrieNode, word: str, index: int) -> bool:
        """Search supporting '.' wildcard matching any character."""
        if index == len(word):
            return node.is_end
        
        char = word[index]
        if char == '.':
            # Try all children
            for child in node.children.values():
                if self._search_with_wildcard(child, word, index + 1):
                    return True
            return False
        else:
            if char not in node.children:
                return False
            return self._search_with_wildcard(node.children[char], word, index + 1)


class CompressedTrie:
    """Space-optimized Trie using path compression."""
    
    def __init__(self):
        self.root = {}
        self.END = '#'
    
    def insert(self, word: str) -> None:
        node = self.root
        i = 0
        
        while i < len(word):
            # Find matching edge
            matched = False
            for key in list(node.keys()):
                if key == self.END:
                    continue
                
                # Find common prefix
                j = 0
                while (j < len(key) and i + j < len(word) and 
                       key[j] == word[i + j]):
                    j += 1
                
                if j > 0:
                    if j == len(key):
                        # Full match, continue down
                        node = node[key]
                        i += j
                        matched = True
                        break
                    else:
                        # Partial match, split node
                        remaining_key = key[j:]
                        new_child = {}
                        new_child[remaining_key] = node[key]
                        del node[key]
                        node[key[:j]] = new_child
                        node = new_child
                        i += j
                        matched = True
                        break
            
            if not matched:
                # No match, add new edge
                node[word[i:]] = {self.END: True}
                return
        
        node[self.END] = True
    
    def search(self, word: str) -> bool:
        node = self.root
        i = 0
        
        while i < len(word):
            matched = False
            for key in node:
                if key == self.END:
                    continue
                if word[i:].startswith(key):
                    node = node[key]
                    i += len(key)
                    matched = True
                    break
            
            if not matched:
                return False
        
        return self.END in node


# Usage Examples
if __name__ == "__main__":
    # Basic Trie operations
    trie = Trie()
    words = ["apple", "app", "application", "apply", "banana", "band"]
    
    for word in words:
        trie.insert(word, {"length": len(word)})
    
    print(f"Search 'apple': {trie.search('apple')}")
    print(f"Search 'app': {trie.search('app')}")
    print(f"Starts with 'app': {trie.starts_with('app')}")
    print(f"Words with prefix 'app': {trie.get_words_with_prefix('app')}")
    print(f"Longest common prefix: {trie.longest_common_prefix()}")
    
    # Autocomplete
    auto = AutocompleteSystem(
        ["i love you", "island", "ironman", "i love leetcode"],
        [5, 3, 2, 2]
    )
    print(f"Autocomplete 'i ': {auto.input('i')}")
    print(f"Autocomplete 'i l': {auto.input(' ')}")
    
    # Word dictionary with wildcard
    wd = WordDictionary()
    wd.add_word("bad")
    wd.add_word("dad")
    wd.add_word("mad")
    print(f"Search 'b.d': {wd.search('b.d')}")  # True
    print(f"Search '.ad': {wd.search('.ad')}")  # True
```

## Tests

```python
import pytest

class TestTrie:
    
    @pytest.fixture
    def trie(self):
        t = Trie()
        words = ["apple", "app", "application", "apply", "banana"]
        for word in words:
            t.insert(word)
        return t
    
    def test_insert_and_search(self, trie):
        """Test basic insert and search operations."""
        assert trie.search("apple")[0] is True
        assert trie.search("app")[0] is True
        assert trie.search("appl")[0] is False
        assert trie.search("application")[0] is True
    
    def test_starts_with(self, trie):
        """Test prefix checking."""
        assert trie.starts_with("app") is True
        assert trie.starts_with("ban") is True
        assert trie.starts_with("cat") is False
    
    def test_delete(self, trie):
        """Test word deletion."""
        assert trie.delete("app") is True
        assert trie.search("app")[0] is False
        assert trie.search("apple")[0] is True  # Other words intact
        assert trie.delete("app") is False  # Already deleted
    
    def test_get_words_with_prefix(self, trie):
        """Test prefix-based word retrieval."""
        words = trie.get_words_with_prefix("app")
        assert "apple" in words
        assert "app" in words
        assert "application" in words
        assert "apply" in words
        assert "banana" not in words
    
    def test_count_words_with_prefix(self, trie):
        """Test counting words with prefix."""
        count = trie.count_words_with_prefix("app")
        assert count == 4
    
    def test_longest_common_prefix(self):
        """Test longest common prefix."""
        t = Trie()
        for word in ["flower", "flow", "flight"]:
            t.insert(word)
        assert t.longest_common_prefix() == "fl"
    
    def test_metadata(self):
        """Test word metadata storage."""
        t = Trie()
        t.insert("test", {"pos": "noun", "freq": 100})
        exists, meta = t.search("test")
        assert exists is True
        assert meta["pos"] == "noun"
        assert meta["freq"] == 100
    
    def test_empty_trie(self):
        """Test operations on empty trie."""
        t = Trie()
        assert t.search("anything")[0] is False
        assert t.starts_with("a") is False
        assert t.get_words_with_prefix("a") == []
        assert t.longest_common_prefix() == ""


class TestAutocompleteSystem:
    
    def test_autocomplete_basic(self):
        """Test basic autocomplete functionality."""
        auto = AutocompleteSystem(
            ["i love you", "island", "ironman"],
            [5, 3, 2]
        )
        results = auto.input('i')
        assert "i love you" in results
        assert "island" in results
    
    def test_autocomplete_ranking(self):
        """Test frequency-based ranking."""
        auto = AutocompleteSystem(
            ["apple", "application", "apply"],
            [10, 5, 8]
        )
        auto.input('a')
        # Higher frequency should rank first
        results = auto.input('p')
        assert results[0] == "apple"  # freq 10


class TestWordDictionary:
    
    @pytest.fixture
    def dict(self):
        wd = WordDictionary()
        for word in ["bad", "dad", "mad", "pad"]:
            wd.add_word(word)
        return wd
    
    def test_exact_search(self, dict):
        """Test exact word search."""
        assert dict.search("bad") is True
        assert dict.search("rad") is False
    
    def test_wildcard_single(self, dict):
        """Test single wildcard search."""
        assert dict.search(".ad") is True  # bad, dad, mad, pad
        assert dict.search("b.d") is True  # bad
        assert dict.search("ba.") is True  # bad
    
    def test_wildcard_multiple(self, dict):
        """Test multiple wildcards."""
        assert dict.search("..d") is True
        assert dict.search("...") is True
    
    def test_wildcard_not_found(self, dict):
        """Test wildcard with no matches."""
        assert dict.search("z.d") is False
        assert dict.search(".z.") is False


class TestCompressedTrie:
    
    def test_compressed_operations(self):
        """Test compressed trie operations."""
        ct = CompressedTrie()
        words = ["apple", "app", "application"]
        
        for word in words:
            ct.insert(word)
        
        for word in words:
            assert ct.search(word) is True
        
        assert ct.search("appl") is False
    
    def test_space_efficiency(self):
        """Test space efficiency of compressed trie."""
        ct = CompressedTrie()
        # Long common prefix
        words = ["abcdefghij", "abcdefghik", "abcdefghil"]
        
        for word in words:
            ct.insert(word)
        
        # Should share common prefix nodes
        assert ct.search("abcdefghij") is True
```

## Complexity Analysis

**Time Complexity:**
- Insert: O(m) where m is word length
- Search: O(m)
- Delete: O(m)
- Starts with: O(m)
- Get words with prefix: O(m + k) where k is number of results
- Count with prefix: O(n) worst case where n is total trie nodes

**Space Complexity:**
- Standard Trie: O(n × m) worst case where n is words, m is avg length
- Compressed Trie: O(n × m) but with better constants due to path compression

**Applications:**
- Autocomplete systems
- Spell checkers
- IP routing (longest prefix matching)
- Word games (Scrabble, Boggle)
- Search engines (prefix-based search)
- DNA sequence analysis
