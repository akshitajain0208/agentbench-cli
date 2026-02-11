"""Fix remaining test case and evaluator issues."""

import json
from pathlib import Path


def fix_hard012_test_case():
    """Fix HARD-012 to accept both string and integer representations."""
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    tasks = []
    fixed = False
    
    with open(tasks_file, 'r') as f:
        for line in f:
            if line.strip():
                task = json.loads(line)
                
                if task['task_id'] == 'HARD-012':
                    # Update description to clarify data type
                    task['description'] = "Find the number of islands in a 2D grid. Grid contains '1' (land) and '0' (water) as strings."
                    
                    # Update constraints
                    task['constraints'] = [
                        "Grid edges are water",
                        "Grid cells are strings: '1' for land, '0' for water"
                    ]
                    
                    fixed = True
                    print(f"Fixed HARD-012: Clarified that grid uses strings")
                
                tasks.append(task)
    
    with open(tasks_file, 'w') as f:
        for task in tasks:
            f.write(json.dumps(task) + '\n')
    
    return fixed


def create_flexible_evaluator():
    """Create a more flexible comparison function."""
    
    code = '''
"""Flexible output comparison for benchmark evaluation."""

def normalize_value(val):
    """Normalize a value for comparison."""
    if isinstance(val, tuple):
        return list(normalize_value(x) for x in val)
    elif isinstance(val, list):
        return [normalize_value(x) for x in val]
    elif isinstance(val, set):
        return sorted([normalize_value(x) for x in val], key=str)
    return val


def compare_outputs(result, expected, order_sensitive=True):
    """
    Flexibly compare outputs.
    
    Args:
        result: Actual output from code
        expected: Expected output from test case
        order_sensitive: If False, sort lists before comparison
    
    Returns:
        True if outputs match
    """
    # Normalize both
    result = normalize_value(result)
    expected = normalize_value(expected)
    
    # Direct equality
    if result == expected:
        return True
    
    # Order-insensitive comparison for lists
    if not order_sensitive:
        if isinstance(result, list) and isinstance(expected, list):
            try:
                # Sort by string representation
                result_sorted = sorted(result, key=lambda x: str(x))
                expected_sorted = sorted(expected, key=lambda x: str(x))
                if result_sorted == expected_sorted:
                    return True
            except:
                pass
    
    return False


# Tasks that need order-insensitive comparison
ORDER_INSENSITIVE_TASKS = {
    'HARD-009',  # palindrome pairs
    'MED-010',   # permutations  
    'MED-027',   # subsets
}
'''
    
    output_file = Path("src/evaluation/flexible_compare.py")
    with open(output_file, 'w') as f:
        f.write(code)
    
    print(f"Created: {output_file}")


def generate_fix_summary():
    """Generate summary of fixes for paper."""
    
    summary = """
================================================================================
TEST CASE ISSUE SUMMARY (For Paper Methodology Section)
================================================================================

## Issues Identified:

### 1. HARD-009 (Palindrome Pairs)
   - **Problem**: Order-sensitive comparison for unordered output
   - **Impact**: Valid solutions rejected due to different ordering
   - **Fix**: Use set-based or sorted comparison
   - **Learning**: Specify output ordering in task description

### 2. HARD-012 (Number of Islands)
   - **Problem**: Type ambiguity (string '1' vs integer 1)
   - **Impact**: Some agents check for wrong type
   - **Fix**: Clarify in task description that grid uses strings
   - **Learning**: Be explicit about data types in function signature

## Implications for Benchmark Design:

1. **Type Clarity**: Always specify exact input/output types
2. **Order Sensitivity**: Explicitly state if output order matters
3. **Edge Cases**: Test with edge cases during task creation
4. **Flexible Evaluation**: Use type/order normalization when appropriate

## Paper Discussion Points:

- These issues highlight the importance of precise task specifications
- Even well-designed benchmarks can have subtle evaluation issues
- Agents may produce functionally correct but syntactically different outputs
- Recommend using flexible evaluators that handle:
  - Tuple vs list equivalence
  - Order-insensitive list comparison
  - Floating point tolerance
"""
    
    print(summary)
    
    # Save to file
    with open("results/fix_summary.md", 'w') as f:
        f.write(summary)
    
    print("\nSaved to: results/fix_summary.md")


def main():
    print("=" * 70)
    print("FIXING REMAINING ISSUES")
    print("=" * 70)
    
    print("\n1. Fixing HARD-012 test case...")
    fix_hard012_test_case()
    
    print("\n2. Creating flexible evaluator...")
    create_flexible_evaluator()
    
    print("\n3. Generating fix summary...")
    generate_fix_summary()
    
    print("\n" + "=" * 70)
    print("✅ FIXES COMPLETE")
    print("=" * 70)
    
    print("""
## Next Steps:

1. When Codex rate limit resets:
   - Re-run: python scripts/run_pilot.py
   
2. Update Pass@k evaluator to use flexible comparison:
   - Import from src/evaluation/flexible_compare.py
   
3. In your paper, discuss:
   - Importance of precise task specifications
   - Evaluation methodology considerations
   - How different agents handle type ambiguity
""")


if __name__ == "__main__":
    main()
