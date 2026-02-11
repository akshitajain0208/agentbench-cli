"""Prompt templates and generation for standardized agent evaluation."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from pathlib import Path
import json

from .task_schema import Task


@dataclass
class PromptTemplate:
    """Agent-specific prompt for a task."""
    task_id: str
    agent_name: str  # "claude_code", "codex_cli", "gemini_cli"
    
    system_prompt: Optional[str] = None
    user_prompt: str = ""
    
    # Agent-specific CLI arguments
    cli_args: Dict[str, Any] = field(default_factory=dict)
    
    # Documentation of adaptations made
    adaptations: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "cli_args": self.cli_args,
            "adaptations": self.adaptations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create PromptTemplate from dictionary."""
        return cls(
            task_id=data["task_id"],
            agent_name=data["agent_name"],
            system_prompt=data.get("system_prompt"),
            user_prompt=data.get("user_prompt", ""),
            cli_args=data.get("cli_args", {}),
            adaptations=data.get("adaptations", ""),
        )


class PromptGenerator:
    """Generate standardized prompts for all agents from a task."""
    
    # Default system prompts (semantically equivalent across agents)
    DEFAULT_SYSTEM_PROMPTS = {
        "claude_code": (
            "You are a coding assistant. Complete tasks precisely following "
            "all constraints. Output only the requested code unless asked for explanation."
        ),
        "codex_cli": (
            "You are a coding assistant. Complete tasks precisely following "
            "all constraints. Output only the requested code unless asked for explanation."
        ),
        "gemini_cli": (
            "You are a coding assistant. Complete tasks precisely following "
            "all constraints. Output only the requested code unless asked for explanation."
        ),
    }
    
    @classmethod
    def generate_user_prompt(cls, task: Task) -> str:
        """Generate the universal user prompt from a task."""
        parts = [task.description]
        
        if task.function_signature:
            parts.append(f"\nFunction signature: {task.function_signature}")
        
        if task.constraints:
            parts.append("\nConstraints:")
            for constraint in task.constraints:
                parts.append(f"- {constraint}")
        
        parts.append("\nOutput only the implementation, no explanations.")
        
        return "\n".join(parts)
    
    @classmethod
    def generate_prompts(cls, task: Task) -> Dict[str, PromptTemplate]:
        """Generate prompts for all three agents."""
        user_prompt = cls.generate_user_prompt(task)
        
        prompts = {}
        for agent_name in ["claude_code", "codex_cli", "gemini_cli"]:
            prompts[agent_name] = PromptTemplate(
                task_id=task.task_id,
                agent_name=agent_name,
                system_prompt=cls.DEFAULT_SYSTEM_PROMPTS[agent_name],
                user_prompt=user_prompt,
                cli_args={},
                adaptations="Standard template, no agent-specific adaptations required."
            )
        
        return prompts
    
    @classmethod
    def save_prompts(cls, prompts: Dict[str, PromptTemplate], output_dir: Path):
        """Save prompts to the registry structure."""
        task_id = list(prompts.values())[0].task_id
        task_dir = output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        for agent_name, prompt in prompts.items():
            prompt_file = task_dir / f"{agent_name}.json"
            with open(prompt_file, 'w') as f:
                json.dump(prompt.to_dict(), f, indent=2)
    
    @classmethod
    def load_prompt(cls, prompt_file: Path) -> PromptTemplate:
        """Load a prompt from file."""
        with open(prompt_file, 'r') as f:
            data = json.load(f)
        return PromptTemplate.from_dict(data)
