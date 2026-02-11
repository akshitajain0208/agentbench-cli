"""Determinism/output variance metric implementation."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter
import numpy as np


@dataclass
class DeterminismResult:
    """Result of determinism evaluation."""
    exact_match_rate: float  # Fraction matching most common output
    unique_outputs: int
    total_outputs: int
    most_common_frequency: float
    stability_score: float  # 1.0 = perfectly deterministic
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "exact_match_rate": round(self.exact_match_rate, 4),
            "unique_outputs": self.unique_outputs,
            "total_outputs": self.total_outputs,
            "most_common_frequency": round(self.most_common_frequency, 4),
            "stability_score": round(self.stability_score, 4),
        }


class DeterminismEvaluator:
    """Evaluator for output determinism/variance."""
    
    def evaluate(self, outputs: List[str]) -> DeterminismResult:
        """
        Evaluate determinism from multiple runs of the same prompt.
        
        Args:
            outputs: List of output strings from repeated runs
            
        Returns:
            DeterminismResult with variance statistics
        """
        if not outputs:
            raise ValueError("No outputs provided")
        
        n = len(outputs)
        
        # Normalize outputs (strip whitespace)
        normalized = [o.strip() for o in outputs]
        
        # Count unique outputs
        counter = Counter(normalized)
        unique_count = len(counter)
        
        # Most common output
        most_common, most_common_count = counter.most_common(1)[0]
        most_common_freq = most_common_count / n
        
        # Exact match rate (fraction matching most common)
        exact_match_rate = most_common_freq
        
        # Stability score using entropy
        if unique_count == 1:
            stability_score = 1.0
        else:
            # Calculate normalized entropy
            probs = np.array([count / n for count in counter.values()])
            entropy = -np.sum(probs * np.log2(probs))
            max_entropy = np.log2(n)  # Maximum when all outputs unique
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            stability_score = 1.0 - normalized_entropy
        
        return DeterminismResult(
            exact_match_rate=exact_match_rate,
            unique_outputs=unique_count,
            total_outputs=n,
            most_common_frequency=most_common_freq,
            stability_score=stability_score
        )
