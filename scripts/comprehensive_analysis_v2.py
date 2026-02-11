"""
Comprehensive Analysis with 25+ Metrics - Fixed Version.
Uses actual test pass results from benchmark runs.
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
    levenshtein_distance, code_bleu, rouge_l, token_f1_score,
    jaccard_similarity, sequence_similarity, syntactic_validity,
    ast_node_similarity, ast_structure_match, cyclomatic_complexity,
    halstead_metrics, maintainability_index, token_count, character_count,
    METRIC_DESCRIPTIONS
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
            ref_code = references.get(task_id, {}).get('reference_code', '')
            runs = result.get('runs', [])
            
            generated = ''
            outputs = []
            for run in runs:
                content = run.get('content', '')
                if content:
                    if not generated:
                        generated = content
                    outputs.append(content)
            
            if not generated:
                continue
            
            # USE ACTUAL PASS RESULTS FROM BENCHMARK
            pass_at_k_data = result.get('pass_at_k', {})
            pass_at_1 = pass_at_k_data.get('pass_at_1', 0)
            passing_samples = pass_at_k_data.get('passing_samples', 0)
            total_samples = pass_at_k_data.get('total_samples', len(runs))
            
            first_pass = 1.0 if runs and runs[0].get('passed', False) else 0.0
            
            mrr = 0.0
            for i, run in enumerate(runs):
                if run.get('passed', False):
                    mrr = 1.0 / (i + 1)
                    break
            
            precision, recall, f1 = token_f1_score(generated, ref_code)
            halstead = halstead_metrics(generated) or {'volume': 0, 'difficulty': 0, 'effort': 0}
            
            unique_outputs = len(set(outputs)) if outputs else 1
            stability = 1.0 - (unique_outputs - 1) / len(outputs) if len(outputs) > 1 else 1.0
            
            if len(outputs) >= 2:
                sims = []
                for i in range(len(outputs)):
                    for j in range(i+1, len(outputs)):
                        sims.append(sequence_similarity(outputs[i], outputs[j]))
                semantic_consistency = np.mean(sims) if sims else 1.0
            else:
                semantic_consistency = 1.0
            
            max_len = max(len(generated), len(ref_code)) if ref_code else 1
            ned = 1.0 - levenshtein_distance(generated, ref_code) / max_len if max_len > 0 else 1.0
            
            metrics = {
                'task_id': task_id,
                'agent': agent,
                'difficulty': tasks.get(task_id, {}).get('difficulty', 'unknown'),
                
                'functional_pass_at_1': pass_at_1,
                'functional_first_pass_success': first_pass,
                'functional_mean_reciprocal_rank': mrr,
                'functional_success_rate': passing_samples / total_samples if total_samples > 0 else 0,
                
                'similarity_normalized_edit_distance': ned,
                'similarity_sequence_similarity': sequence_similarity(generated, ref_code),
                'similarity_jaccard_similarity': jaccard_similarity(generated, ref_code),
                'similarity_code_bleu': code_bleu(generated, ref_code),
                'similarity_rouge_l': rouge_l(generated, ref_code),
                'similarity_token_precision': precision,
                'similarity_token_recall': recall,
                'similarity_token_f1': f1,
                
                'quality_syntactic_validity': syntactic_validity(generated),
                'quality_ast_node_similarity': ast_node_similarity(generated, ref_code),
                'quality_ast_structure_match': ast_structure_match(generated, ref_code),
                'quality_cyclomatic_complexity': cyclomatic_complexity(generated),
                'quality_halstead_volume': halstead['volume'],
                'quality_halstead_difficulty': halstead['difficulty'],
                'quality_halstead_effort': halstead['effort'],
                'quality_maintainability_index': maintainability_index(generated),
                
                'efficiency_token_count': token_count(generated),
                'efficiency_character_count': character_count(generated),
                
                'reliability_output_stability': stability,
                'reliability_unique_outputs': unique_outputs,
                'reliability_semantic_consistency': semantic_consistency,
                
                'latency_ms': result.get('latency', {}).get('median_ms', 0),
            }
            
            all_metrics.append(metrics)
    
    df = pd.DataFrame(all_metrics)
    print(f"  Computed metrics for {len(df)} task-agent pairs")
    
    return df


def create_visualizations(df: pd.DataFrame):
    """Generate all visualizations."""
    print("\nGenerating visualizations...")
    
    # 1. Main comparison bar chart
    print("  1. Main comparison...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    metrics_to_plot = [
        ('functional_pass_at_1', 'Pass@1 (Accuracy)', axes[0, 0]),
        ('similarity_code_bleu', 'CodeBLEU', axes[0, 1]),
        ('reliability_output_stability', 'Output Stability', axes[1, 0]),
        ('latency_ms', 'Latency (ms)', axes[1, 1]),
    ]
    
    for metric, title, ax in metrics_to_plot:
        means = df.groupby('agent')[metric].mean()
        stds = df.groupby('agent')[metric].std()
        
        x = np.arange(len(AGENTS))
        bars = ax.bar(x, [means.get(a, 0) for a in AGENTS], 
                      yerr=[stds.get(a, 0) for a in AGENTS],
                      color=[COLORS[a] for a in AGENTS],
                      capsize=5, alpha=0.8)
        
        ax.set_xticks(x)
        ax.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
        ax.set_title(title, fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        
        for bar in bars:
            height = bar.get_height()
            fmt = '.0f' if 'latency' in metric else '.3f'
            ax.annotate(f'{height:{fmt}}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=10)
    
    plt.suptitle('AgentBench-CLI: Main Performance Metrics', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_main_comparison.png", dpi=150)
    plt.savefig(FIGURES_DIR / "01_main_comparison.pdf")
    plt.close()
    
    # 2. Radar chart
    print("  2. Radar chart...")
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    radar_metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('functional_first_pass_success', 'First Pass'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_token_f1', 'Token F1'),
        ('quality_syntactic_validity', 'Syntax Valid'),
        ('reliability_output_stability', 'Stability'),
        ('reliability_semantic_consistency', 'Consistency'),
    ]
    
    angles = np.linspace(0, 2 * np.pi, len(radar_metrics), endpoint=False).tolist()
    angles += angles[:1]
    
    for agent in AGENTS:
        agent_data = df[df['agent'] == agent]
        values = [agent_data[m[0]].mean() for m in radar_metrics]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=AGENT_LABELS[agent], color=COLORS[agent])
        ax.fill(angles, values, alpha=0.15, color=COLORS[agent])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m[1] for m in radar_metrics])
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.set_title('Multi-Metric Performance Radar', size=14, y=1.08)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "02_radar_chart.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "02_radar_chart.pdf", bbox_inches='tight')
    plt.close()
    
    # 3. Similarity metrics comparison
    print("  3. Similarity metrics...")
    fig, ax = plt.subplots(figsize=(14, 6))
    
    sim_metrics = [
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_rouge_l', 'ROUGE-L'),
        ('similarity_token_f1', 'Token F1'),
        ('similarity_jaccard_similarity', 'Jaccard'),
        ('similarity_sequence_similarity', 'Sequence'),
        ('similarity_normalized_edit_distance', 'Edit Dist'),
    ]
    
    x = np.arange(len(sim_metrics))
    width = 0.25
    
    for i, agent in enumerate(AGENTS):
        means = [df[df['agent'] == agent][m[0]].mean() for m in sim_metrics]
        ax.bar(x + i*width, means, width, label=AGENT_LABELS[agent], color=COLORS[agent], alpha=0.8)
    
    ax.set_xticks(x + width)
    ax.set_xticklabels([m[1] for m in sim_metrics])
    ax.set_ylabel('Score')
    ax.set_title('Code Similarity Metrics Comparison')
    ax.legend()
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "03_similarity_metrics.png", dpi=150)
    plt.savefig(FIGURES_DIR / "03_similarity_metrics.pdf")
    plt.close()
    
    # 4. Quality metrics
    print("  4. Quality metrics...")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    qual_metrics = [
        ('quality_syntactic_validity', 'Syntax Valid'),
        ('quality_ast_node_similarity', 'AST Nodes'),
        ('quality_ast_structure_match', 'AST Structure'),
    ]
    qual_metrics = [(m, l) for m, l in qual_metrics if m in df.columns and df[m].notna().sum() > 50]
    
    if qual_metrics:
        x = np.arange(len(qual_metrics))
        width = 0.25
        
        for i, agent in enumerate(AGENTS):
            means = [df[df['agent'] == agent][m[0]].mean() for m in qual_metrics]
            ax.bar(x + i*width, means, width, label=AGENT_LABELS[agent], color=COLORS[agent], alpha=0.8)
        
        ax.set_xticks(x + width)
        ax.set_xticklabels([m[1] for m in qual_metrics])
        ax.set_ylabel('Score')
        ax.set_title('Code Quality Metrics Comparison')
        ax.legend()
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "04_quality_metrics.png", dpi=150)
    plt.savefig(FIGURES_DIR / "04_quality_metrics.pdf")
    plt.close()
    
    # 5. Difficulty breakdown heatmap
    print("  5. Difficulty breakdown...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for ax, metric, title in zip(axes, 
                                  ['functional_pass_at_1', 'similarity_code_bleu', 'reliability_output_stability'],
                                  ['Pass@1', 'CodeBLEU', 'Stability']):
        pivot = df.pivot_table(values=metric, index='difficulty', columns='agent', aggfunc='mean')
        if 'easy' in pivot.index:
            pivot = pivot.reindex(['easy', 'medium', 'hard'])
        pivot = pivot[[a for a in AGENTS if a in pivot.columns]]
        pivot.columns = [AGENT_LABELS[a][:8] for a in pivot.columns]
        
        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', ax=ax, vmin=0, vmax=1)
        ax.set_title(title)
        ax.set_ylabel('')
    
    plt.suptitle('Performance by Difficulty Level', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "05_difficulty_heatmap.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "05_difficulty_heatmap.pdf", bbox_inches='tight')
    plt.close()
    
    # 6. Box plots - FIXED
    print("  6. Box plots...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    box_metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_token_f1', 'Token F1'),
        ('quality_maintainability_index', 'Maintainability'),
        ('reliability_output_stability', 'Stability'),
        ('latency_ms', 'Latency (ms)'),
    ]
    
    for ax, (metric, title) in zip(axes, box_metrics):
        # Collect data and corresponding labels together
        data = []
        labels = []
        colors_used = []
        
        for agent in AGENTS:
            agent_data = df[df['agent'] == agent][metric].dropna().values
            if len(agent_data) > 0:
                data.append(agent_data)
                labels.append(AGENT_LABELS[agent][:8])
                colors_used.append(COLORS[agent])
        
        if data:
            bp = ax.boxplot(data, patch_artist=True)
            for patch, color in zip(bp['boxes'], colors_used):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_xticklabels(labels)
            ax.set_title(title)
            ax.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Metric Distributions', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "06_box_plots.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "06_box_plots.pdf", bbox_inches='tight')
    plt.close()
    
    # 7. Correlation heatmap
    print("  7. Correlation heatmap...")
    numeric_cols = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'reliability_'))]
    numeric_cols = [c for c in numeric_cols if df[c].notna().sum() > 50 and 'unique' not in c]
    
    if len(numeric_cols) > 2:
        corr = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(14, 12))
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        
        sns.heatmap(corr, mask=mask, cmap='RdYlBu_r', center=0,
                    annot=True, fmt='.2f', square=True, linewidths=0.5,
                    cbar_kws={"shrink": 0.8}, ax=ax, annot_kws={'size': 8})
        
        ax.set_title('Metric Correlation Matrix', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(fontsize=9)
        
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "07_correlation_matrix.png", dpi=150)
        plt.savefig(FIGURES_DIR / "07_correlation_matrix.pdf")
        plt.close()
    
    # 8. Metric rankings
    print("  8. Metric rankings...")
    metrics = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'reliability_'))]
    metrics = [m for m in metrics if 'unique' not in m and df[m].notna().sum() > 50]
    
    rankings = []
    for metric in metrics:
        means = df.groupby('agent')[metric].mean()
        reverse = any(r in metric for r in ['complexity', 'difficulty', 'effort', 'lines_ratio'])
        best = means.idxmin() if reverse else means.idxmax()
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
    ax.set_title(f'Metric Leadership ({len(metrics)} metrics)')
    ax.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "08_metric_rankings.png", dpi=150)
    plt.savefig(FIGURES_DIR / "08_metric_rankings.pdf")
    plt.close()
    
    # 9. Category summary
    print("  9. Category summary...")
    categories = {
        'Functional': [c for c in df.columns if c.startswith('functional_')],
        'Similarity': [c for c in df.columns if c.startswith('similarity_')],
        'Quality': [c for c in df.columns if c.startswith('quality_') and 'unique' not in c],
        'Reliability': [c for c in df.columns if c.startswith('reliability_') and 'unique' not in c],
    }
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    
    for ax, (cat_name, cat_metrics) in zip(axes, categories.items()):
        cat_metrics = [m for m in cat_metrics if m in df.columns and df[m].notna().sum() > 50]
        
        if not cat_metrics:
            ax.set_visible(False)
            continue
        
        for i, agent in enumerate(AGENTS):
            agent_data = df[df['agent'] == agent]
            scores = [agent_data[m].mean() for m in cat_metrics]
            avg_score = np.nanmean(scores)
            
            ax.bar(i, avg_score, color=COLORS[agent], alpha=0.8)
            ax.annotate(f'{avg_score:.2f}', xy=(i, avg_score), xytext=(0, 2),
                        textcoords='offset points', ha='center', fontsize=10)
        
        ax.set_xticks(range(len(AGENTS)))
        ax.set_xticklabels([AGENT_LABELS[a][:8] for a in AGENTS])
        ax.set_title(f'{cat_name}\n({len(cat_metrics)} metrics)')
        ax.set_ylim(0, 1.2)
        ax.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Average Score by Metric Category', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "09_category_summary.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "09_category_summary.pdf", bbox_inches='tight')
    plt.close()
    
    # 10. Comprehensive dashboard
    print("  10. Comprehensive dashboard...")
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.3)
    
    # Row 1: Key metrics
    for idx, (metric, title) in enumerate([
        ('functional_pass_at_1', 'Pass@1'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('reliability_output_stability', 'Stability'),
        ('latency_ms', 'Latency (ms)'),
    ]):
        ax = fig.add_subplot(gs[0, idx])
        means = df.groupby('agent')[metric].mean()
        bars = ax.bar(range(len(AGENTS)), [means.get(a, 0) for a in AGENTS], 
                      color=[COLORS[a] for a in AGENTS])
        ax.set_xticks(range(len(AGENTS)))
        ax.set_xticklabels([AGENT_LABELS[a][:6] for a in AGENTS], fontsize=9)
        ax.set_title(title)
        if 'latency' not in metric:
            ax.set_ylim(0, 1.1)
        for bar in bars:
            fmt = '.0f' if 'latency' in metric else '.2f'
            ax.annotate(f'{bar.get_height():{fmt}}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        xytext=(0, 2), textcoords='offset points', ha='center', fontsize=9)
    
    # Row 2: Radar and heatmap
    ax_radar = fig.add_subplot(gs[1, :2], polar=True)
    angles = np.linspace(0, 2 * np.pi, len(radar_metrics), endpoint=False).tolist()
    angles += angles[:1]
    
    for agent in AGENTS:
        agent_data = df[df['agent'] == agent]
        values = [agent_data[m[0]].mean() for m in radar_metrics]
        values += values[:1]
        ax_radar.plot(angles, values, 'o-', linewidth=2, label=AGENT_LABELS[agent], color=COLORS[agent])
        ax_radar.fill(angles, values, alpha=0.1, color=COLORS[agent])
    
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels([m[1] for m in radar_metrics], fontsize=9)
    ax_radar.set_ylim(0, 1.1)
    ax_radar.legend(loc='upper left', bbox_to_anchor=(-0.1, 1.1), fontsize=9)
    
    ax_heat = fig.add_subplot(gs[1, 2:])
    pivot = df.pivot_table(values='functional_pass_at_1', index='difficulty', columns='agent', aggfunc='mean')
    if 'easy' in pivot.index:
        pivot = pivot.reindex(['easy', 'medium', 'hard'])
    pivot = pivot[[a for a in AGENTS if a in pivot.columns]]
    pivot.columns = [AGENT_LABELS[a][:8] for a in pivot.columns]
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', ax=ax_heat, vmin=0, vmax=1)
    ax_heat.set_title('Pass@1 by Difficulty')
    
    # Row 3: Similarity and rankings
    ax_sim = fig.add_subplot(gs[2, :2])
    x = np.arange(len(sim_metrics))
    width = 0.25
    for i, agent in enumerate(AGENTS):
        means = [df[df['agent'] == agent][m[0]].mean() for m in sim_metrics]
        ax_sim.bar(x + i*width, means, width, label=AGENT_LABELS[agent], color=COLORS[agent], alpha=0.8)
    ax_sim.set_xticks(x + width)
    ax_sim.set_xticklabels([m[1] for m in sim_metrics], fontsize=9)
    ax_sim.set_title('Similarity Metrics')
    ax_sim.legend(fontsize=9)
    ax_sim.set_ylim(0, 1.1)
    
    ax_rank = fig.add_subplot(gs[2, 2:])
    x = np.arange(len(AGENTS))
    bars = ax_rank.bar(x, [counts.get(a, 0) for a in AGENTS], color=[COLORS[a] for a in AGENTS])
    ax_rank.set_xticks(x)
    ax_rank.set_xticklabels([AGENT_LABELS[a] for a in AGENTS])
    ax_rank.set_title(f'Metrics Won ({len(metrics)} total)')
    for bar in bars:
        ax_rank.annotate(f'{int(bar.get_height())}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 2), textcoords='offset points', ha='center', fontsize=12, fontweight='bold')
    
    plt.suptitle('AgentBench-CLI: Comprehensive Performance Dashboard (25+ Metrics)', fontsize=16, y=0.98)
    plt.savefig(FIGURES_DIR / "10_comprehensive_dashboard.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "10_comprehensive_dashboard.pdf", bbox_inches='tight')
    plt.close()
    
    # 11. All metrics horizontal bar
    print("  11. All metrics summary...")
    all_metrics_list = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'reliability_'))]
    all_metrics_list = [m for m in all_metrics_list if 'unique' not in m and df[m].notna().sum() > 50]
    all_metrics_list = sorted(all_metrics_list)
    
    fig, ax = plt.subplots(figsize=(14, len(all_metrics_list) * 0.35 + 2))
    
    y_pos = np.arange(len(all_metrics_list))
    height = 0.25
    
    for i, agent in enumerate(AGENTS):
        means = [df[df['agent'] == agent][m].mean() for m in all_metrics_list]
        ax.barh(y_pos + i*height, means, height, label=AGENT_LABELS[agent], color=COLORS[agent], alpha=0.8)
    
    ax.set_yticks(y_pos + height)
    ax.set_yticklabels([m.replace('_', ' ').replace('functional ', '').replace('similarity ', '')
                        .replace('quality ', '').replace('reliability ', '').title()[:30] 
                        for m in all_metrics_list], fontsize=8)
    ax.set_xlabel('Score')
    ax.set_title('All Metrics Comparison')
    ax.legend(loc='lower right')
    ax.set_xlim(0, max(1.2, df[all_metrics_list].max().max() * 1.1))
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "11_all_metrics.png", dpi=150, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "11_all_metrics.pdf", bbox_inches='tight')
    plt.close()
    
    return rankings_df


def generate_latex_tables(df: pd.DataFrame):
    """Generate LaTeX tables for paper."""
    print("\nGenerating LaTeX tables...")
    
    key_metrics = [
        ('functional_pass_at_1', 'Pass@1'),
        ('functional_first_pass_success', 'First Pass Success'),
        ('functional_mean_reciprocal_rank', 'MRR'),
        ('similarity_code_bleu', 'CodeBLEU'),
        ('similarity_rouge_l', 'ROUGE-L'),
        ('similarity_token_f1', 'Token F1'),
        ('similarity_jaccard_similarity', 'Jaccard'),
        ('quality_syntactic_validity', 'Syntactic Validity'),
        ('quality_ast_node_similarity', 'AST Node Sim'),
        ('quality_maintainability_index', 'Maintainability'),
        ('reliability_output_stability', 'Stability'),
        ('reliability_semantic_consistency', 'Consistency'),
        ('latency_ms', 'Latency (ms)'),
    ]
    
    latex = r'''
\begin{table*}[t]
\centering
\caption{Comprehensive Benchmark Results: 25+ Metrics Across 100 Tasks}
\label{tab:comprehensive}
\begin{tabular}{lccc}
\toprule
\textbf{Metric} & \textbf{Claude Code} & \textbf{Codex CLI} & \textbf{Gemini CLI} \\
\midrule
'''
    
    for metric, label in key_metrics:
        if metric not in df.columns:
            continue
        row = [label]
        for agent in AGENTS:
            data = df[df['agent'] == agent][metric]
            mean = data.mean()
            std = data.std()
            if 'latency' in metric:
                row.append(f'{mean:,.0f} $\\pm$ {std:,.0f}')
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
    
    print(f"  Saved to {OUTPUT_DIR / 'latex_tables.tex'}")


def main():
    """Main analysis pipeline."""
    print("=" * 70)
    print("COMPREHENSIVE METRICS ANALYSIS (25+ Metrics)")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    results, references, tasks = load_data()
    df = compute_metrics_for_all(results, references, tasks)
    
    df.to_csv(OUTPUT_DIR / "all_metrics.csv", index=False)
    print(f"\n✅ Saved metrics to {OUTPUT_DIR / 'all_metrics.csv'}")
    
    rankings_df = create_visualizations(df)
    rankings_df.to_csv(OUTPUT_DIR / "metric_rankings.csv", index=False)
    
    generate_latex_tables(df)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    all_metrics = [c for c in df.columns if c.startswith(('functional_', 'similarity_', 'quality_', 'efficiency_', 'reliability_'))]
    print(f"\n📊 Total metrics: {len(all_metrics)}")
    print(f"�� Total observations: {len(df)}")
    
    print("\n📈 Key Results:")
    for agent in AGENTS:
        agent_df = df[df['agent'] == agent]
        print(f"\n  {AGENT_LABELS[agent]}:")
        print(f"    Pass@1:    {agent_df['functional_pass_at_1'].mean():.3f}")
        print(f"    CodeBLEU:  {agent_df['similarity_code_bleu'].mean():.3f}")
        print(f"    Token F1:  {agent_df['similarity_token_f1'].mean():.3f}")
        print(f"    Stability: {agent_df['reliability_output_stability'].mean():.3f}")
        print(f"    Latency:   {agent_df['latency_ms'].mean():.0f}ms")
    
    figures = list(FIGURES_DIR.glob("*.png"))
    print(f"\n📁 Generated {len(figures)} figures in {FIGURES_DIR}")


if __name__ == "__main__":
    main()
