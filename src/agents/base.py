"""Base agent interface and data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import subprocess
import time


@dataclass
class AgentResponse:
    """Standardized response from any agent."""
    content: str
    raw_output: str
    latency_seconds: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    token_count: Optional[int] = None
    cost_usd: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    command: str
    version: Optional[str] = None
    default_args: List[str] = field(default_factory=list)
    timeout_seconds: int = 120
    supports_temperature: bool = True
    supports_system_prompt: bool = True


class BaseAgent(ABC):
    """Abstract base class for all CLI agents."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self._version: Optional[str] = None
    
    @abstractmethod
    async def execute(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs
    ) -> AgentResponse:
        """Execute a prompt and return standardized response."""
        pass
    
    @abstractmethod
    def build_command(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs
    ) -> List[str]:
        """Build the CLI command for execution."""
        pass
    
    def get_version(self) -> str:
        """Get the agent's version string."""
        if self._version is None:
            self._version = self._detect_version()
        return self._version
    
    @abstractmethod
    def _detect_version(self) -> str:
        """Detect the installed version of the agent."""
        pass
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if the agent CLI is available."""
        return False
    
    async def _run_subprocess(
        self,
        command: List[str],
        input_text: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> tuple:
        """Run a subprocess and return (stdout, stderr, returncode, elapsed_time)."""
        timeout = timeout or self.config.timeout_seconds
        start_time = time.perf_counter()
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE if input_text else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=input_text.encode() if input_text else None),
                timeout=timeout
            )
            
            elapsed = time.perf_counter() - start_time
            return (
                stdout.decode('utf-8', errors='replace'),
                stderr.decode('utf-8', errors='replace'),
                process.returncode,
                elapsed
            )
            
        except asyncio.TimeoutError:
            process.kill()
            elapsed = time.perf_counter() - start_time
            return "", f"Timeout after {timeout}s", -1, elapsed
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return "", str(e), -1, elapsed
