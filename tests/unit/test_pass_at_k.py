"""Tests for src.evaluation.metrics.pass_at_k – Pass@k evaluation."""

import pytest
from src.evaluation.metrics.pass_at_k import (
    PassAtKEvaluator,
    PassAtKResult,
    estimate_pass_at_k,
    execute_python_code,
    generate_test_code,
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

CLAUDE_FIZZBUZZ = (
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

CODEX_TWO_SUM_RAW = (
    "def two_sum(nums: list, target: int) -> list:\n"
    "    lookup = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        diff = target - n\n"
    "        if diff in lookup:\n"
    "            return [lookup[diff], i]\n"
    "        lookup[n] = i\n"
)

GEMINI_TWO_SUM = (
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
    "This code works by using a hash map.\n"
)

# Deliberately broken code to test error tracking
BROKEN_CODE = (
    "```python\n"
    "def two_sum(nums, target):\n"
    "    return [0, 0]  # always wrong\n"
    "```"
)

SYNTAX_ERROR_CODE = "def two_sum(:"


# ── Test case fixtures ────────────────────────────────────────────────────

TWO_SUM_TEST_CASES = [
    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]},
    {"input": {"nums": [3, 2, 4], "target": 6}, "expected_output": [1, 2]},
    {"input": {"nums": [3, 3], "target": 6}, "expected_output": [0, 1]},
]

PALINDROME_TEST_CASES = [
    {"input": {"s": "A man, a plan, a canal: Panama"}, "expected_output": True},
    {"input": {"s": "race a car"}, "expected_output": False},
    {"input": {"s": ""}, "expected_output": True},
]

FIZZBUZZ_TEST_CASES = [
    {"input": {"n": 5}, "expected_output": ["1", "2", "Fizz", "4", "Buzz"]},
    {"input": {"n": 1}, "expected_output": ["1"]},
]


# ── estimate_pass_at_k ───────────────────────────────────────────────────


class TestEstimatePassAtK:
    def test_all_pass(self):
        assert estimate_pass_at_k(3, 3, 1) == 1.0

    def test_none_pass(self):
        assert estimate_pass_at_k(3, 0, 1) == 0.0

    def test_partial_pass(self):
        result = estimate_pass_at_k(5, 2, 1)
        assert 0.0 < result < 1.0

    def test_k_larger_than_failures(self):
        # 3 samples, 2 pass, k=2 → guaranteed at least one pass
        assert estimate_pass_at_k(3, 2, 2) == 1.0


# ── generate_test_code ────────────────────────────────────────────────────


class TestGenerateTestCode:
    def test_dict_input(self):
        code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        assert "two_sum(" in code
        assert "assert" in code
        assert "All tests passed!" in code

    def test_skips_hidden(self):
        cases = [
            {"input": {"x": 1}, "expected_output": 2},
            {"input": {"x": 2}, "expected_output": 3, "is_hidden": True},
        ]
        code = generate_test_code(cases, "foo")
        assert "Test 1" in code
        assert "Test 2" not in code

    def test_non_dict_input(self):
        cases = [{"input": 5, "expected_output": 10}]
        code = generate_test_code(cases, "double")
        assert "double(5)" in code


# ── execute_python_code ───────────────────────────────────────────────────


class TestExecutePythonCode:
    def test_passing_code_claude(self):
        test_code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        passed, error = execute_python_code(
            CLAUDE_TWO_SUM, test_code, agent_name="claude_code"
        )
        assert passed is True
        assert error == ""

    def test_passing_code_codex(self):
        test_code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        passed, error = execute_python_code(
            CODEX_TWO_SUM_RAW, test_code, agent_name="codex_cli"
        )
        assert passed is True
        assert error == ""

    def test_passing_code_gemini(self):
        test_code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        passed, error = execute_python_code(
            GEMINI_TWO_SUM, test_code, agent_name="gemini_cli"
        )
        assert passed is True
        assert error == ""

    def test_failing_code(self):
        test_code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        passed, error = execute_python_code(
            BROKEN_CODE, test_code, agent_name="claude_code"
        )
        assert passed is False
        assert error  # non-empty error message

    def test_syntax_error_code(self):
        test_code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        passed, error = execute_python_code(
            SYNTAX_ERROR_CODE, test_code, agent_name="codex_cli"
        )
        assert passed is False
        assert error

    def test_empty_code(self):
        test_code = generate_test_code(TWO_SUM_TEST_CASES, "two_sum")
        passed, error = execute_python_code("", test_code, agent_name="claude_code")
        assert passed is False
        assert "Empty code" in error

    def test_palindrome_claude(self):
        test_code = generate_test_code(PALINDROME_TEST_CASES, "is_palindrome")
        passed, error = execute_python_code(
            CLAUDE_PALINDROME, test_code, agent_name="claude_code"
        )
        assert passed is True

    def test_fizzbuzz_claude(self):
        test_code = generate_test_code(FIZZBUZZ_TEST_CASES, "fizzbuzz")
        passed, error = execute_python_code(
            CLAUDE_FIZZBUZZ, test_code, agent_name="claude_code"
        )
        assert passed is True


# ── PassAtKEvaluator ──────────────────────────────────────────────────────


class TestPassAtKEvaluator:
    def test_all_passing_claude(self):
        evaluator = PassAtKEvaluator()
        # 3 identical correct runs (like the real pilot)
        codes = [CLAUDE_TWO_SUM] * 3
        result = evaluator.evaluate(
            codes, TWO_SUM_TEST_CASES,
            func_name="two_sum", agent_name="claude_code",
        )
        assert result.pass_at_1 == 1.0
        assert result.passing_samples == 3
        assert result.total_samples == 3
        assert all(r is True for r in result.individual_results)
        assert all(e is None for e in result.errors)

    def test_mixed_passing_failing(self):
        evaluator = PassAtKEvaluator()
        codes = [CLAUDE_TWO_SUM, BROKEN_CODE, CLAUDE_TWO_SUM]
        result = evaluator.evaluate(
            codes, TWO_SUM_TEST_CASES,
            func_name="two_sum", agent_name="claude_code",
        )
        assert result.passing_samples == 2
        assert result.total_samples == 3
        assert result.individual_results == [True, False, True]
        # There should be exactly one non-None error
        non_none_errors = [e for e in result.errors if e is not None]
        assert len(non_none_errors) == 1

    def test_all_failing(self):
        evaluator = PassAtKEvaluator()
        codes = [BROKEN_CODE, BROKEN_CODE]
        result = evaluator.evaluate(
            codes, TWO_SUM_TEST_CASES,
            func_name="two_sum", agent_name="claude_code",
        )
        assert result.pass_at_1 == 0.0
        assert result.passing_samples == 0
        assert len(result.errors) == 2
        assert all(e is not None for e in result.errors)

    def test_empty_codes(self):
        evaluator = PassAtKEvaluator()
        result = evaluator.evaluate(
            [], TWO_SUM_TEST_CASES, func_name="two_sum",
        )
        assert result.total_samples == 0
        assert result.pass_at_1 == 0.0
        assert result.errors == []

    def test_to_dict_errors_field(self):
        evaluator = PassAtKEvaluator()
        codes = [CLAUDE_TWO_SUM, BROKEN_CODE]
        result = evaluator.evaluate(
            codes, TWO_SUM_TEST_CASES,
            func_name="two_sum", agent_name="claude_code",
        )
        d = result.to_dict()
        assert "errors" in d
        # to_dict filters out None errors
        assert len(d["errors"]) == 1
        assert isinstance(d["errors"][0], str)

    def test_cross_agent_same_task(self):
        """All three agents' outputs for two_sum should pass."""
        evaluator = PassAtKEvaluator()

        for code, agent in [
            (CLAUDE_TWO_SUM, "claude_code"),
            (CODEX_TWO_SUM_RAW, "codex_cli"),
            (GEMINI_TWO_SUM, "gemini_cli"),
        ]:
            result = evaluator.evaluate(
                [code], TWO_SUM_TEST_CASES,
                func_name="two_sum", agent_name=agent,
            )
            assert result.passing_samples == 1, f"{agent} should pass two_sum"
