"""Benchmark execution runner."""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import logging

from src.agents import get_agent, list_available_agents, AgentResponse
from src.evaluation.task_schema import Task, TaskSuite, TaskCategory
from src.evaluation.prompt_schema import PromptTemplate
from src.evaluation.metrics import (
    PassAtKEvaluator,
    LatencyEvaluator,
    DeterminismEvaluator
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    """Result of a single execution run."""
    task_id: str
    agent_name: str
    run_index: int
    content: str
    latency_seconds: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "run_index": self.run_index,
            "content": self.content,
            "latency_seconds": self.latency_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass 
class TaskResult:
    """Aggregated results for a task across all runs."""
    task_id: str
    agent_name: str
    runs: List[RunResult]
    pass_at_k: Optional[Dict] = None
    latency: Optional[Dict] = None
    determinism: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "runs": [r.to_dict() for r in self.runs],
            "pass_at_k": self.pass_at_k,
            "latency": self.latency,
            "determinism": self.determinism,
        }


class BenchmarkRunner:
    """Main benchmark execution engine."""
    
    def __init__(
        self,
        agents: List[str],
        runs_per_task: int = 3,
        output_dir: Path = Path("results/v0.1.0")
    ):
        self.agent_names = agents
        self.agents = {}
        self.runs_per_task = runs_per_task
        self.output_dir = Path(output_dir)
        
        # Initialize agents
        for name in agents:
            try:
                self.agents[name] = get_agent(name)
                logger.info(f"Initialized agent: {name}")
            except Exception as e:
                logger.warning(f"Could not initialize {name}: {e}")
        
        # Initialize evaluators
        self.pass_at_k_eval = PassAtKEvaluator()
        self.latency_eval = LatencyEvaluator()
        self.determinism_eval = DeterminismEvaluator()
    
    async def run_single(
        self,
        agent_name: str,
        prompt: PromptTemplate,
        run_index: int
    ) -> RunResult:
        """Execute a single run."""
        agent = self.agents[agent_name]
        
        response = await agent.execute(
            prompt=prompt.user_prompt,
            system_prompt=prompt.system_prompt
        )
        
        return RunResult(
            task_id=prompt.task_id,
            agent_name=agent_name,
            run_index=run_index,
            content=response.content,
            latency_seconds=response.latency_seconds,
            success=response.success,
            error_message=response.error_message
        )
    
    async def run_task(
        self,
        task: Task,
        agent_name: str,
        prompt: PromptTemplate
    ) -> TaskResult:
        """Run a task multiple times for one agent."""
        logger.info(f"Running {task.task_id} on {agent_name} ({self.runs_per_task} runs)")
        
        runs = []
        for i in range(self.runs_per_task):
            logger.info(f"  Run {i + 1}/{self.runs_per_task}")
            run_result = await self.run_single(agent_name, prompt, i)
            runs.append(run_result)
            
            # Brief delay between runs
            if i < self.runs_per_task - 1:
                await asyncio.sleep(0.5)
        
        # Create task result
        result = TaskResult(
            task_id=task.task_id,
            agent_name=agent_name,
            runs=runs
        )
        
        # Calculate metrics
        successful_outputs = [r.content for r in runs if r.success]
        
        # Latency (all runs)
        latencies = [r.latency_seconds for r in runs]
        result.latency = self.latency_eval.evaluate(latencies).to_dict()
        
        # Determinism (successful runs only)
        if len(successful_outputs) > 1:
            result.determinism = self.determinism_eval.evaluate(successful_outputs).to_dict()
        
        # Pass@k (if test cases exist)
        if task.test_cases and successful_outputs:
            # Extract function name from signature
            func_name = "solution"
            if task.function_signature:
                # Parse "def func_name(...)" to get func_name
                sig = task.function_signature.strip()
                if sig.startswith("def "):
                    func_name = sig[4:].split("(")[0].strip()
            
            test_cases = [
                {"input": tc.input, "expected_output": tc.expected_output}
                for tc in task.test_cases
            ]
            
            try:
                pass_result = self.pass_at_k_eval.evaluate(
                    successful_outputs,
                    test_cases,
                    func_name=func_name,
                    agent_name=agent_name,
                )
                result.pass_at_k = pass_result.to_dict()
            except Exception as e:
                logger.warning(f"Pass@k evaluation failed: {e}")
        
        return result
    
    def save_result(self, result: TaskResult):
        """Save a task result to file."""
        output_path = self.output_dir / result.agent_name / f"{result.task_id}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        logger.info(f"Saved result to {output_path}")
    
    async def run_benchmark(
        self,
        task_suite: TaskSuite,
        prompts_dir: Path
    ) -> Dict[str, List[TaskResult]]:
        """Run full benchmark for all agents."""
        results = {name: [] for name in self.agents}
        
        for task in task_suite.tasks:
            for agent_name in self.agents:
                # Load prompt
                prompt_file = prompts_dir / task.task_id / f"{agent_name}.json"
                if not prompt_file.exists():
                    logger.warning(f"Prompt not found: {prompt_file}")
                    continue
                
                with open(prompt_file) as f:
                    prompt_data = json.load(f)
                prompt = PromptTemplate.from_dict(prompt_data)
                
                # Run task
                try:
                    task_result = await self.run_task(task, agent_name, prompt)
                    results[agent_name].append(task_result)
                    self.save_result(task_result)
                except Exception as e:
                    logger.error(f"Failed {task.task_id} on {agent_name}: {e}")
        
        return results
