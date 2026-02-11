"""Agent module - provides unified interface to all CLI agents."""

from typing import Dict, Type, Optional

from .base import BaseAgent, AgentConfig, AgentResponse
from .claude_code import ClaudeCodeAgent
from .codex_cli import CodexCLIAgent
from .gemini_cli import GeminiCLIAgent


# Registry of all available agents
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "claude_code": ClaudeCodeAgent,
    "codex_cli": CodexCLIAgent,
    "gemini_cli": GeminiCLIAgent,
}


def get_agent(agent_name: str, config: Optional[AgentConfig] = None) -> BaseAgent:
    """
    Factory function to get an agent by name.
    
    Args:
        agent_name: One of 'claude_code', 'codex_cli', 'gemini_cli'
        config: Optional custom configuration
        
    Returns:
        Initialized agent instance
    """
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Available agents: {list(AGENT_REGISTRY.keys())}"
        )
    
    agent_class = AGENT_REGISTRY[agent_name]
    return agent_class(config)


def list_available_agents() -> Dict[str, bool]:
    """
    List all agents and their availability status.
    
    Returns:
        Dict mapping agent names to availability (True if installed)
    """
    return {
        name: agent_class.is_available()
        for name, agent_class in AGENT_REGISTRY.items()
    }


__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentResponse",
    "ClaudeCodeAgent",
    "CodexCLIAgent",
    "GeminiCLIAgent",
    "get_agent",
    "list_available_agents",
    "AGENT_REGISTRY",
]
