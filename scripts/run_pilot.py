"""Run pilot benchmark to validate the pipeline."""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import list_available_agents
from src.evaluation.task_schema import TaskSuite, TaskCategory
from src.execution.runner import BenchmarkRunner


def print_header():
    """Print script header."""
    print("=" * 60)
    print("  AgentBench-CLI Pilot Run")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def check_agents():
    """Check which agents are available."""
    print("\n📋 Checking agent availability...")
    available = list_available_agents()
    
    for name, is_available in available.items():
        status = "✅ Available" if is_available else "❌ Not installed"
        print(f"   {name}: {status}")
    
    ready_agents = [name for name, avail in available.items() if avail]
    
    if not ready_agents:
        print("\n⚠️  No agents available!")
        print("   Install at least one agent to run the benchmark.")
        return []
    
    return ready_agents


def load_tasks():
    """Load the pilot task suite."""
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    
    if not tasks_file.exists():
        print(f"\n⚠️  Tasks file not found: {tasks_file}")
        print("   Run: python scripts/create_pilot_tasks.py")
        return None
    
    suite = TaskSuite.load(
        tasks_file,
        name="codegen-pilot",
        category=TaskCategory.CODEGEN_CORE,
        version="0.1.0"
    )
    
    print(f"\n📚 Loaded {len(suite)} tasks from {tasks_file}")
    return suite


def print_summary(results):
    """Print results summary."""
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    
    for agent_name, task_results in results.items():
        if not task_results:
            continue
            
        print(f"\n🤖 {agent_name}")
        print(f"   Tasks completed: {len(task_results)}")
        
        # Aggregate latency
        latencies = [r.latency["median_ms"] for r in task_results if r.latency]
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            print(f"   Avg latency: {avg_latency:.0f}ms")
        
        # Aggregate pass rate
        pass_rates = [r.pass_at_k["pass_at_1"] for r in task_results if r.pass_at_k]
        if pass_rates:
            avg_pass = sum(pass_rates) / len(pass_rates) * 100
            print(f"   Avg Pass@1: {avg_pass:.1f}%")
        
        # Determinism
        det_scores = [r.determinism["stability_score"] for r in task_results if r.determinism]
        if det_scores:
            avg_det = sum(det_scores) / len(det_scores) * 100
            print(f"   Avg Stability: {avg_det:.1f}%")


async def main():
    """Main entry point."""
    print_header()
    
    # Check agents
    ready_agents = check_agents()
    if not ready_agents:
        return
    
    # Load tasks
    task_suite = load_tasks()
    if task_suite is None:
        return
    
    # Configure runner
    print(f"\n🚀 Starting benchmark with {ready_agents}...")
    print(f"   Runs per task: 3")
    
    runner = BenchmarkRunner(
        agents=ready_agents,
        runs_per_task=3,
        output_dir=Path("results/pilot")
    )
    
    # Run benchmark
    results = await runner.run_benchmark(
        task_suite=task_suite,
        prompts_dir=Path("prompts/codegen-core")
    )
    
    # Print summary
    print_summary(results)
    
    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "agents": ready_agents,
        "tasks": len(task_suite),
        "runs_per_task": 3,
    }
    
    summary_path = Path("results/pilot/summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📁 Results saved to: results/pilot/")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
