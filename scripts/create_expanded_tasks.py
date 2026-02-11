"""Create expanded benchmark suite with 50 tasks."""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.task_schema import Task, TaskCategory, Difficulty, TestCase
from src.evaluation.prompt_schema import PromptGenerator


def create_easy_tasks() -> list:
    """Create easy baseline tasks."""
    tasks = []
    
    tasks.append(Task(
        task_id="EASY-001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Return the sum of all elements in a list.",
        function_signature="def sum_list(nums: list) -> int",
        constraints=["Handle empty list (return 0)"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4, 5]}, expected_output=15),
            TestCase(input={"nums": []}, expected_output=0),
            TestCase(input={"nums": [-1, 1]}, expected_output=0),
        ],
        tags=["basic", "list"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Return the maximum element in a list.",
        function_signature="def find_max(nums: list) -> int",
        constraints=["Assume list is non-empty"],
        test_cases=[
            TestCase(input={"nums": [1, 5, 3, 9, 2]}, expected_output=9),
            TestCase(input={"nums": [-5, -1, -10]}, expected_output=-1),
            TestCase(input={"nums": [42]}, expected_output=42),
        ],
        tags=["basic", "list"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Count occurrences of a target value in a list.",
        function_signature="def count_occurrences(nums: list, target: int) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [1, 2, 2, 3, 2], "target": 2}, expected_output=3),
            TestCase(input={"nums": [1, 2, 3], "target": 5}, expected_output=0),
            TestCase(input={"nums": [], "target": 1}, expected_output=0),
        ],
        tags=["basic", "counting"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-004",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Check if a string contains only digits.",
        function_signature="def is_numeric(s: str) -> bool",
        constraints=["Empty string returns False"],
        test_cases=[
            TestCase(input={"s": "12345"}, expected_output=True),
            TestCase(input={"s": "123a5"}, expected_output=False),
            TestCase(input={"s": ""}, expected_output=False),
            TestCase(input={"s": "0"}, expected_output=True),
        ],
        tags=["string", "validation"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-005",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Remove all duplicates from a list while preserving order.",
        function_signature="def remove_duplicates(nums: list) -> list",
        constraints=["Preserve first occurrence order"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 2, 3, 1, 4]}, expected_output=[1, 2, 3, 4]),
            TestCase(input={"nums": [1, 1, 1]}, expected_output=[1]),
            TestCase(input={"nums": []}, expected_output=[]),
        ],
        tags=["list", "dedup"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-006",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Capitalize the first letter of each word in a string.",
        function_signature="def title_case(s: str) -> str",
        constraints=[],
        test_cases=[
            TestCase(input={"s": "hello world"}, expected_output="Hello World"),
            TestCase(input={"s": "HELLO"}, expected_output="Hello"),
            TestCase(input={"s": ""}, expected_output=""),
        ],
        tags=["string"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-007",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Return the factorial of a non-negative integer.",
        function_signature="def factorial(n: int) -> int",
        constraints=["n >= 0", "factorial(0) = 1"],
        test_cases=[
            TestCase(input={"n": 5}, expected_output=120),
            TestCase(input={"n": 0}, expected_output=1),
            TestCase(input={"n": 1}, expected_output=1),
        ],
        tags=["math", "recursion"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def create_medium_tasks() -> list:
    """Create medium difficulty tasks."""
    tasks = []
    
    # Data structure tasks
    tasks.append(Task(
        task_id="MED-001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Implement a function that finds the kth largest element in an unsorted list.",
        function_signature="def find_kth_largest(nums: list, k: int) -> int",
        constraints=["1 <= k <= len(nums)"],
        test_cases=[
            TestCase(input={"nums": [3, 2, 1, 5, 6, 4], "k": 2}, expected_output=5),
            TestCase(input={"nums": [3, 2, 3, 1, 2, 4, 5, 5, 6], "k": 4}, expected_output=4),
            TestCase(input={"nums": [1], "k": 1}, expected_output=1),
        ],
        tags=["sorting", "heap"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the longest common prefix among a list of strings.",
        function_signature="def longest_common_prefix(strs: list) -> str",
        constraints=["Return empty string if no common prefix"],
        test_cases=[
            TestCase(input={"strs": ["flower", "flow", "flight"]}, expected_output="fl"),
            TestCase(input={"strs": ["dog", "racecar", "car"]}, expected_output=""),
            TestCase(input={"strs": ["single"]}, expected_output="single"),
            TestCase(input={"strs": []}, expected_output=""),
        ],
        tags=["string"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Merge overlapping intervals.",
        function_signature="def merge_intervals(intervals: list) -> list",
        constraints=["Return sorted by start time"],
        test_cases=[
            TestCase(input={"intervals": [[1,3],[2,6],[8,10],[15,18]]}, 
                    expected_output=[[1,6],[8,10],[15,18]]),
            TestCase(input={"intervals": [[1,4],[4,5]]}, expected_output=[[1,5]]),
            TestCase(input={"intervals": [[1,4]]}, expected_output=[[1,4]]),
        ],
        tags=["intervals", "sorting"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-004",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find all pairs in a list that sum to a target value.",
        function_signature="def find_pairs(nums: list, target: int) -> list",
        constraints=["Return list of tuples (a, b) where a < b", "No duplicate pairs"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4, 5], "target": 6}, 
                    expected_output=[(1, 5), (2, 4)]),
            TestCase(input={"nums": [1, 1, 2, 2], "target": 3}, 
                    expected_output=[(1, 2)]),
            TestCase(input={"nums": [1, 2], "target": 10}, expected_output=[]),
        ],
        tags=["hash-table", "two-pointer"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-005",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Implement run-length encoding for a string.",
        function_signature="def run_length_encode(s: str) -> str",
        constraints=["Format: char followed by count if count > 1"],
        test_cases=[
            TestCase(input={"s": "aaabbc"}, expected_output="a3b2c"),
            TestCase(input={"s": "abcd"}, expected_output="abcd"),
            TestCase(input={"s": "aaa"}, expected_output="a3"),
            TestCase(input={"s": ""}, expected_output=""),
        ],
        tags=["string", "encoding"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-006",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the first non-repeating character in a string.",
        function_signature="def first_unique_char(s: str) -> str",
        constraints=["Return empty string if none found"],
        test_cases=[
            TestCase(input={"s": "leetcode"}, expected_output="l"),
            TestCase(input={"s": "loveleetcode"}, expected_output="v"),
            TestCase(input={"s": "aabb"}, expected_output=""),
        ],
        tags=["string", "hash-table"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-007",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Check if two strings are anagrams of each other.",
        function_signature="def is_anagram(s1: str, s2: str) -> bool",
        constraints=["Case-sensitive"],
        test_cases=[
            TestCase(input={"s1": "anagram", "s2": "nagaram"}, expected_output=True),
            TestCase(input={"s1": "rat", "s2": "car"}, expected_output=False),
            TestCase(input={"s1": "", "s2": ""}, expected_output=True),
        ],
        tags=["string", "sorting"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-008",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the missing number in a list containing n distinct numbers from 0 to n.",
        function_signature="def missing_number(nums: list) -> int",
        constraints=["Use O(1) extra space"],
        test_cases=[
            TestCase(input={"nums": [3, 0, 1]}, expected_output=2),
            TestCase(input={"nums": [0, 1]}, expected_output=2),
            TestCase(input={"nums": [9,6,4,2,3,5,7,0,1]}, expected_output=8),
        ],
        tags=["math", "bit-manipulation"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-009",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Implement binary search that returns the index of target, or -1 if not found.",
        function_signature="def binary_search(nums: list, target: int) -> int",
        constraints=["Input list is sorted", "O(log n) time"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4, 5], "target": 3}, expected_output=2),
            TestCase(input={"nums": [1, 2, 3, 4, 5], "target": 6}, expected_output=-1),
            TestCase(input={"nums": [], "target": 1}, expected_output=-1),
        ],
        tags=["binary-search"],
        source="classic",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-010",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Generate all permutations of a list of unique integers.",
        function_signature="def permutations(nums: list) -> list",
        constraints=["Return list of lists", "Any order"],
        test_cases=[
            TestCase(input={"nums": [1, 2]}, expected_output=[[1, 2], [2, 1]]),
            TestCase(input={"nums": [1]}, expected_output=[[1]]),
            TestCase(input={"nums": []}, expected_output=[[]]),
        ],
        tags=["backtracking", "recursion"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-011",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Determine if a 9x9 Sudoku board is valid (no duplicates in rows, columns, 3x3 boxes).",
        function_signature="def is_valid_sudoku(board: list) -> bool",
        constraints=["Empty cells are represented by '.'"],
        test_cases=[
            TestCase(input={"board": [
                ["5","3",".",".","7",".",".",".","."],
                ["6",".",".","1","9","5",".",".","."],
                [".","9","8",".",".",".",".","6","."],
                ["8",".",".",".","6",".",".",".","3"],
                ["4",".",".","8",".","3",".",".","1"],
                ["7",".",".",".","2",".",".",".","6"],
                [".","6",".",".",".",".","2","8","."],
                [".",".",".","4","1","9",".",".","5"],
                [".",".",".",".","8",".",".","7","9"]
            ]}, expected_output=True),
        ],
        tags=["matrix", "hash-table"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-012",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Convert a Roman numeral string to an integer.",
        function_signature="def roman_to_int(s: str) -> int",
        constraints=["Valid input only (I, V, X, L, C, D, M)"],
        test_cases=[
            TestCase(input={"s": "III"}, expected_output=3),
            TestCase(input={"s": "LVIII"}, expected_output=58),
            TestCase(input={"s": "MCMXCIV"}, expected_output=1994),
        ],
        tags=["string", "math"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def create_hard_tasks() -> list:
    """Create hard algorithm tasks."""
    tasks = []
    
    tasks.append(Task(
        task_id="HARD-001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the length of the longest substring without repeating characters.",
        function_signature="def length_of_longest_substring(s: str) -> int",
        constraints=["O(n) time complexity"],
        test_cases=[
            TestCase(input={"s": "abcabcbb"}, expected_output=3),
            TestCase(input={"s": "bbbbb"}, expected_output=1),
            TestCase(input={"s": "pwwkew"}, expected_output=3),
            TestCase(input={"s": ""}, expected_output=0),
        ],
        tags=["sliding-window", "hash-table"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement a function to serialize and deserialize a binary tree represented as nested lists [val, left, right].",
        function_signature="def serialize(root: list) -> str",
        constraints=["None represents empty node"],
        test_cases=[
            TestCase(input={"root": [1, [2, None, None], [3, None, None]]}, 
                    expected_output="1,2,null,null,3,null,null"),
            TestCase(input={"root": None}, expected_output="null"),
        ],
        tags=["tree", "serialization"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the minimum window substring of s that contains all characters of t.",
        function_signature="def min_window(s: str, t: str) -> str",
        constraints=["Return empty string if no such window exists"],
        test_cases=[
            TestCase(input={"s": "ADOBECODEBANC", "t": "ABC"}, expected_output="BANC"),
            TestCase(input={"s": "a", "t": "a"}, expected_output="a"),
            TestCase(input={"s": "a", "t": "aa"}, expected_output=""),
        ],
        tags=["sliding-window", "hash-table"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-004",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement regular expression matching with '.' and '*' support.",
        function_signature="def is_match(s: str, p: str) -> bool",
        constraints=["'.' matches any single char", "'*' matches zero or more of preceding"],
        test_cases=[
            TestCase(input={"s": "aa", "p": "a"}, expected_output=False),
            TestCase(input={"s": "aa", "p": "a*"}, expected_output=True),
            TestCase(input={"s": "ab", "p": ".*"}, expected_output=True),
            TestCase(input={"s": "aab", "p": "c*a*b"}, expected_output=True),
        ],
        tags=["dynamic-programming", "recursion"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-005",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Given n non-negative integers representing an elevation map, compute trapped rainwater.",
        function_signature="def trap(height: list) -> int",
        constraints=["O(n) time, O(1) space preferred"],
        test_cases=[
            TestCase(input={"height": [0,1,0,2,1,0,1,3,2,1,2,1]}, expected_output=6),
            TestCase(input={"height": [4,2,0,3,2,5]}, expected_output=9),
            TestCase(input={"height": []}, expected_output=0),
        ],
        tags=["two-pointer", "dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-006",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the longest palindromic substring in a string.",
        function_signature="def longest_palindrome(s: str) -> str",
        constraints=["Return any one if multiple exist"],
        test_cases=[
            TestCase(input={"s": "babad"}, expected_output="bab"),
            TestCase(input={"s": "cbbd"}, expected_output="bb"),
            TestCase(input={"s": "a"}, expected_output="a"),
        ],
        tags=["dynamic-programming", "string"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-007",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Calculate the maximum profit from at most k stock transactions.",
        function_signature="def max_profit(k: int, prices: list) -> int",
        constraints=["Must sell before buying again"],
        test_cases=[
            TestCase(input={"k": 2, "prices": [2,4,1]}, expected_output=2),
            TestCase(input={"k": 2, "prices": [3,2,6,5,0,3]}, expected_output=7),
            TestCase(input={"k": 1, "prices": [1,2]}, expected_output=1),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-008",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the number of distinct subsequences of s that equal t.",
        function_signature="def num_distinct(s: str, t: str) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"s": "rabbbit", "t": "rabbit"}, expected_output=3),
            TestCase(input={"s": "babgbag", "t": "bag"}, expected_output=5),
            TestCase(input={"s": "a", "t": "b"}, expected_output=0),
        ],
        tags=["dynamic-programming", "string"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-009",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Given a list of words, find all pairs (i, j) where words[i] + words[j] is a palindrome.",
        function_signature="def palindrome_pairs(words: list) -> list",
        constraints=["Return list of [i, j] pairs"],
        test_cases=[
            TestCase(input={"words": ["abcd", "dcba", "lls", "s", "sssll"]}, 
                    expected_output=[[0, 1], [1, 0], [2, 4], [3, 2]]),
            TestCase(input={"words": ["bat", "tab", "cat"]}, 
                    expected_output=[[0, 1], [1, 0]]),
        ],
        tags=["hash-table", "string", "trie"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-010",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Compute the edit distance (minimum operations to convert s1 to s2).",
        function_signature="def edit_distance(s1: str, s2: str) -> int",
        constraints=["Operations: insert, delete, replace"],
        test_cases=[
            TestCase(input={"s1": "horse", "s2": "ros"}, expected_output=3),
            TestCase(input={"s1": "intention", "s2": "execution"}, expected_output=5),
            TestCase(input={"s1": "", "s2": "abc"}, expected_output=3),
        ],
        tags=["dynamic-programming", "string"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-011",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the maximum sum of any contiguous subarray of size k.",
        function_signature="def max_sum_subarray(nums: list, k: int) -> int",
        constraints=["Sliding window O(n)"],
        test_cases=[
            TestCase(input={"nums": [1, 4, 2, 10, 23, 3, 1, 0, 20], "k": 4}, expected_output=39),
            TestCase(input={"nums": [2, 3], "k": 3}, expected_output=-1),
        ],
        tags=["sliding-window"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-012",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the number of islands in a 2D grid (1=land, 0=water).",
        function_signature="def num_islands(grid: list) -> int",
        constraints=["Grid edges are water"],
        test_cases=[
            TestCase(input={"grid": [
                ["1","1","0","0","0"],
                ["1","1","0","0","0"],
                ["0","0","1","0","0"],
                ["0","0","0","1","1"]
            ]}, expected_output=3),
            TestCase(input={"grid": [["1"]]}, expected_output=1),
        ],
        tags=["dfs", "bfs", "matrix"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-013",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement integer division without using /, *, or %.",
        function_signature="def divide(dividend: int, divisor: int) -> int",
        constraints=["Handle overflow: return 2^31-1 if overflow"],
        test_cases=[
            TestCase(input={"dividend": 10, "divisor": 3}, expected_output=3),
            TestCase(input={"dividend": 7, "divisor": -3}, expected_output=-2),
            TestCase(input={"dividend": -2147483648, "divisor": -1}, expected_output=2147483647),
        ],
        tags=["math", "bit-manipulation"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-014",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the maximum rectangle area in a histogram.",
        function_signature="def largest_rectangle_histogram(heights: list) -> int",
        constraints=["O(n) time using stack"],
        test_cases=[
            TestCase(input={"heights": [2,1,5,6,2,3]}, expected_output=10),
            TestCase(input={"heights": [2,4]}, expected_output=4),
            TestCase(input={"heights": [1]}, expected_output=1),
        ],
        tags=["stack", "monotonic-stack"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-015",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Given an array of meeting intervals [start, end], find minimum meeting rooms required.",
        function_signature="def min_meeting_rooms(intervals: list) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"intervals": [[0,30],[5,10],[15,20]]}, expected_output=2),
            TestCase(input={"intervals": [[7,10],[2,4]]}, expected_output=1),
            TestCase(input={"intervals": []}, expected_output=0),
        ],
        tags=["sorting", "heap", "intervals"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def main():
    """Create expanded task suite."""
    print("Creating expanded task suite...")
    
    benchmark_dir = Path("benchmark/v0.1.0")
    prompts_dir = Path("prompts")
    tasks_file = benchmark_dir / "codegen-core" / "tasks.jsonl"
    
    # Load existing tasks
    existing_tasks = []
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    existing_tasks.append(json.loads(line))
        print(f"  Found {len(existing_tasks)} existing tasks")
    
    # Create new tasks
    easy_tasks = create_easy_tasks()
    medium_tasks = create_medium_tasks()
    hard_tasks = create_hard_tasks()
    
    all_new_tasks = easy_tasks + medium_tasks + hard_tasks
    
    print(f"\n  Created {len(all_new_tasks)} new tasks:")
    print(f"    Easy:   {len(easy_tasks)}")
    print(f"    Medium: {len(medium_tasks)}")
    print(f"    Hard:   {len(hard_tasks)}")
    
    # Save all tasks (replace old file)
    with open(tasks_file, 'w') as f:
        # Keep existing tasks
        for task_data in existing_tasks:
            f.write(json.dumps(task_data) + '\n')
        # Add new tasks
        for task in all_new_tasks:
            f.write(json.dumps(task.to_dict()) + '\n')
    
    total = len(existing_tasks) + len(all_new_tasks)
    print(f"\n  Total tasks: {total}")
    
    # Generate prompts
    prompts_output = prompts_dir / "codegen-core"
    for task in all_new_tasks:
        prompts = PromptGenerator.generate_prompts(task)
        PromptGenerator.save_prompts(prompts, prompts_output)
    
    print(f"  Generated prompts for {len(all_new_tasks)} new tasks")
    
    # Summary
    print(f"\n{'='*50}")
    print("TASK SUITE SUMMARY")
    print(f"{'='*50}")
    print(f"Total tasks: {total}")
    print(f"  - Previous: {len(existing_tasks)}")
    print(f"  - New Easy: {len(easy_tasks)}")
    print(f"  - New Medium: {len(medium_tasks)}")
    print(f"  - New Hard: {len(hard_tasks)}")
    print(f"\nRun 'python scripts/run_pilot.py' to benchmark all tasks.")


if __name__ == "__main__":
    main()
