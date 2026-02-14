"""Create 15 Test Generation tasks."""

import json
from pathlib import Path

TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")

TESTGEN_TASKS = [
    {
        "task_id": "TESTGEN-001",
        "category": "test_generation",
        "difficulty": "easy",
        "description": "Write a test function for this add function. Return a function that tests add(2,3)==5 and add(-1,1)==0.",
        "code_to_test": '''def add(a, b):
    return a + b''',
        "function_signature": "def test_add() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "basic"]
    },
    {
        "task_id": "TESTGEN-002",
        "category": "test_generation",
        "difficulty": "easy",
        "description": "Write a test function that verifies is_even correctly identifies even and odd numbers.",
        "code_to_test": '''def is_even(n):
    return n % 2 == 0''',
        "function_signature": "def test_is_even() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "boolean"]
    },
    {
        "task_id": "TESTGEN-003",
        "category": "test_generation",
        "difficulty": "easy",
        "description": "Write a test function for the factorial function including edge case n=0.",
        "code_to_test": '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)''',
        "function_signature": "def test_factorial() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "recursion"]
    },
    {
        "task_id": "TESTGEN-004",
        "category": "test_generation",
        "difficulty": "easy",
        "description": "Write a test function for string reversal.",
        "code_to_test": '''def reverse_string(s):
    return s[::-1]''',
        "function_signature": "def test_reverse_string() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "string"]
    },
    {
        "task_id": "TESTGEN-005",
        "category": "test_generation",
        "difficulty": "easy",
        "description": "Write a test function for list max finder including empty list edge case.",
        "code_to_test": '''def find_max(lst):
    if not lst:
        return None
    return max(lst)''',
        "function_signature": "def test_find_max() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "edge_case"]
    },
    {
        "task_id": "TESTGEN-006",
        "category": "test_generation",
        "difficulty": "medium",
        "description": "Write comprehensive tests for this palindrome checker including spaces and case.",
        "code_to_test": '''def is_palindrome(s):
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]''',
        "function_signature": "def test_is_palindrome() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "string", "comprehensive"]
    },
    {
        "task_id": "TESTGEN-007",
        "category": "test_generation",
        "difficulty": "medium",
        "description": "Write tests for binary search including not-found and boundary cases.",
        "code_to_test": '''def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
        "function_signature": "def test_binary_search() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "search", "boundary"]
    },
    {
        "task_id": "TESTGEN-008",
        "category": "test_generation",
        "difficulty": "medium",
        "description": "Write tests for FizzBuzz function.",
        "code_to_test": '''def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return str(n)''',
        "function_signature": "def test_fizzbuzz() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "conditional"]
    },
    {
        "task_id": "TESTGEN-009",
        "category": "test_generation",
        "difficulty": "medium",
        "description": "Write tests for this stack implementation including empty stack cases.",
        "code_to_test": '''class Stack:
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        if not self.items:
            return None
        return self.items.pop()
    def peek(self):
        if not self.items:
            return None
        return self.items[-1]
    def is_empty(self):
        return len(self.items) == 0''',
        "function_signature": "def test_stack() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "data_structure"]
    },
    {
        "task_id": "TESTGEN-010",
        "category": "test_generation",
        "difficulty": "medium",
        "description": "Write tests for merge sorted lists function.",
        "code_to_test": '''def merge_sorted(lst1, lst2):
    result = []
    i = j = 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] <= lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1
    result.extend(lst1[i:])
    result.extend(lst2[j:])
    return result''',
        "function_signature": "def test_merge_sorted() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "merge", "sorting"]
    },
    {
        "task_id": "TESTGEN-011",
        "category": "test_generation",
        "difficulty": "hard",
        "description": "Write comprehensive tests for this LRU Cache implementation.",
        "code_to_test": '''class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []
    
    def get(self, key):
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1
    
    def put(self, key, value):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)''',
        "function_signature": "def test_lru_cache() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "cache", "comprehensive"]
    },
    {
        "task_id": "TESTGEN-012",
        "category": "test_generation",
        "difficulty": "hard",
        "description": "Write tests for graph BFS including disconnected nodes.",
        "code_to_test": '''def bfs(graph, start):
    visited = set()
    queue = [start]
    result = []
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            result.append(node)
            queue.extend(graph.get(node, []))
    return result''',
        "function_signature": "def test_bfs() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "graph", "bfs"]
    },
    {
        "task_id": "TESTGEN-013",
        "category": "test_generation",
        "difficulty": "hard",
        "description": "Write tests for this expression validator with nested brackets.",
        "code_to_test": '''def is_valid_expression(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack.pop() != mapping[char]:
                return False
    return len(stack) == 0''',
        "function_signature": "def test_is_valid_expression() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "validation", "stack"]
    },
    {
        "task_id": "TESTGEN-014",
        "category": "test_generation",
        "difficulty": "hard",
        "description": "Write tests for this rate limiter class.",
        "code_to_test": '''class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self, timestamp):
        # Remove old requests
        self.requests = [t for t in self.requests if timestamp - t < self.time_window]
        if len(self.requests) < self.max_requests:
            self.requests.append(timestamp)
            return True
        return False''',
        "function_signature": "def test_rate_limiter() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "rate_limiting", "time"]
    },
    {
        "task_id": "TESTGEN-015",
        "category": "test_generation",
        "difficulty": "hard",
        "description": "Write tests for this trie (prefix tree) implementation.",
        "code_to_test": '''class Trie:
    def __init__(self):
        self.children = {}
        self.is_end = False
    
    def insert(self, word):
        node = self
        for char in word:
            if char not in node.children:
                node.children[char] = Trie()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word):
        node = self
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    
    def starts_with(self, prefix):
        node = self
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True''',
        "function_signature": "def test_trie() -> bool",
        "test_cases": [
            {"input": {}, "expected_output": True}
        ],
        "tags": ["unit_test", "trie", "data_structure"]
    }
]


def main():
    print("Creating 15 Test Generation tasks...")
    
    with open(TASKS_FILE) as f:
        existing = sum(1 for line in f if line.strip())
    
    print(f"  Existing tasks: {existing}")
    
    with open(TASKS_FILE, 'a') as f:
        for task in TESTGEN_TASKS:
            f.write(json.dumps(task) + '\n')
    
    print(f"  Added: {len(TESTGEN_TASKS)} test generation tasks")
    print(f"  Total now: {existing + len(TESTGEN_TASKS)}")


if __name__ == "__main__":
    main()
