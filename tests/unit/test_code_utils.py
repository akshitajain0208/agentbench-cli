"""Tests for src.evaluation.code_utils – code extraction and cleaning."""

import pytest
from src.evaluation.code_utils import (
    extract_code_from_markdown,
    extract_code_claude,
    extract_code_codex,
    extract_code_gemini,
    clean_code_output,
    validate_python_syntax,
)


# ── Real agent output samples (taken from pilot results) ──────────────────

CLAUDE_TWO_SUM = (
    "```python\n"
    "def two_sum(nums: list, target: int) -> list:\n"
    "    seen = {}\n"
    "    for i, num in enumerate(nums):\n"
    "        complement = target - num\n"
    "        if complement in seen:\n"
    "            return [seen[complement], i]\n"
    "        seen[num] = i\n"
    "```"
)

CLAUDE_PALINDROME = (
    "```python\n"
    "def is_palindrome(s: str) -> bool:\n"
    "    filtered = [c.lower() for c in s if c.isalnum()]\n"
    "    return filtered == filtered[::-1]\n"
    "```"
)

CLAUDE_VALID_PARENS = (
    "```python\n"
    "def is_valid(s: str) -> bool:\n"
    "    if not s:\n"
    "        return True\n"
    "    \n"
    "    stack = []\n"
    "    matching = {')': '(', '}': '{', ']': '['}\n"
    "    \n"
    "    for char in s:\n"
    "        if char in '({[':\n"
    "            stack.append(char)\n"
    "        elif char in ')}]':\n"
    "            if not stack or stack[-1] != matching[char]:\n"
    "                return False\n"
    "            stack.pop()\n"
    "    \n"
    "    return len(stack) == 0\n"
    "```"
)

CLAUDE_WITH_PREAMBLE = (
    "Here's the implementation:\n"
    "\n"
    "```python\n"
    "def fizzbuzz(n: int) -> list:\n"
    "    result = []\n"
    "    for i in range(1, n + 1):\n"
    "        if i % 15 == 0:\n"
    "            result.append('FizzBuzz')\n"
    "        elif i % 3 == 0:\n"
    "            result.append('Fizz')\n"
    "        elif i % 5 == 0:\n"
    "            result.append('Buzz')\n"
    "        else:\n"
    "            result.append(str(i))\n"
    "    return result\n"
    "```"
)

# Simulate Codex returning raw code (no markdown wrapping)
CODEX_RAW = (
    "def two_sum(nums: list, target: int) -> list:\n"
    "    lookup = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        diff = target - n\n"
    "        if diff in lookup:\n"
    "            return [lookup[diff], i]\n"
    "        lookup[n] = i\n"
)

CODEX_WITH_PREAMBLE_RAW = (
    "Sure, here is the code:\n"
    "\n"
    "def reverse_list(lst: list) -> list:\n"
    "    left, right = 0, len(lst) - 1\n"
    "    while left < right:\n"
    "        lst[left], lst[right] = lst[right], lst[left]\n"
    "        left += 1\n"
    "        right -= 1\n"
    "    return lst\n"
)

# Simulate Gemini wrapping in markdown with verbose explanation
GEMINI_VERBOSE = (
    "Here's the solution:\n"
    "\n"
    "```python\n"
    "def two_sum(nums: list, target: int) -> list:\n"
    "    seen = {}\n"
    "    for idx, val in enumerate(nums):\n"
    "        complement = target - val\n"
    "        if complement in seen:\n"
    "            return [seen[complement], idx]\n"
    "        seen[val] = idx\n"
    "```\n"
    "\n"
    "This code works by using a hash map to store previously seen values.\n"
    "The time complexity is O(n).\n"
)

GEMINI_RAW_WITH_EXPLANATION = (
    "Below is the implementation:\n"
    "\n"
    "def is_palindrome(s: str) -> bool:\n"
    "    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n"
    "    return cleaned == cleaned[::-1]\n"
    "\n"
    "This function handles case-insensitive comparison.\n"
)

# Multiple code blocks – should pick the longest (the main one)
MULTI_BLOCK = (
    "Here's the solution:\n"
    "\n"
    "```python\n"
    "# helper\n"
    "pass\n"
    "```\n"
    "\n"
    "And the main implementation:\n"
    "\n"
    "```python\n"
    "def two_sum(nums: list, target: int) -> list:\n"
    "    seen = {}\n"
    "    for i, num in enumerate(nums):\n"
    "        complement = target - num\n"
    "        if complement in seen:\n"
    "            return [seen[complement], i]\n"
    "        seen[num] = i\n"
    "```\n"
    "\n"
    "```python\n"
    "print(two_sum([2,7,11,15], 9))\n"
    "```\n"
)


# ── extract_code_from_markdown ────────────────────────────────────────────


class TestExtractCodeFromMarkdown:
    def test_basic_python_block(self):
        result = extract_code_from_markdown(CLAUDE_TWO_SUM)
        assert "def two_sum" in result
        assert "```" not in result

    def test_no_code_block_returns_text(self):
        raw = "def foo():\n    return 1"
        assert extract_code_from_markdown(raw) == raw

    def test_empty_input(self):
        assert extract_code_from_markdown("") == ""
        assert extract_code_from_markdown(None) == ""

    def test_multiple_blocks_picks_longest(self):
        result = extract_code_from_markdown(MULTI_BLOCK)
        assert "def two_sum" in result
        # Should NOT be the tiny helper or the print snippet
        assert result.count("def ") == 1

    def test_unlabeled_code_block(self):
        text = "```\ndef greet():\n    return 'hi'\n```"
        result = extract_code_from_markdown(text)
        assert result == "def greet():\n    return 'hi'"


# ── extract_code_claude ───────────────────────────────────────────────────


class TestExtractCodeClaude:
    def test_standard_markdown_output(self):
        code = extract_code_claude(CLAUDE_TWO_SUM)
        assert code.startswith("def two_sum")
        assert "```" not in code

    def test_palindrome(self):
        code = extract_code_claude(CLAUDE_PALINDROME)
        assert "def is_palindrome" in code
        assert "isalnum" in code

    def test_valid_parens(self):
        code = extract_code_claude(CLAUDE_VALID_PARENS)
        assert "def is_valid" in code
        assert "stack" in code

    def test_with_preamble(self):
        code = extract_code_claude(CLAUDE_WITH_PREAMBLE)
        assert "def fizzbuzz" in code
        assert "Here's" not in code

    def test_empty(self):
        assert extract_code_claude("") == ""


# ── extract_code_codex ────────────────────────────────────────────────────


class TestExtractCodeCodex:
    def test_raw_code(self):
        code = extract_code_codex(CODEX_RAW)
        assert "def two_sum" in code

    def test_with_preamble_raw(self):
        code = extract_code_codex(CODEX_WITH_PREAMBLE_RAW)
        assert "def reverse_list" in code
        assert "Sure" not in code

    def test_empty(self):
        assert extract_code_codex("") == ""


# ── extract_code_gemini ───────────────────────────────────────────────────


class TestExtractCodeGemini:
    def test_markdown_with_explanation(self):
        code = extract_code_gemini(GEMINI_VERBOSE)
        assert "def two_sum" in code
        assert "hash map" not in code
        assert "```" not in code

    def test_raw_with_explanation(self):
        code = extract_code_gemini(GEMINI_RAW_WITH_EXPLANATION)
        assert "def is_palindrome" in code
        assert "case-insensitive" not in code

    def test_empty(self):
        assert extract_code_gemini("") == ""


# ── clean_code_output ─────────────────────────────────────────────────────


class TestCleanCodeOutput:
    def test_with_agent_name_claude(self):
        code = clean_code_output(CLAUDE_TWO_SUM, agent_name="claude_code")
        assert code.startswith("def two_sum")

    def test_with_agent_name_codex(self):
        code = clean_code_output(CODEX_RAW, agent_name="codex_cli")
        assert "def two_sum" in code

    def test_with_agent_name_gemini(self):
        code = clean_code_output(GEMINI_VERBOSE, agent_name="gemini_cli")
        assert "def two_sum" in code
        assert "hash map" not in code

    def test_without_agent_name_markdown(self):
        code = clean_code_output(CLAUDE_TWO_SUM)
        assert "def two_sum" in code

    def test_without_agent_name_raw(self):
        code = clean_code_output(CODEX_RAW)
        assert "def two_sum" in code

    def test_empty_string(self):
        assert clean_code_output("") == ""

    def test_none_text(self):
        assert clean_code_output(None) == ""

    def test_whitespace_only(self):
        assert clean_code_output("   \n\n  ") == ""

    def test_crlf_normalization(self):
        code = "def foo():\r\n    return 1\r\n"
        result = clean_code_output(code)
        assert "\r" not in result
        assert "def foo" in result

    def test_unknown_agent_falls_back_to_generic(self):
        code = clean_code_output(CLAUDE_TWO_SUM, agent_name="unknown_agent")
        assert "def two_sum" in code


# ── validate_python_syntax ────────────────────────────────────────────────


class TestValidatePythonSyntax:
    def test_valid_function(self):
        code = "def foo(x):\n    return x + 1"
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True
        assert error is None

    def test_syntax_error(self):
        code = "def foo(:\n    return"
        is_valid, error = validate_python_syntax(code)
        assert is_valid is False
        assert "SyntaxError" in error

    def test_empty_code(self):
        is_valid, error = validate_python_syntax("")
        assert is_valid is False
        assert error == "Empty code"

    def test_none_code(self):
        is_valid, error = validate_python_syntax(None)
        assert is_valid is False

    def test_real_claude_output(self):
        code = clean_code_output(CLAUDE_TWO_SUM, agent_name="claude_code")
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True

    def test_real_claude_palindrome(self):
        code = clean_code_output(CLAUDE_PALINDROME, agent_name="claude_code")
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True

    def test_real_claude_valid_parens(self):
        code = clean_code_output(CLAUDE_VALID_PARENS, agent_name="claude_code")
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True

    def test_real_codex_raw(self):
        code = clean_code_output(CODEX_RAW, agent_name="codex_cli")
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True

    def test_real_gemini_verbose(self):
        code = clean_code_output(GEMINI_VERBOSE, agent_name="gemini_cli")
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True

    def test_multiline_class(self):
        code = (
            "class Foo:\n"
            "    def bar(self):\n"
            "        pass\n"
        )
        is_valid, error = validate_python_syntax(code)
        assert is_valid is True

    def test_indentation_error(self):
        code = "def foo():\nreturn 1"
        is_valid, error = validate_python_syntax(code)
        # Python 3 raises IndentationError (subclass of SyntaxError)
        assert is_valid is False
        assert error is not None
