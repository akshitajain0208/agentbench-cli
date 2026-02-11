"""Pass@k metric implementation."""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import subprocess
import tempfile
import os

from src.evaluation.code_utils import clean_code_output


@dataclass
class PassAtKResult:
    """Result of Pass@k evaluation."""
    pass_at_1: float
    pass_at_5: float
    pass_at_10: float
    total_samples: int
    passing_samples: int
    individual_results: List[bool]
    errors: List[Optional[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass_at_1": self.pass_at_1,
            "pass_at_5": self.pass_at_5,
            "pass_at_10": self.pass_at_10,
            "total_samples": self.total_samples,
            "passing_samples": self.passing_samples,
            "errors": [e for e in self.errors if e is not None],
        }


def estimate_pass_at_k(n: int, c: int, k: int) -> float:
    """Estimate Pass@k using the unbiased estimator."""
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def execute_python_code(
    code: str,
    test_code: str,
    timeout: int = 10,
    agent_name: Optional[str] = None,
) -> Tuple[bool, str]:
    """Execute Python code with test cases.

    Args:
        code: Raw code output from the agent.
        test_code: Generated assertion-based test code.
        timeout: Max seconds before the subprocess is killed.
        agent_name: Agent that produced *code* (used for cleaning).
    """
    code = clean_code_output(code, agent_name=agent_name)

    if not code:
        return False, "Empty code after cleaning"

    with tempfile.TemporaryDirectory() as tmpdir:
        solution_file = os.path.join(tmpdir, "solution.py")
        with open(solution_file, 'w') as f:
            f.write(code)

        test_file = os.path.join(tmpdir, "test_solution.py")
        full_test = f"from solution import *\n\n{test_code}"
        with open(test_file, 'w') as f:
            f.write(full_test)

        try:
            result = subprocess.run(
                ["python", test_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir
            )

            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            return False, str(e)


def generate_test_code(test_cases: List[Dict[str, Any]], func_name: str = "solution") -> str:
    """Generate Python test code from test cases."""
    lines = []

    for i, tc in enumerate(test_cases):
        if tc.get("is_hidden", False):
            continue

        input_data = tc["input"]
        expected = tc["expected_output"]

        if isinstance(input_data, dict):
            args = ", ".join(f"{k}={repr(v)}" for k, v in input_data.items())
            call = f"{func_name}({args})"
        else:
            call = f"{func_name}({repr(input_data)})"

        expected_repr = repr(expected)
        lines.append(f"# Test {i + 1}")
        lines.append(f"result_{i} = {call}")
        lines.append(f'expected_{i} = {expected_repr}')
        lines.append(f'assert result_{i} == expected_{i}, f"Test {i + 1} failed: got {{result_{i}}}, expected {{expected_{i}}}"')
        lines.append("")

    lines.append("print('All tests passed!')")
    return "\n".join(lines)


class PassAtKEvaluator:
    """Evaluator for Pass@k metrics."""

    def __init__(self, k_values: List[int] = None):
        self.k_values = k_values or [1, 5, 10]

    def evaluate(
        self,
        generated_codes: List[str],
        test_cases: List[Dict[str, Any]],
        func_name: str = "solution",
        timeout: int = 10,
        agent_name: Optional[str] = None,
    ) -> PassAtKResult:
        """Evaluate Pass@k for a list of generated code samples.

        Args:
            generated_codes: Raw code strings produced by the agent.
            test_cases: List of dicts with 'input' and 'expected_output'.
            func_name: Name of the function under test.
            timeout: Per-sample execution timeout in seconds.
            agent_name: Agent identifier (forwarded to code cleaning).
        """
        n = len(generated_codes)
        if n == 0:
            return PassAtKResult(
                pass_at_1=0.0, pass_at_5=0.0, pass_at_10=0.0,
                total_samples=0, passing_samples=0,
                individual_results=[], errors=[],
            )

        test_code = generate_test_code(test_cases, func_name)

        results = []
        errors: List[Optional[str]] = []
        for code in generated_codes:
            passed, error = execute_python_code(
                code, test_code, timeout, agent_name=agent_name
            )
            results.append(passed)
            errors.append(error if error else None)

        c = sum(results)

        pass_at_1 = estimate_pass_at_k(n, c, min(1, n))
        pass_at_5 = estimate_pass_at_k(n, c, min(5, n))
        pass_at_10 = estimate_pass_at_k(n, c, min(10, n))

        return PassAtKResult(
            pass_at_1=pass_at_1, pass_at_5=pass_at_5, pass_at_10=pass_at_10,
            total_samples=n, passing_samples=c,
            individual_results=results, errors=errors,
        )
