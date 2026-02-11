"""
Comprehensive Analysis with 25+ Metrics.
Analyzes all results and generates detailed visualizations.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.evaluation.metrics.comprehensive_metrics import (
    compute_all_metrics, get_flat_metrics, METRIC_DESCRIPTIONS
)

# Paths
RESULTS_DIR = Path("results/pilot")
REFS_FILE = Path("benchmark/v0.1.0/codegen-core/reference_solutions.json")
TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
OUTPUT_DIR = Path("results/comprehensive_analysis")
FIGURES_DIR = OUTPUT_DIR / "figures"

AGENTS = ['claude_code', 'codex_cli', 'gemini_cli']
AGENT_LABELS = {'claude_code': 'Claude Code', 'codex_cli': 'Codex CLI', 'gemini_cli': 'Gemini CLI'}
COLORS = {'claude_code': '#E74C3C', 'codex_cli': '#3498DB', 'gemini_cli': '#2ECC71'}


def load_data():
    """Load all results, references, and tasks."""
    print("Loading data...")
    
    with open(REFS_FILE) as f:
        references = json.load(f)
    print(f"  Loaded {len(references)} reference solutions")
    
    tasks = {}
    with open(TASKS_FILE) as f:
        for line in f:
            if line.strip():
                task = json.loads(line)
                tasks[task['task_id']] = task
    print(f"  Loaded {len(tasks)} tasks")
    
    results = {agent: {} for agent in AGENTS}
    for agent in AGENTS:
        agent_dir = RESULTS_DIR / agent
        for f in agent_dir.glob("*.json"):
            with open(f) as file:
                data = json.load(file)
                results[agent][f.stem] = data
        print(f"  Loaded {len(results[agent])} results for {agent}")
    
    return results, references, tasks


def compute_metrics_for_all(results: dict, references: dict, tasks: dict) -> pd.DataFrame:
    """Compute all metrics for all results."""
    print("\nComputing comprehensive metrics...")
    
    all_metrics = []
    
    for agent in AGENTS:
        print(f"  Processing {agent}...")
        for task_id, result in results[agent].items():
            if task_id not in references:
                continue
            
            ref_code = references[task_id]['reference_code']
            runs = result.get('runs', [])
            
            generated = ''
            for run in runs:
                if run.get('content'):
                    generated = run['content']
                    break
            
            if not generated:
                continue
            
            passed = result.get('pass_at_k', {}).get('pass_at_1', 0) > 0
            
            metrics = compute_all_metrics(generated, ref_code, runs, passed)
            flat = get_flat_metrics(metrics)
            
            flat['task_id'] = task_id
            flat['agent'] = agent
            flat['difficulty'] = tasks.get(task_id, {}).get('difficulty', 'unknown')
            
            latency = result.get('latency', {})
            flat['latency_ms'] = latency.get('median_ms', latency.get('mean_ms', 0))
            
            all_metrics.append(flat)
    
    df = pd.DataFrame(all_metrics)
    print(f"  Computed metrics for {len(df)} task-agent pairs")
    
    return df


def create_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary statistics by agent."""
    print("\nCreating summary statistics...")
    
    key_metrics = [
        'functional_pass_at_1',
        'functional_first_pass_success',
        'functional_mean_reciprocal_rank',
        'similarity_exact_match',
        'similarity_code_bleu',
        'similarity_rouge_l',
        'similarity_token_f1',
        'similarity_normalized_edit_distance',
        'quality_syntactic_validity',
        'quality_ast_node_similarity',
        'quality_cyclomatic_complexity',
        'quality_maintainability_index',
        'efficiency_token_efficiency',
        'reliability_output_stability',
        'reliability_semantic_consistency',
        'latency_ms'
    ]
    
    available_metrics = [m for m in key_metrics if m in df.columns]
    summary = df.groupby('agent')[available_metrics].agg(['mean', 'std']).round(3)
    
    return summary


def plot_metric_comparison(df: pd.DataFrame, metric: str, title: str, filename: str):
    """Create bar chart comparing agents on a single metric."""
    if metric not in df.columns:
        return
        
    fig, ax = plt.subplots(figsize=(10, 6))
    
    means = df.groupby('agent')[metric].mean()
    stds = df.groupby('agent')[metric].std()
    
    x = np.arange(len(AGENTS))
    bars = ax.bar(x, [means.get(a, 0) for a in AGENTS], 
                  yerr=[stds.get(a, 0) for a in AGENTS],
                  color=[COLORS[a] for a in AGENTS],
                  capsize=5, alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylabel(metric.replace('_', ' ').title())
    ax.set_title(title)
    ax.grid(axis='y', alpha=0.3)
    
    for bar, agent in zip(bars, AGENTS):
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"{filename}.png", dpi=150)
    plt.savefig(FIGURES_DIR / f"{filename}.pdf")
    plt.close()


def plot_radar_chart(df: pd.DataFrame):
    """Create radar chart with all key metrics."""
    print("  Creating radar chart...")
    
    metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('functional_first_pass_success', 'First Pass'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_token_f1', 'Token F1'),
        ('quality_syntactic_validity', 'Syntax Valid'),
        ('quality_ast_node_similarity', 'AST Similarity'),
        ('reliability_output_stability', 'Stability'),
        ('reliability_semantic_consistency', 'Consistency'),
    ]
    
    # Filter to available metrics
    metrics = [(m, l) for m, l in metrics if m in df.columns]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]
    
    for agent in AGENTS:
        agent_data = df[df['agent'] == agent]
        values = [agent_data[m[0]].mean() for m in metrics]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=AGENT_LABELS[agent], color=COLORS[agent])
        ax.fill(angles, values, alpha=0.15, color=COLORS[agent])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m[1] for m in metrics])
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.set_title('Comprehensive Performance Radar', size=14, y=1.08)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "radar_comprehensive.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "radar_comprehensive.pdf", bbox_inches='tight')
    plt.close()


def plot_correlation_heatmap(df: pd.DataFrame):
    """Create correlation heatmap between metrics."""
    print("  Creating correlation heatmap...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if not c.startswith('latency') and c not in ['unique_outputs']]
    
    if len(numeric_cols) < 2:
        print("    Skipping - not enough numeric columns")
        return
    
    corr = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(16, 14))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    
    sns.heatmap(corr, mask=mask, cmap='RdYlBu_r', center=0,
                annot=False, square=True, linewidths=0.5,
                cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title('Metric Correlation Heatmap', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(fontsize=8)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_heatmap.png", dpi=150)
    plt.savefig(FIGURES_DIR / "correlation_heatmap.pdf")
    plt.close()


def plot_metric_distributions(df: pd.DataFrame):
    """Create box plots for key metrics."""
    print("  Creating metric distribution plots...")
    
    key_metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_normalized_edit_distance', 'Edit Distance (Norm)'),
        ('similarity_token_f1', 'Token F1'),
        ('quality_maintainability_index', 'Maintainability'),
        ('reliability_output_stability', 'Stability'),
    ]
    
    # Filter to available metrics
    key_metrics = [(m, l) for m, l in key_metrics if m in df.columns]
    
    if not key_metrics:
        print("    Skipping - no metrics available")
        return
    
    n_metrics = len(key_metrics)
    n_cols = 3
    n_rows = (n_metrics + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    axes = axes.flatten() if n_metrics > 1 else [axes]
    
    for idx, (metric, label) in enumerate(key_metrics):
        ax = axes[idx]
        
        # Use boxplot instead of violin to avoid empty data issues
        data_to_plot = []
        labels_to_use = []
        colors_to_use = []
        
        for agent in AGENTS:
            agent_data = df[df['agent'] == agent][metric].dropna().values
            if len(agent_data) > 0:
                data_to_plot.append(agent_data)
                labels_to_use.append(AGENT_LABELS[agent])
                colors_to_use.append(COLORS[agent])
        
        if data_to_plot:
            bp = ax.boxplot(data_to_plot, patch_artist=True)
            for patch, color in zip(bp['boxes'], colors_to_use):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_xticklabels(labels_to_use)
        
        ax.set_title(label)
        ax.grid(axis='y', alpha=0.3)
    
    # Hide unused axes
    for idx in range(len(key_metrics), len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle('Metric Distributions by Agent', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "metric_distributions.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "metric_distributions.pdf", bbox_inches='tight')
    plt.close()


def plot_difficulty_breakdown(df: pd.DataFrame):
    """Create heatmap of metrics by difficulty and agent."""
    print("  Creating difficulty breakdown...")
    
    key_metrics = [
        'functional_pass_at_1',
        'similarity_code_bleu',
        'similarity_token_f1',
        'quality_syntactic_validity',
        'reliability_output_stability',
    ]
    
    key_metrics = [m for m in key_metrics if m in df.columns]
    
    if not key_metrics:
        print("    Skipping - no metrics available")
        return
    
    fig, axes = plt.subplots(1, len(key_metrics), figsize=(4 * len(key_metrics), 5))
    if len(key_metrics) == 1:
        axes = [axes]
    
    for ax, metric in zip(axes, key_metrics):
        pivot = df.pivot_table(
            values=metric, 
            index='difficulty', 
            columns='agent',
            aggfunc='mean'
        )
        if 'easy' in pivot.index:
            pivot = pivot.reindex(['easy', 'medium', 'hard'])
        pivot = pivot[[a for a in AGENTS if a in pivot.columns]]
        
        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', 
                    ax=ax, vmin=0, vmax=1, cbar=False)
        ax.set_title(metric.split('_')[-1].title())
        ax.set_ylabel('')
        ax.set_xticklabels([AGENT_LABELS[a][:6] for a in pivot.columns], rotation=45)
    
    plt.suptitle('Metrics by Difficulty Level', fontsize=14, y=1.05)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "difficulty_breakdown.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "difficulty_breakdown.pdf", bbox_inches='tight')
    plt.close()


def plot_scatter_matrix(df: pd.DataFrame):
    """Create scatter plot matrix of key metrics."""
    print("  Creating scatter matrix...")
    
    key_metrics = [
        'functional_pass_at_1',
        'similarity_code_bleu',
        'quality_maintainability_index',
        'reliability_output_stability',
    ]
    
    key_metrics = [m for m in key_metrics if m in df.columns]
    
    if len(key_metrics) < 2:
        print("    Skipping - not enough metrics")
        return
    
    fig, axes = plt.subplots(len(key_metrics), len(key_metrics), figsize=(14, 14))
    
    for i, m1 in enumerate(key_metrics):
        for j, m2 in enumerate(key_metrics):
            ax = axes[i, j]
            
            if i == j:
                for agent in AGENTS:
                    data = df[df['agent'] == agent][m1].dropna()
                    if len(data) > 0:
                        ax.hist(data, bins=20, alpha=0.5, color=COLORS[agent], label=AGENT_LABELS[agent])
                ax.set_xlabel(m1.split('_')[-1])
            else:
                for agent in AGENTS:
                    agent_df = df[df['agent'] == agent]
                    ax.scatter(agent_df[m2], agent_df[m1], alpha=0.5, 
                              color=COLORS[agent], s=20, label=AGENT_LABELS[agent])
                
            if j == 0:
                ax.set_ylabel(m1.split('_')[-1])
            if i == len(key_metrics) - 1:
                ax.set_xlabel(m2.split('_')[-1])
    
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS[a], 
                          markersize=10, label=AGENT_LABELS[a]) for a in AGENTS]
    fig.legend(handles=handles, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    plt.suptitle('Metric Scatter Matrix', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "scatter_matrix.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "scatter_matrix.pdf", bbox_inches='tight')
    plt.close()


def plot_metric_rankings(df: pd.DataFrame):
    """Create bar chart showing which agent ranks best on each metric."""
    print("  Creating metric rankings...")
    
    metrics = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'efficiency_', 'reliability_'))]
    
    rankings = []
    for metric in metrics:
        means = df.groupby('agent')[metric].mean()
        reverse_metrics = ['character_error_rate', 'cyclomatic_complexity', 'halstead_difficulty', 
                          'halstead_effort', 'code_lines_ratio']
        
        if any(r in metric for r in reverse_metrics):
            best = means.idxmin()
        else:
            best = means.idxmax()
        
        rankings.append({'metric': metric, 'best_agent': best})
    
    rankings_df = pd.DataFrame(rankings)
    counts = rankings_df['best_agent'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(AGENTS))
    bars = ax.bar(x, [counts.get(a, 0) for a in AGENTS], 
                  color=[COLORS[a] for a in AGENTS], alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax.set_ylabel('Number of Metrics Won')
    ax.set_title('Metric Leadership by Agent')
    ax.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "metric_rankings.png", dpi=150)
    plt.savefig(FIGURES_DIR / "metric_rankings.pdf")
    plt.close()
    
    return rankings_df


def plot_comprehensive_dashboard(df: pd.DataFrame):
    """Create a comprehensive dashboard with multiple panels."""
    print("  Creating comprehensive dashboard...")
    
    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # Panel 1: Overall accuracy
    ax1 = fig.add_subplot(gs[0, 0])
    if 'functional_pass_at_1' in df.columns:
        means = df.groupby('agent')['functional_pass_at_1'].mean()
        bars = ax1.bar(range(len(AGENTS)), [means.get(a, 0) for a in AGENTS], 
                       color=[COLORS[a] for a in AGENTS])
        ax1.set_xticks(range(len(AGENTS)))
        ax1.set_xticklabels([AGENT_LABELS[a][:8] for a in AGENTS], fontsize=9)
        ax1.set_ylabel('Pass@1')
        ax1.set_title('Functional Correctness')
        ax1.set_ylim(0, 1.1)
        for bar in bars:
            ax1.annotate(f'{bar.get_height():.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 2), textcoords='offset points', ha='center', fontsize=9)
    
    # Panel 2: CodeBLEU
    ax2 = fig.add_subplot(gs[0, 1])
    if 'similarity_code_bleu' in df.columns:
        means = df.groupby('agent')['similarity_code_bleu'].mean()
        bars = ax2.bar(range(len(AGENTS)), [means.get(a, 0) for a in AGENTS], 
                       color=[COLORS[a] for a in AGENTS])
        ax2.set_xticks(range(len(AGENTS)))
        ax2.set_xticklabels([AGENT_LABELS[a][:8] for a in AGENTS], fontsize=9)
        ax2.set_ylabel('CodeBLEU')
        ax2.set_title('Code Similarity')
        ax2.set_ylim(0, 1.1)
        for bar in bars:
            ax2.annotate(f'{bar.get_height():.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 2), textcoords='offset points', ha='center', fontsize=9)
    
    # Panel 3: Stability
    ax3 = fig.add_subplot(gs[0, 2])
    if 'reliability_output_stability' in df.columns:
        means = df.groupby('agent')['reliability_output_stability'].mean()
        bars = ax3.bar(range(len(AGENTS)), [means.get(a, 0) for a in AGENTS], 
                       color=[COLORS[a] for a in AGENTS])
        ax3.set_xticks(range(len(AGENTS)))
        ax3.set_xticklabels([AGENT_LABELS[a][:8] for a in AGENTS], fontsize=9)
        ax3.set_ylabel('Stability')
        ax3.set_title('Output Reliability')
        ax3.set_ylim(0, 1.1)
        for bar in bars:
            ax3.annotate(f'{bar.get_height():.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 2), textcoords='offset points', ha='center', fontsize=9)
    
    # Panel 4: Latency
    ax4 = fig.add_subplot(gs[0, 3])
    if 'latency_ms' in df.columns:
        means = df.groupby('agent')['latency_ms'].mean() / 1000
        bars = ax4.bar(range(len(AGENTS)), [means.get(a, 0) for a in AGENTS], 
                       color=[COLORS[a] for a in AGENTS])
        ax4.set_xticks(range(len(AGENTS)))
        ax4.set_xticklabels([AGENT_LABELS[a][:8] for a in AGENTS], fontsize=9)
        ax4.set_ylabel('Latency (s)')
        ax4.set_title('Response Time')
        for bar in bars:
            ax4.annotate(f'{bar.get_height():.1f}s', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 2), textcoords='offset points', ha='center', fontsize=9)
    
    # Panel 5: Radar chart
    ax5 = fig.add_subplot(gs[1, :2], polar=True)
    metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_token_f1', 'Token F1'),
        ('quality_syntactic_validity', 'Syntax'),
        ('reliability_output_stability', 'Stability'),
        ('reliability_semantic_consistency', 'Consistency'),
    ]
    metrics = [(m, l) for m, l in metrics if m in df.columns]
    
    if metrics:
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]
        
        for agent in AGENTS:
            agent_data = df[df['agent'] == agent]
            values = [agent_data[m[0]].mean() for m in metrics]
            values += values[:1]
            ax5.plot(angles, values, 'o-', linewidth=2, label=AGENT_LABELS[agent], color=COLORS[agent])
            ax5.fill(angles, values, alpha=0.1, color=COLORS[agent])
        
        ax5.set_xticks(angles[:-1])
        ax5.set_xticklabels([m[1] for m in metrics], fontsize=9)
        ax5.set_ylim(0, 1.1)
        ax5.legend(loc='upper left', bbox_to_anchor=(-0.2, 1.1), fontsize=9)
        ax5.set_title('Multi-Metric Radar', y=1.1)
    
    # Panel 6: Difficulty heatmap
    ax6 = fig.add_subplot(gs[1, 2:])
    if 'functional_pass_at_1' in df.columns:
        pivot = df.pivot_table(values='functional_pass_at_1', index='difficulty', columns='agent', aggfunc='mean')
        if 'easy' in pivot.index:
            pivot = pivot.reindex(['easy', 'medium', 'hard'])
        pivot = pivot[[a for a in AGENTS if a in pivot.columns]]
        pivot.columns = [AGENT_LABELS[a][:8] for a in pivot.columns]
        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', ax=ax6, vmin=0, vmax=1,
                    cbar_kws={'shrink': 0.8})
        ax6.set_title('Pass@1 by Difficulty')
        ax6.set_ylabel('')
    
    # Panel 7: Similarity metrics
    ax7 = fig.add_subplot(gs[2, :2])
    sim_metrics = ['similarity_code_bleu', 'similarity_rouge_l', 'similarity_token_f1', 
                   'similarity_jaccard_similarity', 'similarity_sequence_similarity']
    sim_metrics = [m for m in sim_metrics if m in df.columns]
    
    if sim_metrics:
        x = np.arange(len(sim_metrics))
        width = 0.25
        
        for i, agent in enumerate(AGENTS):
            means = [df[df['agent'] == agent][m].mean() for m in sim_metrics]
            ax7.bar(x + i*width, means, width, label=AGENT_LABELS[agent], color=COLORS[agent], alpha=0.8)
        
        ax7.set_xticks(x + width)
        ax7.set_xticklabels([m.split('_')[-1].title() for m in sim_metrics], fontsize=9)
        ax7.set_ylabel('Score')
        ax7.set_title('Code Similarity Metrics')
        ax7.legend(fontsize=9)
        ax7.set_ylim(0, 1.1)
    
    # Panel 8: Quality metrics
    ax8 = fig.add_subplot(gs[2, 2:])
    qual_metrics = ['quality_syntactic_validity', 'quality_ast_node_similarity', 
                    'quality_ast_structure_match']
    qual_metrics = [m for m in qual_metrics if m in df.columns]
    
    if qual_metrics:
        x = np.arange(len(qual_metrics))
        width = 0.25
        
        for i, agent in enumerate(AGENTS):
            means = [df[df['agent'] == agent][m].mean() for m in qual_metrics]
            ax8.bar(x + i*width, means, width, label=AGENT_LABELS[agent], color=COLORS[agent], alpha=0.8)
        
        ax8.set_xticks(x + width)
        ax8.set_xticklabels(['Syntax Valid', 'AST Nodes', 'AST Structure'][:len(qual_metrics)], fontsize=9)
        ax8.set_ylabel('Score')
        ax8.set_title('Code Quality Metrics')
        ax8.legend(fontsize=9)
        ax8.set_ylim(0, 1.1)
    
    plt.suptitle('AgentBench-CLI: Comprehensive Analysis Dashboard', fontsize=16, y=0.98)
    plt.savefig(FIGURES_DIR / "comprehensive_dashboard.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "comprehensive_dashboard.pdf", bbox_inches='tight')
    plt.close()


def plot_all_metrics_summary(df: pd.DataFrame):
    """Create a large summary plot of all metrics."""
    print("  Creating all-metrics summary...")
    
    metrics = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'efficiency_', 'reliability_'))]
    metrics = [m for m in metrics if df[m].notna().sum() > 50]
    metrics = sorted(metrics)
    
    if not metrics:
        print("    Skipping - no metrics available")
        return
    
    fig, ax = plt.subplots(figsize=(16, len(metrics) * 0.4 + 2))
    
    y_positions = np.arange(len(metrics))
    height = 0.25
    
    for i, agent in enumerate(AGENTS):
        means = [df[df['agent'] == agent][m].mean() for m in metrics]
        ax.barh(y_positions + i*height, means, height, label=AGENT_LABELS[agent], 
                color=COLORS[agent], alpha=0.8)
    
    ax.set_yticks(y_positions + height)
    ax.set_yticklabels([m.replace('_', ' ').title() for m in metrics], fontsize=8)
    ax.set_xlabel('Score')
    ax.set_title('All Metrics Comparison')
    ax.legend(loc='lower right')
    ax.set_xlim(0, 1.5)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "all_metrics_summary.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "all_metrics_summary.pdf", bbox_inches='tight')
    plt.close()


def plot_category_summary(df: pd.DataFrame):
    """Create summary by metric category."""
    print("  Creating category summary...")
    
    categories = {
        'Functional': [c for c in df.columns if c.startswith('functional_')],
        'Similarity': [c for c in df.columns if c.startswith('similarity_')],
        'Quality': [c for c in df.columns if c.startswith('quality_')],
        'Efficiency': [c for c in df.columns if c.startswith('efficiency_')],
        'Reliability': [c for c in df.columns if c.startswith('reliability_')],
    }
    
    fig, axes = plt.subplots(1, 5, figsize=(20, 5))
    
    for ax, (cat_name, cat_metrics) in zip(axes, categories.items()):
        cat_metrics = [m for m in cat_metrics if m in df.columns and df[m].notna().sum() > 50]
        
        if not cat_metrics:
            ax.set_visible(False)
            continue
        
        # Calculate average score for category
        for agent in AGENTS:
            agent_data = df[df['agent'] == agent]
            scores = [agent_data[m].mean() for m in cat_metrics]
            avg_score = np.mean(scores)
            
            ax.bar(AGENTS.index(agent), avg_score, color=COLORS[agent], alpha=0.8)
        
        ax.set_xticks(range(len(AGENTS)))
        ax.set_xticklabels([AGENT_LABELS[a][:8] for a in AGENTS], fontsize=9)
        ax.set_ylabel('Avg Score')
        ax.set_title(f'{cat_name}\n({len(cat_metrics)} metrics)')
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Performance by Metric Category', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "category_summary.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "category_summary.pdf", bbox_inches='tight')
    plt.close()


def generate_latex_tables(df: pd.DataFrame):
    """Generate LaTeX tables for paper."""
    print("\nGenerating LaTeX tables...")
    
    key_metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('functional_first_pass_success', 'First Pass'),
        ('functional_mean_reciprocal_rank', 'MRR'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_rouge_l', 'ROUGE-L'),
        ('similarity_token_f1', 'Token F1'),
        ('quality_syntactic_validity', 'Syntax'),
        ('quality_ast_node_similarity', 'AST Sim'),
        ('reliability_output_stability', 'Stability'),
        ('latency_ms', 'Latency (ms)'),
    ]
    
    key_metrics = [(m, l) for m, l in key_metrics if m in df.columns]
    
    latex = r'''
\begin{table*}[t]
\centering
\caption{Comprehensive Benchmark Results (Mean $\pm$ Std)}
\label{tab:comprehensive}
\begin{tabular}{l''' + 'c' * len(AGENTS) + r'''}
\toprule
\textbf{Metric} & ''' + ' & '.join([f'\\textbf{{{AGENT_LABELS[a]}}}' for a in AGENTS]) + r''' \\
\midrule
'''
    
    for metric, label in key_metrics:
        row = [label]
        for agent in AGENTS:
            data = df[df['agent'] == agent][metric]
            mean = data.mean()
            std = data.std()
            if metric == 'latency_ms':
                row.append(f'{mean:.0f} $\\pm$ {std:.0f}')
            else:
                row.append(f'{mean:.3f} $\\pm$ {std:.3f}')
        latex += ' & '.join(row) + r' \\' + '\n'
    
    latex += r'''
\bottomrule
\end{tabular}
\end{table*}
'''
    
    with open(OUTPUT_DIR / "latex_tables.tex", 'w') as f:
        f.write(latex)
    
    print(f"  Saved LaTeX tables to {OUTPUT_DIR / 'latex_tables.tex'}")


def main():
    """Main analysis pipeline."""
    print("=" * 70)
    print("COMPREHENSIVE METRICS ANALYSIS")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    results, references, tasks = load_data()
    df = compute_metrics_for_all(results, references, tasks)
    
    df.to_csv(OUTPUT_DIR / "all_metrics.csv", index=False)
    print(f"\n✅ Saved metrics to {OUTPUT_DIR / 'all_metrics.csv'}")
    
    summary = create_summary_table(df)
    summary.to_csv(OUTPUT_DIR / "summary_stats.csv")
    print(f"✅ Saved summary to {OUTPUT_DIR / 'summary_stats.csv'}")
    
    print("\nGenerating visualizations...")
    
    # Individual metrics
    plot_metric_comparison(df, 'functional_pass_at_1', 'Pass@1 by Agent', 'metric_pass_at_1')
    plot_metric_comparison(df, 'similarity_code_bleu', 'CodeBLEU by Agent', 'metric_code_bleu')
    plot_metric_comparison(df, 'similarity_token_f1', 'Token F1 by Agent', 'metric_token_f1')
    plot_metric_comparison(df, 'reliability_output_stability', 'Stability by Agent', 'metric_stability')
    plot_metric_comparison(df, 'similarity_rouge_l', 'ROUGE-L by Agent', 'metric_rouge_l')
    plot_metric_comparison(df, 'similarity_jaccard_similarity', 'Jaccard Similarity by Agent', 'metric_jaccard')
    plot_metric_comparison(df, 'quality_maintainability_index', 'Maintainability Index by Agent', 'metric_maintainability')
    
    # Complex visualizations
    plot_radar_chart(df)
    plot_correlation_heatmap(df)
    plot_metric_distributions(df)
    plot_difficulty_breakdown(df)
    plot_scatter_matrix(df)
    rankings_df = plot_metric_rankings(df)
    plot_comprehensive_dashboard(df)
    plot_all_metrics_summary(df)
    plot_category_summary(df)
    
    rankings_df.to_csv(OUTPUT_DIR / "metric_rankings.csv", index=False)
    generate_latex_tables(df)
    
    # Print summary
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    all_metrics = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'efficiency_', 'reliability_'))]
    print(f"\n📊 Total metrics computed: {len(all_metrics)}")
    print(f"📊 Total observations: {len(df)}")
    
    print("\n📈 Key Results:")
    for agent in AGENTS:
        agent_df = df[df['agent'] == agent]
        print(f"\n  {AGENT_LABELS[agent]}:")
        if 'functional_pass_at_1' in df.columns:
            print(f"    Pass@1:    {agent_df['functional_pass_at_1'].mean():.3f}")
        if 'similarity_code_bleu' in df.columns:
            print(f"    CodeBLEU:  {agent_df['similarity_code_bleu'].mean():.3f}")
        if 'similarity_token_f1' in df.columns:
            print(f"    Token F1:  {agent_df['similarity_token_f1'].mean():.3f}")
        if 'reliability_output_stability' in df.columns:
            print(f"    Stability: {agent_df['reliability_output_stability'].mean():.3f}")
    
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"📁 Figures: {FIGURES_DIR}")
    
    figures = list(FIGURES_DIR.glob("*.png"))
    print(f"\n�� Generated {len(figures)} figures:")
    for f in sorted(figures):
        print(f"    - {f.name}")


if __name__ == "__main__":
    main()
