# AgentBench-CLI 🤖

**A Comprehensive Benchmark for Console-Based AI Coding Agents**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tasks](https://img.shields.io/badge/tasks-100-green.svg)]()
[![Agents](https://img.shields.io/badge/agents-3-orange.svg)]()

---

## 🎯 Key Results

| Agent | Pass@1 | Latency | Stability |
|-------|--------|---------|-----------|
| **Claude Code** | **98.7%** 🏆 | 5,924ms | **80.7%** 🎯 |
| Codex CLI | 95.7% | **3,178ms** ⚡ | 41.7% |
| Gemini CLI | 95.0% | 17,114ms | 12.2% |

**Key Findings:**
- No significant accuracy difference (p=0.24)
- Significant latency difference (p<0.001) - Codex 1.9x faster
- Significant stability difference (p<0.001) - Claude most deterministic

---

## 📊 Overview

- **100 tasks** (20 easy, 37 medium, 43 hard)
- **3 agents**: Claude Code, Codex CLI, Gemini CLI
- **3 metrics**: Pass@k, Latency, Determinism
- **24 visualizations** for paper publication

---

## 🚀 Quick Start
```bash
# Clone and setup
git clone https://github.com/yourusername/agentbench-cli.git
cd agentbench-cli
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run benchmark
python scripts/run_pilot.py

# Analyze results
python scripts/analyze_results.py
python scripts/create_all_visualizations.py
```

---

## 📁 Structure
```
agentbench-cli/
├── benchmark/v0.1.0/codegen-core/tasks.jsonl  # 100 tasks
├── src/agents/                                 # Agent wrappers
├── src/evaluation/metrics/                     # Pass@k, Latency, Determinism
├── results/figures/                            # 24 visualizations
├── scripts/                                    # Run & analyze
└── paper/outline.md                            # Paper structure
```

---

## 📈 Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Pass@k** | Functional correctness | Unbiased estimator |
| **Latency** | Response time | Median, P95, P99 |
| **Stability** | Output consistency | 1 - normalized_entropy |

---

## 📊 Figures

| Key Figures | File |
|-------------|------|
| Main comparison | `01_main_comparison.pdf` |
| Difficulty breakdown | `04_difficulty_grouped_bars.pdf` |
| Heatmap | `08_difficulty_heatmap.pdf` |
| Pareto frontier | `12_pareto_frontier.pdf` |
| Summary dashboard | `15_summary_dashboard.pdf` |

---

## 🔬 Statistical Significance

| Metric | ANOVA F | p-value |
|--------|---------|---------|
| Pass@1 | 1.43 | 0.240 |
| Latency | 103.32 | <0.001*** |
| Stability | 120.40 | <0.001*** |

---

## 📝 Citation
```bibtex
@article{agentbench-cli-2024,
  title={AgentBench-CLI: Benchmarking Console-Based AI Coding Agents},
  author={Your Name},
  year={2024}
}
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)
