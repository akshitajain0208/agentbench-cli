"""Export only valid benchmark results (exclude rate-limited runs)."""

import json
import csv
from pathlib import Path


def safe_get(data, *keys, default=0):
    for key in keys:
        if data is None or not isinstance(data, dict):
            return default
        data = data.get(key)
    return data if data is not None else default


def is_valid_result(data: dict) -> bool:
    """Check if result has valid pass_at_k data."""
    if not data:
        return False
    pass_at_k = data.get("pass_at_k")
    if not pass_at_k:
        return False
    if "pass_at_1" not in pass_at_k:
        return False
    return True


def load_valid_results(results_dir: Path) -> list:
    """Load only valid results."""
    records = []
    skipped = {"claude_code": 0, "codex_cli": 0, "gemini_cli": 0}
    
    for agent_dir in results_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
            agent_name = agent_dir.name
            
            for result_file in agent_dir.glob("*.json"):
                if result_file.name.startswith('.'):
                    continue
                
                try:
                    with open(result_file) as f:
                        data = json.load(f)
                except:
                    skipped[agent_name] = skipped.get(agent_name, 0) + 1
                    continue
                
                if not is_valid_result(data):
                    skipped[agent_name] = skipped.get(agent_name, 0) + 1
                    continue
                
                record = {
                    "task_id": result_file.stem,
                    "agent": agent_name,
                    "pass_at_1": safe_get(data, "pass_at_k", "pass_at_1", default=0),
                    "pass_at_5": safe_get(data, "pass_at_k", "pass_at_5", default=0),
                    "latency_median_ms": safe_get(data, "latency", "median_ms", default=0),
                    "stability_score": safe_get(data, "determinism", "stability_score", default=0),
                }
                records.append(record)
    
    return records, skipped


def main():
    results_dir = Path("results/pilot")
    output_dir = Path("results/exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading valid results only...")
    records, skipped = load_valid_results(results_dir)
    
    print(f"\nResults loaded:")
    agent_counts = {}
    for r in records:
        agent_counts[r['agent']] = agent_counts.get(r['agent'], 0) + 1
    
    for agent in ["claude_code", "codex_cli", "gemini_cli"]:
        valid = agent_counts.get(agent, 0)
        skip = skipped.get(agent, 0)
        print(f"  {agent}: {valid} valid, {skip} skipped (rate-limited)")
    
    # Compute stats
    print("\n" + "=" * 60)
    print("VALID RESULTS SUMMARY")
    print("=" * 60)
    
    agent_stats = {}
    for record in records:
        agent = record['agent']
        if agent not in agent_stats:
            agent_stats[agent] = {'pass': [], 'latency': [], 'stability': []}
        agent_stats[agent]['pass'].append(record['pass_at_1'])
        agent_stats[agent]['latency'].append(record['latency_median_ms'])
        agent_stats[agent]['stability'].append(record['stability_score'])
    
    print(f"\n{'Agent':<15} {'Tasks':>6} {'Pass@1':>10} {'Latency':>12} {'Stability':>10}")
    print("-" * 55)
    
    for agent in ["claude_code", "codex_cli", "gemini_cli"]:
        if agent not in agent_stats:
            print(f"{agent:<15} {'N/A':>6}")
            continue
        stats = agent_stats[agent]
        n = len(stats['pass'])
        p = sum(stats['pass']) / n * 100
        l = sum(stats['latency']) / n
        s = sum(stats['stability']) / n * 100
        print(f"{agent:<15} {n:>6} {p:>9.1f}% {l:>11,.0f}ms {s:>9.1f}%")
    
    # Export valid summary
    summary_file = output_dir / "valid_agent_summary.csv"
    rows = []
    for agent, stats in agent_stats.items():
        n = len(stats['pass'])
        rows.append({
            'agent': agent,
            'valid_tasks': n,
            'pass_at_1': round(sum(stats['pass']) / n, 4),
            'latency_ms': round(sum(stats['latency']) / n, 2),
            'stability': round(sum(stats['stability']) / n, 4),
        })
    
    with open(summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['agent', 'valid_tasks', 'pass_at_1', 'latency_ms', 'stability'])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda x: x['agent']))
    
    print(f"\nExported: {summary_file}")
    
    # Note about Codex
    if skipped.get('codex_cli', 0) > 0:
        print(f"\n⚠️  Note: {skipped['codex_cli']} Codex tasks skipped due to rate limiting")
        print("   Re-run later or use these partial results with caveat in paper")


if __name__ == "__main__":
    main()
