"""Statistical analysis for benchmark results."""

import json
import numpy as np
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_all_results(results_dir: Path) -> Dict[str, Dict]:
    """Load all results organized by agent."""
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


def get_common_tasks(results: Dict) -> set:
    """Get task IDs that all agents have results for."""
    task_sets = [set(tasks.keys()) for tasks in results.values()]
    return set.intersection(*task_sets) if task_sets else set()


def extract_metrics(results: Dict, common_only: bool = False) -> Dict[str, Dict[str, List[float]]]:
    """Extract metric arrays per agent."""
    common_tasks = get_common_tasks(results) if common_only else None
    metrics = {}
    
    for agent, tasks in results.items():
        pass_rates = []
        latencies = []
        stabilities = []
        task_ids = []
        
        for task_id, data in sorted(tasks.items()):
            if common_only and task_id not in common_tasks:
                continue
                
            task_ids.append(task_id)
            if data.get("pass_at_k"):
                pass_rates.append(data["pass_at_k"]["pass_at_1"])
            if data.get("latency"):
                latencies.append(data["latency"]["median_ms"])
            if data.get("determinism"):
                stabilities.append(data["determinism"]["stability_score"])
        
        metrics[agent] = {
            "pass_rates": pass_rates,
            "latencies": latencies,
            "stabilities": stabilities,
            "task_ids": task_ids,
        }
    
    return metrics


def compute_confidence_interval(data: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
    """Compute mean and confidence interval."""
    n = len(data)
    if n < 2:
        return np.mean(data) if data else 0, 0, 0
    
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    
    return mean, mean - h, mean + h


def perform_t_tests(metrics: Dict, metric_name: str) -> Dict:
    """Perform pairwise t-tests between agents."""
    agents = list(metrics.keys())
    results = {}
    
    for i, agent1 in enumerate(agents):
        for agent2 in agents[i+1:]:
            data1 = metrics[agent1][metric_name]
            data2 = metrics[agent2][metric_name]
            
            # Check lengths match
            if len(data1) != len(data2):
                results[f"{agent1}_vs_{agent2}"] = {
                    "t_statistic": float('nan'),
                    "p_value": float('nan'),
                    "cohens_d": float('nan'),
                    "significant_05": False,
                    "significant_01": False,
                    "error": f"Unequal lengths: {len(data1)} vs {len(data2)}"
                }
                continue
            
            if len(data1) < 2:
                continue
            
            # Paired t-test (same tasks)
            t_stat, p_value = stats.ttest_rel(data1, data2)
            
            # Effect size (Cohen's d)
            diff = np.array(data1) - np.array(data2)
            cohens_d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff) > 0 else 0
            
            results[f"{agent1}_vs_{agent2}"] = {
                "t_statistic": t_stat,
                "p_value": p_value,
                "cohens_d": cohens_d,
                "significant_05": p_value < 0.05,
                "significant_01": p_value < 0.01,
            }
    
    return results


def perform_anova(metrics: Dict, metric_name: str) -> Dict:
    """Perform one-way ANOVA across all agents."""
    groups = [metrics[agent][metric_name] for agent in metrics if metrics[agent][metric_name]]
    
    if len(groups) < 2:
        return {"f_statistic": 0, "p_value": 1.0, "significant": False}
    
    f_stat, p_value = stats.f_oneway(*groups)
    
    return {
        "f_statistic": f_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }


def print_statistical_report(metrics: Dict, metrics_common: Dict):
    """Print comprehensive statistical report."""
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    cohens_label = "Cohen's d"
    
    print("=" * 70)
    print("STATISTICAL ANALYSIS REPORT")
    print("=" * 70)
    
    # Descriptive Statistics (all data)
    print("\n## Descriptive Statistics with 95% Confidence Intervals (All Data)")
    print("-" * 70)
    
    for metric_name, metric_label in [
        ("pass_rates", "Pass@1"),
        ("latencies", "Latency (ms)"),
        ("stabilities", "Stability"),
    ]:
        print(f"\n### {metric_label}")
        header = f"{'Agent':<15} {'Mean':>10} {'Std':>10} {'95% CI':>20} {'N':>5}"
        print(header)
        print("-" * 60)
        
        for agent in agents:
            data = metrics[agent][metric_name]
            if not data:
                print(f"{agent:<15} {'N/A':>10}")
                continue
                
            mean, ci_low, ci_high = compute_confidence_interval(data)
            std = np.std(data, ddof=1) if len(data) > 1 else 0
            
            if metric_name == "pass_rates":
                print(f"{agent:<15} {mean*100:>9.1f}% {std*100:>9.1f}% [{ci_low*100:>6.1f}%, {ci_high*100:>6.1f}%] {len(data):>5}")
            elif metric_name == "latencies":
                print(f"{agent:<15} {mean:>10,.0f} {std:>10,.0f} [{ci_low:>8,.0f}, {ci_high:>8,.0f}] {len(data):>5}")
            else:
                print(f"{agent:<15} {mean*100:>9.1f}% {std*100:>9.1f}% [{ci_low*100:>6.1f}%, {ci_high*100:>6.1f}%] {len(data):>5}")
    
    # Common tasks count
    n_common = len(metrics_common["claude_code"]["task_ids"])
    print(f"\n\n## Paired Comparisons on Common Tasks (N={n_common})")
    print("-" * 70)
    
    # ANOVA Tests on common tasks
    print("\n### ANOVA Tests (Are there significant differences between agents?)")
    
    for metric_name, metric_label in [
        ("pass_rates", "Pass@1"),
        ("latencies", "Latency"),
        ("stabilities", "Stability"),
    ]:
        anova = perform_anova(metrics_common, metric_name)
        sig = "***" if anova["p_value"] < 0.001 else "**" if anova["p_value"] < 0.01 else "*" if anova["p_value"] < 0.05 else ""
        print(f"{metric_label:<15} F={anova['f_statistic']:>8.2f}, p={anova['p_value']:.4f} {sig}")
    
    print("\nSignificance: * p<0.05, ** p<0.01, *** p<0.001")
    
    # Pairwise T-Tests on common tasks
    print("\n\n### Pairwise Comparisons (Paired T-Tests)")
    
    for metric_name, metric_label in [
        ("pass_rates", "Pass@1"),
        ("latencies", "Latency"),
        ("stabilities", "Stability"),
    ]:
        print(f"\n#### {metric_label}")
        header = f"{'Comparison':<30} {'t-stat':>10} {'p-value':>10} {cohens_label:>10} {'Sig':>5}"
        print(header)
        print("-" * 65)
        
        t_tests = perform_t_tests(metrics_common, metric_name)
        for comparison, result in t_tests.items():
            if "error" in result:
                print(f"{comparison:<30} Error: {result['error']}")
                continue
            sig = "***" if result["p_value"] < 0.001 else "**" if result["p_value"] < 0.01 else "*" if result["p_value"] < 0.05 else ""
            print(f"{comparison:<30} {result['t_statistic']:>10.3f} {result['p_value']:>10.4f} {result['cohens_d']:>10.3f} {sig:>5}")
    
    # Effect Size Interpretation
    print("\n\n## Effect Size Interpretation (Cohen's d)")
    print("-" * 70)
    print("Small: |d| < 0.2")
    print("Medium: 0.2 <= |d| < 0.8")
    print("Large: |d| >= 0.8")


def print_latex_statistical_table(metrics: Dict, metrics_common: Dict):
    """Print LaTeX table with statistical results."""
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    n_common = len(metrics_common["claude_code"]["task_ids"])
    
    print("\n\n" + "=" * 70)
    print("LaTeX TABLES FOR PAPER")
    print("=" * 70)
    
    print(r"""
\begin{table}[h]
\centering
\caption{Performance Metrics with 95\% Confidence Intervals (N=100 tasks)}
\label{tab:stats}
\begin{tabular}{lccc}
\hline
\textbf{Metric} & \textbf{Claude Code} & \textbf{Codex CLI} & \textbf{Gemini CLI} \\
\hline""")
    
    for metric_name, metric_label, is_pct in [
        ("pass_rates", r"Pass@1 (\%)", True),
        ("stabilities", r"Stability (\%)", True),
        ("latencies", "Latency (ms)", False),
    ]:
        row = metric_label
        for agent in agents:
            data = metrics[agent][metric_name]
            if not data:
                row += " & N/A"
                continue
            mean, ci_low, ci_high = compute_confidence_interval(data)
            
            if is_pct:
                row += f" & {mean*100:.1f} [{ci_low*100:.1f}, {ci_high*100:.1f}]"
            else:
                row += f" & {mean:,.0f} [{ci_low:,.0f}, {ci_high:,.0f}]"
        
        print(row + r" \\")
    
    print(r"""\hline
\end{tabular}
\end{table}""")
    
    # Significance table
    print(f"""
\\begin{{table}}[h]
\\centering
\\caption{{Pairwise Statistical Significance on Common Tasks (N={n_common})}}
\\label{{tab:significance}}
\\begin{{tabular}}{{lccc}}
\\hline
\\textbf{{Comparison}} & \\textbf{{Pass@1}} & \\textbf{{Latency}} & \\textbf{{Stability}} \\\\
\\hline""")
    
    comparisons = [
        ("claude_code_vs_codex_cli", "Claude vs Codex"),
        ("claude_code_vs_gemini_cli", "Claude vs Gemini"),
        ("codex_cli_vs_gemini_cli", "Codex vs Gemini"),
    ]
    
    for comp_key, comp_name in comparisons:
        row = comp_name
        for metric_name in ["pass_rates", "latencies", "stabilities"]:
            t_tests = perform_t_tests(metrics_common, metric_name)
            if comp_key not in t_tests or "error" in t_tests.get(comp_key, {}):
                row += " & N/A"
                continue
            p = t_tests[comp_key]["p_value"]
            if p < 0.001:
                sig = "^{***}"
            elif p < 0.01:
                sig = "^{**}"
            elif p < 0.05:
                sig = "^{*}"
            else:
                sig = ""
            row += f" & {p:.3f}${sig}$"
        print(row + r" \\")
    
    print(r"""\hline
\multicolumn{4}{l}{\footnotesize $^{*}$p<0.05, $^{**}$p<0.01, $^{***}$p<0.001} \\
\end{tabular}
\end{table}""")


def main():
    """Run statistical analysis."""
    results_dir = Path("results/pilot")
    
    if not results_dir.exists():
        print("No results found. Run benchmark first.")
        return
    
    print("Loading results...")
    results = load_all_results(results_dir)
    
    print("Extracting metrics...")
    # All data
    metrics = extract_metrics(results, common_only=False)
    # Common tasks only (for paired tests)
    metrics_common = extract_metrics(results, common_only=True)
    
    # Verify data
    print("\nAll tasks:")
    for agent, data in metrics.items():
        print(f"  {agent}: {len(data['pass_rates'])} tasks")
    
    common_tasks = get_common_tasks(results)
    print(f"\nCommon tasks across all agents: {len(common_tasks)}")
    
    # Run analysis
    print_statistical_report(metrics, metrics_common)
    print_latex_statistical_table(metrics, metrics_common)
    
    # Save results
    output = {
        "n_total_tasks": {agent: len(data["pass_rates"]) for agent, data in metrics.items()},
        "n_common_tasks": len(common_tasks),
        "descriptive": {},
        "anova": {},
        "pairwise": {},
    }
    
    for agent in metrics:
        output["descriptive"][agent] = {}
        for metric_name in ["pass_rates", "latencies", "stabilities"]:
            data = metrics[agent][metric_name]
            if not data:
                continue
            mean, ci_low, ci_high = compute_confidence_interval(data)
            output["descriptive"][agent][metric_name] = {
                "mean": float(mean),
                "std": float(np.std(data, ddof=1)) if len(data) > 1 else 0,
                "ci_95_low": float(ci_low),
                "ci_95_high": float(ci_high),
                "n": len(data),
            }
    
    for metric_name in ["pass_rates", "latencies", "stabilities"]:
        anova_result = perform_anova(metrics_common, metric_name)
        output["anova"][metric_name] = {
            "f_statistic": float(anova_result["f_statistic"]),
            "p_value": float(anova_result["p_value"]),
            "significant": anova_result["significant"],
        }
        
        pairwise = perform_t_tests(metrics_common, metric_name)
        output["pairwise"][metric_name] = {}
        for k, v in pairwise.items():
            if "error" in v:
                output["pairwise"][metric_name][k] = {"error": v["error"]}
            else:
                output["pairwise"][metric_name][k] = {
                    "t_statistic": float(v["t_statistic"]),
                    "p_value": float(v["p_value"]),
                    "cohens_d": float(v["cohens_d"]),
                    "significant_05": v["significant_05"],
                    "significant_01": v["significant_01"],
                }
    
    output_file = results_dir / "statistical_analysis.json"
    with open(output_file, 'w') as f:
        json.dump({k: (bool(v) if isinstance(v, np.bool_) else v) for k, v in output.items()}, f, indent=2)
    
    print(f"\n\nStatistical analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
