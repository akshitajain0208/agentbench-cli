"""Add 50 more tasks to reach 100 total."""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.task_schema import Task, TaskCategory, Difficulty, TestCase
from src.evaluation.prompt_schema import PromptGenerator


def create_additional_easy_tasks() -> list:
    """More easy tasks for baseline."""
    tasks = []
    
    tasks.append(Task(
        task_id="EASY-008",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Return True if all elements in a list are unique.",
        function_signature="def all_unique(nums: list) -> bool",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4]}, expected_output=True),
            TestCase(input={"nums": [1, 2, 2, 3]}, expected_output=False),
            TestCase(input={"nums": []}, expected_output=True),
        ],
        tags=["list", "set"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-009",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Reverse a string.",
        function_signature="def reverse_string(s: str) -> str",
        constraints=[],
        test_cases=[
            TestCase(input={"s": "hello"}, expected_output="olleh"),
            TestCase(input={"s": ""}, expected_output=""),
            TestCase(input={"s": "a"}, expected_output="a"),
        ],
        tags=["string"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-010",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Check if a number is prime.",
        function_signature="def is_prime(n: int) -> bool",
        constraints=["n >= 0"],
        test_cases=[
            TestCase(input={"n": 7}, expected_output=True),
            TestCase(input={"n": 4}, expected_output=False),
            TestCase(input={"n": 1}, expected_output=False),
            TestCase(input={"n": 2}, expected_output=True),
        ],
        tags=["math"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-011",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Find the second largest element in a list.",
        function_signature="def second_largest(nums: list) -> int",
        constraints=["List has at least 2 distinct elements"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4, 5]}, expected_output=4),
            TestCase(input={"nums": [5, 5, 4, 4]}, expected_output=4),
            TestCase(input={"nums": [1, 2]}, expected_output=1),
        ],
        tags=["list", "sorting"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-012",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Count vowels in a string.",
        function_signature="def count_vowels(s: str) -> int",
        constraints=["Count both upper and lowercase vowels (aeiouAEIOU)"],
        test_cases=[
            TestCase(input={"s": "Hello World"}, expected_output=3),
            TestCase(input={"s": "xyz"}, expected_output=0),
            TestCase(input={"s": "AEIOU"}, expected_output=5),
        ],
        tags=["string"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="EASY-013",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Return the Fibonacci number at position n.",
        function_signature="def fibonacci(n: int) -> int",
        constraints=["fib(0)=0, fib(1)=1"],
        test_cases=[
            TestCase(input={"n": 0}, expected_output=0),
            TestCase(input={"n": 1}, expected_output=1),
            TestCase(input={"n": 10}, expected_output=55),
        ],
        tags=["math", "recursion"],
        source="classic",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def create_additional_medium_tasks() -> list:
    """More medium tasks."""
    tasks = []
    
    tasks.append(Task(
        task_id="MED-013",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Rotate a list to the right by k positions.",
        function_signature="def rotate_list(nums: list, k: int) -> list",
        constraints=["Modify in-place and return"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4, 5], "k": 2}, expected_output=[4, 5, 1, 2, 3]),
            TestCase(input={"nums": [1, 2], "k": 3}, expected_output=[2, 1]),
            TestCase(input={"nums": [], "k": 1}, expected_output=[]),
        ],
        tags=["list", "rotation"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-014",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the peak element in a list (strictly greater than neighbors).",
        function_signature="def find_peak(nums: list) -> int",
        constraints=["Return index of any peak", "nums[-1] and nums[n] are -infinity"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 1]}, expected_output=2),
            TestCase(input={"nums": [1, 2, 1, 3, 5, 6, 4]}, expected_output=5),
        ],
        tags=["binary-search"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-015",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Check if a linked list represented as a list has a cycle pattern.",
        function_signature="def has_cycle_pattern(nums: list, k: int) -> bool",
        constraints=["Return True if pattern of length k repeats"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 1, 2, 1, 2], "k": 2}, expected_output=True),
            TestCase(input={"nums": [1, 2, 3, 1, 2, 3], "k": 3}, expected_output=True),
            TestCase(input={"nums": [1, 2, 3, 4], "k": 2}, expected_output=False),
        ],
        tags=["pattern", "list"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-016",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the majority element (appears more than n/2 times).",
        function_signature="def majority_element(nums: list) -> int",
        constraints=["Majority element always exists"],
        test_cases=[
            TestCase(input={"nums": [3, 2, 3]}, expected_output=3),
            TestCase(input={"nums": [2, 2, 1, 1, 1, 2, 2]}, expected_output=2),
        ],
        tags=["boyer-moore", "counting"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-017",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Implement atoi: convert string to integer.",
        function_signature="def my_atoi(s: str) -> int",
        constraints=["Handle leading whitespace", "Handle +/- sign", "Clamp to 32-bit range"],
        test_cases=[
            TestCase(input={"s": "42"}, expected_output=42),
            TestCase(input={"s": "   -42"}, expected_output=-42),
            TestCase(input={"s": "4193 with words"}, expected_output=4193),
            TestCase(input={"s": "words and 987"}, expected_output=0),
        ],
        tags=["string", "parsing"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-018",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Generate Pascal's triangle up to n rows.",
        function_signature="def generate_pascal(n: int) -> list",
        constraints=[],
        test_cases=[
            TestCase(input={"n": 5}, expected_output=[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]),
            TestCase(input={"n": 1}, expected_output=[[1]]),
        ],
        tags=["dynamic-programming", "math"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-019",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the single number in a list where every other number appears twice.",
        function_signature="def single_number(nums: list) -> int",
        constraints=["O(1) space using XOR"],
        test_cases=[
            TestCase(input={"nums": [2, 2, 1]}, expected_output=1),
            TestCase(input={"nums": [4, 1, 2, 1, 2]}, expected_output=4),
        ],
        tags=["bit-manipulation"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-020",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Count the number of set bits (1s) in an integer.",
        function_signature="def count_bits(n: int) -> int",
        constraints=["n >= 0"],
        test_cases=[
            TestCase(input={"n": 11}, expected_output=3),
            TestCase(input={"n": 128}, expected_output=1),
            TestCase(input={"n": 0}, expected_output=0),
        ],
        tags=["bit-manipulation"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-021",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find the length of the last word in a string.",
        function_signature="def length_of_last_word(s: str) -> int",
        constraints=["Words are separated by spaces"],
        test_cases=[
            TestCase(input={"s": "Hello World"}, expected_output=5),
            TestCase(input={"s": "   fly me   to   the moon  "}, expected_output=4),
            TestCase(input={"s": "a"}, expected_output=1),
        ],
        tags=["string"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-022",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Add two numbers represented as strings.",
        function_signature="def add_strings(num1: str, num2: str) -> str",
        constraints=["Do not convert to int directly"],
        test_cases=[
            TestCase(input={"num1": "11", "num2": "123"}, expected_output="134"),
            TestCase(input={"num1": "456", "num2": "77"}, expected_output="533"),
            TestCase(input={"num1": "0", "num2": "0"}, expected_output="0"),
        ],
        tags=["string", "math"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-023",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find product of all elements except self without using division.",
        function_signature="def product_except_self(nums: list) -> list",
        constraints=["O(n) time, no division"],
        test_cases=[
            TestCase(input={"nums": [1, 2, 3, 4]}, expected_output=[24, 12, 8, 6]),
            TestCase(input={"nums": [-1, 1, 0, -3, 3]}, expected_output=[0, 0, 9, 0, 0]),
        ],
        tags=["array", "prefix-sum"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="MED-024",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Find minimum in a rotated sorted array.",
        function_signature="def find_min_rotated(nums: list) -> int",
        constraints=["O(log n) time"],
        test_cases=[
            TestCase(input={"nums": [3, 4, 5, 1, 2]}, expected_output=1),
            TestCase(input={"nums": [4, 5, 6, 7, 0, 1, 2]}, expected_output=0),
            TestCase(input={"nums": [1]}, expected_output=1),
        ],
        tags=["binary-search"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def create_additional_hard_tasks() -> list:
    """More hard tasks for differentiation."""
    tasks = []
    
    tasks.append(Task(
        task_id="HARD-016",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement a basic calculator that evaluates string expressions with +, -, (, ).",
        function_signature="def calculate(s: str) -> int",
        constraints=["Handle parentheses", "Handle negative numbers"],
        test_cases=[
            TestCase(input={"s": "1 + 1"}, expected_output=2),
            TestCase(input={"s": " 2-1 + 2 "}, expected_output=3),
            TestCase(input={"s": "(1+(4+5+2)-3)+(6+8)"}, expected_output=23),
        ],
        tags=["stack", "parsing"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-017",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the longest valid parentheses substring.",
        function_signature="def longest_valid_parentheses(s: str) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"s": "(()"}, expected_output=2),
            TestCase(input={"s": ")()())"}, expected_output=4),
            TestCase(input={"s": ""}, expected_output=0),
        ],
        tags=["stack", "dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-018",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Given a matrix where each row and column is sorted, search for a target.",
        function_signature="def search_matrix(matrix: list, target: int) -> bool",
        constraints=["O(m + n) time"],
        test_cases=[
            TestCase(input={"matrix": [[1,4,7],[2,5,8],[3,6,9]], "target": 5}, expected_output=True),
            TestCase(input={"matrix": [[1,4,7],[2,5,8],[3,6,9]], "target": 10}, expected_output=False),
        ],
        tags=["matrix", "binary-search"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-019",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Count inversions in an array (pairs where i < j but arr[i] > arr[j]).",
        function_signature="def count_inversions(nums: list) -> int",
        constraints=["O(n log n) using merge sort"],
        test_cases=[
            TestCase(input={"nums": [2, 4, 1, 3, 5]}, expected_output=3),
            TestCase(input={"nums": [5, 4, 3, 2, 1]}, expected_output=10),
            TestCase(input={"nums": [1, 2, 3]}, expected_output=0),
        ],
        tags=["merge-sort", "divide-conquer"],
        source="classic",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-020",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the shortest path in a grid with obstacles (0=empty, 1=obstacle).",
        function_signature="def shortest_path(grid: list) -> int",
        constraints=["Return -1 if no path exists", "Start top-left, end bottom-right"],
        test_cases=[
            TestCase(input={"grid": [[0,0,0],[1,1,0],[0,0,0]]}, expected_output=4),
            TestCase(input={"grid": [[0,1],[1,0]]}, expected_output=-1),
        ],
        tags=["bfs", "matrix"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-021",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the kth smallest element in a sorted matrix.",
        function_signature="def kth_smallest_matrix(matrix: list, k: int) -> int",
        constraints=["Each row and column is sorted"],
        test_cases=[
            TestCase(input={"matrix": [[1,5,9],[10,11,13],[12,13,15]], "k": 8}, expected_output=13),
            TestCase(input={"matrix": [[1]], "k": 1}, expected_output=1),
        ],
        tags=["heap", "binary-search"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-022",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Decode ways: count ways to decode a digit string (1=A, 2=B, ..., 26=Z).",
        function_signature="def num_decodings(s: str) -> int",
        constraints=["Leading zeros invalid"],
        test_cases=[
            TestCase(input={"s": "12"}, expected_output=2),
            TestCase(input={"s": "226"}, expected_output=3),
            TestCase(input={"s": "06"}, expected_output=0),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-023",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the maximum sum of non-adjacent elements.",
        function_signature="def max_non_adjacent_sum(nums: list) -> int",
        constraints=[],
        test_cases=[
            TestCase(input={"nums": [2, 7, 9, 3, 1]}, expected_output=12),
            TestCase(input={"nums": [1, 2, 3, 1]}, expected_output=4),
            TestCase(input={"nums": []}, expected_output=0),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-024",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find minimum number of coins to make a given amount.",
        function_signature="def coin_change(coins: list, amount: int) -> int",
        constraints=["Return -1 if not possible"],
        test_cases=[
            TestCase(input={"coins": [1, 2, 5], "amount": 11}, expected_output=3),
            TestCase(input={"coins": [2], "amount": 3}, expected_output=-1),
            TestCase(input={"coins": [1], "amount": 0}, expected_output=0),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-025",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement wildcard pattern matching with '?' and '*'.",
        function_signature="def is_match_wildcard(s: str, p: str) -> bool",
        constraints=["'?' matches one char", "'*' matches any sequence"],
        test_cases=[
            TestCase(input={"s": "aa", "p": "a"}, expected_output=False),
            TestCase(input={"s": "aa", "p": "*"}, expected_output=True),
            TestCase(input={"s": "cb", "p": "?a"}, expected_output=False),
            TestCase(input={"s": "adceb", "p": "*a*b"}, expected_output=True),
        ],
        tags=["dynamic-programming", "greedy"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-026",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find longest consecutive sequence in unsorted array.",
        function_signature="def longest_consecutive(nums: list) -> int",
        constraints=["O(n) time"],
        test_cases=[
            TestCase(input={"nums": [100, 4, 200, 1, 3, 2]}, expected_output=4),
            TestCase(input={"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]}, expected_output=9),
        ],
        tags=["hash-set"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-027",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Given n pairs of parentheses, generate all valid combinations.",
        function_signature="def generate_parentheses(n: int) -> list",
        constraints=[],
        test_cases=[
            TestCase(input={"n": 3}, expected_output=["((()))","(()())","(())()","()(())","()()()"]),
            TestCase(input={"n": 1}, expected_output=["()"]),
        ],
        tags=["backtracking", "recursion"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-028",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the maximum product of a contiguous subarray.",
        function_signature="def max_product_subarray(nums: list) -> int",
        constraints=["Handle negative numbers"],
        test_cases=[
            TestCase(input={"nums": [2, 3, -2, 4]}, expected_output=6),
            TestCase(input={"nums": [-2, 0, -1]}, expected_output=0),
            TestCase(input={"nums": [-2, 3, -4]}, expected_output=24),
        ],
        tags=["dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-029",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Find the minimum path sum from top-left to bottom-right of a grid.",
        function_signature="def min_path_sum(grid: list) -> int",
        constraints=["Can only move right or down"],
        test_cases=[
            TestCase(input={"grid": [[1,3,1],[1,5,1],[4,2,1]]}, expected_output=7),
            TestCase(input={"grid": [[1,2,3],[4,5,6]]}, expected_output=12),
        ],
        tags=["dynamic-programming", "matrix"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    tasks.append(Task(
        task_id="HARD-030",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.HARD,
        description="Implement jump game: determine if you can reach the last index.",
        function_signature="def can_jump(nums: list) -> bool",
        constraints=["nums[i] is max jump length from position i"],
        test_cases=[
            TestCase(input={"nums": [2, 3, 1, 1, 4]}, expected_output=True),
            TestCase(input={"nums": [3, 2, 1, 0, 4]}, expected_output=False),
        ],
        tags=["greedy", "dynamic-programming"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return tasks


def main():
    """Add 50 more tasks to reach 100 total."""
    print("Adding 50 more tasks...")
    
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
    easy_tasks = create_additional_easy_tasks()
    medium_tasks = create_additional_medium_tasks()
    hard_tasks = create_additional_hard_tasks()
    
    all_new_tasks = easy_tasks + medium_tasks + hard_tasks
    
    print(f"\n  Created {len(all_new_tasks)} new tasks:")
    print(f"    Easy:   {len(easy_tasks)}")
    print(f"    Medium: {len(medium_tasks)}")
    print(f"    Hard:   {len(hard_tasks)}")
    
    # Save all tasks
    with open(tasks_file, 'w') as f:
        for task_data in existing_tasks:
            f.write(json.dumps(task_data) + '\n')
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
    print("TASK SUITE COMPLETE")
    print(f"{'='*50}")
    print(f"Total tasks: {total}")
    print(f"\nRun 'python scripts/run_pilot.py' to benchmark.")


if __name__ == "__main__":
    main()
