"""Create pilot benchmark tasks for testing the pipeline."""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.task_schema import Task, TaskCategory, Difficulty, TestCase, TaskSuite
from src.evaluation.prompt_schema import PromptGenerator


def create_codegen_tasks() -> TaskSuite:
    """Create pilot CodeGen tasks."""
    tasks = []
    
    # Task 1: Two Sum (Easy)
    tasks.append(Task(
        task_id="CODEGEN-001",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Write a function that takes a list of integers and a target sum, and returns the indices of two numbers that add up to the target.",
        function_signature="def two_sum(nums: list, target: int) -> list",
        constraints=[
            "Return a list of two indices",
            "Each input has exactly one solution",
            "You may not use the same element twice"
        ],
        test_cases=[
            TestCase(input={"nums": [2, 7, 11, 15], "target": 9}, expected_output=[0, 1]),
            TestCase(input={"nums": [3, 2, 4], "target": 6}, expected_output=[1, 2]),
            TestCase(input={"nums": [3, 3], "target": 6}, expected_output=[0, 1]),
        ],
        reference_solution='''def two_sum(nums: list, target: int) -> list:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []''',
        tags=["array", "hash-table", "easy"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # Task 2: Palindrome Check (Easy)
    tasks.append(Task(
        task_id="CODEGEN-002",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Write a function that checks if a given string is a palindrome, considering only alphanumeric characters and ignoring case.",
        function_signature="def is_palindrome(s: str) -> bool",
        constraints=[
            "Ignore non-alphanumeric characters",
            "Case-insensitive comparison"
        ],
        test_cases=[
            TestCase(input={"s": "A man, a plan, a canal: Panama"}, expected_output=True),
            TestCase(input={"s": "race a car"}, expected_output=False),
            TestCase(input={"s": ""}, expected_output=True),
            TestCase(input={"s": "a"}, expected_output=True),
        ],
        reference_solution='''def is_palindrome(s: str) -> bool:
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]''',
        tags=["string", "easy"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    # Task 3: FizzBuzz (Easy)
    tasks.append(Task(
        task_id="CODEGEN-003",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.EASY,
        description="Write a function that returns a list of strings from 1 to n. For multiples of 3 use 'Fizz', for multiples of 5 use 'Buzz', for multiples of both use 'FizzBuzz'.",
        function_signature="def fizzbuzz(n: int) -> list",
        constraints=[
            "Return list of strings",
            "Numbers not divisible by 3 or 5 should be string representation"
        ],
        test_cases=[
            TestCase(input={"n": 5}, expected_output=["1", "2", "Fizz", "4", "Buzz"]),
            TestCase(input={"n": 15}, expected_output=["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]),
            TestCase(input={"n": 1}, expected_output=["1"]),
        ],
        reference_solution='''def fizzbuzz(n: int) -> list:
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result''',
        tags=["basic", "loop", "easy"],
        source="classic",
        creation_date=datetime.now().isoformat(),
    ))
    
    # Task 4: Reverse Linked List (Medium)
    tasks.append(Task(
        task_id="CODEGEN-004",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Write a function that reverses a list in-place and returns it.",
        function_signature="def reverse_list(lst: list) -> list",
        constraints=[
            "Modify the list in-place",
            "Return the reversed list"
        ],
        test_cases=[
            TestCase(input={"lst": [1, 2, 3, 4, 5]}, expected_output=[5, 4, 3, 2, 1]),
            TestCase(input={"lst": [1, 2]}, expected_output=[2, 1]),
            TestCase(input={"lst": []}, expected_output=[]),
            TestCase(input={"lst": [1]}, expected_output=[1]),
        ],
        reference_solution='''def reverse_list(lst: list) -> list:
    left, right = 0, len(lst) - 1
    while left < right:
        lst[left], lst[right] = lst[right], lst[left]
        left += 1
        right -= 1
    return lst''',
        tags=["list", "two-pointer", "medium"],
        source="novel",
        creation_date=datetime.now().isoformat(),
    ))
    
    # Task 5: Valid Parentheses (Medium)
    tasks.append(Task(
        task_id="CODEGEN-005",
        category=TaskCategory.CODEGEN_CORE,
        difficulty=Difficulty.MEDIUM,
        description="Write a function that determines if a string of parentheses '()', '{}', '[]' is valid. A string is valid if brackets are closed in correct order.",
        function_signature="def is_valid(s: str) -> bool",
        constraints=[
            "Use a stack-based approach",
            "Empty string is valid"
        ],
        test_cases=[
            TestCase(input={"s": "()"}, expected_output=True),
            TestCase(input={"s": "()[]{}"}, expected_output=True),
            TestCase(input={"s": "(]"}, expected_output=False),
            TestCase(input={"s": "([)]"}, expected_output=False),
            TestCase(input={"s": "{[]}"}, expected_output=True),
            TestCase(input={"s": ""}, expected_output=True),
        ],
        reference_solution='''def is_valid(s: str) -> bool:
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)
    return len(stack) == 0''',
        tags=["stack", "string", "medium"],
        source="adapted-leetcode",
        creation_date=datetime.now().isoformat(),
    ))
    
    return TaskSuite(
        name="codegen-core-pilot",
        category=TaskCategory.CODEGEN_CORE,
        version="0.1.0",
        tasks=tasks,
        description="Pilot code generation tasks for pipeline testing"
    )


def main():
    """Create all pilot tasks and prompts."""
    print("Creating pilot tasks...")
    
    # Paths
    benchmark_dir = Path("benchmark/v0.1.0")
    prompts_dir = Path("prompts")
    
    # Create CodeGen tasks
    codegen_suite = create_codegen_tasks()
    tasks_file = benchmark_dir / "codegen-core" / "tasks.jsonl"
    codegen_suite.save(tasks_file)
    print(f"  Created {len(codegen_suite.tasks)} CodeGen tasks -> {tasks_file}")
    
    # Generate prompts for all tasks
    prompts_output = prompts_dir / "codegen-core"
    for task in codegen_suite.tasks:
        prompts = PromptGenerator.generate_prompts(task)
        PromptGenerator.save_prompts(prompts, prompts_output)
    print(f"  Generated prompts for {len(codegen_suite.tasks)} tasks -> {prompts_output}")
    
    print("\nPilot task creation complete!")
    print(f"\nTo verify, run:")
    print(f"  cat {tasks_file}")


if __name__ == "__main__":
    main()
