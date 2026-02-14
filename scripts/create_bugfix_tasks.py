"""Create 20 Bug Fixing tasks."""

import json
from pathlib import Path

TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")

BUGFIX_TASKS = [
    # Easy bugs (off-by-one, typos, wrong operators)
    {
        "task_id": "BUGFIX-001",
        "category": "bug_fixing",
        "difficulty": "easy",
        "description": "Fix the off-by-one error in this function that should return numbers from 1 to n inclusive.",
        "buggy_code": '''def count_to_n(n):
    result = []
    for i in range(n):  # Bug: should be range(1, n+1)
        result.append(i)
        return result''',
        "function_signature": "def count_to_n(n: int) -> list",
        "test_cases": [
            {"input": {"n": 5}, "expected_output": [1, 2, 3, 4, 5]},
            {"input": {"n": 3}, "expected_output": [1, 2, 3]},
            {"input": {"n": 1}, "expected_output": [1]}
        ],
        "tags": ["off-by-one", "loop"]
    },
    {
        "task_id": "BUGFIX-002",
        "category": "bug_fixing",
        "difficulty": "easy",
        "description": "Fix the wrong operator in this function that should multiply two numbers.",
        "buggy_code": '''def multiply(a, b):
    return a + b  # Bug: should be a * b''',
        "function_signature": "def multiply(a: int, b: int) -> int",
        "test_cases": [
            {"input": {"a": 3, "b": 4}, "expected_output": 12},
            {"input": {"a": 5, "b": 5}, "expected_output": 25},
            {"input": {"a": 0, "b": 10}, "expected_output": 0}
        ],
        "tags": ["operator", "arithmetic"]
    },
    {
        "task_id": "BUGFIX-003",
        "category": "bug_fixing",
        "difficulty": "easy",
        "description": "Fix the indentation error causing early return.",
        "buggy_code": '''def sum_list(numbers):
    total = 0
    for num in numbers:
        total += num
        return total  # Bug: return is inside loop''',
        "function_signature": "def sum_list(numbers: list) -> int",
        "test_cases": [
            {"input": {"numbers": [1, 2, 3, 4]}, "expected_output": 10},
            {"input": {"numbers": [10, 20]}, "expected_output": 30},
            {"input": {"numbers": []}, "expected_output": 0}
        ],
        "tags": ["indentation", "loop"]
    },
    {
        "task_id": "BUGFIX-004",
        "category": "bug_fixing",
        "difficulty": "easy",
        "description": "Fix the comparison operator bug in this max function.",
        "buggy_code": '''def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers:
        if num < max_val:  # Bug: should be >
            max_val = num
    return max_val''',
        "function_signature": "def find_max(numbers: list) -> int",
        "test_cases": [
            {"input": {"numbers": [1, 5, 3, 9, 2]}, "expected_output": 9},
            {"input": {"numbers": [10]}, "expected_output": 10},
            {"input": {"numbers": [-1, -5, -2]}, "expected_output": -1}
        ],
        "tags": ["comparison", "loop"]
    },
    {
        "task_id": "BUGFIX-005",
        "category": "bug_fixing",
        "difficulty": "easy",
        "description": "Fix the string concatenation bug.",
        "buggy_code": '''def greet(name):
    return "Hello, " + name  # Bug: missing exclamation mark''',
        "function_signature": "def greet(name: str) -> str",
        "test_cases": [
            {"input": {"name": "Alice"}, "expected_output": "Hello, Alice!"},
            {"input": {"name": "Bob"}, "expected_output": "Hello, Bob!"}
        ],
        "tags": ["string", "concatenation"]
    },
    # Medium bugs (logic errors, boundary conditions)
    {
        "task_id": "BUGFIX-006",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the logic error in this palindrome checker.",
        "buggy_code": '''def is_palindrome(s):
    s = s.lower()
    return s == s[::-1]  # Bug: doesn't remove spaces''',
        "function_signature": "def is_palindrome(s: str) -> bool",
        "test_cases": [
            {"input": {"s": "A man a plan a canal Panama"}, "expected_output": True},
            {"input": {"s": "race car"}, "expected_output": True},
            {"input": {"s": "hello"}, "expected_output": False}
        ],
        "tags": ["string", "logic"]
    },
    {
        "task_id": "BUGFIX-007",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the boundary condition bug in binary search.",
        "buggy_code": '''def binary_search(arr, target):
    left, right = 0, len(arr)  # Bug: should be len(arr) - 1
    while left < right:  # Bug: should be <=
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
        "function_signature": "def binary_search(arr: list, target: int) -> int",
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 4, 5], "target": 3}, "expected_output": 2},
            {"input": {"arr": [1, 2, 3, 4, 5], "target": 5}, "expected_output": 4},
            {"input": {"arr": [1, 2, 3, 4, 5], "target": 6}, "expected_output": -1}
        ],
        "tags": ["binary_search", "boundary"]
    },
    {
        "task_id": "BUGFIX-008",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the fibonacci function that has wrong base cases.",
        "buggy_code": '''def fibonacci(n):
    if n == 0:
        return 1  # Bug: should return 0
    if n == 1:
        return 0  # Bug: should return 1
    return fibonacci(n-1) + fibonacci(n-2)''',
        "function_signature": "def fibonacci(n: int) -> int",
        "test_cases": [
            {"input": {"n": 0}, "expected_output": 0},
            {"input": {"n": 1}, "expected_output": 1},
            {"input": {"n": 6}, "expected_output": 8},
            {"input": {"n": 10}, "expected_output": 55}
        ],
        "tags": ["recursion", "base_case"]
    },
    {
        "task_id": "BUGFIX-009",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the bug in this function that counts occurrences.",
        "buggy_code": '''def count_occurrences(lst, target):
    count = 1  # Bug: should start at 0
    for item in lst:
        if item == target:
            count += 1
    return count''',
        "function_signature": "def count_occurrences(lst: list, target) -> int",
        "test_cases": [
            {"input": {"lst": [1, 2, 3, 2, 2, 4], "target": 2}, "expected_output": 3},
            {"input": {"lst": [1, 1, 1, 1], "target": 1}, "expected_output": 4},
            {"input": {"lst": [1, 2, 3], "target": 5}, "expected_output": 0}
        ],
        "tags": ["counting", "initialization"]
    },
    {
        "task_id": "BUGFIX-010",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the merge function that doesn't handle empty lists.",
        "buggy_code": '''def merge_sorted(lst1, lst2):
    result = []
    i = j = 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] <= lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1
    # Bug: missing remaining elements
    return result''',
        "function_signature": "def merge_sorted(lst1: list, lst2: list) -> list",
        "test_cases": [
            {"input": {"lst1": [1, 3, 5], "lst2": [2, 4, 6]}, "expected_output": [1, 2, 3, 4, 5, 6]},
            {"input": {"lst1": [1, 2], "lst2": []}, "expected_output": [1, 2]},
            {"input": {"lst1": [], "lst2": [3, 4]}, "expected_output": [3, 4]}
        ],
        "tags": ["merge", "edge_case"]
    },
    # Hard bugs (complex logic, multiple issues)
    {
        "task_id": "BUGFIX-011",
        "category": "bug_fixing",
        "difficulty": "hard",
        "description": "Fix the quicksort implementation with multiple bugs.",
        "buggy_code": '''def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]  # Bug: better to use middle
    left = [x for x in arr if x < pivot]
    right = [x for x in arr if x > pivot]  # Bug: missing equal elements
    return quicksort(left) + quicksort(right)''',
        "function_signature": "def quicksort(arr: list) -> list",
        "test_cases": [
            {"input": {"arr": [3, 1, 4, 1, 5, 9, 2, 6]}, "expected_output": [1, 1, 2, 3, 4, 5, 6, 9]},
            {"input": {"arr": [5, 5, 5]}, "expected_output": [5, 5, 5]},
            {"input": {"arr": []}, "expected_output": []}
        ],
        "tags": ["sorting", "recursion", "multiple_bugs"]
    },
    {
        "task_id": "BUGFIX-012",
        "category": "bug_fixing",
        "difficulty": "hard",
        "description": "Fix the depth-first search that has visited tracking bug.",
        "buggy_code": '''def dfs(graph, start, target):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        # Bug: should check visited before processing
        for neighbor in graph.get(node, []):
            stack.append(neighbor)
        visited.add(node)
    return False''',
        "function_signature": "def dfs(graph: dict, start: str, target: str) -> bool",
        "test_cases": [
            {"input": {"graph": {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}, "start": "A", "target": "D"}, "expected_output": True},
            {"input": {"graph": {"A": ["B"], "B": ["A"]}, "start": "A", "target": "C"}, "expected_output": False}
        ],
        "tags": ["graph", "dfs", "visited"]
    },
    {
        "task_id": "BUGFIX-013",
        "category": "bug_fixing",
        "difficulty": "hard",
        "description": "Fix the LRU cache implementation.",
        "buggy_code": '''def lru_cache_get(cache, capacity, key):
    # cache is a dict, returns (new_cache, value)
    if key in cache:
        value = cache[key]
        # Bug: should move to end (most recent)
        return cache, value
    return cache, None''',
        "function_signature": "def lru_cache_get(cache: dict, capacity: int, key: str) -> tuple",
        "test_cases": [
            {"input": {"cache": {"a": 1, "b": 2}, "capacity": 2, "key": "a"}, "expected_output": [{"a": 1, "b": 2}, 1]},
            {"input": {"cache": {"a": 1}, "capacity": 2, "key": "c"}, "expected_output": [{"a": 1}, None]}
        ],
        "tags": ["cache", "data_structure"]
    },
    {
        "task_id": "BUGFIX-014",
        "category": "bug_fixing",
        "difficulty": "hard",
        "description": "Fix the balanced parentheses checker with multiple bracket types.",
        "buggy_code": '''def is_balanced(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack:  # Bug: should return False
                continue
            if stack.pop() != mapping[char]:
                return False
    return True  # Bug: should check if stack is empty''',
        "function_signature": "def is_balanced(s: str) -> bool",
        "test_cases": [
            {"input": {"s": "({[]})"}, "expected_output": True},
            {"input": {"s": "([)]"}, "expected_output": False},
            {"input": {"s": "((("}, "expected_output": False},
            {"input": {"s": ")"}, "expected_output": False}
        ],
        "tags": ["stack", "validation", "multiple_bugs"]
    },
    {
        "task_id": "BUGFIX-015",
        "category": "bug_fixing",
        "difficulty": "hard",
        "description": "Fix the matrix rotation function.",
        "buggy_code": '''def rotate_90(matrix):
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[j][i] = matrix[i][j]  # Bug: wrong transformation
    return result''',
        "function_signature": "def rotate_90(matrix: list) -> list",
        "test_cases": [
            {"input": {"matrix": [[1, 2], [3, 4]]}, "expected_output": [[3, 1], [4, 2]]},
            {"input": {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, "expected_output": [[7, 4, 1], [8, 5, 2], [9, 6, 3]]}
        ],
        "tags": ["matrix", "transformation"]
    },
    {
        "task_id": "BUGFIX-016",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the prime number checker.",
        "buggy_code": '''def is_prime(n):
    if n < 2:
        return True  # Bug: should return False
    for i in range(2, n):  # Bug: inefficient, should be sqrt(n)
        if n % i == 0:
            return False
    return True''',
        "function_signature": "def is_prime(n: int) -> bool",
        "test_cases": [
            {"input": {"n": 2}, "expected_output": True},
            {"input": {"n": 17}, "expected_output": True},
            {"input": {"n": 1}, "expected_output": False},
            {"input": {"n": 4}, "expected_output": False}
        ],
        "tags": ["prime", "math"]
    },
    {
        "task_id": "BUGFIX-017",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the string reversal that should reverse words, not characters.",
        "buggy_code": '''def reverse_words(s):
    return s[::-1]  # Bug: reverses characters, not words''',
        "function_signature": "def reverse_words(s: str) -> str",
        "test_cases": [
            {"input": {"s": "hello world"}, "expected_output": "world hello"},
            {"input": {"s": "the quick brown fox"}, "expected_output": "fox brown quick the"},
            {"input": {"s": "a"}, "expected_output": "a"}
        ],
        "tags": ["string", "logic"]
    },
    {
        "task_id": "BUGFIX-018",
        "category": "bug_fixing",
        "difficulty": "easy",
        "description": "Fix the average calculation with integer division bug.",
        "buggy_code": '''def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) // len(numbers)  # Bug: should use / not //''',
        "function_signature": "def average(numbers: list) -> float",
        "test_cases": [
            {"input": {"numbers": [1, 2, 3, 4]}, "expected_output": 2.5},
            {"input": {"numbers": [10, 20, 30]}, "expected_output": 20.0},
            {"input": {"numbers": []}, "expected_output": 0}
        ],
        "tags": ["math", "division"]
    },
    {
        "task_id": "BUGFIX-019",
        "category": "bug_fixing",
        "difficulty": "medium",
        "description": "Fix the flatten nested list function.",
        "buggy_code": '''def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):
            result.append(flatten(item))  # Bug: should extend, not append
        else:
            result.append(item)
    return result''',
        "function_signature": "def flatten(nested: list) -> list",
        "test_cases": [
            {"input": {"nested": [1, [2, 3], [4, [5, 6]]]}, "expected_output": [1, 2, 3, 4, 5, 6]},
            {"input": {"nested": [[1, 2], [3, 4]]}, "expected_output": [1, 2, 3, 4]},
            {"input": {"nested": [1, 2, 3]}, "expected_output": [1, 2, 3]}
        ],
        "tags": ["recursion", "list"]
    },
    {
        "task_id": "BUGFIX-020",
        "category": "bug_fixing",
        "difficulty": "hard",
        "description": "Fix the topological sort with cycle detection.",
        "buggy_code": '''def topological_sort(graph):
    visited = set()
    result = []
    
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        result.append(node)  # Bug: cycle detection missing
    
    for node in graph:
        dfs(node)
    return result[::-1]''',
        "function_signature": "def topological_sort(graph: dict) -> list",
        "test_cases": [
            {"input": {"graph": {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}}, "expected_output": ["a", "c", "b", "d"]},
            {"input": {"graph": {"a": ["b"], "b": []}}, "expected_output": ["a", "b"]}
        ],
        "tags": ["graph", "topological", "dfs"]
    }
]


def main():
    print("Creating 20 Bug Fixing tasks...")
    
    # Load existing tasks
    existing_tasks = []
    with open(TASKS_FILE) as f:
        for line in f:
            if line.strip():
                existing_tasks.append(json.loads(line))
    
    print(f"  Existing tasks: {len(existing_tasks)}")
    
    # Add new tasks
    with open(TASKS_FILE, 'a') as f:
        for task in BUGFIX_TASKS:
            f.write(json.dumps(task) + '\n')
    
    print(f"  Added: {len(BUGFIX_TASKS)} bug fixing tasks")
    print(f"  Total now: {len(existing_tasks) + len(BUGFIX_TASKS)}")


if __name__ == "__main__":
    main()
