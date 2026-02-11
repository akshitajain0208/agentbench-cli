"""Re-run only failed/empty Codex CLI tasks - Using codex exec."""

import json
import subprocess
import time
import tempfile
import os
from pathlib import Path

TASKS_FILE = Path("benchmark/v0.1.0/codegen-core/tasks.jsonl")
RESULTS_DIR = Path("results/pilot/codex_cli")
PROMPTS_DIR = Path("prompts/codegen-core")


def load_tasks():
    """Load all tasks."""
    tasks = []
    with open(TASKS_FILE) as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    return {t['task_id']: t for t in tasks}


def find_failed_tasks():
    """Find Codex tasks with empty or invalid results."""
    failed = []
    for f in RESULTS_DIR.glob("*.json"):
        try:
            with open(f) as file:
                data = json.load(file)
            if "pass_at_1" not in data.get("pass_at_k", {}):
                failed.append(f.stem)
        except:
            failed.append(f.stem)
    return sorted(failed)


def run_codex(prompt: str, timeout: int = 180) -> tuple:
    """Run Codex CLI exec."""
    try:
        result = subprocess.run(
            [
                "codex", "exec",
                "--full-auto",
                "--skip-git-repo-check",
                prompt
            ],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
        
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1
    except Exception as e:
        return "", str(e), -1


def extract_code(text: str) -> str:
    """Extract Python code from codex exec output."""
    if not text:
        return ""
    
    # The output has ```python ... ``` blocks
    if "```python" in text:
        parts = text.split("```python")
        for part in parts[1:]:
            if "```" in part:
                code = part.split("```")[0].strip()
                if code:
                    return code
    
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            code = parts[1].strip()
            if code.startswith("python\n"):
                code = code[7:]
            return code.strip()
    
    # Fallback: look for def
    if "def " in text:
        lines = text.split('\n')
        code_lines = []
        in_func = False
        for line in lines:
            if 'def ' in line:
                in_func = True
            if in_func:
                code_lines.append(line)
        return '\n'.join(code_lines).strip()
    
    return ""


def evaluate_code(code: str, task: dict) -> tuple:
    """Evaluate code against test cases."""
    if not code:
        return False, "Empty code"
    
    test_cases = task.get("test_cases", [])
    func_name = task["function_signature"].split("(")[0].replace("def ", "").strip()
    
    for i, tc in enumerate(test_cases):
        test_code = f'''
{code}

import json
inputs = json.loads('{json.dumps(tc["input"])}')
expected = json.loads('{json.dumps(tc["expected_output"])}')
result = {func_name}(**inputs)
assert result == expected, f"Test {i+1} failed: got {{result}}, expected {{expected}}"
print("PASS")
'''
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_code)
                f.flush()
                temp_path = f.name
            
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            os.unlink(temp_path)
            
            if "PASS" not in result.stdout:
                return False, result.stderr or result.stdout
        except Exception as e:
            return False, str(e)
    
    return True, "All tests passed"


def run_task(task_id: str, task: dict, num_runs: int = 3) -> dict:
    """Run a single task."""
    prompt_file = PROMPTS_DIR / task_id / "codex_cli.json"
    
    if not prompt_file.exists():
        print(f"  ⚠️ Prompt file not found: {prompt_file}")
        return None
    
    with open(prompt_file) as f:
        prompt_data = json.load(f)
    
    # FIX: Use user_prompt instead of prompt
    prompt = prompt_data.get("user_prompt") or prompt_data.get("prompt", "")
    
    if not prompt:
        print(f"  ⚠️ No prompt found in file")
        return None
    
    runs = []
    passing = 0
    latencies = []
    outputs = []
    errors = []
    
    for run_num in range(num_runs):
        start = time.time()
        stdout, stderr, code = run_codex(prompt)
        latency = (time.time() - start) * 1000
        
        extracted = extract_code(stdout)
        passed, error = evaluate_code(extracted, task)
        
        runs.append({
            "run": run_num + 1,
            "content": extracted,
            "latency_ms": latency,
            "passed": passed
        })
        
        latencies.append(latency)
        outputs.append(extracted)
        
        if passed:
            passing += 1
        else:
            errors.append(error)
        
        status = '✓' if passed else '✗'
        has_output = '📝' if extracted else '❌'
        print(f"    Run {run_num+1}: {status} {has_output} ({latency/1000:.1f}s)")
        time.sleep(1)
    
    # Calculate metrics
    unique_outputs = len(set(outputs))
    stability = 1.0 if unique_outputs == 1 else 1.0 - (unique_outputs - 1) / num_runs
    
    result = {
        "task_id": task_id,
        "agent": "codex_cli",
        "runs": runs,
        "pass_at_k": {
            "pass_at_1": passing / num_runs,
            "passing_samples": passing,
            "total_samples": num_runs,
            "errors": errors[:3]
        },
        "latency": {
            "median_ms": sorted(latencies)[len(latencies)//2],
            "mean_ms": sum(latencies) / len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies)
        },
        "determinism": {
            "stability_score": stability,
            "unique_outputs": unique_outputs
        }
    }
    
    # Save result
    output_file = RESULTS_DIR / f"{task_id}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


def main():
    print("=" * 60)
    print("RE-RUNNING FAILED CODEX TASKS")
    print("=" * 60)
    
    # Quick test
    print("\nTesting codex exec...")
    stdout, stderr, _ = run_codex("Write Python: def test(): return 42")
    extracted = extract_code(stdout)
    print(f"Test stdout: {stdout[:100]}..." if stdout else "No stdout")
    print(f"Extracted: {extracted[:50]}..." if extracted else "No code extracted")
    
    if not extracted:
        print("\n⚠️ Code extraction failed. Check codex exec output.")
        return
    
    print("✅ Test passed!\n")
    
    failed = find_failed_tasks()
    print(f"Found {len(failed)} failed tasks")
    
    if not failed:
        print("✅ All Codex results are complete!")
        return
    
    print("\nTasks to re-run:")
    for t in failed[:5]:
        print(f"  - {t}")
    if len(failed) > 5:
        print(f"  ... and {len(failed) - 5} more")
    
    response = input(f"\nRe-run {len(failed)} tasks? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    tasks = load_tasks()
    success = 0
    empty_streak = 0
    
    for i, task_id in enumerate(failed):
        print(f"\n[{i+1}/{len(failed)}] {task_id}")
        
        if task_id not in tasks:
            print("  ⚠️ Task not found in tasks.jsonl")
            continue
        
        result = run_task(task_id, tasks[task_id])
        
        if result:
            pass_rate = result["pass_at_k"]["pass_at_1"]
            has_content = any(r["content"] for r in result["runs"])
            print(f"  Result: {pass_rate*100:.0f}% Pass@1")
            
            if has_content:
                success += 1
                empty_streak = 0
            else:
                empty_streak += 1
                print(f"  ⚠️ No code extracted ({empty_streak} in a row)")
                if empty_streak >= 3:
                    print("  🛑 Multiple empty outputs - possible issue")
                    cont = input("  Continue? (y/n): ")
                    if cont.lower() != 'y':
                        break
        
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {success}/{len(failed)} tasks successful")
    print("=" * 60)
    
    remaining = find_failed_tasks()
    print(f"{len(remaining)} tasks still need results")


if __name__ == "__main__":
    main()
