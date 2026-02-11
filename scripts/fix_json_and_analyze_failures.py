"""Fix JSON serialization and analyze remaining failures."""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict


def load_results(results_dir: Path) -> dict:
    """Load all results."""
    results = {}
    for agent_dir in results_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
            agent_name = agent_dir.name
            results[agent_name] = {}
            for result_file in agent_dir.glob("*.json"):
                task_id = result_file.stem
                with open(result_file) as f:
                    results[agent_name][task_id] = json.load(f)
    return results


def analyze_failures(results: dict) -> dict:
    """Detailed analysis of all failures."""
    failures = defaultdict(list)
    
    for agent, tasks in results.items():
        for task_id, data in tasks.items():
            if data.get("pass_at_k") and data["pass_at_k"]["pass_at_1"] < 1.0:
                failures[task_id].append({
                    "agent": agent,
                    "pass_at_1": data["pass_at_k"]["pass_at_1"],
                    "pass_at_5": data["pass_at_k"].get("pass_at_5", 0),
                    "errors": data["pass_at_k"].get("errors", []),
                })
    
    return dict(failures)


def load_task_info(tasks_file: Path) -> dict:
    """Load task metadata."""
    tasks = {}
    with open(tasks_file, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                tasks[data['task_id']] = {
                    "description": data['description'],
                    "difficulty": data['difficulty'],
                    "function_signature": data['function_signature'],
                    "constraints": data.get('constraints', []),
                }
    return tasks


def main():
    results_dir = Path("results/pilot")
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    print("Loading results...")
    results = load_results(results_dir)
    task_info = load_task_info(tasks_file)
    
    print("Analyzing failures...")
    failures = analyze_failures(results)
    
    # Categorize failures
    all_fail = {}  # Failed by all agents
    some_fail = {}  # Failed by some agents
    
    for task_id, agents_failed in failures.items():
        agent_names = [f["agent"] for f in agents_failed]
        if len(agent_names) >= 3:
            all_fail[task_id] = agents_failed
        else:
            some_fail[task_id] = agents_failed
    
    # Print report
    print("\n" + "=" * 70)
    print("FAILURE ANALYSIS REPORT")
    print("=" * 70)
    
    total_failures = sum(len(v) for v in failures.values())
    print(f"\nTotal failures: {total_failures}")
    print(f"Tasks failed by all 3 agents: {len(all_fail)}")
    print(f"Tasks failed by 1-2 agents: {len(some_fail)}")
    
    # Tasks failed by all agents
    if all_fail:
        print("\n\n## Tasks Failed by ALL Agents (Likely Test Case Issues)")
        print("-" * 70)
        
        for task_id, agents in sorted(all_fail.items()):
            info = task_info.get(task_id, {})
            print(f"\n### {task_id} ({info.get('difficulty', 'unknown')})")
            print(f"Description: {info.get('description', 'N/A')[:80]}...")
            print(f"Signature: {info.get('function_signature', 'N/A')}")
            print(f"Constraints: {info.get('constraints', [])}")
            print("\nAgent Results:")
            for a in agents:
                print(f"  - {a['agent']}: {a['pass_at_1']*100:.0f}% Pass@1")
                if a['errors']:
                    error_preview = a['errors'][0][:200].replace('\n', ' ')
                    print(f"    Error: {error_preview}...")
    
    # Tasks failed by some agents
    if some_fail:
        print("\n\n## Tasks Failed by SOME Agents (Agent-Specific Issues)")
        print("-" * 70)
        
        for task_id, agents in sorted(some_fail.items()):
            info = task_info.get(task_id, {})
            failed_agents = [a['agent'] for a in agents]
            
            # Find which agents passed
            all_agents = {"claude_code", "codex_cli", "gemini_cli"}
            passed_agents = all_agents - set(failed_agents)
            
            print(f"\n### {task_id} ({info.get('difficulty', 'unknown')})")
            print(f"Description: {info.get('description', 'N/A')[:80]}...")
            print(f"Passed: {', '.join(passed_agents) if passed_agents else 'None'}")
            print(f"Failed:")
            for a in agents:
                print(f"  - {a['agent']}: {a['pass_at_1']*100:.0f}% Pass@1")
    
    # Summary by agent
    print("\n\n## Failure Summary by Agent")
    print("-" * 70)
    
    agent_failures = defaultdict(list)
    for task_id, agents in failures.items():
        for a in agents:
            agent_failures[a['agent']].append(task_id)
    
    for agent in ["claude_code", "codex_cli", "gemini_cli"]:
        failed = agent_failures.get(agent, [])
        n_tasks = len(results.get(agent, {}))
        print(f"\n{agent}:")
        print(f"  Failed: {len(failed)}/{n_tasks} tasks")
        if failed:
            print(f"  Tasks: {', '.join(sorted(failed))}")
    
    # Save analysis
    output = {
        "summary": {
            "total_failures": total_failures,
            "tasks_failed_by_all": len(all_fail),
            "tasks_failed_by_some": len(some_fail),
        },
        "all_agents_failed": {
            task_id: [
                {"agent": a["agent"], "pass_at_1": float(a["pass_at_1"])}
                for a in agents
            ]
            for task_id, agents in all_fail.items()
        },
        "some_agents_failed": {
            task_id: [
                {"agent": a["agent"], "pass_at_1": float(a["pass_at_1"])}
                for a in agents
            ]
            for task_id, agents in some_fail.items()
        },
        "by_agent": {
            agent: sorted(tasks) 
            for agent, tasks in agent_failures.items()
        },
    }
    
    output_file = results_dir / "failure_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n\nAnalysis saved to: {output_file}")
    
    # Recommendations
    print("\n\n## Recommendations")
    print("-" * 70)
    
    if all_fail:
        print("\n### Test Cases to Review (failed by all agents):")
        for task_id in sorted(all_fail.keys()):
            print(f"  - {task_id}")
    
    if some_fail:
        print("\n### Agent-Specific Weaknesses:")
        for agent in ["claude_code", "codex_cli", "gemini_cli"]:
            unique_fails = [
                t for t, agents in some_fail.items()
                if agent in [a['agent'] for a in agents]
            ]
            if unique_fails:
                print(f"  {agent}: Struggles with {', '.join(unique_fails)}")


if __name__ == "__main__":
    main()
