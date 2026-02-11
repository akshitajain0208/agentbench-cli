"""Comprehensive error categorization and analysis."""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import numpy as np

# Constants
AGENTS = ['claude_code', 'codex_cli', 'gemini_cli']
AGENT_LABELS = {
    'claude_code': 'Claude Code',
    'codex_cli': 'Codex CLI',
    'gemini_cli': 'Gemini CLI',
}
COLORS = {
    'claude_code': '#4A90D9',
    'codex_cli': '#50C878',
    'gemini_cli': '#FF6B6B',
}

# Error categories
ERROR_CATEGORIES = {
    'wrong_output': 'Wrong Output',
    'syntax_error': 'Syntax Error',
    'runtime_error': 'Runtime Error',
    'timeout': 'Timeout',
    'name_error': 'NameError',
    'type_error': 'TypeError',
    'index_error': 'IndexError',
    'key_error': 'KeyError',
    'value_error': 'ValueError',
    'attribute_error': 'AttributeError',
    'import_error': 'ImportError',
    'recursion_error': 'RecursionError',
    'memory_error': 'MemoryError',
    'zero_division': 'ZeroDivisionError',
    'assertion_error': 'AssertionError',
    'empty_output': 'Empty Output',
    'rate_limited': 'Rate Limited',
    'format_error': 'Format Error',
    'unknown': 'Unknown Error',
}


def categorize_error(error_msg: str) -> str:
    """Categorize an error message."""
    if not error_msg:
        return 'unknown'
    
    error_lower = error_msg.lower()
    
    # Rate limiting
    if 'rate limit' in error_lower or 'usage limit' in error_lower or 'too many requests' in error_lower:
        return 'rate_limited'
    
    # Empty output
    if 'empty' in error_lower or error_msg.strip() == '':
        return 'empty_output'
    
    # Specific Python errors
    if 'syntaxerror' in error_lower or 'syntax error' in error_lower:
        return 'syntax_error'
    if 'nameerror' in error_lower:
        return 'name_error'
    if 'typeerror' in error_lower:
        return 'type_error'
    if 'indexerror' in error_lower:
        return 'index_error'
    if 'keyerror' in error_lower:
        return 'key_error'
    if 'valueerror' in error_lower:
        return 'value_error'
    if 'attributeerror' in error_lower:
        return 'attribute_error'
    if 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
        return 'import_error'
    if 'recursionerror' in error_lower or 'maximum recursion' in error_lower:
        return 'recursion_error'
    if 'memoryerror' in error_lower:
        return 'memory_error'
    if 'zerodivisionerror' in error_lower:
        return 'zero_division'
    if 'timeout' in error_lower or 'timed out' in error_lower:
        return 'timeout'
    
    # Assertion/Test failures (wrong output)
    if 'assertionerror' in error_lower or 'assert' in error_lower:
        return 'wrong_output'
    if 'test' in error_lower and 'failed' in error_lower:
        return 'wrong_output'
    if 'expected' in error_lower and 'got' in error_lower:
        return 'wrong_output'
    
    # Runtime errors
    if 'runtimeerror' in error_lower or 'exception' in error_lower:
        return 'runtime_error'
    
    # Format issues
    if 'format' in error_lower or 'parse' in error_lower:
        return 'format_error'
    
    return 'unknown'


def extract_error_details(error_msg: str) -> dict:
    """Extract detailed information from error message."""
    details = {
        'category': categorize_error(error_msg),
        'has_traceback': 'Traceback' in error_msg,
        'line_number': None,
        'expected': None,
        'got': None,
    }
    
    # Extract line number
    line_match = re.search(r'line (\d+)', error_msg, re.IGNORECASE)
    if line_match:
        details['line_number'] = int(line_match.group(1))
    
    # Extract expected vs got
    expected_match = re.search(r'expected[:\s]+([^\n,]+)', error_msg, re.IGNORECASE)
    got_match = re.search(r'got[:\s]+([^\n,]+)', error_msg, re.IGNORECASE)
    if expected_match:
        details['expected'] = expected_match.group(1)[:50]
    if got_match:
        details['got'] = got_match.group(1)[:50]
    
    return details


def load_all_errors(results_dir: Path) -> dict:
    """Load all error information from results."""
    errors_by_agent = {agent: [] for agent in AGENTS}
    
    for agent in AGENTS:
        agent_dir = results_dir / agent
        if not agent_dir.exists():
            continue
        
        for f in agent_dir.glob("*.json"):
            try:
                with open(f) as file:
                    data = json.load(file)
                
                task_id = f.stem
                pass_at_k = data.get("pass_at_k", {})
                pass_rate = pass_at_k.get("pass_at_1", 1.0)
                errors = pass_at_k.get("errors", [])
                
                # Check for rate limiting in runs
                runs = data.get("runs", [])
                is_rate_limited = any(
                    'rate limit' in r.get('error_message', '').lower() or
                    'usage limit' in r.get('error_message', '').lower()
                    for r in runs if r.get('error_message')
                )
                
                if pass_rate < 1.0 or is_rate_limited:
                    for error in errors:
                        error_info = {
                            'task_id': task_id,
                            'pass_rate': pass_rate,
                            'error_raw': error[:500] if error else '',
                            'is_rate_limited': is_rate_limited,
                            **extract_error_details(error)
                        }
                        errors_by_agent[agent].append(error_info)
                    
                    # If no errors but still failed, add unknown
                    if not errors and pass_rate < 1.0:
                        errors_by_agent[agent].append({
                            'task_id': task_id,
                            'pass_rate': pass_rate,
                            'error_raw': '',
                            'is_rate_limited': is_rate_limited,
                            'category': 'rate_limited' if is_rate_limited else 'unknown',
                            'has_traceback': False,
                            'line_number': None,
                            'expected': None,
                            'got': None,
                        })
            except Exception as e:
                continue
    
    return errors_by_agent


def analyze_errors(errors_by_agent: dict) -> dict:
    """Analyze error patterns."""
    analysis = {}
    
    for agent in AGENTS:
        errors = errors_by_agent[agent]
        
        # Count by category
        category_counts = Counter(e['category'] for e in errors)
        
        # Unique failed tasks
        failed_tasks = set(e['task_id'] for e in errors)
        
        # Rate limited vs actual failures
        rate_limited = sum(1 for e in errors if e['is_rate_limited'])
        actual_failures = len(errors) - rate_limited
        
        # Common patterns
        has_traceback = sum(1 for e in errors if e['has_traceback'])
        has_expected_got = sum(1 for e in errors if e['expected'] and e['got'])
        
        analysis[agent] = {
            'total_errors': len(errors),
            'unique_failed_tasks': len(failed_tasks),
            'failed_tasks': sorted(failed_tasks),
            'rate_limited': rate_limited,
            'actual_failures': actual_failures,
            'category_counts': dict(category_counts),
            'has_traceback': has_traceback,
            'has_expected_got': has_expected_got,
        }
    
    return analysis


def find_common_failures(errors_by_agent: dict) -> dict:
    """Find tasks that failed for multiple agents."""
    task_failures = defaultdict(list)
    
    for agent in AGENTS:
        for error in errors_by_agent[agent]:
            if not error['is_rate_limited']:
                task_failures[error['task_id']].append({
                    'agent': agent,
                    'category': error['category'],
                    'pass_rate': error['pass_rate'],
                })
    
    # Filter to tasks failed by 2+ agents
    common = {k: v for k, v in task_failures.items() if len(set(e['agent'] for e in v)) >= 2}
    
    return common


def print_report(errors_by_agent: dict, analysis: dict, common_failures: dict):
    """Print comprehensive error report."""
    print("=" * 70)
    print("ERROR CATEGORIZATION REPORT")
    print("=" * 70)
    
    # Summary per agent
    print("\n## Error Summary by Agent")
    print("-" * 70)
    print(f"{'Agent':<15} {'Total':<8} {'Tasks':<8} {'Rate Ltd':<10} {'Actual':<8}")
    print("-" * 70)
    
    for agent in AGENTS:
        a = analysis[agent]
        print(f"{AGENT_LABELS[agent]:<15} {a['total_errors']:<8} {a['unique_failed_tasks']:<8} "
              f"{a['rate_limited']:<10} {a['actual_failures']:<8}")
    
    # Error categories per agent
    print("\n\n## Error Categories by Agent")
    print("-" * 70)
    
    all_categories = set()
    for agent in AGENTS:
        all_categories.update(analysis[agent]['category_counts'].keys())
    all_categories = sorted(all_categories)
    
    # Header
    header = f"{'Category':<20}"
    for agent in AGENTS:
        header += f" {AGENT_LABELS[agent].split()[0]:<12}"
    print(header)
    print("-" * 60)
    
    for cat in all_categories:
        row = f"{ERROR_CATEGORIES.get(cat, cat):<20}"
        for agent in AGENTS:
            count = analysis[agent]['category_counts'].get(cat, 0)
            row += f" {count:<12}"
        print(row)
    
    # Common failures
    if common_failures:
        print("\n\n## Tasks Failed by Multiple Agents (Excluding Rate Limits)")
        print("-" * 70)
        
        for task_id, failures in sorted(common_failures.items()):
            agents_failed = [f['agent'] for f in failures]
            categories = [f['category'] for f in failures]
            print(f"\n  {task_id}:")
            for f in failures:
                print(f"    - {AGENT_LABELS[f['agent']]}: {ERROR_CATEGORIES.get(f['category'], f['category'])}")
    
    # Unique failures per agent
    print("\n\n## Unique Failures (Only One Agent Failed)")
    print("-" * 70)
    
    all_failed_tasks = defaultdict(set)
    for agent in AGENTS:
        for error in errors_by_agent[agent]:
            if not error['is_rate_limited']:
                all_failed_tasks[error['task_id']].add(agent)
    
    for agent in AGENTS:
        unique = [t for t, agents in all_failed_tasks.items() if agents == {agent}]
        if unique:
            print(f"\n  {AGENT_LABELS[agent]} only ({len(unique)} tasks):")
            for t in sorted(unique)[:10]:
                print(f"    - {t}")
            if len(unique) > 10:
                print(f"    ... and {len(unique) - 10} more")
    
    # Sample errors
    print("\n\n## Sample Errors (First 3 per Agent)")
    print("-" * 70)
    
    for agent in AGENTS:
        print(f"\n### {AGENT_LABELS[agent]}")
        errors = [e for e in errors_by_agent[agent] if not e['is_rate_limited']][:3]
        for i, e in enumerate(errors, 1):
            print(f"\n  [{i}] Task: {e['task_id']}")
            print(f"      Category: {ERROR_CATEGORIES.get(e['category'], e['category'])}")
            if e['expected']:
                print(f"      Expected: {e['expected']}")
            if e['got']:
                print(f"      Got: {e['got']}")
            if e['error_raw']:
                preview = e['error_raw'][:150].replace('\n', ' ')
                print(f"      Preview: {preview}...")


def create_visualizations(analysis: dict, output_dir: Path):
    """Create error analysis visualizations."""
    print("\n\nCreating visualizations...")
    
    # Figure 1: Error count by agent (excluding rate limits)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    agents_labels = [AGENT_LABELS[a] for a in AGENTS]
    actual = [analysis[a]['actual_failures'] for a in AGENTS]
    rate_ltd = [analysis[a]['rate_limited'] for a in AGENTS]
    
    x = np.arange(len(AGENTS))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, actual, width, label='Actual Failures', color='#FF6B6B', edgecolor='black')
    bars2 = ax.bar(x + width/2, rate_ltd, width, label='Rate Limited', color='#CCCCCC', edgecolor='black')
    
    ax.set_ylabel('Number of Errors')
    ax.set_title('Error Count by Agent', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(agents_labels)
    ax.legend()
    
    for bar in bars1:
        ax.annotate(f'{int(bar.get_height())}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                   xytext=(0, 3), textcoords='offset points', ha='center', fontsize=10)
    for bar in bars2:
        if bar.get_height() > 0:
            ax.annotate(f'{int(bar.get_height())}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       xytext=(0, 3), textcoords='offset points', ha='center', fontsize=10)
    
    # Figure 2: Error categories (stacked bar)
    ax = axes[1]
    
    # Get all categories (excluding rate_limited)
    all_cats = set()
    for agent in AGENTS:
        for cat in analysis[agent]['category_counts']:
            if cat != 'rate_limited':
                all_cats.add(cat)
    all_cats = sorted(all_cats)
    
    # Category colors
    cat_colors = plt.cm.Set3(np.linspace(0, 1, len(all_cats)))
    
    bottom = np.zeros(len(AGENTS))
    for i, cat in enumerate(all_cats):
        values = [analysis[a]['category_counts'].get(cat, 0) for a in AGENTS]
        ax.bar(x, values, 0.6, bottom=bottom, label=ERROR_CATEGORIES.get(cat, cat), 
               color=cat_colors[i], edgecolor='black', linewidth=0.5)
        bottom += values
    
    ax.set_ylabel('Number of Errors')
    ax.set_title('Error Categories by Agent', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(agents_labels)
    ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / "error_analysis_summary.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "error_analysis_summary.pdf", bbox_inches='tight')
    plt.close()
    print("  ✓ error_analysis_summary.png/pdf")
    
    # Figure 3: Pie charts for each agent
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, agent in enumerate(AGENTS):
        ax = axes[i]
        counts = {k: v for k, v in analysis[agent]['category_counts'].items() if k != 'rate_limited' and v > 0}
        
        if counts:
            labels = [ERROR_CATEGORIES.get(k, k) for k in counts.keys()]
            sizes = list(counts.values())
            
            ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90,
                  colors=plt.cm.Set3(np.linspace(0, 1, len(sizes))))
        
        ax.set_title(AGENT_LABELS[agent], fontweight='bold')
    
    plt.suptitle('Error Distribution by Category', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / "error_pie_charts.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "error_pie_charts.pdf", bbox_inches='tight')
    plt.close()
    print("  ✓ error_pie_charts.png/pdf")
    
    # Figure 4: Heatmap of error categories
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Filter categories with at least one occurrence
    cats_with_data = [cat for cat in all_cats if any(analysis[a]['category_counts'].get(cat, 0) > 0 for a in AGENTS)]
    
    matrix = np.zeros((len(AGENTS), len(cats_with_data)))
    for i, agent in enumerate(AGENTS):
        for j, cat in enumerate(cats_with_data):
            matrix[i, j] = analysis[agent]['category_counts'].get(cat, 0)
    
    im = ax.imshow(matrix, cmap='Reds', aspect='auto')
    
    ax.set_xticks(range(len(cats_with_data)))
    ax.set_yticks(range(len(AGENTS)))
    ax.set_xticklabels([ERROR_CATEGORIES.get(c, c) for c in cats_with_data], rotation=45, ha='right')
    ax.set_yticklabels([AGENT_LABELS[a] for a in AGENTS])
    
    for i in range(len(AGENTS)):
        for j in range(len(cats_with_data)):
            val = int(matrix[i, j])
            if val > 0:
                color = 'white' if val > matrix.max() / 2 else 'black'
                ax.text(j, i, str(val), ha='center', va='center', fontsize=11, fontweight='bold', color=color)
    
    ax.set_title('Error Category Heatmap', fontweight='bold')
    cbar = fig.colorbar(im, ax=ax, shrink=0.6)
    cbar.set_label('Error Count')
    
    plt.tight_layout()
    plt.savefig(output_dir / "error_heatmap.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "error_heatmap.pdf", bbox_inches='tight')
    plt.close()
    print("  ✓ error_heatmap.png/pdf")


def save_report(errors_by_agent: dict, analysis: dict, common_failures: dict, output_dir: Path):
    """Save error analysis to JSON."""
    output = {
        'summary': {agent: {
            'total_errors': analysis[agent]['total_errors'],
            'unique_failed_tasks': analysis[agent]['unique_failed_tasks'],
            'rate_limited': analysis[agent]['rate_limited'],
            'actual_failures': analysis[agent]['actual_failures'],
            'category_counts': analysis[agent]['category_counts'],
        } for agent in AGENTS},
        'common_failures': {
            task: [{'agent': f['agent'], 'category': f['category']} for f in failures]
            for task, failures in common_failures.items()
        },
        'failed_tasks_by_agent': {
            agent: analysis[agent]['failed_tasks']
            for agent in AGENTS
        },
    }
    
    output_file = output_dir / "error_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")


def main():
    results_dir = Path("results/pilot")
    output_dir = Path("results/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading error data...")
    errors_by_agent = load_all_errors(results_dir)
    
    for agent in AGENTS:
        print(f"  {AGENT_LABELS[agent]}: {len(errors_by_agent[agent])} errors")
    
    print("\nAnalyzing errors...")
    analysis = analyze_errors(errors_by_agent)
    common_failures = find_common_failures(errors_by_agent)
    
    print_report(errors_by_agent, analysis, common_failures)
    create_visualizations(analysis, output_dir)
    save_report(errors_by_agent, analysis, common_failures, output_dir)
    
    print("\n" + "=" * 70)
    print("✅ ERROR CATEGORIZATION COMPLETE!")
    print("=" * 70)
    
    # Key insights
    print("\n## Key Insights for Paper")
    print("-" * 70)
    
    # Most common error type per agent
    for agent in AGENTS:
        counts = {k: v for k, v in analysis[agent]['category_counts'].items() if k != 'rate_limited'}
        if counts:
            top_cat = max(counts, key=counts.get)
            print(f"  {AGENT_LABELS[agent]}: Most common error = {ERROR_CATEGORIES.get(top_cat, top_cat)} ({counts[top_cat]})")
    
    print(f"\n  Common failures (multiple agents): {len(common_failures)} tasks")
    print(f"  → These may indicate ambiguous test cases or genuinely hard problems")


if __name__ == "__main__":
    main()
