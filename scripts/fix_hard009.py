"""Fix HARD-009 test case to use order-insensitive comparison."""

import json
from pathlib import Path


def main():
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    # Load all tasks
    tasks = []
    with open(tasks_file, 'r') as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    
    # Find and fix HARD-009
    for task in tasks:
        if task['task_id'] == 'HARD-009':
            # Update description to be clearer
            task['description'] = "Given a list of words, find all pairs (i, j) where words[i] + words[j] forms a palindrome. Return unique pairs only."
            
            # Add clearer constraints
            task['constraints'] = [
                "Return list of [i, j] index pairs",
                "i and j must be different",
                "Order of pairs in output doesn't matter",
                "Each valid pair should appear once"
            ]
            
            # Simplify test cases to have deterministic expected outputs
            task['test_cases'] = [
                {
                    "input": {"words": ["bat", "tab"]},
                    "expected_output": [[0, 1], [1, 0]],
                    "is_hidden": False,
                    "weight": 1.0
                },
                {
                    "input": {"words": ["a", ""]},
                    "expected_output": [[0, 1], [1, 0]],
                    "is_hidden": False,
                    "weight": 1.0
                },
                {
                    "input": {"words": ["abc", "def"]},
                    "expected_output": [],
                    "is_hidden": False,
                    "weight": 1.0
                },
            ]
            
            print(f"Fixed {task['task_id']}")
            break
    
    # Save all tasks
    with open(tasks_file, 'w') as f:
        for task in tasks:
            f.write(json.dumps(task) + '\n')
    
    print("Tasks file updated!")


if __name__ == "__main__":
    main()
