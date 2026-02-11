"""Fix problematic test cases identified from failure analysis."""

import json
from pathlib import Path
from datetime import datetime


def fix_test_cases():
    """Fix known problematic test cases."""
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    # Load all tasks
    tasks = []
    with open(tasks_file, 'r') as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    
    fixes_applied = []
    
    for task in tasks:
        task_id = task['task_id']
        
        # FIX 1: MED-004 - Change expected output from lists to tuples format
        # Actually, we need to change constraint to say "lists" not "tuples"
        if task_id == "MED-004":
            task['constraints'] = [
                "Return list of lists [a, b] where a < b",
                "No duplicate pairs"
            ]
            fixes_applied.append(f"{task_id}: Changed constraint from tuples to lists")
        
        # FIX 2: HARD-009 - Add note about order and uniqueness
        if task_id == "HARD-009":
            task['constraints'] = [
                "Return list of [i, j] pairs",
                "No duplicate pairs",
                "Order of pairs in result doesn't matter"
            ]
            # The test case comparison needs to be order-insensitive
            # We'll note this for the evaluator
            fixes_applied.append(f"{task_id}: Added order-insensitive constraint")
        
        # FIX 3: HARD-011 - Clarify edge case
        if task_id == "HARD-011":
            task['constraints'] = [
                "Sliding window O(n)",
                "Return -1 if k > len(nums)"
            ]
            fixes_applied.append(f"{task_id}: Clarified edge case for k > len(nums)")
        
        # FIX 4: HARD-002 - Make serialization format clearer
        if task_id == "HARD-002":
            task['description'] = "Implement a function to serialize a binary tree represented as nested lists [val, left, right] into a comma-separated string using preorder traversal. Use 'null' for empty nodes."
            fixes_applied.append(f"{task_id}: Clarified serialization format")
        
        # FIX 5: EASY-015 - Intersection should return sorted list
        if task_id == "EASY-015":
            task['constraints'] = [
                "Return unique elements only",
                "Return sorted list"
            ]
            # Fix expected outputs to be sorted
            for tc in task['test_cases']:
                if isinstance(tc['expected_output'], list):
                    tc['expected_output'] = sorted(tc['expected_output'])
            fixes_applied.append(f"{task_id}: Added sorted constraint")
    
    # Save fixed tasks
    with open(tasks_file, 'w') as f:
        for task in tasks:
            f.write(json.dumps(task) + '\n')
    
    print(f"Fixed {len(fixes_applied)} test cases:")
    for fix in fixes_applied:
        print(f"  - {fix}")
    
    return fixes_applied


def create_flexible_evaluator():
    """Create a more flexible test comparison that handles order-insensitive cases."""
    
    code = '''
def flexible_compare(result, expected, task_id: str) -> bool:
    """Flexibly compare results handling known edge cases."""
    
    # Direct match
    if result == expected:
        return True
    
    # Handle list of tuples vs list of lists
    if isinstance(result, list) and isinstance(expected, list):
        # Convert tuples to lists for comparison
        def normalize(x):
            if isinstance(x, tuple):
                return list(x)
            elif isinstance(x, list):
                return [normalize(i) for i in x]
            return x
        
        result_norm = normalize(result)
        expected_norm = normalize(expected)
        
        if result_norm == expected_norm:
            return True
        
        # Try sorted comparison for order-insensitive cases
        try:
            if sorted(map(str, result_norm)) == sorted(map(str, expected_norm)):
                return True
        except:
            pass
    
    return False
'''
    print("\nNote: Consider adding flexible comparison to pass_at_k.py")
    print("This would handle tuple/list mismatches and order-insensitive comparisons.")


if __name__ == "__main__":
    fixes = fix_test_cases()
    print(f"\n✅ Applied {len(fixes)} fixes")
    print("\nNext steps:")
    print("1. Regenerate prompts: python scripts/create_pilot_tasks.py")
    print("2. Re-run benchmark: python scripts/run_pilot.py")
    print("3. Or update evaluator to be more flexible")
