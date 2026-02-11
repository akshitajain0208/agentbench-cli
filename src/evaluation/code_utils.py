"""Utilities for code extraction and processing from AI agent outputs."""

import ast
import re
from typing import Optional, Tuple


# Preamble lines agents commonly prepend before actual code
_PREAMBLE_PATTERNS = [
    re.compile(r"^here(?:'s| is)(?: the| my)? (?:the )?(?:code|solution|implementation|function|answer).*:?\s*$", re.IGNORECASE),
    re.compile(r"^solution:?\s*$", re.IGNORECASE),
    re.compile(r"^(?:the )?(?:code|implementation|answer):?\s*$", re.IGNORECASE),
    re.compile(r"^sure[,!.].*$", re.IGNORECASE),
    re.compile(r"^certainly[,!.].*$", re.IGNORECASE),
    re.compile(r"^of course[,!.].*$", re.IGNORECASE),
    re.compile(r"^below is.*:?\s*$", re.IGNORECASE),
    re.compile(r"^I'?(?:ll| will).*:?\s*$", re.IGNORECASE),
]

# Trailing explanation lines agents commonly append after code
_POSTAMBLE_PATTERNS = [
    re.compile(r"^this (?:code |function |solution )?(?:works|uses|takes|returns|handles|implements|checks).*", re.IGNORECASE),
    re.compile(r"^the (?:code |function |solution )?(?:works|uses|takes|returns|handles|implements|checks).*", re.IGNORECASE),
    re.compile(r"^explanation:?\s*$", re.IGNORECASE),
    re.compile(r"^how it works:?\s*$", re.IGNORECASE),
    re.compile(r"^note:?\s.*", re.IGNORECASE),
    re.compile(r"^let me (?:explain|know).*", re.IGNORECASE),
]


def extract_code_from_markdown(text: str, language: str = "python") -> str:
    """
    Extract code from markdown code blocks.

    Handles:
      - ```python\\ncode\\n```
      - ```\\ncode\\n```
      - Multiple blocks (returns the longest, which is typically the main function)

    If no code blocks are found, returns the original text stripped.
    """
    if not text:
        return ""

    pattern = r"```(?:" + re.escape(language) + r")?\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    if not matches:
        return text.strip()

    # Return the longest block – the main implementation is almost always
    # the longest; short blocks tend to be usage examples or test snippets.
    return max(matches, key=len).strip()


def _strip_preamble(text: str) -> str:
    """Remove common conversational preamble lines before code."""
    lines = text.split("\n")
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if any(p.match(stripped) for p in _PREAMBLE_PATTERNS):
            start = i + 1
            continue
        # Stop at the first line that doesn't match a preamble pattern
        break
    return "\n".join(lines[start:])


def _strip_postamble(text: str) -> str:
    """Remove trailing explanation lines after code."""
    lines = text.split("\n")
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped:
            end = i
            continue
        if any(p.match(stripped) for p in _POSTAMBLE_PATTERNS):
            end = i
            continue
        break
    return "\n".join(lines[:end])


def _find_contiguous_python(text: str) -> str:
    """
    Given text that may mix prose and code, extract the contiguous block of
    lines that look like Python source (starting from the first ``def``,
    ``class``, ``import``, or indented line).
    """
    lines = text.split("\n")
    code_start = None
    code_end = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        is_code_line = (
            stripped.startswith(("def ", "class ", "import ", "from ", "@"))
            or (stripped and line[0] in (" ", "\t"))
            or stripped.startswith(("#",))
            or stripped == ""
            or stripped.startswith(("return ", "if ", "for ", "while ", "elif ", "else:", "try:", "except ", "raise ", "with ", "yield ", "pass", "break", "continue"))
        )

        if code_start is None:
            if stripped.startswith(("def ", "class ", "import ", "from ", "@")):
                code_start = i
                code_end = i + 1
        else:
            if is_code_line:
                code_end = i + 1
            elif stripped == "":
                # blank line could be mid-function; keep going
                continue
            else:
                # hit prose – stop
                break

    if code_start is not None:
        return "\n".join(lines[code_start:code_end]).rstrip()
    return text.strip()


# ── Agent-specific extractors ──────────────────────────────────────────────


def extract_code_claude(text: str) -> str:
    """
    Extract Python code from Claude Code CLI output.

    Claude Code typically returns code wrapped in ```python ... ``` blocks.
    It may also include a brief preamble like "Here's the implementation:".
    """
    if not text:
        return ""

    # Try markdown extraction first – Claude almost always uses fenced blocks
    extracted = extract_code_from_markdown(text)
    if extracted != text.strip():
        return extracted

    # Fallback: strip preamble/postamble prose, then extract contiguous Python
    cleaned = _strip_preamble(text)
    cleaned = _strip_postamble(cleaned)
    return _find_contiguous_python(cleaned)


def extract_code_codex(text: str) -> str:
    """
    Extract Python code from OpenAI Codex CLI output.

    Codex CLI tends to return raw code directly or inside markdown blocks.
    It may prefix output with "# Solution" or similar comments.
    """
    if not text:
        return ""

    # Try markdown first
    extracted = extract_code_from_markdown(text)
    if extracted != text.strip():
        return extracted

    # Codex often returns nearly raw code; strip conversational wrappers
    cleaned = _strip_preamble(text)
    cleaned = _strip_postamble(cleaned)
    return _find_contiguous_python(cleaned)


def extract_code_gemini(text: str) -> str:
    """
    Extract Python code from Gemini CLI output.

    Gemini frequently wraps code in markdown blocks and adds explanations
    both before and after the code.
    """
    if not text:
        return ""

    # Try markdown first
    extracted = extract_code_from_markdown(text)
    if extracted != text.strip():
        return extracted

    # Gemini tends to be verbose; aggressively strip prose
    cleaned = _strip_preamble(text)
    cleaned = _strip_postamble(cleaned)
    return _find_contiguous_python(cleaned)


# ── Registry mapping agent names → extractors ─────────────────────────────

_AGENT_EXTRACTORS = {
    "claude_code": extract_code_claude,
    "codex_cli": extract_code_codex,
    "gemini_cli": extract_code_gemini,
}


# ── Public API ─────────────────────────────────────────────────────────────


def clean_code_output(text: str, agent_name: Optional[str] = None) -> str:
    """
    Main entry point: clean and extract Python code from agent output.

    Args:
        text: Raw output string from the agent.
        agent_name: One of 'claude_code', 'codex_cli', 'gemini_cli'.
                    When provided, uses the agent-specific extractor.

    Returns:
        Cleaned Python source code, or empty string if nothing usable found.
    """
    if not text or not text.strip():
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Agent-specific extraction
    if agent_name and agent_name in _AGENT_EXTRACTORS:
        code = _AGENT_EXTRACTORS[agent_name](text)
    else:
        # Generic path: try markdown, then fallback heuristics
        code = extract_code_from_markdown(text)
        if code == text.strip():
            code = _strip_preamble(code)
            code = _strip_postamble(code)
            code = _find_contiguous_python(code)

    return code.strip()


def validate_python_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Check whether *code* is syntactically valid Python.

    Returns:
        (True, None) if valid, or (False, error_message) if not.
    """
    if not code or not code.strip():
        return False, "Empty code"

    try:
        ast.parse(code)
        return True, None
    except SyntaxError as exc:
        location = ""
        if exc.lineno is not None:
            location = f" (line {exc.lineno}"
            if exc.offset is not None:
                location += f", col {exc.offset}"
            location += ")"
        return False, f"SyntaxError: {exc.msg}{location}"
