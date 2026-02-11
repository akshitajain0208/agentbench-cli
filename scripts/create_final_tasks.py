"""Add final 17 tasks to reach 100 total."""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.task_schema import Task, TaskCategory, Difficulty, TestCase
from src.evaluation.prompt_schema import PromptGenerator


def create_final_tasks() -> list:
    """Create final 17 tasks: 4 easy, 5 medium, 8 hard."""
    tasks = []
    
    # EASY TASKS (4)
    tasks.append(Task(
        task_id="EASY-014",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Check if a list is sorted in ascending order.",
        function_signature="def is_sorted(nums: list) -> bool",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4]}, expected_output=True),
            TestCase(input={"nums": [1, 3, 2]}, expected_output=False),
            TestCase(input={"nums": []}, expected_output=True),
        ],
        tags=["list"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-015",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Find the intersection of two lists.",
        function_signature="def intersection(nums1: list, nums2: list) -> list",
        constraints=["Return unique elements only", "Order doesn't matter"],
        test_cases=[
            TestCase(input={"nums1": [1, 2, 2, 1], "nums2": [2, 2]}, expected_output=[2]),
            TestCase(input={"nums1": [4, 9, 5], "nums2": [9, 4, 9, 8, 4]}, expected_output=[4, 9]),
        ],
        tags=["set", "list"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-016",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Convert temperature from Celsius to Fahrenheit.",
        function_signature="def celsius_to_fahrenheit(c: float) -> float",
        constraints=["Formula: F = C * 9/5 + 32"],
        test_cases=[
            TestCase(input={"c": 0}, expected_output=32.0),
            TestCase(input={"c": 100}, expected_output=212.0),
            TestCase(input={"c": -40}, expected_output=-40.0),
        ],
        tags=["math"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-017",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Find GCD (Greatest Common Divisor) of two numbers.",
        function_signature="def gcd(a: int, b: int) -> int",
        constraints=["Use Euclidean algorithm"],
        test_cases=[
            TestCase(input={"a": 48, "b": 18}, expected_output=6),
            TestCase(input={"a": 7, "b": 5}, expected_output=1),
            TestCase(input={"a": 100, "b": 25}, expected_output=25),
        ],
        tags=["math", "recursion"],
        source="classic",
        creation_date=datetime.now().isoformat(),
    ))
    
    # MEDIUM TASKS (5)
    tasks.append(Task(
        task_id="MED-025",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Flatten a dictionary with nested keys using dot notation.",
        function_signature="def flatten_dict(d: dict, parent_key: str = '') -> dict",
        constraints=["Use '.' as separator"],
        test_cases=[
            TestCase(input={"d": {"a": 1, "b": {"c": 2, "d": 3}}}, 
                    expected_output={"a": 1, "b.c": 2, "b.d": 3}),
            TestCase(input={"d": {"x": {"y": {"z": 1}}}}, 
                    expected_output={"x.y.z": 1}),
        ],
        tags=["recursion", "dictionary"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-026",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Check if one string is a rotation of another.",
        function_signature="def is_rotation(s1: str, s2: str) -> bool",
        constraints=["Same length required"],
        test_cases=[
            TestCase(input={"s1": "waterbottle", "s2": "erbottlewat"}, expected_output=True),
            TestCase(input={"s1": "hello", "s2": "llohe"}, expected_output=True),
            TestCase(input={"s1": "hello", "s2": "world"}, expected_output=False),
        ],
        tags=["string"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-027",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find all subsets of a list.",
        function_signature="def subsets(nums: list) -> list",
        constraints=["Include empty set"],
        test_cases=[
            TestCase(input={"nums": [1, 2]}, expected_output=[[], [1], [2], [1, 2]]),
            TestCase(input={"nums": []}, expected_output=[[]]),
        ],
        tags=["backtracking", "bit-manipulation"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-028",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Compute the power set size of a list.",
        function_signature="def power_set_size(nums: list) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3]}, expected_output=8),
            TestCase(input={"nums": []}, expected_output=1),
        ],
        tags=["math"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-029",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the next greater element for each element in a list.",
        function_signature="def next_greater_element(nums: list) -> list",
        constraints=["Return -1 if no greater element exists"],
        test_cases=[
            TestCase(input={"nums": [4, 5, 2, 25]}, expected_output=[5, 25, 25, -1]),
            TestCase(input={"nums": [13, 7, 6, 12]}, expected_output=[-1, 12, 12, -1]),
        ],
        tags=["stack", "monotonic-stack"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # HARD TASKS (8)
    tasks.append(Task(
        task_id="HARD-031",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the longest common subsequence of two strings.",
        function_signature="def longest_common_subsequence(s1: str, s2: str) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"s1": "abcde", "s2": "ace"}, expected_output=3),
            TestCase(input={"s1": "abc", "s2": "def"}, expected_output=0),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-032",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find minimum insertions to make a string palindrome.",
        function_signature="def min_insertions_palindrome(s: str) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"s": "abc"}, expected_output=2),
            TestCase(input={"s": "aa"}, expected_output=0),
            TestCase(input={"s": "ab"}, expected_output=1),
        ],
        tags=["dynamic-programming", "palindrome"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-033",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find if there's a subset that sums to target.",
        function_signature="def subset_sum(nums: list, target: int) -> bool",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [3, 34, 4, 12, 5, 2], "target": 9}, expected_output=True),
            TestCase(input={"nums": [3, 34, 4, 12, 5, 2], "target": 30}, expected_output=False),
        ],
        tags=["dynamic-programming"],
        source="classic",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-034",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the number of ways to climb n stairs (1 or 2 steps at a time).",
        function_signature="def climb_stairs(n: int) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"n": 2}, expected_output=2),
            TestCase(input={"n": 3}, expected_output=3),
            TestCase(input={"n": 5}, expected_output=8),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-035",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find unique paths from top-left to bottom-right of an m x n grid.",
        function_signature="def unique_paths(m: int, n: int) -> int",
        constraints=["Can only move right or down"],
        test_cases=[
            TestCase(input={"m": 3, "n": 7}, expected_output=28),
            TestCase(input={"m": 3, "n": 2}, expected_output=3),
        ],
        tags=["dynamic-programming", "combinatorics"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-036",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Check if a string can be segmented into dictionary words.",
        function_signature="def can_segment(s: str, word_dict: list) -> bool",
        constraints=[],
        test_cases=[
            TestCase(input={"s": "leetcode", "word_dict": ["leet", "code"]}, expected_output=True),
            TestCase(input={"s": "applepenapple", "word_dict": ["apple", "pen"]}, expected_output=True),
            TestCase(input={"s": "catsandog", "word_dict": ["cats", "dog", "sand", "and", "cat"]}, expected_output=False),
        ],
        tags=["dynamic-programming", "string"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-037",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the maximum length of a subarray with sum <= k.",
        function_signature="def max_subarray_len(nums: list, k: int) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3], "k": 5}, expected_output=2),
            TestCase(input={"nums": [1, 2, 1, 0, 1, 1, 0], "k": 4}, expected_output=5),
        ],
        tags=["sliding-window", "prefix-sum"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-038",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the minimum number of jumps to reach the end.",
        function_signature="def min_jumps(nums: list) -> int",
        constraints=["nums[i] is max jump length from i", "Always reachable"],
        test_cases=[
            TestCase(input={"nums": [2, 3, 1, 1, 4]}, expected_output=2),
            TestCase(input={"nums": [2, 3, 0, 1, 4]}, expected_output=2),
        ],
        tags=["greedy", "dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def main():
    """Add final 17 tasks to reach 100."""
    print("Adding final tasks to reach 100...")
    
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
    new_tasks = create_final_tasks()
    print(f"  Created {len(new_tasks)} new tasks")
    
    # Save all tasks
    with open(tasks_file, 'w') as f:
        for task_data in existing_tasks:
            f.write(json.dumps(task_data) + '\n')
        for task in new_tasks:
            f.write(json.dumps(task.to_dict()) + '\n')
    
    total = len(existing_tasks) + len(new_tasks)
    
    # Generate prompts
    prompts_output = prompts_dir / "codegen-core"
    for task in new_tasks:
        prompts = PromptGenerator.generate_prompts(task)
        PromptGenerator.save_prompts(prompts, prompts_output)
    
    print(f"\n{'='*50}")
    print(f"BENCHMARK SUITE: {total} TASKS")
    print(f"{'='*50}")
    print("Ready for full benchmark run!")


if __name__ == "__main__":
    main()
