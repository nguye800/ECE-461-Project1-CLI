from __future__ import annotations
from dataclasses import dataclass
from Metric import Metric
from src.utils.hf_api import get_info


@dataclass
class PerformanceClaims(Metric):
    def __init__(self, metricName="Performance Claims", metricWeighting=0.2, benchmarks={"batch size": 64, "accuracy": 0.0, "time": 0.0}):
        super().__init__(metricName, 0, metricWeighting)
        self.benchmarks = benchmarks
        

    def evaluate(self, url: str) -> float:
        modelinfo = get_info(url)
        model_index = modelinfo.get("data", {}).get("model-index", None)
        model_index = modelinfo.get("data", {}).get("model-index", None)

        if not model_index:
            return 0.0  # No performance claims

        score = 0.0
        for entry in model_index:
            results = entry.get("results", [])
            for res in results:
                metrics = res.get("metrics", [])
                # Count each metric as 1 point
                score += len(metrics)
                # Bonus if task and dataset documented
                if res.get("task"):
                    score += 1
                if res.get("dataset"):
                    score += 1
        
        return score


