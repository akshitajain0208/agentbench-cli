"""
Comprehensive Code Evaluation Metrics for LLM Benchmarking.

Contains 20+ metrics across 5 categories:
1. Functional Correctness
2. Code Similarity
3. Code Quality
4. Efficiency
5. Reliability
"""

import ast
import re
import math
import difflib
from typing import Optional, Dict, Any, List, Tuple
from collections import Counter
import hashlib


# =============================================================================
# CATEGORY 1: FUNCTIONAL CORRECTNESS METRICS
# =============================================================================

def pass_at_k(n: int, c: int, k: int) -> float:
    """
    Calculate pass@k metric using unbiased estimator.
    
    Args:
        n: Total number of samples
        c: Number of correct samples
        k: k value for pass@k
    
    Returns:
        Probability that at least one of k samples passes
    """
    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def first_pass_success(runs: List[dict]) -> float:
    """
    First-pass success rate: Did the first attempt pass?
    
    Returns:
        1.0 if first run passed, 0.0 otherwise
    """
    if not runs:
        return 0.0
    return 1.0 if runs[0].get('passed', False) else 0.0


def mean_reciprocal_rank(runs: List[dict]) -> float:
    """
    Mean Reciprocal Rank: 1/rank of first correct answer.
    
    Returns:
        1/rank if any passed, 0 if none passed
    """
    for i, run in enumerate(runs):
        if run.get('passed', False):
            return 1.0 / (i + 1)
    return 0.0


def success_rate(runs: List[dict]) -> float:
    """Simple success rate: proportion of passing runs."""
    if not runs:
        return 0.0
    passed = sum(1 for r in runs if r.get('passed', False))
    return passed / len(runs)


# =============================================================================
# CATEGORY 2: CODE SIMILARITY METRICS
# =============================================================================

def exact_match(generated: str, reference: str) -> float:
    """
    Exact Match (EM): Binary score if normalized code matches exactly.
    """
    def normalize(code: str) -> str:
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Normalize whitespace
        code = ' '.join(code.split())
        return code.strip()
    
    return 1.0 if normalize(generated) == normalize(reference) else 0.0


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein (edit) distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    
    return prev_row[-1]


def normalized_edit_distance(generated: str, reference: str) -> float:
    """
    Normalized Edit Distance (NED): Edit distance / max length.
    Range: 0 (identical) to 1 (completely different)
    """
    dist = levenshtein_distance(generated, reference)
    max_len = max(len(generated), len(reference))
    return 1.0 - (dist / max_len) if max_len > 0 else 1.0


def character_error_rate(generated: str, reference: str) -> float:
    """
    Character Error Rate (CER): Edit distance / reference length.
    Lower is better. Can exceed 1.0 for longer generated text.
    """
    dist = levenshtein_distance(generated, reference)
    return dist / len(reference) if reference else 0.0


def sequence_similarity(generated: str, reference: str) -> float:
    """
    Sequence Similarity using SequenceMatcher.
    Range: 0 to 1 (1 = identical)
    """
    return difflib.SequenceMatcher(None, generated, reference).ratio()


def jaccard_similarity(generated: str, reference: str) -> float:
    """
    Jaccard Similarity on token sets.
    Range: 0 to 1 (1 = identical token sets)
    """
    gen_tokens = set(generated.split())
    ref_tokens = set(reference.split())
    
    if not gen_tokens and not ref_tokens:
        return 1.0
    if not gen_tokens or not ref_tokens:
        return 0.0
    
    intersection = len(gen_tokens & ref_tokens)
    union = len(gen_tokens | ref_tokens)
    
    return intersection / union


def token_f1_score(generated: str, reference: str) -> Tuple[float, float, float]:
    """
    Token-level Precision, Recall, and F1 Score.
    
    Returns:
        (precision, recall, f1)
    """
    gen_tokens = generated.split()
    ref_tokens = reference.split()
    
    if not gen_tokens and not ref_tokens:
        return 1.0, 1.0, 1.0
    if not gen_tokens:
        return 0.0, 0.0, 0.0
    if not ref_tokens:
        return 0.0, 0.0, 0.0
    
    gen_counter = Counter(gen_tokens)
    ref_counter = Counter(ref_tokens)
    
    common = sum((gen_counter & ref_counter).values())
    
    precision = common / len(gen_tokens)
    recall = common / len(ref_tokens)
    
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    
    return precision, recall, f1


def rouge_l(generated: str, reference: str) -> float:
    """
    ROUGE-L: Longest Common Subsequence based metric.
    Range: 0 to 1
    """
    def lcs_length(x: str, y: str) -> int:
        m, n = len(x), len(y)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if x[i-1] == y[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    if not generated or not reference:
        return 0.0
    
    lcs = lcs_length(generated, reference)
    precision = lcs / len(generated)
    recall = lcs / len(reference)
    
    if precision + recall == 0:
        return 0.0
    
    return 2 * precision * recall / (precision + recall)


def code_bleu(generated: str, reference: str, weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)) -> float:
    """
    CodeBLEU: BLEU score adapted for code.
    Includes n-gram precision for n=1,2,3,4.
    
    Range: 0 to 1
    """
    def get_ngrams(tokens: List[str], n: int) -> Counter:
        return Counter(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))
    
    gen_tokens = generated.split()
    ref_tokens = reference.split()
    
    if not gen_tokens:
        return 0.0
    
    precisions = []
    for n in range(1, 5):
        if len(gen_tokens) < n:
            precisions.append(0.0)
            continue
            
        gen_ngrams = get_ngrams(gen_tokens, n)
        ref_ngrams = get_ngrams(ref_tokens, n)
        
        matches = sum((gen_ngrams & ref_ngrams).values())
        total = sum(gen_ngrams.values())
        
        precisions.append(matches / total if total > 0 else 0.0)
    
    # Smoothed geometric mean
    log_precisions = []
    for p in precisions:
        log_precisions.append(math.log(p + 1e-10))
    
    weighted_log = sum(w * lp for w, lp in zip(weights, log_precisions))
    bleu = math.exp(weighted_log)
    
    # Brevity penalty
    if len(gen_tokens) < len(ref_tokens):
        bp = math.exp(1 - len(ref_tokens) / len(gen_tokens))
    else:
        bp = 1.0
    
    return bleu * bp


# =============================================================================
# CATEGORY 3: CODE QUALITY METRICS
# =============================================================================

def syntactic_validity(code: str) -> float:
    """
    Syntactic Validity: Can the code be parsed?
    Returns: 1.0 if valid Python, 0.0 otherwise
    """
    try:
        ast.parse(code)
        return 1.0
    except SyntaxError:
        return 0.0


def ast_node_similarity(generated: str, reference: str) -> Optional[float]:
    """
    AST Node Similarity: Jaccard similarity of AST node types.
    
    Returns:
        Similarity score (0-1) or None if parsing fails
    """
    try:
        gen_ast = ast.parse(generated)
        ref_ast = ast.parse(reference)
    except SyntaxError:
        return None
    
    def get_node_types(tree: ast.AST) -> Counter:
        return Counter(type(node).__name__ for node in ast.walk(tree))
    
    gen_nodes = get_node_types(gen_ast)
    ref_nodes = get_node_types(ref_ast)
    
    intersection = sum((gen_nodes & ref_nodes).values())
    union = sum((gen_nodes | ref_nodes).values())
    
    return intersection / union if union > 0 else 0.0


def ast_structure_match(generated: str, reference: str) -> Optional[float]:
    """
    AST Structure Match: Compare tree structure, not just node types.
    
    Returns:
        Similarity score (0-1) or None if parsing fails
    """
    try:
        gen_ast = ast.parse(generated)
        ref_ast = ast.parse(reference)
    except SyntaxError:
        return None
    
    def tree_to_string(node: ast.AST, depth: int = 0) -> str:
        result = [f"{depth}:{type(node).__name__}"]
        for child in ast.iter_child_nodes(node):
            result.append(tree_to_string(child, depth + 1))
        return "|".join(result)
    
    gen_str = tree_to_string(gen_ast)
    ref_str = tree_to_string(ref_ast)
    
    return sequence_similarity(gen_str, ref_str)


def cyclomatic_complexity(code: str) -> Optional[int]:
    """
    Cyclomatic Complexity: Number of independent paths through code.
    
    Higher = more complex code
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    
    complexity = 1
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, 
                            ast.With, ast.Assert)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, 
                               ast.GeneratorExp)):
            complexity += sum(1 for _ in node.generators)
        elif isinstance(node, ast.IfExp):
            complexity += 1
    
    return complexity


def halstead_metrics(code: str) -> Optional[Dict[str, float]]:
    """
    Halstead Complexity Metrics.
    
    Returns dict with:
        - vocabulary: n1 + n2 (unique operators + operands)
        - length: N1 + N2 (total operators + operands)
        - volume: N * log2(n)
        - difficulty: (n1/2) * (N2/n2)
        - effort: difficulty * volume
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    
    operators = []
    operands = []
    
    for node in ast.walk(tree):
        # Operators
        if isinstance(node, ast.BinOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.UnaryOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.BoolOp):
            operators.append(type(node.op).__name__)
        elif isinstance(node, ast.Compare):
            for op in node.ops:
                operators.append(type(op).__name__)
        elif isinstance(node, ast.Call):
            operators.append('Call')
        elif isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
            operators.append(type(node).__name__)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            operators.append('def')
        elif isinstance(node, ast.Return):
            operators.append('return')
        
        # Operands
        elif isinstance(node, ast.Constant):
            operands.append(str(node.value))
        elif isinstance(node, ast.Name):
            operands.append(node.id)
    
    n1 = len(set(operators))  # Unique operators
    n2 = len(set(operands))   # Unique operands
    N1 = len(operators)        # Total operators
    N2 = len(operands)         # Total operands
    
    n = n1 + n2  # Vocabulary
    N = N1 + N2  # Length
    
    if n == 0 or n2 == 0:
        return {
            'vocabulary': 0,
            'length': 0,
            'volume': 0,
            'difficulty': 0,
            'effort': 0
        }
    
    volume = N * math.log2(n) if n > 0 else 0
    difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
    effort = difficulty * volume
    
    return {
        'vocabulary': n,
        'length': N,
        'volume': round(volume, 2),
        'difficulty': round(difficulty, 2),
        'effort': round(effort, 2)
    }


def maintainability_index(code: str) -> Optional[float]:
    """
    Maintainability Index (MI): Composite metric of code maintainability.
    
    MI = 171 - 5.2*ln(V) - 0.23*G - 16.2*ln(LOC)
    Where V=Halstead Volume, G=Cyclomatic Complexity, LOC=Lines of Code
    
    Range: 0-100 (higher = more maintainable)
    """
    halstead = halstead_metrics(code)
    cc = cyclomatic_complexity(code)
    
    if halstead is None or cc is None:
        return None
    
    loc = len([l for l in code.split('\n') if l.strip()])
    
    if loc == 0 or halstead['volume'] == 0:
        return 100.0
    
    mi = 171 - 5.2 * math.log(halstead['volume'] + 1) - 0.23 * cc - 16.2 * math.log(loc)
    
    # Normalize to 0-100
    return max(0, min(100, mi))


def code_lines_ratio(generated: str, reference: str) -> float:
    """
    Lines of Code Ratio: LOC(generated) / LOC(reference).
    
    Ideal = 1.0, <1 = more concise, >1 = more verbose
    """
    def count_loc(code: str) -> int:
        return len([l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')])
    
    gen_loc = count_loc(generated)
    ref_loc = count_loc(reference)
    
    if ref_loc == 0:
        return 1.0
    
    return gen_loc / ref_loc


# =============================================================================
# CATEGORY 4: EFFICIENCY METRICS
# =============================================================================

def token_count(code: str) -> int:
    """Count tokens in code."""
    return len(code.split())


def character_count(code: str) -> int:
    """Count non-whitespace characters."""
    return len(code.replace(' ', '').replace('\n', '').replace('\t', ''))


def token_efficiency(generated: str, reference: str) -> float:
    """
    Token Efficiency: reference_tokens / generated_tokens.
    
    >1 = generated is more concise
    <1 = generated is more verbose
    """
    gen_tokens = token_count(generated)
    ref_tokens = token_count(reference)
    
    if gen_tokens == 0:
        return 0.0
    
    return ref_tokens / gen_tokens


def compression_ratio(generated: str, reference: str) -> float:
    """
    Compression Ratio: len(reference) / len(generated).
    
    Measures how concise the generated code is.
    """
    if len(generated) == 0:
        return 0.0
    
    return len(reference) / len(generated)


# =============================================================================
# CATEGORY 5: RELIABILITY METRICS
# =============================================================================

def output_stability(outputs: List[str]) -> float:
    """
    Output Stability: How consistent are outputs across runs?
    
    Returns: 1.0 if all identical, lower for more variation
    """
    if not outputs:
        return 0.0
    
    # Normalize outputs
    normalized = [' '.join(o.split()) for o in outputs]
    unique = len(set(normalized))
    
    return 1.0 - (unique - 1) / len(outputs) if len(outputs) > 1 else 1.0


def output_hash_diversity(outputs: List[str]) -> int:
    """
    Count of unique output hashes.
    
    Lower = more deterministic
    """
    hashes = set()
    for output in outputs:
        h = hashlib.md5(output.encode()).hexdigest()
        hashes.add(h)
    return len(hashes)


def semantic_consistency(outputs: List[str]) -> float:
    """
    Semantic Consistency: Average pairwise similarity of outputs.
    
    High = outputs are semantically similar even if not identical
    """
    if len(outputs) < 2:
        return 1.0
    
    similarities = []
    for i in range(len(outputs)):
        for j in range(i + 1, len(outputs)):
            sim = sequence_similarity(outputs[i], outputs[j])
            similarities.append(sim)
    
    return sum(similarities) / len(similarities) if similarities else 1.0


# =============================================================================
# MASTER FUNCTION: Compute All Metrics
# =============================================================================

def compute_all_metrics(
    generated: str,
    reference: str,
    runs: List[dict],
    passed: bool
) -> Dict[str, Any]:
    """
    Compute all 20+ metrics for a single task.
    
    Args:
        generated: Generated code (best/first attempt)
        reference: Reference solution
        runs: List of run results with 'passed' and 'content' keys
        passed: Whether any run passed tests
    
    Returns:
        Dictionary with all metrics organized by category
    """
    outputs = [r.get('content', '') for r in runs if r.get('content')]
    passing_count = sum(1 for r in runs if r.get('passed', False))
    n_runs = len(runs)
    
    # Token-level metrics
    precision, recall, f1 = token_f1_score(generated, reference)
    
    # Halstead metrics
    halstead = halstead_metrics(generated) or {
        'vocabulary': 0, 'length': 0, 'volume': 0, 'difficulty': 0, 'effort': 0
    }
    
    metrics = {
        # Category 1: Functional Correctness
        'functional': {
            'pass_at_1': pass_at_k(n_runs, passing_count, 1) if n_runs > 0 else 0.0,
            'pass_at_3': pass_at_k(n_runs, passing_count, 3) if n_runs >= 3 else None,
            'pass_at_5': pass_at_k(n_runs, passing_count, 5) if n_runs >= 5 else None,
            'first_pass_success': first_pass_success(runs),
            'mean_reciprocal_rank': mean_reciprocal_rank(runs),
            'success_rate': success_rate(runs),
        },
        
        # Category 2: Code Similarity
        'similarity': {
            'exact_match': exact_match(generated, reference),
            'normalized_edit_distance': normalized_edit_distance(generated, reference),
            'character_error_rate': character_error_rate(generated, reference),
            'sequence_similarity': sequence_similarity(generated, reference),
            'jaccard_similarity': jaccard_similarity(generated, reference),
            'code_bleu': code_bleu(generated, reference),
            'rouge_l': rouge_l(generated, reference),
            'token_precision': precision,
            'token_recall': recall,
            'token_f1': f1,
        },
        
        # Category 3: Code Quality
        'quality': {
            'syntactic_validity': syntactic_validity(generated),
            'ast_node_similarity': ast_node_similarity(generated, reference),
            'ast_structure_match': ast_structure_match(generated, reference),
            'cyclomatic_complexity': cyclomatic_complexity(generated),
            'halstead_volume': halstead['volume'],
            'halstead_difficulty': halstead['difficulty'],
            'halstead_effort': halstead['effort'],
            'maintainability_index': maintainability_index(generated),
            'code_lines_ratio': code_lines_ratio(generated, reference),
        },
        
        # Category 4: Efficiency
        'efficiency': {
            'token_count': token_count(generated),
            'character_count': character_count(generated),
            'token_efficiency': token_efficiency(generated, reference),
            'compression_ratio': compression_ratio(generated, reference),
        },
        
        # Category 5: Reliability
        'reliability': {
            'output_stability': output_stability(outputs),
            'unique_outputs': output_hash_diversity(outputs),
            'semantic_consistency': semantic_consistency(outputs),
        },
    }
    
    return metrics


def get_flat_metrics(metrics: Dict[str, Any]) -> Dict[str, float]:
    """Flatten nested metrics dict to single level."""
    flat = {}
    for category, values in metrics.items():
        for name, value in values.items():
            if value is not None:
                flat[f"{category}_{name}"] = value
    return flat


# Metric descriptions for documentation
METRIC_DESCRIPTIONS = {
    'pass_at_1': 'Probability of passing with 1 attempt',
    'pass_at_3': 'Probability of passing within 3 attempts',
    'pass_at_5': 'Probability of passing within 5 attempts',
    'first_pass_success': 'Binary: first attempt passed (1) or not (0)',
    'mean_reciprocal_rank': '1/rank of first passing attempt',
    'success_rate': 'Proportion of runs that passed',
    'exact_match': 'Binary: normalized code matches exactly',
    'normalized_edit_distance': '1 - (edit_distance / max_length)',
    'character_error_rate': 'Edit distance / reference length',
    'sequence_similarity': 'SequenceMatcher ratio',
    'jaccard_similarity': 'Token set intersection / union',
    'code_bleu': 'BLEU score adapted for code',
    'rouge_l': 'LCS-based F1 score',
    'token_precision': 'Correct tokens / generated tokens',
    'token_recall': 'Correct tokens / reference tokens',
    'token_f1': 'Harmonic mean of precision and recall',
    'syntactic_validity': 'Code parses without errors (0/1)',
    'ast_node_similarity': 'Jaccard similarity of AST node types',
    'ast_structure_match': 'Tree structure similarity',
    'cyclomatic_complexity': 'Number of independent code paths',
    'halstead_volume': 'N * log2(vocabulary)',
    'halstead_difficulty': 'Code difficulty measure',
    'halstead_effort': 'Difficulty * Volume',
    'maintainability_index': 'Composite maintainability (0-100)',
    'code_lines_ratio': 'Generated LOC / Reference LOC',
    'token_count': 'Number of tokens in output',
    'character_count': 'Non-whitespace character count',
    'token_efficiency': 'Reference tokens / Generated tokens',
    'compression_ratio': 'Reference chars / Generated chars',
    'output_stability': 'Consistency across runs (0-1)',
    'unique_outputs': 'Number of distinct outputs',
    'semantic_consistency': 'Average pairwise similarity',
}
