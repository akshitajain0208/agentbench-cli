"""Deep investigation of specific failing tasks."""

import json
from pathlib import Path

AGENTS = ['claude_code', 'codex_cli', 'gemini_cli']
AGENT_LABELS = {
    'claude_code': 'Claude Code',
    'codex_cli': 'Codex CLI',
    'gemini_cli': 'Gemini CLI',
}


def load_task(tasks_file: Path, task_id: str) -> dict:
    """Load specific task from tasks file."""
    with open(tasks_file) as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if data['task_id'] == task_id:
                    return data
    return None


def load_result(results_dir: Path, agent: str, task_id: str) -> dict:
    """Load result for specific agent and task."""
    result_file = results_dir / agent / f"{task_id}.json"
    if result_file.exists():
        with open(result_file) as f:
            return json.load(f)
    return None


def analyze_task(task: dict, results_dir: Path):
    """Analyze a single task in detail."""
    task_id = task['task_id']
    
    print("\n" + "=" * 80)
    print(f"TASK: {task_id}")
    print("=" * 80)
    
    # Task details
    print(f"\n## Task Description")
    print(f"   {task['description']}")
    print(f"\n## Function Signature")
    print(f"   {task['function_signature']}")
    print(f"\n## Difficulty: {task['difficulty']}")
    print(f"\n## Constraints:")
    for c in task.get('constraints', []):
        print(f"   - {c}")
    
    # Test cases
    print(f"\n## Test Cases ({len(task['test_cases'])} total):")
    for i, tc in enumerate(task['test_cases'][:3]):  # Show first 3
        print(f"\n   Test {i+1}:")
        print(f"   Input: {tc['input']}")
        print(f"   Expected: {tc['expected_output']}")
    
    # Reference solution if available
    if task.get('reference_solution'):
        print(f"\n## Reference Solution:")
        print("   " + task['reference_solution'][:300].replace('\n', '\n   '))
    
    # Agent results
    print(f"\n## Agent Results:")
    print("-" * 80)
    
    for agent in AGENTS:
        result = load_result(results_dir, agent, task_id)
        
        print(f"\n### {AGENT_LABELS[agent]}")
        
        if not result:
            print("   ❌ No result found")
            continue
        
        pass_at_k = result.get('pass_at_k', {})
        pass_rate = pass_at_k.get('pass_at_1', 0)
        
        print(f"   Pass@1: {pass_rate * 100:.0f}%")
        print(f"   Passing: {pass_at_k.get('passing_samples', 0)}/{pass_at_k.get('total_samples', 0)}")
        
        # Show generated code for each run
        runs = result.get('runs', [])
        
        for i, run in enumerate(runs[:3]):
            content = run.get('content', '')
            success = pass_at_k.get('passing_samples', 0) > i if pass_rate > 0 else False
            
            print(f"\n   --- Run {i+1} {'✓' if success else '✗'} ---")
            
            if content:
                # Extract just the function
                lines = content.strip().split('\n')
                code_preview = '\n'.join(lines[:15])
                print(f"   {code_preview.replace(chr(10), chr(10) + '   ')}")
                if len(lines) > 15:
                    print(f"   ... ({len(lines) - 15} more lines)")
            else:
                print("   (empty output)")
        
        # Show errors
        errors = pass_at_k.get('errors', [])
        if errors:
            print(f"\n   --- Errors ---")
            for j, err in enumerate(errors[:2]):
                # Extract the key part of the error
                if 'got' in err.lower() and 'expected' in err.lower():
                    # Find the assertion error details
                    lines = err.split('\n')
                    for line in lines:
                        if 'got' in line.lower() or 'expected' in line.lower() or 'assert' in line.lower():
                            print(f"   Error {j+1}: {line.strip()[:100]}")
                            break
                else:
                    print(f"   Error {j+1}: {err[:150].replace(chr(10), ' ')}")


def compare_outputs(task: dict, results_dir: Path):
    """Compare actual outputs across agents."""
    task_id = task['task_id']
    
    print(f"\n\n## Output Comparison for {task_id}")
    print("-" * 80)
    
    # Get first test case
    if not task['test_cases']:
        print("No test cases found")
        return
    
    test_input = task['test_cases'][0]['input']
    expected = task['test_cases'][0]['expected_output']
    
    print(f"\nTest Input: {test_input}")
    print(f"Expected Output: {expected}")
    print(f"\nActual Outputs:")
    
    for agent in AGENTS:
        result = load_result(results_dir, agent, task_id)
        if not result:
            print(f"\n  {AGENT_LABELS[agent]}: No result")
            continue
        
        print(f"\n  {AGENT_LABELS[agent]}:")
        
        # Try to execute the code and get actual output
        runs = result.get('runs', [])
        for i, run in enumerate(runs[:1]):  # Just first run
            content = run.get('content', '')
            if content:
                # Extract function name
                func_name = task['function_signature'].split('(')[0].replace('def ', '').strip()
                
                print(f"    Run {i+1}:")
                # Show what the code looks like
                lines = content.strip().split('\n')[:5]
                for line in lines:
                    print(f"      {line}")


def suggest_fixes(task: dict, results_dir: Path):
    """Suggest fixes for the failing task."""
    task_id = task['task_id']
    
    print(f"\n\n## Suggested Fixes for {task_id}")
    print("-" * 80)
    
    issues = []
    
    # Check test case format
    for i, tc in enumerate(task['test_cases']):
        expected = tc['expected_output']
        
        # Check for list vs tuple issues
        if isinstance(expected, list) and any(isinstance(x, list) for x in expected):
            issues.append(f"Test {i+1}: Nested lists - agents may return tuples")
        
        # Check for order sensitivity
        if isinstance(expected, list) and len(expected) > 1:
            issues.append(f"Test {i+1}: List output - order may vary")
    
    # Check constraints clarity
    constraints = task.get('constraints', [])
    if not any('order' in c.lower() for c in constraints):
        if isinstance(task['test_cases'][0]['expected_output'], list):
            issues.append("Missing constraint: Output order not specified")
    
    if issues:
        print("\nPotential Issues Found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
        
        print("\nRecommended Fixes:")
        print("  1. Add order-insensitive comparison in evaluator")
        print("  2. Clarify output format in constraints")
        print("  3. Normalize outputs before comparison (sort, convert types)")
    else:
        print("\nNo obvious issues found - may be algorithmic difficulty")


def main():
    results_dir = Path("results/pilot")
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    # Tasks to investigate
    failing_tasks = ['HARD-009', 'HARD-012']
    
    print("=" * 80)
    print("DEEP INVESTIGATION OF FAILING TASKS")
    print("=" * 80)
    
    for task_id in failing_tasks:
        task = load_task(tasks_file, task_id)
        
        if task:
            analyze_task(task, results_dir)
            compare_outputs(task, results_dir)
            suggest_fixes(task, results_dir)
        else:
            print(f"\n❌ Task {task_id} not found")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)
    
    print("""
## Findings:

### HARD-009 (Palindrome Pairs)
- Complex algorithmic task
- Output order matters but shouldn't
- Multiple valid orderings possible
- FIX: Use order-insensitive comparison

### HARD-012 (Number of Islands)
- Grid traversal problem
- May have edge case handling issues
- Check for grid mutation during DFS
- FIX: Review test cases for edge cases

## Recommended Actions:

1. Update evaluator to handle:
   - Order-insensitive list comparison
   - Tuple vs list normalization
   
2. Update test cases to:
   - Clarify output format requirements
   - Add sorting constraints if order matters

3. Consider marking these as "known difficult" in paper:
   - Note that all agents struggle with these
   - Discuss why (algorithmic complexity, output format ambiguity)
""")


if __name__ == "__main__":
    main()
