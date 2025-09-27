from __future__ import annotations
from dataclasses import dataclass
from Metric import Metric
from huggingface_hub import model_info


@dataclass
class PerformanceClaims(Metric):
    def __init__(self, metricName="Performance Claims", metricWeighting=0.2, benchmarks={"batch size": 64, "accuracy": 0.0, "time": 0.0}):
        super().__init__(metricName, 0, metricWeighting)
        self.benchmarks = benchmarks
        
    def getBenchmarks(self) -> dict:
        return self.benchmarks
    
    def evaluate(self, model_id: str) -> float:
        """Check if performance claims (eval results) exist in model-index."""
        try:
            info = model_info(model_id)
            card_data = getattr(info, "cardData", {})
            model_index = card_data.get("model-index", [])

            if not model_index:
                self.score = 0.0
                return self.score

            # Parse metrics (e.g., accuracy, f1, etc.)
            found_metrics = []
            for entry in model_index:
                results = entry.get("results", [])
                for result in results:
                    metrics = result.get("metrics", [])
                    for m in metrics:
                        metric_name = m.get("type")
                        metric_value = m.get("value")
                        if metric_name and metric_value is not None:
                            found_metrics.append(metric_value)

            if found_metrics:
                # normalize average metric value to [0,1] (assuming % metrics)
                avg_score = sum(found_metrics) / len(found_metrics)
                self.score = min(1.0, avg_score / 100.0)
            else:
                self.score = 0.0

        except Exception:
            self.score = 0.0

        return self.score