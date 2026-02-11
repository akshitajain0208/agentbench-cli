# AgentBench-CLI: Benchmarking Console-Based AI Coding Agents

## ABSTRACT (250 words)

Console-based AI coding agents have emerged as powerful tools for software development, yet no standardized benchmark exists to evaluate their performance across multiple dimensions. We present AgentBench-CLI, a comprehensive benchmark framework for evaluating console-based AI coding agents on code generation tasks. Our benchmark comprises 100 carefully curated programming tasks spanning three difficulty levels (easy, medium, hard) and measures three critical dimensions: functional correctness (Pass@k), response latency, and output determinism.

We evaluate three prominent console-based agents—Claude Code, Codex CLI, and Gemini CLI—revealing significant trade-offs between speed and reliability. Our results show that while all agents achieve comparable accuracy (91-99% Pass@1, ANOVA p=0.24), they differ dramatically in latency (F=103.32, p<0.001) and determinism (F=120.40, p<0.001). Claude Code demonstrates the highest accuracy (98.7%) and stability (80.7%), Codex CLI offers the fastest responses (3.2s, 1.9x faster than Claude), while Gemini CLI shows the highest variability (12.2% stability) despite competitive accuracy.

Our analysis reveals that wrong output errors dominate failures across all agents, with algorithmic complexity—not syntax—being the primary challenge. We identify critical benchmark design considerations including type clarity, order sensitivity, and flexible evaluation strategies. AgentBench-CLI provides researchers and practitioners with a reproducible framework for agent comparison, and our findings offer practical guidance for selecting agents based on use-case priorities.

**Keywords:** AI coding agents, benchmark, code generation, LLM evaluation, software engineering

---

## RESEARCH QUESTIONS

- **RQ1**: How do console-based AI coding agents compare in functional correctness?
- **RQ2**: What are the latency characteristics of different agents?
- **RQ3**: How deterministic are agent outputs across repeated executions?
- **RQ4**: What types of errors do agents make, and are there systematic patterns?

---

## PAPER STRUCTURE

### 1. INTRODUCTION (2 pages)
- Motivation: Rise of AI coding assistants, need for evaluation
- Gap: No benchmark for CLI agents
- Contributions: Benchmark + empirical study + error analysis

### 2. BACKGROUND & RELATED WORK (1.5 pages)
- AI Code Generation (LLMs, commercial tools)
- Existing Benchmarks (HumanEval, MBPP, SWE-bench)
- Console-Based Agents (Claude Code, Codex CLI, Gemini CLI)

### 3. BENCHMARK DESIGN (2 pages)
- Design Principles (fairness, reproducibility)
- Task Suite (100 tasks: 20 easy, 37 medium, 43 hard)
- Task Schema (JSON structure)
- Prompt Design (standardized across agents)

### 4. EVALUATION FRAMEWORK (1.5 pages)
- Pass@k Metric (unbiased estimator)
- Latency Measurement (median, P95, P99)
- Determinism Score (1 - normalized entropy)
- Statistical Methods (ANOVA, t-tests, Cohen d)

### 5. EXPERIMENTAL SETUP (1 page)
- Agents and versions
- Hardware/software environment
- Protocol (3 runs x 100 tasks x 3 agents = 900 executions)

### 6. RESULTS (3-4 pages)
- Overall Performance (Table: Pass@1, Latency, Stability)
- Statistical Significance (ANOVA results)
- Performance by Difficulty (heatmap)
- Latency Distribution (boxplots, CDF)
- Trade-off Analysis (Pareto frontier)

### 7. ERROR ANALYSIS (2 pages)
- Error Categories (wrong output, syntax, empty)
- Failure Patterns by Agent
- Common vs Unique Failures
- Insights for Benchmark Design

### 8. DISCUSSION (2 pages)
- Key Findings (speed vs reliability trade-off)
- Practical Recommendations
- Limitations
- Threats to Validity

### 9. CONCLUSION (0.5 pages)
- Summary
- Future Work

---

## KEY RESULTS TABLE

| Metric | Claude Code | Codex CLI | Gemini CLI |
|--------|-------------|-----------|------------|
| Pass@1 | **98.7%** | 95.7% | 95.0% |
| Latency | 5,924ms | **3,178ms** | 17,114ms |
| Stability | **80.7%** | 41.7% | 12.2% |
| Failed Tasks | 2 | 3 | 9 |

---

## STATISTICAL SIGNIFICANCE

| Metric | ANOVA F | p-value | Interpretation |
|--------|---------|---------|----------------|
| Pass@1 | 1.43 | 0.240 | NOT significant |
| Latency | 103.32 | <0.001 | Highly significant*** |
| Stability | 120.40 | <0.001 | Highly significant*** |

---

## PRACTICAL RECOMMENDATIONS

| Use Case | Best Agent | Why |
|----------|------------|-----|
| Interactive coding | Codex CLI | 1.9x faster responses |
| CI/CD pipelines | Claude Code | Most deterministic (80.7%) |
| Batch processing | Claude Code | Highest accuracy (98.7%) |
| Cost-sensitive | Gemini CLI | (add pricing data) |

---

## FIGURES FOR PAPER

1. **Main comparison** (01_main_comparison.pdf) - Section 6.1
2. **Difficulty breakdown** (04_difficulty_grouped_bars.pdf) - Section 6.3
3. **Heatmap** (08_difficulty_heatmap.pdf) - Section 6.3
4. **Latency boxplot** (07_boxplot_comparison.pdf) - Section 6.4
5. **Pareto frontier** (12_pareto_frontier.pdf) - Section 6.6
6. **Error analysis** (error_analysis_summary.pdf) - Section 7.1

---

## TARGET VENUES

### Tier 1 Journals (IF > 10)
- IEEE TSE (Transactions on Software Engineering)
- ACM TOSEM

### Tier 2 Journals (IF 6-10)  
- Empirical Software Engineering (EMSE)
- Journal of Systems and Software (JSS)
- Information and Software Technology (IST)

### Top Conferences
- ICSE, FSE, ASE, ISSTA

---

## ESTIMATED LENGTH: 18-20 pages
