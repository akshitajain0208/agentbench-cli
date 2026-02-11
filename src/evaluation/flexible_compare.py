
"""Flexible output comparison for benchmark evaluation."""

def normalize_value(val):
    """Normalize a value for comparison."""
    if isinstance(val, tuple):
        return list(normalize_value(x) for x in val)
    elif isinstance(val, list):
        return [normalize_value(x) for x in val]
    elif isinstance(val, set):
        return sorted([normalize_value(x) for x in val], key=str)
    return val


def compare_outputs(result, expected, order_sensitive=True):
    """
    Flexibly compare outputs.
    
    Args:
        result: Actual output from code
        expected: Expected output from test case
        order_sensitive: If False, sort lists before comparison
    
    Returns:
        True if outputs match
    """
    # Normalize both
    result = normalize_value(result)
    expected = normalize_value(expected)
    
    # Direct equality
    if result == expected:
        return True
    
    # Order-insensitive comparison for lists
    if not order_sensitive:
        if isinstance(result, list) and isinstance(expected, list):
            try:
                # Sort by string representation
                result_sorted = sorted(result, key=lambda x: str(x))
                expected_sorted = sorted(expected, key=lambda x: str(x))
                if result_sorted == expected_sorted:
                    return True
            except:
                pass
    
    return False


# Tasks that need order-insensitive comparison
ORDER_INSENSITIVE_TASKS = {
    'HARD-009',  # palindrome pairs
    'MED-010',   # permutations  
    'MED-027',   # subsets
}
