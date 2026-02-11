"""Comprehensive analysis of benchmark results."""

import json
from pathlib import Path
from collections import defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_results(results_dir: Path) -> dict:
    """Load all results organized by agent and task."""
    results = defaultdict(dict)
    
    for agent_dir in results_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
            agent_name = agent_dir.name
            for result_file in agent_dir.glob("*.json"):
                task_id = result_file.stem
                with open(result_file) as f:
                    results[agent_name][task_id] = json.load(f)
    
    return dict(results)


def load_task_difficulties(tasks_file: Path) -> dict:
    """Load task difficulty mapping from tasks file."""
    difficulty_map = {}
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            for line in f:
                if line.strip():
                    task = json.loads(line)
                    difficulty_map[task['task_id']] = task['difficulty']
    return difficulty_map


def analyze_by_difficulty(results: dict, difficulty_map: dict) -> dict:
    """Analyze pass rates by task difficulty."""
    stats = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "total": 0, "tasks": []}))
    
    for agent, tasks in results.items():
        for task_id, data in tasks.items():
            difficulty = difficulty_map.get(task_id, "unknown")
            if data.get("pass_at_k"):
                stats[agent][difficulty]["total"] += 1
                passed = data["pass_at_k"]["pass_at_1"] == 1.0
                if passed:
                    stats[agent][difficulty]["pass"] += 1
                else:
                    stats[agent][difficulty]["tasks"].append(task_id)
    
    return dict(stats)


def analyze_failures(results: dict) -> list:
    """Find all failure cases with details."""
    failures = []
    
    for agent, tasks in results.items():
        for task_id, data in tasks.items():
            if data.get("pass_at_k") and data["pass_at_k"]["pass_at_1"] < 1.0:
                failures.append({
                    "agent": agent,
                    "task_id": task_id,
                    "pass_at_1": data["pass_at_k"]["pass_at_1"],
                    "pass_at_5": data["pass_at_k"].get("pass_at_5", 0),
                    "errors": data["pass_at_k"].get("errors", [])[:2],
                })
    
    return failures


def analyze_common_failures(results: dict) -> dict:
    """Find tasks that multiple agents fail."""
    task_failures = defaultdict(list)
    
    for agent, tasks in results.items():
        for task_id, data in tasks.items():
            if data.get("pass_at_k") and data["pass_at_k"]["pass_at_1"] < 1.0:
                task_failures[task_id].append({
                    "agent": agent,
                    "pass_at_1": data["pass_at_k"]["pass_at_1"]
                })
    
    # Filter to tasks failed by 2+ agents
    common = {k: v for k, v in task_failures.items() if len(v) >= 2}
    return common


def compute_aggregate_stats(results: dict) -> dict:
    """Compute aggregate statistics per agent."""
    stats = {}
    
    for agent, tasks in results.items():
        latencies = []
        pass_rates = []
        stabilities = []
        pass_at_5_rates = []
        
        for task_id, data in tasks.items():
            if data.get("latency"):
                latencies.append(data["latency"]["median_ms"])
            if data.get("pass_at_k"):
                pass_rates.append(data["pass_at_k"]["pass_at_1"])
                pass_at_5_rates.append(data["pass_at_k"].get("pass_at_5", 0))
            if data.get("determinism"):
                stabilities.append(data["determinism"]["stability_score"])
        
        stats[agent] = {
            "tasks": len(tasks),
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "avg_pass_at_1": sum(pass_rates) / len(pass_rates) if pass_rates else 0,
            "avg_pass_at_5": sum(pass_at_5_rates) / len(pass_at_5_rates) if pass_at_5_rates else 0,
            "avg_stability": sum(stabilities) / len(stabilities) if stabilities else 0,
            "perfect_pass_tasks": sum(1 for p in pass_rates if p == 1.0),
            "failed_tasks": sum(1 for p in pass_rates if p < 1.0),
            "perfect_stability_tasks": sum(1 for s in stabilities if s == 1.0),
        }
    
    return stats


def print_latex_tables(stats: dict, by_difficulty: dict):
    """Print LaTeX-formatted tables for paper."""
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    agent_names = ["Claude Code", "Codex CLI", "Gemini CLI"]
    
    print("\n" + "=" * 60)
    print("LaTeX TABLES FOR PAPER")
    print("=" * 60)
    
    # Main comparison table
    print("""
\\begin{table}[h]
\\centering
\\caption{Overall Performance Comparison of Console-Based AI Coding Agents (n=100 tasks)}
\\label{tab:overall}
\\begin{tabular}{lccc}
\\hline
\\textbf{Metric} & \\textbf{Claude Code} & \\textbf{Codex CLI} & \\textbf{Gemini CLI} \\\\
\\hline""")
    
    # Pass@1
    row = "Pass@1 (\\%)"
    for agent in agents:
        val = stats.get(agent, {}).get("avg_pass_at_1", 0) * 100
        row += f" & {val:.1f}"
    print(row + " \\\\")
    
    # Pass@5
    row = "Pass@5 (\\%)"
    for agent in agents:
        val = stats.get(agent, {}).get("avg_pass_at_5", 0) * 100
        row += f" & {val:.1f}"
    print(row + " \\\\")
    
    # Latency
    row = "Median Latency (ms)"
    for agent in agents:
        val = stats.get(agent, {}).get("avg_latency_ms", 0)
        row += f" & {val:,.0f}"
    print(row + " \\\\")
    
    # Stability
    row = "Stability (\\%)"
    for agent in agents:
        val = stats.get(agent, {}).get("avg_stability", 0) * 100
        row += f" & {val:.1f}"
    print(row + " \\\\")
    
    # Failed tasks
    row = "Failed Tasks"
    for agent in agents:
        val = stats.get(agent, {}).get("failed_tasks", 0)
        row += f" & {val}"
    print(row + " \\\\")
    
    print("""\\hline
\\end{tabular}
\\end{table}""")
    
    # Difficulty breakdown table
    print("""
\\begin{table}[h]
\\centering
\\caption{Pass@1 Rate by Task Difficulty}
\\label{tab:difficulty}
\\begin{tabular}{lccc}
\\hline
\\textbf{Difficulty} & \\textbf{Claude Code} & \\textbf{Codex CLI} & \\textbf{Gemini CLI} \\\\
\\hline""")
    
    for diff in ["easy", "medium", "hard"]:
        row = diff.capitalize()
        for agent in agents:
            d = by_difficulty.get(agent, {}).get(diff, {"pass": 0, "total": 0})
            if d["total"] > 0:
                rate = d["pass"] / d["total"] * 100
                row += f" & {rate:.1f}\\% ({d['pass']}/{d['total']})"
            else:
                row += " & N/A"
        print(row + " \\\\")
    
    print("""\\hline
\\end{tabular}
\\end{table}""")


def print_markdown_summary(stats: dict, by_difficulty: dict, failures: list, common_failures: dict):
    """Print comprehensive markdown summary."""
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS ANALYSIS")
    print("=" * 60)
    
    # Overall Stats
    print("\n## Overall Performance (100 Tasks)")
    print("| Agent | Pass@1 | Pass@5 | Latency | Stability | Failed |")
    print("|-------|--------|--------|---------|-----------|--------|")
    
    for agent in ["claude_code", "codex_cli", "gemini_cli"]:
        s = stats.get(agent, {})
        print(f"| {agent} | "
              f"{s.get('avg_pass_at_1', 0)*100:.1f}% | "
              f"{s.get('avg_pass_at_5', 0)*100:.1f}% | "
              f"{s.get('avg_latency_ms', 0):,.0f}ms | "
              f"{s.get('avg_stability', 0)*100:.1f}% | "
              f"{s.get('failed_tasks', 0)} |")
    
    # By Difficulty
    print("\n## Pass@1 by Difficulty")
    print("| Difficulty | Tasks | Claude Code | Codex CLI | Gemini CLI |")
    print("|------------|-------|-------------|-----------|------------|")
    
    for diff in ["easy", "medium", "hard"]:
        # Get total count for this difficulty
        total_count = 0
        for agent in ["claude_code"]:
            d = by_difficulty.get(agent, {}).get(diff, {"total": 0})
            total_count = d["total"]
            break
        
        row = f"| {diff.capitalize()} | {total_count} |"
        for agent in ["claude_code", "codex_cli", "gemini_cli"]:
            d = by_difficulty.get(agent, {}).get(diff, {"pass": 0, "total": 0})
            if d["total"] > 0:
                rate = d["pass"] / d["total"] * 100
                row += f" {rate:.1f}% ({d['pass']}/{d['total']}) |"
            else:
                row += " N/A |"
        print(row)
    
    # Common Failures
    if common_failures:
        print("\n## Tasks Failed by Multiple Agents")
        print("| Task | Agents Failed | Details |")
        print("|------|---------------|---------|")
        for task_id, agents in sorted(common_failures.items()):
            agent_str = ", ".join([f"{a['agent']}({a['pass_at_1']*100:.0f}%)" for a in agents])
            print(f"| {task_id} | {len(agents)} | {agent_str} |")
    
    # Unique Failures
    print("\n## Unique Failures (Only One Agent Failed)")
    all_failed = set()
    for f in failures:
        all_failed.add((f['agent'], f['task_id']))
    
    common_task_ids = set(common_failures.keys())
    
    for agent in ["claude_code", "codex_cli", "gemini_cli"]:
        unique = [f for f in failures if f['agent'] == agent and f['task_id'] not in common_task_ids]
        if unique:
            print(f"\n**{agent}** unique failures:")
            for f in unique:
                print(f"  - {f['task_id']}: {f['pass_at_1']*100:.0f}% Pass@1")
    
    # Key Findings
    print("\n## Key Statistical Findings")
    
    sorted_by_acc = sorted(stats.items(), key=lambda x: x[1].get("avg_pass_at_1", 0), reverse=True)
    sorted_by_speed = sorted(stats.items(), key=lambda x: x[1].get("avg_latency_ms", float('inf')))
    sorted_by_det = sorted(stats.items(), key=lambda x: x[1].get("avg_stability", 0), reverse=True)
    
    print(f"1. **Most Accurate**: {sorted_by_acc[0][0]} ({sorted_by_acc[0][1]['avg_pass_at_1']*100:.1f}% Pass@1)")
    print(f"2. **Fastest**: {sorted_by_speed[0][0]} ({sorted_by_speed[0][1]['avg_latency_ms']:,.0f}ms)")
    print(f"3. **Most Deterministic**: {sorted_by_det[0][0]} ({sorted_by_det[0][1]['avg_stability']*100:.1f}% stability)")
    
    # Speed comparison
    fastest = sorted_by_speed[0][1]['avg_latency_ms']
    for agent, s in sorted_by_speed[1:]:
        ratio = s['avg_latency_ms'] / fastest
        print(f"4. **Speed Ratio**: {agent} is {ratio:.1f}x slower than {sorted_by_speed[0][0]}")


def main():
    """Main analysis routine."""
    results_dir = Path("results/pilot")
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    if not results_dir.exists():
        print("No results found. Run benchmark first.")
        return
    
    print("Loading results...")
    results = load_results(results_dir)
    difficulty_map = load_task_difficulties(tasks_file)
    
    print(f"Found results for {len(results)} agents")
    print(f"Loaded {len(difficulty_map)} task difficulty mappings")
    
    # Compute statistics
    stats = compute_aggregate_stats(results)
    by_difficulty = analyze_by_difficulty(results, difficulty_map)
    failures = analyze_failures(results)
    common_failures = analyze_common_failures(results)
    
    # Print summaries
    print_markdown_summary(stats, by_difficulty, failures, common_failures)
    print_latex_tables(stats, by_difficulty)
    
    # Save to file
    output_file = results_dir / "analysis.json"
    with open(output_file, 'w') as f:
        json.dump({
            "aggregate": stats,
            "by_difficulty": {
                agent: {
                    diff: {"pass": d["pass"], "total": d["total"]}
                    for diff, d in diffs.items()
                }
                for agent, diffs in by_difficulty.items()
            },
            "failures": failures,
            "common_failures": {k: v for k, v in common_failures.items()},
        }, f, indent=2)
    
    print(f"\n\nAnalysis saved to: {output_file}")


if __name__ == "__main__":
    main()
