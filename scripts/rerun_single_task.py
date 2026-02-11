"""Re-run a single task for all agents."""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import get_agent, list_available_agents
from src.evaluation.task_schema import Task, TaskCategory, Difficulty, TestCase
from src.evaluation.prompt_schema import PromptGenerator
from src.evaluation.metrics.pass_at_k import PassAtKEvaluator, generate_test_code
from src.evaluation.metrics.latency import LatencyEvaluator
from src.evaluation.metrics.determinism import DeterminismEvaluator


async def run_task_for_agent(agent_name: str, task: Task, runs: int = 3):
    """Run a single task for one agent."""
    agent = get_agent(agent_name)
    if not agent:
        print(f"  {agent_name}: Not available")
        return None
    
    # Generate prompt
    prompts = PromptGenerator.generate_prompts(task)
    prompt = prompts[agent_name]
    
    print(f"  {agent_name}: Running {runs} times...")
    
    results = []
    for i in range(runs):
        response = await agent.execute(prompt.user_prompt)
        results.append({
            "run_index": i,
            "content": response.content,
            "latency_seconds": response.latency_seconds,
            "success": response.success,
        })
        print(f"    Run {i+1}: {'✓' if response.success else '✗'} ({response.latency_seconds:.1f}s)")
    
    # Evaluate
    codes = [r["content"] for r in results]
    test_cases = [tc.__dict__ if hasattr(tc, '__dict__') else tc for tc in task.test_cases]
    
    # Extract function name from signature
    func_name = task.function_signature.split("(")[0].replace("def ", "").strip()
    
    pass_eval = PassAtKEvaluator()
    pass_result = pass_eval.evaluate(codes, test_cases, func_name=func_name, agent_name=agent_name)
    
    latency_eval = LatencyEvaluator()
    latency_result = latency_eval.evaluate([r["latency_seconds"] for r in results])
    
    det_eval = DeterminismEvaluator()
    det_result = det_eval.evaluate(codes)
    
    return {
        "task_id": task.task_id,
        "agent_name": agent_name,
        "runs": results,
        "pass_at_k": pass_result.to_dict(),
        "latency": latency_result.to_dict(),
        "determinism": det_result.to_dict(),
    }


async def main():
    task_id = "HARD-009"
    tasks_file = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
    results_dir = Path("results/pilot")
    
    print(f"Re-running {task_id}...")
    print("=" * 50)
    
    # Load task
    task = None
    with open(tasks_file, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if data['task_id'] == task_id:
                    task = Task(
                        task_id=data['task_id'],
                        category=TaskCategory(data['category']),
                        difficulty=Difficulty(data['difficulty']),
                        description=data['description'],
                        function_signature=data['function_signature'],
                        constraints=data.get('constraints', []),
                        test_cases=[TestCase(**tc) for tc in data['test_cases']],
                        tags=data.get('tags', []),
                        source=data.get('source', 'unknown'),
                        creation_date=data.get('creation_date', ''),
                    )
                    break
    
    if not task:
        print(f"Task {task_id} not found!")
        return
    
    print(f"\nTask: {task.description[:60]}...")
    print(f"Test cases: {len(task.test_cases)}")
    print()
    
    # Run for all agents
    agents = ["claude_code", "codex_cli", "gemini_cli"]
    
    for agent_name in agents:
        result = await run_task_for_agent(agent_name, task, runs=3)
        
        if result:
            # Save result
            output_file = results_dir / agent_name / f"{task_id}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"    Pass@1: {result['pass_at_k']['pass_at_1']*100:.0f}%")
            print(f"    Saved to: {output_file}")
        print()
    
    print("=" * 50)
    print("Re-run complete!")


if __name__ == "__main__":
    asyncio.run(main())
