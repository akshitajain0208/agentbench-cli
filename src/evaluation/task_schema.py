"""Task and benchmark data schemas."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from pathlib import Path


class TaskCategory(Enum):
    """Categories of benchmark tasks."""
    CODEGEN_CORE = "codegen-core"
    DEBUG_FIX = "debug-fix"
    REFACTOR = "refactor"
    MATH_REASON = "math-reason"
    CLI_WORKFLOW = "cli-workflow"
    LONG_HORIZON = "long-horizon"


class Difficulty(Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class TestCase:
    """A single test case for a task."""
    input: Any
    expected_output: Any
    is_hidden: bool = False
    weight: float = 1.0


@dataclass
class Task:
    """A single benchmark task."""
    task_id: str
    category: TaskCategory
    difficulty: Difficulty
    description: str
    
    # Task specification
    function_signature: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    
    # Test cases
    test_cases: List[TestCase] = field(default_factory=list)
    
    # Ground truth
    reference_solution: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    estimated_time_seconds: int = 60
    requires_tools: List[str] = field(default_factory=list)
    
    # Contamination tracking
    source: Optional[str] = None
    creation_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "description": self.description,
            "function_signature": self.function_signature,
            "constraints": self.constraints,
            "test_cases": [
                {
                    "input": tc.input,
                    "expected_output": tc.expected_output,
                    "is_hidden": tc.is_hidden,
                    "weight": tc.weight
                }
                for tc in self.test_cases
            ],
            "reference_solution": self.reference_solution,
            "tags": self.tags,
            "estimated_time_seconds": self.estimated_time_seconds,
            "requires_tools": self.requires_tools,
            "source": self.source,
            "creation_date": self.creation_date,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary."""
        test_cases = [
            TestCase(
                input=tc["input"],
                expected_output=tc["expected_output"],
                is_hidden=tc.get("is_hidden", False),
                weight=tc.get("weight", 1.0)
            )
            for tc in data.get("test_cases", [])
        ]
        
        return cls(
            task_id=data["task_id"],
            category=TaskCategory(data["category"]),
            difficulty=Difficulty(data["difficulty"]),
            description=data["description"],
            function_signature=data.get("function_signature"),
            constraints=data.get("constraints", []),
            test_cases=test_cases,
            reference_solution=data.get("reference_solution"),
            tags=data.get("tags", []),
            estimated_time_seconds=data.get("estimated_time_seconds", 60),
            requires_tools=data.get("requires_tools", []),
            source=data.get("source"),
            creation_date=data.get("creation_date"),
        )


@dataclass
class TaskSuite:
    """A collection of related tasks."""
    name: str
    category: TaskCategory
    version: str
    tasks: List[Task]
    description: str = ""
    
    def save(self, path: Path):
        """Save task suite to JSONL file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            for task in self.tasks:
                f.write(json.dumps(task.to_dict()) + '\n')
    
    @classmethod
    def load(cls, path: Path, name: str, category: TaskCategory, version: str) -> "TaskSuite":
        """Load task suite from JSONL file."""
        tasks = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    tasks.append(Task.from_dict(json.loads(line)))
        return cls(name=name, category=category, version=version, tasks=tasks)
    
    def __len__(self) -> int:
        return len(self.tasks)
