"""Export all benchmark results to CSV files."""

import json
import csv
from pathlib import Path


def safe_get(data, *keys, default=0):
    """Safely get nested dictionary values."""
    for key in keys:
        if data is None or not isinstance(data, dict):
            return default
        data = data.get(key)
    return data if data is not None else default


def load_all_results(results_dir: Path) -> list:
    """Load all results as flat records."""
    records = []
    
    for agent_dir in results_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
            agent_name = agent_dir.name
            
            for result_file in agent_dir.glob("*.json"):
                if result_file.name.startswith('.'):
                    continue
                    
                task_id = result_file.stem
                
                try:
                    with open(result_file) as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"  Warning: Could not load {result_file}: {e}")
                    continue
                
                if not data:
                    continue
                
                record = {
                    "task_id": task_id,
                    "agent": agent_name,
                    "pass_at_1": safe_get(data, "pass_at_k", "pass_at_1", default=0),
                    "pass_at_5": safe_get(data, "pass_at_k", "pass_at_5", default=0),
                    "passing_samples": safe_get(data, "pass_at_k", "passing_samples", default=0),
                    "total_samples": safe_get(data, "pass_at_k", "total_samples", default=0),
                    "latency_median_ms": safe_get(data, "latency", "median_ms", default=0),
                    "latency_mean_ms": safe_get(data, "latency", "mean_ms", default=0),
                    "latency_p95_ms": safe_get(data, "latency", "p95_ms", default=0),
                    "latency_std_ms": safe_get(data, "latency", "std_ms", default=0),
                    "stability_score": safe_get(data, "determinism", "stability_score", default=0),
                    "exact_match_rate": safe_get(data, "determinism", "exact_match_rate", default=0),
                    "unique_outputs": safe_get(data, "determinism", "unique_outputs", default=0),
                }
                records.append(record)
    
    return records


def load_task_metadata(tasks_file: Path) -> dict:
    """Load task metadata."""
    metadata = {}
    
    with open(tasks_file, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                metadata[data['task_id']] = {
                    "difficulty": data.get('difficulty', 'unknown'),
                    "description": data.get('description', '')[:100],
                    "category": data.get('category', 'unknown'),
                    "tags": ','.join(data.get('tags', [])),
                }
    
    return metadata


def main():
    results_dir = Path("results/pilot")
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    output_dir = Path("results/exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading results...")
    records = load_all_results(results_dir)
    metadata = load_task_metadata(tasks_file)
    
    # Enrich records with metadata
    for record in records:
        task_meta = metadata.get(record['task_id'], {})
        record['difficulty'] = task_meta.get('difficulty', 'unknown')
        record['category'] = task_meta.get('category', 'unknown')
        record['tags'] = task_meta.get('tags', '')
    
    print(f"Loaded {len(records)} result records")
    
    # Export 1: All results
    all_results_file = output_dir / "all_results.csv"
    fieldnames = [
        'task_id', 'agent', 'difficulty', 'category',
        'pass_at_1', 'pass_at_5', 'passing_samples', 'total_samples',
        'latency_median_ms', 'latency_mean_ms', 'latency_p95_ms', 'latency_std_ms',
        'stability_score', 'exact_match_rate', 'unique_outputs', 'tags'
    ]
    
    with open(all_results_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted(records, key=lambda x: (x['task_id'], x['agent'])))
    
    print(f"Exported: {all_results_file}")
    
    # Export 2: Summary by agent
    agent_summary_file = output_dir / "agent_summary.csv"
    
    agent_stats = {}
    for record in records:
        agent = record['agent']
        if agent not in agent_stats:
            agent_stats[agent] = {'pass_at_1': [], 'latency': [], 'stability': []}
        agent_stats[agent]['pass_at_1'].append(record['pass_at_1'])
        agent_stats[agent]['latency'].append(record['latency_median_ms'])
        agent_stats[agent]['stability'].append(record['stability_score'])
    
    summary_rows = []
    for agent, stats in agent_stats.items():
        n = len(stats['pass_at_1'])
        if n == 0:
            continue
        summary_rows.append({
            'agent': agent,
            'tasks': n,
            'pass_at_1_mean': round(sum(stats['pass_at_1']) / n, 4),
            'latency_mean_ms': round(sum(stats['latency']) / n, 2),
            'stability_mean': round(sum(stats['stability']) / n, 4),
        })
    
    with open(agent_summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['agent', 'tasks', 'pass_at_1_mean', 'latency_mean_ms', 'stability_mean'])
        writer.writeheader()
        writer.writerows(sorted(summary_rows, key=lambda x: x['agent']))
    
    print(f"Exported: {agent_summary_file}")
    
    # Export 3: Summary by difficulty
    diff_summary_file = output_dir / "difficulty_summary.csv"
    
    diff_stats = {}
    for record in records:
        key = (record['agent'], record['difficulty'])
        if key not in diff_stats:
            diff_stats[key] = {'pass_at_1': [], 'count': 0}
        diff_stats[key]['pass_at_1'].append(record['pass_at_1'])
        diff_stats[key]['count'] += 1
    
    diff_rows = []
    for (agent, difficulty), stats in diff_stats.items():
        n = len(stats['pass_at_1'])
        diff_rows.append({
            'agent': agent,
            'difficulty': difficulty,
            'tasks': stats['count'],
            'pass_at_1_mean': round(sum(stats['pass_at_1']) / n, 4) if n else 0,
        })
    
    with open(diff_summary_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['agent', 'difficulty', 'tasks', 'pass_at_1_mean'])
        writer.writeheader()
        writer.writerows(sorted(diff_rows, key=lambda x: (x['agent'], x['difficulty'])))
    
    print(f"Exported: {diff_summary_file}")
    
    # Export 4: Failures only (extract only needed fields)
    failures_file = output_dir / "failures.csv"
    failure_fields = ['task_id', 'agent', 'difficulty', 'pass_at_1', 'pass_at_5', 'tags']
    failures = [
        {k: r[k] for k in failure_fields}
        for r in records if r['pass_at_1'] < 1.0
    ]
    
    with open(failures_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=failure_fields)
        writer.writeheader()
        writer.writerows(sorted(failures, key=lambda x: (x['task_id'], x['agent'])))
    
    print(f"Exported: {failures_file}")
    
    # Summary
    print("\n" + "=" * 50)
    print("EXPORT COMPLETE")
    print("=" * 50)
    print(f"\nFiles in {output_dir}/:")
    print(f"  - all_results.csv      ({len(records)} rows)")
    print(f"  - agent_summary.csv    ({len(agent_stats)} agents)")
    print(f"  - difficulty_summary.csv")
    print(f"  - failures.csv         ({len(failures)} failures)")
    
    # Quick preview
    print("\n## Agent Summary Preview:")
    for row in sorted(summary_rows, key=lambda x: x['agent']):
        print(f"  {row['agent']}: {row['pass_at_1_mean']*100:.1f}% Pass@1, {row['latency_mean_ms']:.0f}ms, {row['stability_mean']*100:.1f}% stability")


if __name__ == "__main__":
    main()
