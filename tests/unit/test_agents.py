"""Tests for agent wrappers – build_command and availability."""

from src.agents.claude_code import ClaudeCodeAgent
from src.agents.codex_cli import CodexCLIAgent
from src.agents.gemini_cli import GeminiCLIAgent
from src.agents import get_agent, list_available_agents, AGENT_REGISTRY


# ── ClaudeCodeAgent ───────────────────────────────────────────────────────


class TestClaudeCodeAgent:
    def test_build_command_basic(self):
        agent = ClaudeCodeAgent()
        cmd = agent.build_command("Write hello world")
        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "Write hello world" in cmd

    def test_build_command_with_system_prompt(self):
        agent = ClaudeCodeAgent()
        cmd = agent.build_command(
            "Write hello world",
            system_prompt="You are a coding assistant."
        )
        assert "--system-prompt" in cmd
        idx = cmd.index("--system-prompt")
        assert cmd[idx + 1] == "You are a coding assistant."

    def test_build_command_no_system_prompt_when_none(self):
        agent = ClaudeCodeAgent()
        cmd = agent.build_command("Write hello world", system_prompt=None)
        assert "--system-prompt" not in cmd

    def test_is_available(self):
        # Just verify it returns a bool without crashing
        result = ClaudeCodeAgent.is_available()
        assert isinstance(result, bool)

    def test_default_config(self):
        agent = ClaudeCodeAgent()
        assert agent.config.name == "Claude Code"
        assert agent.config.command == "claude"
        assert agent.config.timeout_seconds == 120


# ── CodexCLIAgent ─────────────────────────────────────────────────────────


class TestCodexCLIAgent:
    def test_build_command_uses_exec(self):
        agent = CodexCLIAgent()
        cmd = agent.build_command("Write hello world")
        assert cmd[0] == "codex"
        assert cmd[1] == "exec"
        assert "Write hello world" in cmd

    def test_exec_is_second_arg(self):
        """exec must come right after the command, before default_args."""
        agent = CodexCLIAgent()
        cmd = agent.build_command("prompt text")
        assert cmd[:2] == ["codex", "exec"]

    def test_is_available(self):
        result = CodexCLIAgent.is_available()
        assert isinstance(result, bool)

    def test_default_config(self):
        agent = CodexCLIAgent()
        assert agent.config.name == "OpenAI Codex CLI"
        assert agent.config.command == "codex"


# ── GeminiCLIAgent ────────────────────────────────────────────────────────


class TestGeminiCLIAgent:
    def test_build_command_basic(self):
        agent = GeminiCLIAgent()
        cmd = agent.build_command("Write hello world")
        assert cmd[0] == "gemini"
        assert "Write hello world" in cmd

    def test_build_command_has_output_format(self):
        agent = GeminiCLIAgent()
        cmd = agent.build_command("prompt")
        assert "--output-format" in cmd
        idx = cmd.index("--output-format")
        assert cmd[idx + 1] == "text"

    def test_prompt_is_last_arg(self):
        agent = GeminiCLIAgent()
        cmd = agent.build_command("my prompt")
        assert cmd[-1] == "my prompt"

    def test_is_available(self):
        result = GeminiCLIAgent.is_available()
        assert isinstance(result, bool)

    def test_default_config(self):
        agent = GeminiCLIAgent()
        assert agent.config.name == "Gemini CLI"
        assert agent.config.command == "gemini"


# ── Agent registry ────────────────────────────────────────────────────────


class TestAgentRegistry:
    def test_get_agent_claude(self):
        agent = get_agent("claude_code")
        assert isinstance(agent, ClaudeCodeAgent)

    def test_get_agent_codex(self):
        agent = get_agent("codex_cli")
        assert isinstance(agent, CodexCLIAgent)

    def test_get_agent_gemini(self):
        agent = get_agent("gemini_cli")
        assert isinstance(agent, GeminiCLIAgent)

    def test_get_agent_unknown_raises(self):
        try:
            get_agent("unknown_agent")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown agent" in str(e)

    def test_list_available_agents(self):
        available = list_available_agents()
        assert set(available.keys()) == {"claude_code", "codex_cli", "gemini_cli"}
        for v in available.values():
            assert isinstance(v, bool)

    def test_registry_has_three_agents(self):
        assert len(AGENT_REGISTRY) == 3
