"""Create publication-ready visualizations."""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path


def load_valid_results(results_dir: Path) -> dict:
    """Load valid results per agent."""
    agent_data = {}
    
    for agent_dir in results_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
            agent = agent_dir.name
            agent_data[agent] = {'pass': [], 'latency': [], 'stability': [], 'tasks': []}
            
            for f in agent_dir.glob("*.json"):
                try:
                    with open(f) as file:
                        data = json.load(file)
                    if data.get("pass_at_k") and "pass_at_1" in data["pass_at_k"]:
                        agent_data[agent]['pass'].append(data["pass_at_k"]["pass_at_1"])
                        agent_data[agent]['latency'].append(data["latency"]["median_ms"])
                        agent_data[agent]['stability'].append(data["determinism"]["stability_score"])
                        agent_data[agent]['tasks'].append(f.stem)
                except:
                    continue
    
    return agent_data


def create_bar_chart(agent_data: dict, output_dir: Path):
    """Create main comparison bar chart."""
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    labels = ["Claude Code", "Codex CLI", "Gemini CLI"]
    colors = ["#4A90D9", "#50C878", "#FF6B6B"]
    
    # Calculate means
    metrics = {}
    for agent in agents:
        data = agent_data.get(agent, {})
        n = len(data.get('pass', []))
        if n > 0:
            metrics[agent] = {
                'pass': sum(data['pass']) / n * 100,
                'stability': sum(data['stability']) / n * 100,
                'latency': sum(data['latency']) / n / 1000,  # Convert to seconds
                'n': n
            }
        else:
            metrics[agent] = {'pass': 0, 'stability': 0, 'latency': 0, 'n': 0}
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    # Plot 1: Pass@1
    ax1 = axes[0]
    x = np.arange(len(agents))
    bars1 = ax1.bar(x, [metrics[a]['pass'] for a in agents], color=colors, edgecolor='black', linewidth=1.2)
    ax1.set_ylabel('Pass@1 (%)', fontsize=12)
    ax1.set_title('Accuracy', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_ylim(0, 105)
    ax1.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    for bar, agent in zip(bars1, agents):
        height = bar.get_height()
        n = metrics[agent]['n']
        ax1.annotate(f'{height:.1f}%\n(n={n})', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)
    
    # Plot 2: Latency
    ax2 = axes[1]
    bars2 = ax2.bar(x, [metrics[a]['latency'] for a in agents], color=colors, edgecolor='black', linewidth=1.2)
    ax2.set_ylabel('Median Latency (seconds)', fontsize=12)
    ax2.set_title('Response Time', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10)
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.1f}s', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)
    
    # Plot 3: Stability
    ax3 = axes[2]
    bars3 = ax3.bar(x, [metrics[a]['stability'] for a in agents], color=colors, edgecolor='black', linewidth=1.2)
    ax3.set_ylabel('Stability Score (%)', fontsize=12)
    ax3.set_title('Determinism', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, fontsize=10)
    ax3.set_ylim(0, 105)
    for bar in bars3:
        height = bar.get_height()
        ax3.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / "comparison_bar_chart.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "comparison_bar_chart.pdf", bbox_inches='tight')
    plt.close()
    print(f"Created: comparison_bar_chart.png/pdf")


def create_radar_chart(agent_data: dict, output_dir: Path):
    """Create radar/spider chart for multi-dimensional comparison."""
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    labels = ["Claude Code", "Codex CLI", "Gemini CLI"]
    colors = ["#4A90D9", "#50C878", "#FF6B6B"]
    
    # Calculate normalized metrics (0-1 scale)
    metrics = {}
    for agent in agents:
        data = agent_data.get(agent, {})
        n = len(data.get('pass', []))
        if n > 0:
            metrics[agent] = {
                'accuracy': sum(data['pass']) / n,
                'speed': 1 - min(sum(data['latency']) / n / 25000, 1),  # Inverse, normalized
                'stability': sum(data['stability']) / n,
            }
        else:
            metrics[agent] = {'accuracy': 0, 'speed': 0, 'stability': 0}
    
    categories = ['Accuracy', 'Speed', 'Stability']
    num_vars = len(categories)
    
    # Compute angle for each category
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]  # Complete the loop
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for i, agent in enumerate(agents):
        values = [metrics[agent]['accuracy'], metrics[agent]['speed'], metrics[agent]['stability']]
        values += values[:1]  # Complete the loop
        
        ax.plot(angles, values, 'o-', linewidth=2, label=labels[i], color=colors[i])
        ax.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_title('Multi-Dimensional Agent Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    plt.savefig(output_dir / "radar_chart.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "radar_chart.pdf", bbox_inches='tight')
    plt.close()
    print(f"Created: radar_chart.png/pdf")


def create_latency_distribution(agent_data: dict, output_dir: Path):
    """Create latency distribution box plot."""
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    labels = ["Claude Code", "Codex CLI", "Gemini CLI"]
    colors = ["#4A90D9", "#50C878", "#FF6B6B"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data_to_plot = []
    for agent in agents:
        latencies = [l/1000 for l in agent_data.get(agent, {}).get('latency', [])]  # Convert to seconds
        data_to_plot.append(latencies)
    
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Latency (seconds)', fontsize=12)
    ax.set_title('Response Time Distribution', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "latency_boxplot.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "latency_boxplot.pdf", bbox_inches='tight')
    plt.close()
    print(f"Created: latency_boxplot.png/pdf")


def create_difficulty_heatmap(results_dir: Path, tasks_file: Path, output_dir: Path):
    """Create heatmap showing pass rate by difficulty."""
    # Load task difficulties
    difficulties = {}
    with open(tasks_file) as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                difficulties[data['task_id']] = data['difficulty']
    
    # Load results
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    diff_levels = ["easy", "medium", "hard"]
    
    matrix = np.zeros((len(agents), len(diff_levels)))
    counts = np.zeros((len(agents), len(diff_levels)))
    
    for i, agent in enumerate(agents):
        agent_dir = results_dir / agent
        if not agent_dir.exists():
            continue
        for f in agent_dir.glob("*.json"):
            try:
                with open(f) as file:
                    data = json.load(file)
                if data.get("pass_at_k") and "pass_at_1" in data["pass_at_k"]:
                    task_id = f.stem
                    diff = difficulties.get(task_id, "unknown")
                    if diff in diff_levels:
                        j = diff_levels.index(diff)
                        matrix[i, j] += data["pass_at_k"]["pass_at_1"]
                        counts[i, j] += 1
            except:
                continue
    
    # Compute averages
    with np.errstate(divide='ignore', invalid='ignore'):
        matrix = np.where(counts > 0, matrix / counts * 100, 0)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=80, vmax=100)
    
    ax.set_xticks(np.arange(len(diff_levels)))
    ax.set_yticks(np.arange(len(agents)))
    ax.set_xticklabels(['Easy', 'Medium', 'Hard'], fontsize=11)
    ax.set_yticklabels(['Claude Code', 'Codex CLI', 'Gemini CLI'], fontsize=11)
    
    # Add text annotations
    for i in range(len(agents)):
        for j in range(len(diff_levels)):
            val = matrix[i, j]
            count = int(counts[i, j])
            text = ax.text(j, i, f'{val:.1f}%\n(n={count})', ha='center', va='center', 
                          fontsize=10, color='black' if val > 90 else 'white')
    
    ax.set_title('Pass@1 Rate by Task Difficulty', fontsize=14, fontweight='bold')
    
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label('Pass@1 (%)', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_dir / "difficulty_heatmap.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "difficulty_heatmap.pdf", bbox_inches='tight')
    plt.close()
    print(f"Created: difficulty_heatmap.png/pdf")


def main():
    results_dir = Path("results/pilot")
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    output_dir = Path("results/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading data...")
    agent_data = load_valid_results(results_dir)
    
    for agent, data in agent_data.items():
        print(f"  {agent}: {len(data['pass'])} valid results")
    
    print("\nCreating visualizations...")
    create_bar_chart(agent_data, output_dir)
    create_radar_chart(agent_data, output_dir)
    create_latency_distribution(agent_data, output_dir)
    create_difficulty_heatmap(results_dir, tasks_file, output_dir)
    
    print(f"\n✅ All figures saved to: {output_dir}/")
    print("\nFiles created:")
    for f in output_dir.glob("*"):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
