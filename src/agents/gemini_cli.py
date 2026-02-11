"""Gemini CLI agent wrapper."""

from typing import Optional, List
from datetime import datetime
import shutil
import subprocess

from .base import BaseAgent, AgentConfig, AgentResponse


class GeminiCLIAgent(BaseAgent):
    """Wrapper for Gemini CLI."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                name="Gemini CLI",
                command="gemini",
                default_args=[],
                timeout_seconds=120
            )
        super().__init__(config)
    
    def build_command(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs
    ) -> List[str]:
        """Build Gemini CLI command."""
        cmd = [self.config.command]
        
        # Add default args
        cmd.extend(self.config.default_args)

        # Force plain-text output for clean piped results
        cmd.extend(["--output-format", "text"])

        # Add prompt as positional argument (one-shot mode by default)
        cmd.append(prompt)

        return cmd
    
    async def execute(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs
    ) -> AgentResponse:
        """Execute prompt via Gemini CLI."""
        
        command = self.build_command(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        stdout, stderr, returncode, elapsed = await self._run_subprocess(command)
        
        success = returncode == 0 and bool(stdout.strip())
        
        return AgentResponse(
            content=stdout.strip() if success else "",
            raw_output=stdout,
            latency_seconds=elapsed,
            timestamp=datetime.now(),
            success=success,
            error_message=stderr if not success else None,
            metadata={
                "command": command,
                "returncode": returncode,
                "stderr": stderr
            }
        )
    
    def _detect_version(self) -> str:
        """Detect Gemini CLI version."""
        try:
            result = subprocess.run(
                [self.config.command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Gemini CLI is installed."""
        return shutil.which("gemini") is not None
