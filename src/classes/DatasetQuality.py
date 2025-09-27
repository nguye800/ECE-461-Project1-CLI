from __future__ import annotations
from dataclasses import dataclass
from Metric import Metric
from huggingface_hub import dataset_info

@dataclass
class DatasetQuality(Metric):
    def __init__(self, metricName="Dataset Quality", metricWeighting = 0.1, datasetShape=(0), datasetEntries=0):
        super().__init__(metricName, 0, metricWeighting)
        self.datasetShape = datasetShape
        self.datasetEntries = datasetEntries
        
    def getDatasetShape(self) -> tuple:
        return self.datasetShape

    def getDatsetEntries(self) -> int:
        return self.datasetEntries
    
    def evaluate(self, dataset_id: str) -> float:
        """Check quality of dataset via downloads, likes, and size."""
        try:
            info = dataset_info(dataset_id)

            downloads = getattr(info, "downloads", 0)
            likes = getattr(info, "likes", 0)
            license_ = getattr(info, "license", None)

            # heuristic scoring
            score = 0.0
            if downloads > 1000:
                score += 0.4
            elif downloads > 100:
                score += 0.2

            if likes > 50:
                score += 0.3
            elif likes > 10:
                score += 0.15

            if license_ is not None:
                score += 0.3

            self.score = min(1.0, score)
        except Exception:
            self.score = 0.0

        return self.score