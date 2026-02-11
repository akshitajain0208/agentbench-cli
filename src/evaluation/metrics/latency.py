"""Latency metric implementation."""

from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np


@dataclass
class LatencyResult:
    """Result of latency measurement."""
    median_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    mean_ms: float
    std_ms: float
    min_ms: float
    max_ms: float
    samples: int
    raw_values_ms: List[float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "median_ms": round(self.median_ms, 2),
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "mean_ms": round(self.mean_ms, 2),
            "std_ms": round(self.std_ms, 2),
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "samples": self.samples,
        }


class LatencyEvaluator:
    """Evaluator for latency metrics."""
    
    def evaluate(self, latencies_seconds: List[float]) -> LatencyResult:
        """
        Calculate latency statistics from raw measurements.
        
        Args:
            latencies_seconds: List of latency measurements in seconds
            
        Returns:
            LatencyResult with all statistics in milliseconds
        """
        if not latencies_seconds:
            raise ValueError("No latency measurements provided")
        
        # Convert to milliseconds
        latencies_ms = [lat * 1000 for lat in latencies_seconds]
        arr = np.array(latencies_ms)
        
        return LatencyResult(
            median_ms=float(np.median(arr)),
            p50_ms=float(np.percentile(arr, 50)),
            p95_ms=float(np.percentile(arr, 95)),
            p99_ms=float(np.percentile(arr, 99)),
            mean_ms=float(np.mean(arr)),
            std_ms=float(np.std(arr)),
            min_ms=float(np.min(arr)),
            max_ms=float(np.max(arr)),
            samples=len(latencies_ms),
            raw_values_ms=latencies_ms
        )
