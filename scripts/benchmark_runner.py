"""
Benchmark Runner for AgentBench-CLI.
Runs agents on tasks and saves results.
"""

import json
import subprocess
import time
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
RESULTS_DIR = Path("results/pilot")

# Number of runs per task for stability measurement
NUM_RUNS = 3


def load_tasks(filter_type: str = "all") -> List[Dict]:
    """Load tasks based on filter."""
    tasks = []
    with open(TASKS_FILE) as f:
        for line in f:
            if line.strip():
                task = json.loads(line)
                task_id = task['task_id']
                
                if filter_type == "new":
                    if task_id.startswith(('BUGFIX-', 'REFACTOR-', 'TESTGEN-')):
                        tasks.append(task)
                elif filter_type == "all":
                    tasks.append(task)
                elif filter_type == "codegen":
                    if task_id.startswith(('EASY-', 'MED-', 'HARD-')):
                        tasks.append(task)
                else:
                    # Specific task ID
                    if task_id == filter_type:
                        tasks.append(task)
    
    return tasks


def get_existing_results(agent: str) -> set:
    """Get task IDs that already have results."""
    agent_dir = RESULTS_DIR / agent
    if not agent_dir.exists():
        return set()
    return {f.stem for f in agent_dir.glob("*.json")}


def build_prompt(task: Dict) -> str:
    """Build the prompt for the agent based on task category."""
    category = task.get('category', 'codegen')
    
    if category == 'bug_fixing':
        return f"""Fix the bug in the following code.

{task.get('description', '')}

Buggy code:
```python
{task.get('buggy_code', '')}
```

Function signature: {task.get('function_signature', '')}

Return ONLY the corrected Python function, no explanations."""

    elif category == 'refactoring':
        return f"""Refactor the following code to improve it.

{task.get('description', '')}

Original code:
```python
{task.get('original_code', '')}
```

Function signature: {task.get('function_signature', '')}

Return ONLY the refactored Python function, no explanations."""

    elif category == 'test_generation':
        return f"""Write a test function for the following code.

{task.get('description', '')}

Code to test:
```python
{task.get('code_to_test', '')}
```

Function signature: {task.get('function_signature', '')}

Return ONLY the test function that returns True if all tests pass, no explanations."""

    else:  # codegen
        return f"""{task.get('description', '')}

Function signature: {task.get('function_signature', '')}

Return ONLY the Python function, no explanations."""


def extract_code(output: str) -> str:
    """Extract Python code from agent output."""
    # Try to extract from code blocks
    patterns = [
        r'```python\n(.*?)```',
        r'```\n(.*?)```',
        r'def \w+\([^)]*\).*?(?=\n(?:def |class |$)|\Z)',
    ]
    
    for pattern in patterns[:2]:
        matches = re.findall(pattern, output, re.DOTALL)
        if matches:
            return matches[0].strip()
    
    # If no code blocks, try to find function definition
    match = re.search(r'(def \w+\([^)]*\):.*)', output, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return output.strip()


def run_test(code: str, task: Dict) -> Dict:
    """Run test cases against generated code."""
    test_cases = task.get('test_cases', [])
    func_name = task.get('function_signature', 'def func()').split('(')[0].replace('def ', '')
    
    passed = 0
    failed = 0
    errors = []
    
    for i, tc in enumerate(test_cases):
        try:
            # Create test environment
            local_env = {}
            exec(code, local_env)
            
            if func_name not in local_env:
                errors.append(f"Function {func_name} not found")
                failed += 1
                continue
            
            func = local_env[func_name]
            inputs = tc.get('input', {})
            expected = tc.get('expected_output')
            
            result = func(**inputs)
            
            if result == expected:
                passed += 1
            else:
                failed += 1
                errors.append(f"Test {i}: expected {expected}, got {result}")
                
        except Exception as e:
            failed += 1
            errors.append(f"Test {i}: {type(e).__name__}: {str(e)[:100]}")
    
    return {
        'passed': passed,
        'failed': failed,
        'total': len(test_cases),
        'errors': errors,
        'success': failed == 0 and passed > 0
    }


def run_claude_code(prompt: str) -> tuple:
    """Run Claude Code CLI and return (output, latency_ms)."""
    start = time.time()
    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--allowedTools', 'computer'],
            capture_output=True,
            text=True,
            timeout=120
        )
        latency = (time.time() - start) * 1000
        return result.stdout or result.stderr, latency
    except subprocess.TimeoutExpired:
        return "", 120000
    except Exception as e:
        return f"Error: {e}", 0


def run_codex_cli(prompt: str) -> tuple:
    """Run Codex CLI and return (output, latency_ms)."""
    start = time.time()
    try:
        result = subprocess.run(
            ['codex', 'exec', '--full-auto', '--skip-git-repo-check', prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        latency = (time.time() - start) * 1000
        return result.stdout or result.stderr, latency
    except subprocess.TimeoutExpired:
        return "", 120000
    except Exception as e:
        return f"Error: {e}", 0


def run_gemini_cli(prompt: str) -> tuple:
    """Run Gemini CLI and return (output, latency_ms)."""
    start = time.time()
    try:
        result = subprocess.run(
            ['gemini', '-p', prompt],
            capture_output=True,
            text=True,
            timeout=180
        )
        latency = (time.time() - start) * 1000
        return result.stdout or result.stderr, latency
    except subprocess.TimeoutExpired:
        return "", 180000
    except Exception as e:
        return f"Error: {e}", 0


def run_agent(agent: str, prompt: str) -> tuple:
    """Run the specified agent."""
    if agent == 'claude_code':
        return run_claude_code(prompt)
    elif agent == 'codex_cli':
        return run_codex_cli(prompt)
    elif agent == 'gemini_cli':
        return run_gemini_cli(prompt)
    else:
        raise ValueError(f"Unknown agent: {agent}")


def run_benchmark(agent: str, tasks: List[Dict], skip_existing: bool = True):
    """Run benchmark for an agent on given tasks."""
    agent_dir = RESULTS_DIR / agent
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    existing = get_existing_results(agent) if skip_existing else set()
    
    pending_tasks = [t for t in tasks if t['task_id'] not in existing]
    
    print(f"\n{'='*60}")
    print(f"Running {agent} on {len(pending_tasks)} tasks")
    print(f"{'='*60}")
    
    for i, task in enumerate(pending_tasks):
        task_id = task['task_id']
        print(f"\n[{i+1}/{len(pending_tasks)}] {task_id}...")
        
        prompt = build_prompt(task)
        runs = []
        latencies = []
        
        for run_num in range(NUM_RUNS):
            print(f"  Run {run_num + 1}/{NUM_RUNS}...", end=" ", flush=True)
            
            output, latency = run_agent(agent, prompt)
            code = extract_code(output)
            test_result = run_test(code, task)
            
            runs.append({
                'run': run_num + 1,
                'output': output[:2000],  # Truncate for storage
                'content': code,
                'passed': test_result['success'],
                'test_results': test_result,
                'latency_ms': latency
            })
            latencies.append(latency)
            
            status = "✓" if test_result['success'] else "✗"
            print(f"{status} ({latency:.0f}ms)")
        
        # Calculate metrics
        passing_runs = sum(1 for r in runs if r['passed'])
        
        result = {
            'task_id': task_id,
            'agent': agent,
            'category': task.get('category', 'codegen'),
            'difficulty': task.get('difficulty', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'runs': runs,
            'pass_at_k': {
                'pass_at_1': 1.0 if runs[0]['passed'] else 0.0,
                'passing_samples': passing_runs,
                'total_samples': NUM_RUNS
            },
            'latency': {
                'mean_ms': sum(latencies) / len(latencies),
                'median_ms': sorted(latencies)[len(latencies)//2],
                'min_ms': min(latencies),
                'max_ms': max(latencies)
            }
        }
        
        # Save result
        result_file = agent_dir / f"{task_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"  Result: {passing_runs}/{NUM_RUNS} passed, saved to {result_file}")


def main():
    parser = argparse.ArgumentParser(description='Run AgentBench-CLI benchmarks')
    parser.add_argument('--agent', choices=['claude_code', 'codex_cli', 'gemini_cli', 'all'],
                        default='all', help='Agent to benchmark')
    parser.add_argument('--tasks', default='new',
                        help='Tasks to run: "all", "new", "codegen", or specific task ID')
    parser.add_argument('--force', action='store_true',
                        help='Re-run even if results exist')
    
    args = parser.parse_args()
    
    # Load tasks
    tasks = load_tasks(args.tasks)
    print(f"Loaded {len(tasks)} tasks (filter: {args.tasks})")
    
    if not tasks:
        print("No tasks found!")
        return
    
    # Show task breakdown
    categories = {}
    for t in tasks:
        cat = t.get('category', 'codegen')
        categories[cat] = categories.get(cat, 0) + 1
    print("Categories:", dict(categories))
    
    # Run benchmarks
    agents = ['claude_code', 'codex_cli', 'gemini_cli'] if args.agent == 'all' else [args.agent]
    
    for agent in agents:
        run_benchmark(agent, tasks, skip_existing=not args.force)
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)
    print("\nRun analysis with:")
    print("  python scripts/comprehensive_analysis_v2.py")


if __name__ == "__main__":
    main()
