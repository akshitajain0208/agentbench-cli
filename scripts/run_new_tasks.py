"""Run benchmark on new task categories (BUGFIX, REFACTOR, TESTGEN)."""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
RESULTS_DIR = Path("results/pilot")

def get_new_tasks():
    """Get tasks that haven't been run yet."""
    new_tasks = []
    with open(TASKS_FILE) as f:
        for line in f:
            if line.strip():
                task = json.loads(line)
                task_id = task['task_id']
                if task_id.startswith(('BUGFIX-', 'REFACTOR-', 'TESTGEN-')):
                    new_tasks.append(task)
    return new_tasks

def check_existing_results(agent):
    """Check which tasks already have results."""
    agent_dir = RESULTS_DIR / agent
    if not agent_dir.exists():
        return set()
    return {f.stem for f in agent_dir.glob("*.json")}

def main():
    new_tasks = get_new_tasks()
    print(f"Found {len(new_tasks)} new tasks")
    
    # Show breakdown
    categories = {}
    for task in new_tasks:
        cat = task.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBreakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Check what's already done
    for agent in ['claude_code', 'codex_cli', 'gemini_cli']:
        existing = check_existing_results(agent)
        new_ids = {t['task_id'] for t in new_tasks}
        pending = new_ids - existing
        print(f"\n{agent}: {len(existing)} done, {len(pending)} pending")
    
    print("\n" + "="*60)
    print("To run benchmarks on new tasks, use:")
    print("  python scripts/benchmark_runner.py --tasks new")
    print("="*60)

if __name__ == "__main__":
    main()
