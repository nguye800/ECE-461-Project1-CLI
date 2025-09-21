from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

@dataclass
class PerformanceClaims(Metric):
    def __init__(self, metricName="Performance Claims", metricWeighting=0.2, benchmarks={"batch size": 64, "accuracy": 0.0, "time": 0.0}):
        super().__init__(metricName, 0, metricWeighting)
        self.benchmarks = benchmarks
        
    def getBenchmarks(self) -> dict:
        return self.benchmarks