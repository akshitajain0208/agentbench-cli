"""Create 15 Code Refactoring tasks."""

import json
from pathlib import Path

TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")

REFACTOR_TASKS = [
    {
        "task_id": "REFACTOR-001",
        "category": "refactoring",
        "difficulty": "easy",
        "description": "Refactor this repetitive code to use a loop.",
        "original_code": '''def print_numbers():
    print(1)
    print(2)
    print(3)
    print(4)
    print(5)
    return [1, 2, 3, 4, 5]''',
        "function_signature": "def print_numbers() -> list",
        "test_cases": [
            {"input": {}, "expected_output": [1, 2, 3, 4, 5]}
        ],
        "tags": ["loop", "dry"]
    },
    {
        "task_id": "REFACTOR-002",
        "category": "refactoring",
        "difficulty": "easy",
        "description": "Refactor to use list comprehension instead of loop.",
        "original_code": '''def square_numbers(numbers):
    result = []
    for n in numbers:
        result.append(n * n)
    return result''',
        "function_signature": "def square_numbers(numbers: list) -> list",
        "test_cases": [
            {"input": {"numbers": [1, 2, 3, 4]}, "expected_output": [1, 4, 9, 16]},
            {"input": {"numbers": [5, 10]}, "expected_output": [25, 100]}
        ],
        "tags": ["list_comprehension", "pythonic"]
    },
    {
        "task_id": "REFACTOR-003",
        "category": "refactoring",
        "difficulty": "easy",
        "description": "Refactor nested if statements to use early returns.",
        "original_code": '''def validate_user(user):
    if user is not None:
        if user.get('name'):
            if user.get('age', 0) >= 18:
                return True
            else:
                return False
        else:
            return False
    else:
        return False''',
        "function_signature": "def validate_user(user: dict) -> bool",
        "test_cases": [
            {"input": {"user": {"name": "Alice", "age": 25}}, "expected_output": True},
            {"input": {"user": {"name": "Bob", "age": 16}}, "expected_output": False},
            {"input": {"user": None}, "expected_output": False},
            {"input": {"user": {}}, "expected_output": False}
        ],
        "tags": ["early_return", "guard_clause"]
    },
    {
        "task_id": "REFACTOR-004",
        "category": "refactoring",
        "difficulty": "easy",
        "description": "Refactor to use f-string instead of concatenation.",
        "original_code": '''def format_greeting(name, age):
    return "Hello, my name is " + name + " and I am " + str(age) + " years old."''',
        "function_signature": "def format_greeting(name: str, age: int) -> str",
        "test_cases": [
            {"input": {"name": "Alice", "age": 30}, "expected_output": "Hello, my name is Alice and I am 30 years old."},
            {"input": {"name": "Bob", "age": 25}, "expected_output": "Hello, my name is Bob and I am 25 years old."}
        ],
        "tags": ["f-string", "string_formatting"]
    },
    {
        "task_id": "REFACTOR-005",
        "category": "refactoring",
        "difficulty": "medium",
        "description": "Refactor to extract repeated logic into a helper function.",
        "original_code": '''def process_data(data):
    # Process first item
    item1 = data[0]
    item1 = item1.strip().lower()
    if item1.startswith('a'):
        item1 = item1.upper()
    
    # Process second item  
    item2 = data[1]
    item2 = item2.strip().lower()
    if item2.startswith('a'):
        item2 = item2.upper()
    
    return [item1, item2]''',
        "function_signature": "def process_data(data: list) -> list",
        "test_cases": [
            {"input": {"data": ["  Apple  ", "  Banana  "]}, "expected_output": ["APPLE", "banana"]},
            {"input": {"data": ["Ant", "Bee"]}, "expected_output": ["ANT", "bee"]}
        ],
        "tags": ["extract_function", "dry"]
    },
    {
        "task_id": "REFACTOR-006",
        "category": "refactoring",
        "difficulty": "medium",
        "description": "Refactor using dict instead of multiple if-elif statements.",
        "original_code": '''def get_day_name(day_num):
    if day_num == 1:
        return "Monday"
    elif day_num == 2:
        return "Tuesday"
    elif day_num == 3:
        return "Wednesday"
    elif day_num == 4:
        return "Thursday"
    elif day_num == 5:
        return "Friday"
    elif day_num == 6:
        return "Saturday"
    elif day_num == 7:
        return "Sunday"
    else:
        return "Invalid"''',
        "function_signature": "def get_day_name(day_num: int) -> str",
        "test_cases": [
            {"input": {"day_num": 1}, "expected_output": "Monday"},
            {"input": {"day_num": 5}, "expected_output": "Friday"},
            {"input": {"day_num": 7}, "expected_output": "Sunday"},
            {"input": {"day_num": 8}, "expected_output": "Invalid"}
        ],
        "tags": ["dict_dispatch", "clean_code"]
    },
    {
        "task_id": "REFACTOR-007",
        "category": "refactoring",
        "difficulty": "medium",
        "description": "Refactor to use enumerate instead of manual index tracking.",
        "original_code": '''def find_index(lst, target):
    i = 0
    for item in lst:
        if item == target:
            return i
        i = i + 1
    return -1''',
        "function_signature": "def find_index(lst: list, target) -> int",
        "test_cases": [
            {"input": {"lst": [1, 2, 3, 4, 5], "target": 3}, "expected_output": 2},
            {"input": {"lst": ["a", "b", "c"], "target": "c"}, "expected_output": 2},
            {"input": {"lst": [1, 2, 3], "target": 5}, "expected_output": -1}
        ],
        "tags": ["enumerate", "pythonic"]
    },
    {
        "task_id": "REFACTOR-008",
        "category": "refactoring",
        "difficulty": "medium",
        "description": "Refactor to use zip instead of index-based iteration.",
        "original_code": '''def combine_lists(list1, list2):
    result = []
    for i in range(min(len(list1), len(list2))):
        result.append((list1[i], list2[i]))
    return result''',
        "function_signature": "def combine_lists(list1: list, list2: list) -> list",
        "test_cases": [
            {"input": {"list1": [1, 2, 3], "list2": ["a", "b", "c"]}, "expected_output": [[1, "a"], [2, "b"], [3, "c"]]},
            {"input": {"list1": [1, 2], "list2": ["x", "y", "z"]}, "expected_output": [[1, "x"], [2, "y"]]}
        ],
        "tags": ["zip", "pythonic"]
    },
    {
        "task_id": "REFACTOR-009",
        "category": "refactoring",
        "difficulty": "medium",
        "description": "Refactor to use collections.Counter instead of manual counting.",
        "original_code": '''def count_chars(s):
    counts = {}
    for char in s:
        if char in counts:
            counts[char] = counts[char] + 1
        else:
            counts[char] = 1
    return counts''',
        "function_signature": "def count_chars(s: str) -> dict",
        "test_cases": [
            {"input": {"s": "hello"}, "expected_output": {"h": 1, "e": 1, "l": 2, "o": 1}},
            {"input": {"s": "aaa"}, "expected_output": {"a": 3}}
        ],
        "tags": ["collections", "counter"]
    },
    {
        "task_id": "REFACTOR-010",
        "category": "refactoring",
        "difficulty": "hard",
        "description": "Refactor to use generator for memory efficiency.",
        "original_code": '''def get_even_squares(n):
    result = []
    for i in range(n):
        square = i * i
        if square % 2 == 0:
            result.append(square)
    return result''',
        "function_signature": "def get_even_squares(n: int) -> list",
        "test_cases": [
            {"input": {"n": 10}, "expected_output": [0, 4, 16, 36, 64]},
            {"input": {"n": 5}, "expected_output": [0, 4, 16]}
        ],
        "tags": ["generator", "memory_efficient"]
    },
    {
        "task_id": "REFACTOR-011",
        "category": "refactoring",
        "difficulty": "hard",
        "description": "Refactor class to use property decorators instead of getters/setters.",
        "original_code": '''class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height
    
    def get_width(self):
        return self._width
    
    def set_width(self, value):
        self._width = value
    
    def get_area(self):
        return self._width * self._height

def rectangle_area(width, height):
    r = Rectangle(width, height)
    return r.get_area()''',
        "function_signature": "def rectangle_area(width: int, height: int) -> int",
        "test_cases": [
            {"input": {"width": 5, "height": 3}, "expected_output": 15},
            {"input": {"width": 10, "height": 10}, "expected_output": 100}
        ],
        "tags": ["property", "oop"]
    },
    {
        "task_id": "REFACTOR-012",
        "category": "refactoring",
        "difficulty": "hard",
        "description": "Refactor to use functools.reduce for aggregation.",
        "original_code": '''def multiply_all(numbers):
    result = 1
    for num in numbers:
        result = result * num
    return result''',
        "function_signature": "def multiply_all(numbers: list) -> int",
        "test_cases": [
            {"input": {"numbers": [1, 2, 3, 4]}, "expected_output": 24},
            {"input": {"numbers": [5, 5, 5]}, "expected_output": 125},
            {"input": {"numbers": [10]}, "expected_output": 10}
        ],
        "tags": ["functools", "reduce"]
    },
    {
        "task_id": "REFACTOR-013",
        "category": "refactoring",
        "difficulty": "hard",
        "description": "Refactor deeply nested code using early returns and guard clauses.",
        "original_code": '''def process_order(order):
    if order is not None:
        if order.get('items'):
            if len(order['items']) > 0:
                total = 0
                for item in order['items']:
                    if item.get('price'):
                        if item.get('quantity'):
                            total += item['price'] * item['quantity']
                return total
    return 0''',
        "function_signature": "def process_order(order: dict) -> int",
        "test_cases": [
            {"input": {"order": {"items": [{"price": 10, "quantity": 2}, {"price": 5, "quantity": 3}]}}, "expected_output": 35},
            {"input": {"order": {"items": []}}, "expected_output": 0},
            {"input": {"order": None}, "expected_output": 0}
        ],
        "tags": ["guard_clause", "clean_code"]
    },
    {
        "task_id": "REFACTOR-014",
        "category": "refactoring",
        "difficulty": "medium",
        "description": "Refactor to use any() and all() built-in functions.",
        "original_code": '''def has_negative(numbers):
    for num in numbers:
        if num < 0:
            return True
    return False''',
        "function_signature": "def has_negative(numbers: list) -> bool",
        "test_cases": [
            {"input": {"numbers": [1, 2, -3, 4]}, "expected_output": True},
            {"input": {"numbers": [1, 2, 3, 4]}, "expected_output": False},
            {"input": {"numbers": []}, "expected_output": False}
        ],
        "tags": ["any", "pythonic"]
    },
    {
        "task_id": "REFACTOR-015",
        "category": "refactoring",
        "difficulty": "hard",
        "description": "Refactor to use defaultdict for cleaner grouping logic.",
        "original_code": '''def group_by_length(words):
    groups = {}
    for word in words:
        length = len(word)
        if length not in groups:
            groups[length] = []
        groups[length].append(word)
    return groups''',
        "function_signature": "def group_by_length(words: list) -> dict",
        "test_cases": [
            {"input": {"words": ["a", "bb", "ccc", "dd", "e"]}, "expected_output": {1: ["a", "e"], 2: ["bb", "dd"], 3: ["ccc"]}},
            {"input": {"words": ["hello", "world"]}, "expected_output": {5: ["hello", "world"]}}
        ],
        "tags": ["defaultdict", "collections"]
    }
]


def main():
    print("Creating 15 Refactoring tasks...")
    
    with open(TASKS_FILE) as f:
        existing = sum(1 for line in f if line.strip())
    
    print(f"  Existing tasks: {existing}")
    
    with open(TASKS_FILE, 'a') as f:
        for task in REFACTOR_TASKS:
            f.write(json.dumps(task) + '\n')
    
    print(f"  Added: {len(REFACTOR_TASKS)} refactoring tasks")
    print(f"  Total now: {existing + len(REFACTOR_TASKS)}")


if __name__ == "__main__":
    main()
