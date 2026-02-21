# AgentBench-CLI

A benchmark framework for evaluating console-based AI coding agents. It measures how well Claude Code, Codex CLI, and Gemini CLI perform on real programming tasks, looking at whether they get the right answer, how fast they respond, and how consistent their outputs are across repeated runs.

## Motivation

There are plenty of benchmarks for LLMs on code generation (HumanEval, MBPP, SWE-bench), but none of them specifically target the CLI-based coding agents that developers actually use day to day. These tools wrap language models with extra capabilities like file I/O, shell access, and multi-turn reasoning, and they behave quite differently from raw model APIs. AgentBench-CLI fills that gap.

## What it measures

The benchmark evaluates three dimensions:

- **Functional correctness (Pass@k)** -- Does the generated code actually work? Measured using an unbiased estimator across multiple runs per task.
- **Latency** -- How long does the agent take to respond? Reported as median, P95, and P99 across all tasks.
- **Determinism** -- If you run the same prompt multiple times, do you get the same output? Measured using normalized entropy over repeated executions.

## Task suite

150 tasks across four categories:

| Category | Count | Description |
|----------|-------|-------------|
| Code generation | 100 | Write a function from a specification |
| Bug fixing | 20 | Find and fix a bug in given code |
| Refactoring | 15 | Restructure code while preserving behavior |
| Test generation | 15 | Write tests for a given function |

Difficulty breakdown: 35 easy, 56 medium, 59 hard.

Each task includes a description, function signature, constraints, test cases (some hidden), and a reference solution. Tasks are stored as JSONL in `benchmark/v0.1.0/codegen-core/tasks.jsonl`.

## Results

Results from our pilot study (150 tasks, 3 agents, 3 runs each = 1,350 total executions):

| Agent | Pass@1 | Median latency | Stability |
|-------|--------|----------------|-----------|
| Claude Code | 98.7% | 5,924 ms | 80.7% |
| Codex CLI | 95.7% | 3,178 ms | 41.7% |
| Gemini CLI | 95.0% | 17,114 ms | 12.2% |

The accuracy differences are not statistically significant (ANOVA p=0.24). The latency and stability differences are highly significant (p<0.001 for both). In short: all three agents are roughly equally accurate, but they differ a lot in speed and consistency. Codex is the fastest, Claude is the most reliable, and Gemini is the most variable.

## Project structure

```
agentbench-cli/
  benchmark/          Task definitions (JSONL + reference solutions)
  src/
    agents/           Wrappers for Claude Code, Codex CLI, Gemini CLI
    evaluation/       Task schemas, prompt generation, code extraction,
                      output comparison, and all metric implementations
    execution/        Benchmark runner that orchestrates everything
  configs/            YAML files for agent, metric, and experiment settings
  scripts/            Scripts for running benchmarks, analyzing results,
                      generating figures, and exporting data
  prompts/            Prompt templates used across agents
  tests/              Unit tests for metrics, code utilities, and agents
  results/            Raw results (JSON per task), CSV exports, figures
  paper/              Paper outline and structure
  docker/             Container setup for sandboxed execution
```

## Setup

Requires Python 3.9 or later.

```
git clone https://github.com/yourusername/agentbench-cli.git
cd agentbench-cli
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You also need the CLI agents installed and accessible on your PATH: `claude`, `codex`, and `gemini`.

## Running the benchmark

Run the full benchmark:

```
python scripts/run_pilot.py
```

This will execute each agent on every task (multiple runs per task), save results as JSON files under `results/pilot/`, and print a summary when finished.

## Analysis

After running the benchmark:

```
python scripts/analyze_results.py
python scripts/create_visualizations.py
python scripts/export_to_csv.py
```

`analyze_results.py` aggregates results and runs statistical tests. `create_visualizations.py` produces the figures used in the paper. `export_to_csv.py` writes everything out as CSV for further analysis in R, pandas, or whatever you prefer.

## Configuration

All settings live in YAML files under `configs/`:

- `agents.yaml` -- Agent commands, timeouts, and feature flags.
- `metrics.yaml` -- Which metrics to compute and their parameters.
- `experiments.yaml` -- Number of runs per task, temperature, random seeds, output paths.

## How it works

The benchmark runner loads the task suite, generates a standardized prompt for each agent, then calls each agent's CLI with that prompt. Agent output goes through a code extraction pipeline (stripping markdown fences, conversational preamble, trailing explanations) to isolate the actual code. That code is then tested against the task's test cases to determine correctness. Latency is measured wall-clock from invocation to completion. Determinism is computed by comparing outputs across repeated runs using entropy.

The agent wrappers use a simple base class with a registry pattern. Adding a new agent means writing a small subclass that knows how to build the right CLI command and parse the output.

## Tests

```
python -m pytest tests/
```

Covers the Pass@k estimator, code extraction logic for all three agents, and command building.

## License

MIT. See LICENSE for details.

## Citation

```
@article{agentbench-cli-2024,
  title={AgentBench-CLI: Benchmarking Console-Based AI Coding Agents},
  author={AgentBench-CLI Authors},
  year={2024}
}
```
