
================================================================================
TEST CASE ISSUE SUMMARY (For Paper Methodology Section)
================================================================================

## Issues Identified:

### 1. HARD-009 (Palindrome Pairs)
   - **Problem**: Order-sensitive comparison for unordered output
   - **Impact**: Valid solutions rejected due to different ordering
   - **Fix**: Use set-based or sorted comparison
   - **Learning**: Specify output ordering in task description

### 2. HARD-012 (Number of Islands)
   - **Problem**: Type ambiguity (string '1' vs integer 1)
   - **Impact**: Some agents check for wrong type
   - **Fix**: Clarify in task description that grid uses strings
   - **Learning**: Be explicit about data types in function signature

## Implications for Benchmark Design:

1. **Type Clarity**: Always specify exact input/output types
2. **Order Sensitivity**: Explicitly state if output order matters
3. **Edge Cases**: Test with edge cases during task creation
4. **Flexible Evaluation**: Use type/order normalization when appropriate

## Paper Discussion Points:

- These issues highlight the importance of precise task specifications
- Even well-designed benchmarks can have subtle evaluation issues
- Agents may produce functionally correct but syntactically different outputs
- Recommend using flexible evaluators that handle:
  - Tuple vs list equivalence
  - Order-insensitive list comparison
  - Floating point tolerance
