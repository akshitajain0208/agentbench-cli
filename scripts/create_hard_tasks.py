"""Create challenging benchmark tasks to differentiate agents."""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.task_schema import Task, TaskCategory, Difficulty, TestCase, TaskSuite
from src.evaluation.prompt_schema import PromptGenerator


def create_hard_tasks() -> list:
    """Create hard tasks that will challenge agents."""
    tasks = []
    
    # HARD 1: Longest Increasing Subsequence
    tasks.append(Task(
        task_id="CODEGEN-H001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the length of the longest strictly increasing subsequence in a list of integers.",
        function_signature="def longest_increasing_subsequence(nums: list) -> int",
        constraints=[
            "Use O(n log n) time complexity",
            "Return 0 for empty list"
        ],
        test_cases=[
            TestCase(input={"nums": [10, 9, 2, 5, 3, 7, 101, 18]}, expected_output=4),
            TestCase(input={"nums": [0, 1, 0, 3, 2, 3]}, expected_output=4),
            TestCase(input={"nums": [7, 7, 7, 7]}, expected_output=1),
            TestCase(input={"nums": []}, expected_output=0),
            TestCase(input={"nums": [5, 4, 3, 2, 1]}, expected_output=1),
        ],
        tags=["dynamic-programming", "binary-search", "hard"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # HARD 2: Deep Flatten Nested List
    tasks.append(Task(
        task_id="CODEGEN-H002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement a function that deep flattens a nested list of integers.",
        function_signature="def flatten(nested_list: list) -> list",
        constraints=[
            "Handle arbitrary nesting depth",
            "Preserve order of elements"
        ],
        test_cases=[
            TestCase(input={"nested_list": [[1, 1], 2, [1, 1]]}, expected_output=[1, 1, 2, 1, 1]),
            TestCase(input={"nested_list": [1, [4, [6]]]}, expected_output=[1, 4, 6]),
            TestCase(input={"nested_list": []}, expected_output=[]),
            TestCase(input={"nested_list": [[[[[1]]]]]}, expected_output=[1]),
        ],
        tags=["recursion", "hard"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    # HARD 3: Combination Sum
    tasks.append(Task(
        task_id="CODEGEN-H003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find all unique combinations of candidates that sum to target. Each number can be used unlimited times.",
        function_signature="def combination_sum(candidates: list, target: int) -> list",
        constraints=[
            "Return list of lists",
            "Each combination should be sorted",
            "No duplicate combinations"
        ],
        test_cases=[
            TestCase(input={"candidates": [2, 3, 6, 7], "target": 7}, expected_output=[[2, 2, 3], [7]]),
            TestCase(input={"candidates": [2, 3, 5], "target": 8}, expected_output=[[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
            TestCase(input={"candidates": [2], "target": 1}, expected_output=[]),
        ],
        tags=["backtracking", "hard"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # HARD 4: Word Break
    tasks.append(Task(
        task_id="CODEGEN-H004",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Given a string s and a list of words, determine if s can be segmented into words from the dictionary.",
        function_signature="def word_break(s: str, word_dict: list) -> bool",
        constraints=["Words can be reused"],
        test_cases=[
            TestCase(input={"s": "leetcode", "word_dict": ["leet", "code"]}, expected_output=True),
            TestCase(input={"s": "applepenapple", "word_dict": ["apple", "pen"]}, expected_output=True),
            TestCase(input={"s": "catsandog", "word_dict": ["cats", "dog", "sand", "and", "cat"]}, expected_output=False),
            TestCase(input={"s": "", "word_dict": ["a"]}, expected_output=True),
        ],
        tags=["dynamic-programming", "hard"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # HARD 5: Median of Two Sorted Arrays
    tasks.append(Task(
        task_id="CODEGEN-H005",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the median of two sorted arrays with O(log(m+n)) complexity.",
        function_signature="def find_median_sorted_arrays(nums1: list, nums2: list) -> float",
        constraints=["O(log(m+n)) time complexity"],
        test_cases=[
            TestCase(input={"nums1": [1, 3], "nums2": [2]}, expected_output=2.0),
            TestCase(input={"nums1": [1, 2], "nums2": [3, 4]}, expected_output=2.5),
            TestCase(input={"nums1": [], "nums2": [1]}, expected_output=1.0),
        ],
        tags=["binary-search", "hard"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def create_edge_case_tasks() -> list:
    """Create tasks with tricky edge cases."""
    tasks = []
    
    # EDGE 1: Multiply Strings
    tasks.append(Task(
        task_id="CODEGEN-E001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Multiply two non-negative integers represented as strings. Return the product as a string.",
        function_signature="def multiply_strings(num1: str, num2: str) -> str",
        constraints=["Do not convert inputs to integer directly"],
        test_cases=[
            TestCase(input={"num1": "2", "num2": "3"}, expected_output="6"),
            TestCase(input={"num1": "123", "num2": "456"}, expected_output="56088"),
            TestCase(input={"num1": "0", "num2": "12345"}, expected_output="0"),
        ],
        tags=["string", "math", "edge-case"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # EDGE 2: Reverse Vowels
    tasks.append(Task(
        task_id="CODEGEN-E002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Reverse only the vowels in a string. Vowels are 'aeiouAEIOU'.",
        function_signature="def reverse_vowels(s: str) -> str",
        constraints=["Preserve case"],
        test_cases=[
            TestCase(input={"s": "hello"}, expected_output="holle"),
            TestCase(input={"s": "leetcode"}, expected_output="leotcede"),
            TestCase(input={"s": "aA"}, expected_output="Aa"),
            TestCase(input={"s": ""}, expected_output=""),
        ],
        tags=["string", "two-pointer"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # EDGE 3: Power Function
    tasks.append(Task(
        task_id="CODEGEN-E003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Implement pow(x, n), calculating x raised to power n.",
        function_signature="def my_pow(x: float, n: int) -> float",
        constraints=["Handle negative exponents", "O(log n) time"],
        test_cases=[
            TestCase(input={"x": 2.0, "n": 10}, expected_output=1024.0),
            TestCase(input={"x": 2.0, "n": -2}, expected_output=0.25),
            TestCase(input={"x": 2.0, "n": 0}, expected_output=1.0),
        ],
        tags=["math", "recursion"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def create_medium_tasks() -> list:
    """Create medium difficulty tasks."""
    tasks = []
    
    # MEDIUM 1: Spiral Matrix
    tasks.append(Task(
        task_id="CODEGEN-M001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Given an m x n matrix, return all elements in spiral order (clockwise).",
        function_signature="def spiral_order(matrix: list) -> list",
        constraints=["Handle non-square matrices"],
        test_cases=[
            TestCase(input={"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, 
                    expected_output=[1, 2, 3, 6, 9, 8, 7, 4, 5]),
            TestCase(input={"matrix": [[1, 2], [3, 4]]}, expected_output=[1, 2, 4, 3]),
            TestCase(input={"matrix": [[1]]}, expected_output=[1]),
        ],
        tags=["array", "matrix"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # MEDIUM 2: Maximum Subarray
    tasks.append(Task(
        task_id="CODEGEN-M002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the contiguous subarray with the largest sum.",
        function_signature="def max_subarray(nums: list) -> int",
        constraints=["Must handle negative numbers"],
        test_cases=[
            TestCase(input={"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, expected_output=6),
            TestCase(input={"nums": [1]}, expected_output=1),
            TestCase(input={"nums": [-1, -2, -3]}, expected_output=-1),
        ],
        tags=["dynamic-programming", "array"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # MEDIUM 3: Rotate Image
    tasks.append(Task(
        task_id="CODEGEN-M003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Rotate an n x n 2D matrix 90 degrees clockwise in-place.",
        function_signature="def rotate(matrix: list) -> list",
        constraints=["Modify in-place", "Return the rotated matrix"],
        test_cases=[
            TestCase(input={"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, 
                    expected_output=[[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
            TestCase(input={"matrix": [[1, 2], [3, 4]]}, 
                    expected_output=[[3, 1], [4, 2]]),
        ],
        tags=["matrix", "in-place"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def main():
    """Create all challenging tasks."""
    print("Creating challenging tasks...")
    
    benchmark_dir = Path("benchmark/v0.1.0")
    prompts_dir = Path("prompts")
    
    # Load existing tasks
    tasks_file = benchmark_dir / "codegen-core" / "tasks.jsonl"
    existing_tasks = []
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    existing_tasks.append(json.loads(line))
        print(f"  Found {len(existing_tasks)} existing tasks")
    
    # Create new tasks
    hard_tasks = create_hard_tasks()
    edge_tasks = create_edge_case_tasks()
    medium_tasks = create_medium_tasks()
    
    all_new_tasks = hard_tasks + edge_tasks + medium_tasks
    print(f"  Created {len(all_new_tasks)} new tasks:")
    print(f"    - {len(hard_tasks)} hard tasks")
    print(f"    - {len(edge_tasks)} edge case tasks")
    print(f"    - {len(medium_tasks)} medium tasks")
    
    # Save all tasks
    with open(tasks_file, 'w') as f:
        for task_data in existing_tasks:
            f.write(json.dumps(task_data) + '\n')
        for task in all_new_tasks:
            f.write(json.dumps(task.to_dict()) + '\n')
    
    print(f"  Total tasks: {len(existing_tasks) + len(all_new_tasks)}")
    
    # Generate prompts
    prompts_output = prompts_dir / "codegen-core"
    for task in all_new_tasks:
        prompts = PromptGenerator.generate_prompts(task)
        PromptGenerator.save_prompts(prompts, prompts_output)
    
    print(f"  Generated prompts for {len(all_new_tasks)} new tasks")
    print("\nDone! Run 'python scripts/run_pilot.py' to test.")


if __name__ == "__main__":
    main()
