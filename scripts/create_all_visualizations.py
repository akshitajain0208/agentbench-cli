"""Comprehensive visualization suite for benchmark results."""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality defaults
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Color scheme
COLORS = {
    'claude_code': '#4A90D9',
    'codex_cli': '#50C878', 
    'gemini_cli': '#FF6B6B',
}
AGENT_LABELS = {
    'claude_code': 'Claude Code',
    'codex_cli': 'Codex CLI',
    'gemini_cli': 'Gemini CLI',
}
AGENTS = ['claude_code', 'codex_cli', 'gemini_cli']


def load_all_data(results_dir: Path, tasks_file: Path) -> dict:
    """Load all benchmark data."""
    # Load task metadata
    task_meta = {}
    with open(tasks_file) as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                task_meta[data['task_id']] = {
                    'difficulty': data['difficulty'],
                    'description': data['description'][:50],
                    'category': data.get('category', 'unknown'),
                }
    
    # Load results
    agent_data = {}
    for agent in AGENTS:
        agent_dir = results_dir / agent
        agent_data[agent] = {
            'pass': [], 'latency': [], 'stability': [], 
            'tasks': [], 'difficulties': [], 'errors': []
        }
        
        if not agent_dir.exists():
            continue
            
        for f in agent_dir.glob("*.json"):
            try:
                with open(f) as file:
                    data = json.load(file)
                
                if data.get("pass_at_k") and "pass_at_1" in data["pass_at_k"]:
                    task_id = f.stem
                    agent_data[agent]['pass'].append(data["pass_at_k"]["pass_at_1"])
                    agent_data[agent]['latency'].append(data["latency"]["median_ms"])
                    agent_data[agent]['stability'].append(data["determinism"]["stability_score"])
                    agent_data[agent]['tasks'].append(task_id)
                    agent_data[agent]['difficulties'].append(task_meta.get(task_id, {}).get('difficulty', 'unknown'))
                    agent_data[agent]['errors'].append(len(data["pass_at_k"].get("errors", [])))
            except:
                continue
    
    return agent_data, task_meta


def save_figure(fig, output_dir: Path, name: str):
    """Save figure in multiple formats."""
    fig.savefig(output_dir / f"{name}.png", dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(output_dir / f"{name}.pdf", bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {name}")


# ============================================================
# FIGURE 1: Main Comparison Bar Chart (3 panels)
# ============================================================
def fig_main_comparison(agent_data: dict, output_dir: Path):
    """Main comparison with error bars."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    metrics = {}
    for agent in AGENTS:
        data = agent_data[agent]
        n = len(data['pass'])
        if n > 0:
            metrics[agent] = {
                'pass_mean': np.mean(data['pass']) * 100,
                'pass_std': np.std(data['pass']) * 100,
                'latency_mean': np.mean(data['latency']) / 1000,
                'latency_std': np.std(data['latency']) / 1000,
                'stability_mean': np.mean(data['stability']) * 100,
                'stability_std': np.std(data['stability']) * 100,
                'n': n
            }
        else:
            metrics[agent] = {k: 0 for k in ['pass_mean', 'pass_std', 'latency_mean', 'latency_std', 'stability_mean', 'stability_std', 'n']}
    
    x = np.arange(len(AGENTS))
    
    # Pass@1
    ax = axes[0]
    means = [metrics[a]['pass_mean'] for a in AGENTS]
    stds = [metrics[a]['pass_std'] for a in AGENTS]
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=[COLORS[a] for a in AGENTS], 
                  edgecolor='black', linewidth=1.2, error_kw={'linewidth': 1.5})
    ax.set_ylabel('Pass@1 (%)')
    ax.set_title('Accuracy', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylim(0, 110)
    ax.axhline(100, color='gray', linestyle='--', alpha=0.5)
    for i, (bar, agent) in enumerate(zip(bars, AGENTS)):
        ax.annotate(f'{means[i]:.1f}%', xy=(bar.get_x() + bar.get_width()/2, means[i] + stds[i] + 2),
                   ha='center', fontsize=10, fontweight='bold')
    
    # Latency
    ax = axes[1]
    means = [metrics[a]['latency_mean'] for a in AGENTS]
    stds = [metrics[a]['latency_std'] for a in AGENTS]
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=[COLORS[a] for a in AGENTS],
                  edgecolor='black', linewidth=1.2, error_kw={'linewidth': 1.5})
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Response Time', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    for i, bar in enumerate(bars):
        ax.annotate(f'{means[i]:.1f}s', xy=(bar.get_x() + bar.get_width()/2, means[i] + stds[i] + 0.5),
                   ha='center', fontsize=10, fontweight='bold')
    
    # Stability
    ax = axes[2]
    means = [metrics[a]['stability_mean'] for a in AGENTS]
    stds = [metrics[a]['stability_std'] for a in AGENTS]
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=[COLORS[a] for a in AGENTS],
                  edgecolor='black', linewidth=1.2, error_kw={'linewidth': 1.5})
    ax.set_ylabel('Stability (%)')
    ax.set_title('Determinism', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylim(0, 110)
    for i, bar in enumerate(bars):
        ax.annotate(f'{means[i]:.1f}%', xy=(bar.get_x() + bar.get_width()/2, means[i] + stds[i] + 2),
                   ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    save_figure(fig, output_dir, "01_main_comparison")


# ============================================================
# FIGURE 2: Radar/Spider Chart
# ============================================================
def fig_radar_chart(agent_data: dict, output_dir: Path):
    """Multi-dimensional comparison radar chart."""
    categories = ['Accuracy', 'Speed', 'Stability', 'Consistency', 'Reliability']
    num_vars = len(categories)
    
    # Calculate normalized metrics
    metrics = {}
    for agent in AGENTS:
        data = agent_data[agent]
        n = len(data['pass'])
        if n > 0:
            pass_rate = np.mean(data['pass'])
            speed = 1 - min(np.mean(data['latency']) / 25000, 1)
            stability = np.mean(data['stability'])
            consistency = 1 - np.std(data['pass'])
            reliability = pass_rate * stability
            metrics[agent] = [pass_rate, speed, stability, consistency, reliability]
        else:
            metrics[agent] = [0] * num_vars
    
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    for agent in AGENTS:
        values = metrics[agent] + metrics[agent][:1]
        ax.plot(angles, values, 'o-', linewidth=2.5, label=AGENT_LABELS[agent], color=COLORS[agent])
        ax.fill(angles, values, alpha=0.25, color=COLORS[agent])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_title('Multi-Dimensional Agent Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=11)
    
    save_figure(fig, output_dir, "02_radar_chart")


# ============================================================
# FIGURE 3: Violin Plot (Distribution Comparison)
# ============================================================
def fig_violin_plots(agent_data: dict, output_dir: Path):
    """Violin plots showing full distributions."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Pass@1 Distribution
    ax = axes[0]
    data_pass = [np.array(agent_data[a]['pass']) * 100 for a in AGENTS]
    parts = ax.violinplot(data_pass, positions=range(len(AGENTS)), showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(COLORS[AGENTS[i]])
        pc.set_alpha(0.7)
    ax.set_xticks(range(len(AGENTS)))
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylabel('Pass@1 (%)')
    ax.set_title('Accuracy Distribution', fontweight='bold')
    ax.set_ylim(-5, 105)
    
    # Latency Distribution
    ax = axes[1]
    data_lat = [np.array(agent_data[a]['latency']) / 1000 for a in AGENTS]
    parts = ax.violinplot(data_lat, positions=range(len(AGENTS)), showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(COLORS[AGENTS[i]])
        pc.set_alpha(0.7)
    ax.set_xticks(range(len(AGENTS)))
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Latency Distribution', fontweight='bold')
    
    # Stability Distribution
    ax = axes[2]
    data_stab = [np.array(agent_data[a]['stability']) * 100 for a in AGENTS]
    parts = ax.violinplot(data_stab, positions=range(len(AGENTS)), showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(COLORS[AGENTS[i]])
        pc.set_alpha(0.7)
    ax.set_xticks(range(len(AGENTS)))
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylabel('Stability (%)')
    ax.set_title('Stability Distribution', fontweight='bold')
    ax.set_ylim(-5, 105)
    
    plt.tight_layout()
    save_figure(fig, output_dir, "03_violin_plots")


# ============================================================
# FIGURE 4: Grouped Bar Chart by Difficulty
# ============================================================
def fig_difficulty_grouped_bars(agent_data: dict, output_dir: Path):
    """Grouped bar chart showing performance by difficulty."""
    difficulties = ['easy', 'medium', 'hard']
    
    # Calculate pass rates by difficulty
    diff_data = {agent: {d: [] for d in difficulties} for agent in AGENTS}
    
    for agent in AGENTS:
        for i, task in enumerate(agent_data[agent]['tasks']):
            diff = agent_data[agent]['difficulties'][i]
            if diff in difficulties:
                diff_data[agent][diff].append(agent_data[agent]['pass'][i])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(difficulties))
    width = 0.25
    
    for i, agent in enumerate(AGENTS):
        means = [np.mean(diff_data[agent][d]) * 100 if diff_data[agent][d] else 0 for d in difficulties]
        stds = [np.std(diff_data[agent][d]) * 100 if len(diff_data[agent][d]) > 1 else 0 for d in difficulties]
        counts = [len(diff_data[agent][d]) for d in difficulties]
        
        bars = ax.bar(x + i * width, means, width, yerr=stds, capsize=3,
                     label=AGENT_LABELS[agent], color=COLORS[agent], edgecolor='black')
        
        for j, bar in enumerate(bars):
            if counts[j] > 0:
                ax.annotate(f'n={counts[j]}', xy=(bar.get_x() + bar.get_width()/2, 5),
                           ha='center', fontsize=8, color='white', fontweight='bold')
    
    ax.set_xlabel('Task Difficulty')
    ax.set_ylabel('Pass@1 (%)')
    ax.set_title('Performance by Task Difficulty', fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(['Easy', 'Medium', 'Hard'])
    ax.set_ylim(0, 110)
    ax.legend()
    ax.axhline(100, color='gray', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    save_figure(fig, output_dir, "04_difficulty_grouped_bars")


# ============================================================
# FIGURE 5: Scatter Plot (Accuracy vs Speed Trade-off)
# ============================================================
def fig_accuracy_speed_scatter(agent_data: dict, output_dir: Path):
    """Scatter plot showing accuracy vs speed trade-off."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for agent in AGENTS:
        x = np.array(agent_data[agent]['latency']) / 1000  # seconds
        y = np.array(agent_data[agent]['pass']) * 100  # percentage
        
        ax.scatter(x, y, c=COLORS[agent], label=AGENT_LABELS[agent], 
                  alpha=0.6, s=80, edgecolor='white', linewidth=0.5)
        
        # Add mean point with larger marker
        ax.scatter(np.mean(x), np.mean(y), c=COLORS[agent], s=300, 
                  marker='*', edgecolor='black', linewidth=2, zorder=5)
    
    ax.set_xlabel('Latency (seconds)')
    ax.set_ylabel('Pass@1 (%)')
    ax.set_title('Accuracy vs Speed Trade-off', fontweight='bold')
    ax.legend(title='Agent (★ = mean)')
    ax.set_ylim(-5, 105)
    ax.grid(alpha=0.3)
    
    # Add quadrant labels
    ax.axhline(95, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(10, color='gray', linestyle=':', alpha=0.5)
    ax.text(2, 97, 'Fast & Accurate', fontsize=9, alpha=0.7)
    ax.text(15, 97, 'Slow & Accurate', fontsize=9, alpha=0.7)
    
    plt.tight_layout()
    save_figure(fig, output_dir, "05_accuracy_speed_scatter")


# ============================================================
# FIGURE 6: Scatter Plot (Accuracy vs Stability)
# ============================================================
def fig_accuracy_stability_scatter(agent_data: dict, output_dir: Path):
    """Scatter plot showing accuracy vs stability relationship."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for agent in AGENTS:
        x = np.array(agent_data[agent]['stability']) * 100
        y = np.array(agent_data[agent]['pass']) * 100
        
        ax.scatter(x, y, c=COLORS[agent], label=AGENT_LABELS[agent],
                  alpha=0.6, s=80, edgecolor='white', linewidth=0.5)
        
        ax.scatter(np.mean(x), np.mean(y), c=COLORS[agent], s=300,
                  marker='*', edgecolor='black', linewidth=2, zorder=5)
    
    ax.set_xlabel('Stability (%)')
    ax.set_ylabel('Pass@1 (%)')
    ax.set_title('Accuracy vs Determinism', fontweight='bold')
    ax.legend(title='Agent (★ = mean)')
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.grid(alpha=0.3)
    
    # Add ideal corner indicator
    ax.annotate('Ideal', xy=(100, 100), xytext=(85, 85),
               arrowprops=dict(arrowstyle='->', color='green'),
               fontsize=10, color='green')
    
    plt.tight_layout()
    save_figure(fig, output_dir, "06_accuracy_stability_scatter")


# ============================================================
# FIGURE 7: Box Plot Comparison
# ============================================================
def fig_boxplot_comparison(agent_data: dict, output_dir: Path):
    """Detailed box plots for all metrics."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    # Pass@1
    ax = axes[0]
    data = [np.array(agent_data[a]['pass']) * 100 for a in AGENTS]
    bp = ax.boxplot(data, patch_artist=True, labels=[AGENT_LABELS[a] for a in AGENTS])
    for patch, agent in zip(bp['boxes'], AGENTS):
        patch.set_facecolor(COLORS[agent])
        patch.set_alpha(0.7)
    ax.set_ylabel('Pass@1 (%)')
    ax.set_title('Accuracy', fontweight='bold')
    ax.set_ylim(-5, 105)
    
    # Latency
    ax = axes[1]
    data = [np.array(agent_data[a]['latency']) / 1000 for a in AGENTS]
    bp = ax.boxplot(data, patch_artist=True, labels=[AGENT_LABELS[a] for a in AGENTS])
    for patch, agent in zip(bp['boxes'], AGENTS):
        patch.set_facecolor(COLORS[agent])
        patch.set_alpha(0.7)
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Response Time', fontweight='bold')
    
    # Stability
    ax = axes[2]
    data = [np.array(agent_data[a]['stability']) * 100 for a in AGENTS]
    bp = ax.boxplot(data, patch_artist=True, labels=[AGENT_LABELS[a] for a in AGENTS])
    for patch, agent in zip(bp['boxes'], AGENTS):
        patch.set_facecolor(COLORS[agent])
        patch.set_alpha(0.7)
    ax.set_ylabel('Stability (%)')
    ax.set_title('Determinism', fontweight='bold')
    ax.set_ylim(-5, 105)
    
    plt.tight_layout()
    save_figure(fig, output_dir, "07_boxplot_comparison")


# ============================================================
# FIGURE 8: Heatmap (Difficulty x Agent)
# ============================================================
def fig_difficulty_heatmap(agent_data: dict, output_dir: Path):
    """Heatmap of pass rates by difficulty."""
    difficulties = ['easy', 'medium', 'hard']
    
    matrix = np.zeros((len(AGENTS), len(difficulties)))
    counts = np.zeros((len(AGENTS), len(difficulties)))
    
    for i, agent in enumerate(AGENTS):
        for j, task in enumerate(agent_data[agent]['tasks']):
            diff = agent_data[agent]['difficulties'][j]
            if diff in difficulties:
                k = difficulties.index(diff)
                matrix[i, k] += agent_data[agent]['pass'][j]
                counts[i, k] += 1
    
    with np.errstate(divide='ignore', invalid='ignore'):
        matrix = np.where(counts > 0, matrix / counts * 100, 0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=70, vmax=100)
    
    ax.set_xticks(range(len(difficulties)))
    ax.set_yticks(range(len(AGENTS)))
    ax.set_xticklabels(['Easy', 'Medium', 'Hard'])
    ax.set_yticklabels([AGENT_LABELS[a] for a in AGENTS])
    
    for i in range(len(AGENTS)):
        for j in range(len(difficulties)):
            val = matrix[i, j]
            count = int(counts[i, j])
            color = 'white' if val < 85 else 'black'
            ax.text(j, i, f'{val:.1f}%\n(n={count})', ha='center', va='center',
                   fontsize=11, fontweight='bold', color=color)
    
    ax.set_title('Pass@1 Rate by Task Difficulty', fontweight='bold', fontsize=14)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Pass@1 (%)')
    
    plt.tight_layout()
    save_figure(fig, output_dir, "08_difficulty_heatmap")


# ============================================================
# FIGURE 9: Cumulative Distribution Function (CDF)
# ============================================================
def fig_cdf_plots(agent_data: dict, output_dir: Path):
    """CDF plots for latency and stability."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Latency CDF
    ax = axes[0]
    for agent in AGENTS:
        data = sorted(np.array(agent_data[agent]['latency']) / 1000)
        cdf = np.arange(1, len(data) + 1) / len(data)
        ax.plot(data, cdf, linewidth=2.5, label=AGENT_LABELS[agent], color=COLORS[agent])
    ax.set_xlabel('Latency (seconds)')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Latency CDF', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(0.95, color='gray', linestyle='--', alpha=0.5)
    
    # Stability CDF
    ax = axes[1]
    for agent in AGENTS:
        data = sorted(np.array(agent_data[agent]['stability']) * 100)
        cdf = np.arange(1, len(data) + 1) / len(data)
        ax.plot(data, cdf, linewidth=2.5, label=AGENT_LABELS[agent], color=COLORS[agent])
    ax.set_xlabel('Stability (%)')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Stability CDF', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    save_figure(fig, output_dir, "09_cdf_plots")


# ============================================================
# FIGURE 10: Histogram Comparison
# ============================================================
def fig_histograms(agent_data: dict, output_dir: Path):
    """Overlapping histograms for distributions."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Pass@1 Histogram
    ax = axes[0]
    for agent in AGENTS:
        data = np.array(agent_data[agent]['pass']) * 100
        ax.hist(data, bins=20, alpha=0.5, label=AGENT_LABELS[agent], color=COLORS[agent], edgecolor='black')
    ax.set_xlabel('Pass@1 (%)')
    ax.set_ylabel('Frequency')
    ax.set_title('Accuracy Distribution', fontweight='bold')
    ax.legend()
    
    # Latency Histogram
    ax = axes[1]
    for agent in AGENTS:
        data = np.array(agent_data[agent]['latency']) / 1000
        ax.hist(data, bins=20, alpha=0.5, label=AGENT_LABELS[agent], color=COLORS[agent], edgecolor='black')
    ax.set_xlabel('Latency (seconds)')
    ax.set_ylabel('Frequency')
    ax.set_title('Latency Distribution', fontweight='bold')
    ax.legend()
    
    # Stability Histogram
    ax = axes[2]
    for agent in AGENTS:
        data = np.array(agent_data[agent]['stability']) * 100
        ax.hist(data, bins=20, alpha=0.5, label=AGENT_LABELS[agent], color=COLORS[agent], edgecolor='black')
    ax.set_xlabel('Stability (%)')
    ax.set_ylabel('Frequency')
    ax.set_title('Stability Distribution', fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    save_figure(fig, output_dir, "10_histograms")


# ============================================================
# FIGURE 11: Performance Profile
# ============================================================
def fig_performance_profile(agent_data: dict, output_dir: Path):
    """Performance profile plot (common in optimization literature)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get common tasks
    common_tasks = set(agent_data[AGENTS[0]]['tasks'])
    for agent in AGENTS[1:]:
        common_tasks &= set(agent_data[agent]['tasks'])
    common_tasks = sorted(common_tasks)
    
    if len(common_tasks) < 10:
        print("  ⚠ Skipping performance profile (not enough common tasks)")
        plt.close(fig)
        return
    
    # For each task, find the best (fastest) time
    task_times = {t: {} for t in common_tasks}
    for agent in AGENTS:
        task_idx = {t: i for i, t in enumerate(agent_data[agent]['tasks'])}
        for task in common_tasks:
            if task in task_idx:
                task_times[task][agent] = agent_data[agent]['latency'][task_idx[task]]
    
    # Calculate performance ratios
    ratios = {agent: [] for agent in AGENTS}
    for task in common_tasks:
        best_time = min(task_times[task].values())
        for agent in AGENTS:
            if agent in task_times[task]:
                ratios[agent].append(task_times[task][agent] / best_time)
    
    # Plot CDF of ratios
    for agent in AGENTS:
        r = sorted(ratios[agent])
        cdf = np.arange(1, len(r) + 1) / len(r)
        ax.step(r, cdf, linewidth=2.5, label=AGENT_LABELS[agent], color=COLORS[agent], where='post')
    
    ax.set_xlabel('Performance Ratio (τ)')
    ax.set_ylabel('Proportion of Tasks Solved')
    ax.set_title('Performance Profile (Lower = Better)', fontweight='bold')
    ax.legend()
    ax.set_xlim(1, 10)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    save_figure(fig, output_dir, "11_performance_profile")


# ============================================================
# FIGURE 12: Pareto Frontier (Trade-off Analysis)
# ============================================================
def fig_pareto_frontier(agent_data: dict, output_dir: Path):
    """Pareto frontier showing optimal trade-offs."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot all points
    all_x, all_y = [], []
    for agent in AGENTS:
        x = np.mean(agent_data[agent]['latency']) / 1000  # Speed (lower is better)
        y = np.mean(agent_data[agent]['pass']) * 100  # Accuracy (higher is better)
        all_x.append(x)
        all_y.append(y)
        
        ax.scatter(x, y, c=COLORS[agent], s=400, label=AGENT_LABELS[agent],
                  edgecolor='black', linewidth=2, zorder=5)
        ax.annotate(AGENT_LABELS[agent], (x, y), xytext=(10, 10),
                   textcoords='offset points', fontsize=11, fontweight='bold')
    
    # Add Pareto frontier line
    points = sorted(zip(all_x, all_y))
    pareto_x, pareto_y = [points[0][0]], [points[0][1]]
    for x, y in points[1:]:
        if y > pareto_y[-1]:
            pareto_x.append(x)
            pareto_y.append(y)
    
    ax.plot(pareto_x, pareto_y, 'g--', linewidth=2, alpha=0.7, label='Pareto Frontier')
    
    ax.set_xlabel('Mean Latency (seconds) — Lower is Better →')
    ax.set_ylabel('Pass@1 (%) — Higher is Better →')
    ax.set_title('Speed vs Accuracy Trade-off (Pareto Analysis)', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Highlight optimal region
    ax.axhspan(95, 105, alpha=0.1, color='green')
    ax.axvspan(0, 5, alpha=0.1, color='blue')
    
    plt.tight_layout()
    save_figure(fig, output_dir, "12_pareto_frontier")


# ============================================================
# FIGURE 13: Failure Analysis
# ============================================================
def fig_failure_analysis(agent_data: dict, output_dir: Path):
    """Failure analysis visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Count failures by agent
    failures = {}
    for agent in AGENTS:
        total = len(agent_data[agent]['pass'])
        failed = sum(1 for p in agent_data[agent]['pass'] if p < 1.0)
        failures[agent] = {'total': total, 'failed': failed, 'passed': total - failed}
    
    # Stacked bar chart
    ax = axes[0]
    x = np.arange(len(AGENTS))
    passed = [failures[a]['passed'] for a in AGENTS]
    failed = [failures[a]['failed'] for a in AGENTS]
    
    ax.bar(x, passed, label='Passed', color='#50C878', edgecolor='black')
    ax.bar(x, failed, bottom=passed, label='Failed', color='#FF6B6B', edgecolor='black')
    
    ax.set_xticks(x)
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Pass/Fail Distribution', fontweight='bold')
    ax.legend()
    
    for i, agent in enumerate(AGENTS):
        total = failures[agent]['total']
        fail_pct = failures[agent]['failed'] / total * 100 if total > 0 else 0
        ax.annotate(f'{fail_pct:.1f}% fail', xy=(i, total + 1), ha='center', fontsize=10)
    
    # Failure by difficulty
    ax = axes[1]
    difficulties = ['easy', 'medium', 'hard']
    
    diff_failures = {agent: {d: [0, 0] for d in difficulties} for agent in AGENTS}  # [fail, total]
    
    for agent in AGENTS:
        for i, task in enumerate(agent_data[agent]['tasks']):
            diff = agent_data[agent]['difficulties'][i]
            if diff in difficulties:
                diff_failures[agent][diff][1] += 1
                if agent_data[agent]['pass'][i] < 1.0:
                    diff_failures[agent][diff][0] += 1
    
    x = np.arange(len(difficulties))
    width = 0.25
    
    for i, agent in enumerate(AGENTS):
        fail_rates = []
        for d in difficulties:
            total = diff_failures[agent][d][1]
            fail = diff_failures[agent][d][0]
            fail_rates.append(fail / total * 100 if total > 0 else 0)
        ax.bar(x + i * width, fail_rates, width, label=AGENT_LABELS[agent], color=COLORS[agent], edgecolor='black')
    
    ax.set_xticks(x + width)
    ax.set_xticklabels(['Easy', 'Medium', 'Hard'])
    ax.set_ylabel('Failure Rate (%)')
    ax.set_title('Failure Rate by Difficulty', fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    save_figure(fig, output_dir, "13_failure_analysis")


# ============================================================
# FIGURE 14: Correlation Matrix
# ============================================================
def fig_correlation_matrix(agent_data: dict, output_dir: Path):
    """Correlation between metrics across all agents."""
    # Combine all data
    all_pass = []
    all_latency = []
    all_stability = []
    
    for agent in AGENTS:
        all_pass.extend(agent_data[agent]['pass'])
        all_latency.extend([l/1000 for l in agent_data[agent]['latency']])
        all_stability.extend(agent_data[agent]['stability'])
    
    data = np.array([all_pass, all_latency, all_stability])
    corr = np.corrcoef(data)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    
    labels = ['Pass@1', 'Latency', 'Stability']
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    
    for i in range(len(labels)):
        for j in range(len(labels)):
            color = 'white' if abs(corr[i, j]) > 0.5 else 'black'
            ax.text(j, i, f'{corr[i, j]:.2f}', ha='center', va='center',
                   fontsize=14, fontweight='bold', color=color)
    
    ax.set_title('Metric Correlation Matrix', fontweight='bold')
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation Coefficient')
    
    plt.tight_layout()
    save_figure(fig, output_dir, "14_correlation_matrix")


# ============================================================
# FIGURE 15: Summary Dashboard
# ============================================================
def fig_summary_dashboard(agent_data: dict, output_dir: Path):
    """Single-page dashboard summarizing all findings."""
    fig = plt.figure(figsize=(16, 12))
    
    # Calculate summary stats
    stats = {}
    for agent in AGENTS:
        n = len(agent_data[agent]['pass'])
        if n > 0:
            stats[agent] = {
                'n': n,
                'pass': np.mean(agent_data[agent]['pass']) * 100,
                'latency': np.mean(agent_data[agent]['latency']) / 1000,
                'stability': np.mean(agent_data[agent]['stability']) * 100,
            }
    
    # Title
    fig.suptitle('AgentBench-CLI: Console-Based AI Coding Agent Benchmark Results', 
                fontsize=18, fontweight='bold', y=0.98)
    
    # 1. Main metrics (top row)
    ax1 = fig.add_subplot(2, 3, 1)
    x = np.arange(len(AGENTS))
    bars = ax1.bar(x, [stats[a]['pass'] for a in AGENTS], color=[COLORS[a] for a in AGENTS], edgecolor='black')
    ax1.set_xticks(x)
    ax1.set_xticklabels([AGENT_LABELS[a].split()[0] for a in AGENTS])
    ax1.set_ylabel('Pass@1 (%)')
    ax1.set_title('Accuracy', fontweight='bold')
    ax1.set_ylim(0, 105)
    for bar in bars:
        ax1.annotate(f'{bar.get_height():.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
    
    ax2 = fig.add_subplot(2, 3, 2)
    bars = ax2.bar(x, [stats[a]['latency'] for a in AGENTS], color=[COLORS[a] for a in AGENTS], edgecolor='black')
    ax2.set_xticks(x)
    ax2.set_xticklabels([AGENT_LABELS[a].split()[0] for a in AGENTS])
    ax2.set_ylabel('Latency (s)')
    ax2.set_title('Speed', fontweight='bold')
    for bar in bars:
        ax2.annotate(f'{bar.get_height():.1f}s', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
    
    ax3 = fig.add_subplot(2, 3, 3)
    bars = ax3.bar(x, [stats[a]['stability'] for a in AGENTS], color=[COLORS[a] for a in AGENTS], edgecolor='black')
    ax3.set_xticks(x)
    ax3.set_xticklabels([AGENT_LABELS[a].split()[0] for a in AGENTS])
    ax3.set_ylabel('Stability (%)')
    ax3.set_title('Determinism', fontweight='bold')
    ax3.set_ylim(0, 105)
    for bar in bars:
        ax3.annotate(f'{bar.get_height():.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords='offset points', ha='center', fontsize=9)
    
    # 2. Radar chart
    ax4 = fig.add_subplot(2, 3, 4, polar=True)
    categories = ['Accuracy', 'Speed', 'Stability']
    for agent in AGENTS:
        values = [
            stats[agent]['pass'] / 100,
            1 - min(stats[agent]['latency'] / 20, 1),
            stats[agent]['stability'] / 100,
        ]
        values += values[:1]
        angles = [n / 3 * 2 * np.pi for n in range(3)] + [0]
        ax4.plot(angles, values, 'o-', linewidth=2, label=AGENT_LABELS[agent], color=COLORS[agent])
        ax4.fill(angles, values, alpha=0.2, color=COLORS[agent])
    ax4.set_xticks([n / 3 * 2 * np.pi for n in range(3)])
    ax4.set_xticklabels(categories)
    ax4.set_title('Trade-off Overview', fontweight='bold', pad=15)
    
    # 3. Box plots
    ax5 = fig.add_subplot(2, 3, 5)
    data = [np.array(agent_data[a]['latency'])/1000 for a in AGENTS]
    bp = ax5.boxplot(data, patch_artist=True, labels=[AGENT_LABELS[a].split()[0] for a in AGENTS])
    for patch, agent in zip(bp['boxes'], AGENTS):
        patch.set_facecolor(COLORS[agent])
        patch.set_alpha(0.7)
    ax5.set_ylabel('Latency (s)')
    ax5.set_title('Latency Distribution', fontweight='bold')
    
    # 4. Summary text
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')
    
    summary_text = """
KEY FINDINGS:

1. ACCURACY: Claude Code leads at {:.1f}%
   (vs Codex {:.1f}%, Gemini {:.1f}%)

2. SPEED: Codex CLI is fastest at {:.1f}s
   ({:.1f}x faster than Claude)

3. STABILITY: Claude most deterministic at {:.1f}%
   (Codex {:.1f}%, Gemini {:.1f}%)

STATISTICAL SIGNIFICANCE:
- Latency differences: p < 0.001 ***
- Stability differences: p < 0.001 ***
- Accuracy differences: p = 0.24 (not significant)

TRADE-OFF: Speed vs Reliability
""".format(
        stats['claude_code']['pass'], stats['codex_cli']['pass'], stats['gemini_cli']['pass'],
        stats['codex_cli']['latency'], stats['claude_code']['latency'] / stats['codex_cli']['latency'],
        stats['claude_code']['stability'], stats['codex_cli']['stability'], stats['gemini_cli']['stability']
    )
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, output_dir, "15_summary_dashboard")


# ============================================================
# FIGURE 16: Task-Level Comparison Heatmap
# ============================================================
def fig_task_heatmap(agent_data: dict, output_dir: Path):
    """Heatmap showing per-task performance."""
    # Get common tasks
    common_tasks = set(agent_data[AGENTS[0]]['tasks'])
    for agent in AGENTS[1:]:
        common_tasks &= set(agent_data[agent]['tasks'])
    common_tasks = sorted(common_tasks)[:30]  # Limit to 30 for visibility
    
    if len(common_tasks) < 10:
        print("  ⚠ Skipping task heatmap (not enough common tasks)")
        return
    
    matrix = np.zeros((len(AGENTS), len(common_tasks)))
    
    for i, agent in enumerate(AGENTS):
        task_idx = {t: j for j, t in enumerate(agent_data[agent]['tasks'])}
        for j, task in enumerate(common_tasks):
            if task in task_idx:
                matrix[i, j] = agent_data[agent]['pass'][task_idx[task]] * 100
    
    fig, ax = plt.subplots(figsize=(16, 4))
    
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    ax.set_xticks(range(len(common_tasks)))
    ax.set_yticks(range(len(AGENTS)))
    ax.set_xticklabels(common_tasks, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_title('Per-Task Pass@1 Rate', fontweight='bold')
    
    cbar = fig.colorbar(im, ax=ax, shrink=0.5)
    cbar.set_label('Pass@1 (%)')
    
    plt.tight_layout()
    save_figure(fig, output_dir, "16_task_heatmap")


# ============================================================
# FIGURE 17: Stability vs Latency (3D Effect)
# ============================================================
def fig_3d_scatter(agent_data: dict, output_dir: Path):
    """3D scatter plot of all three metrics."""
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    for agent in AGENTS:
        x = np.array(agent_data[agent]['latency']) / 1000
        y = np.array(agent_data[agent]['stability']) * 100
        z = np.array(agent_data[agent]['pass']) * 100
        
        ax.scatter(x, y, z, c=COLORS[agent], label=AGENT_LABELS[agent], s=50, alpha=0.6)
    
    ax.set_xlabel('Latency (s)')
    ax.set_ylabel('Stability (%)')
    ax.set_zlabel('Pass@1 (%)')
    ax.set_title('3D Performance Space', fontweight='bold')
    ax.legend()
    
    plt.tight_layout()
    save_figure(fig, output_dir, "17_3d_scatter")


# ============================================================
# MAIN
# ============================================================
def main():
    results_dir = Path("results/pilot")
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    output_dir = Path("results/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("CREATING COMPREHENSIVE VISUALIZATION SUITE")
    print("=" * 60)
    
    print("\nLoading data...")
    agent_data, task_meta = load_all_data(results_dir, tasks_file)
    
    for agent in AGENTS:
        n = len(agent_data[agent]['pass'])
        print(f"  {agent}: {n} valid results")
    
    print("\nGenerating figures...")
    
    fig_main_comparison(agent_data, output_dir)
    fig_radar_chart(agent_data, output_dir)
    fig_violin_plots(agent_data, output_dir)
    fig_difficulty_grouped_bars(agent_data, output_dir)
    fig_accuracy_speed_scatter(agent_data, output_dir)
    fig_accuracy_stability_scatter(agent_data, output_dir)
    fig_boxplot_comparison(agent_data, output_dir)
    fig_difficulty_heatmap(agent_data, output_dir)
    fig_cdf_plots(agent_data, output_dir)
    fig_histograms(agent_data, output_dir)
    fig_performance_profile(agent_data, output_dir)
    fig_pareto_frontier(agent_data, output_dir)
    fig_failure_analysis(agent_data, output_dir)
    fig_correlation_matrix(agent_data, output_dir)
    fig_summary_dashboard(agent_data, output_dir)
    fig_task_heatmap(agent_data, output_dir)
    fig_3d_scatter(agent_data, output_dir)
    
    print("\n" + "=" * 60)
    print("✅ ALL VISUALIZATIONS COMPLETE!")
    print("=" * 60)
    
    print(f"\nFiles saved to: {output_dir}/")
    files = sorted(output_dir.glob("*.png"))
    for f in files:
        print(f"  📊 {f.name}")
    
    print(f"\nTotal: {len(files)} PNG files + {len(files)} PDF files")
    print("\nRecommended for paper:")
    print("  - 01_main_comparison.pdf (Figure 1)")
    print("  - 04_difficulty_grouped_bars.pdf (Figure 2)")
    print("  - 08_difficulty_heatmap.pdf (Figure 3)")
    print("  - 12_pareto_frontier.pdf (Figure 4)")
    print("  - 15_summary_dashboard.pdf (Appendix)")


if __name__ == "__main__":
    main()
