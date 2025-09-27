from __future__ import annotations
from dataclasses import dataclass
from Metric import Metric
from huggingface_hub import model_info

@dataclass
class AvailableDatasetAndCode(Metric):
    def __init__(self, metricName="Available Dataset and Code", metricWeighting=0.2, datasetAvailable=False, codeAvailable=False):
        super().__init__(metricName, 0, metricWeighting)
        self.datasetAvailable = datasetAvailable
        self.codeAvailable = codeAvailable
        
    def getDatasetAvailable(self) -> bool:
        return self.datasetAvailable
    
    def getCodeAvailable(self) -> bool:
        return self.codeAvailable

    def evaluate(self, model_id: str) -> float:
        """Check if dataset and code are available for this model."""
        info = model_info(model_id)
        tags = info.tags if hasattr(info, "tags") else []

        # Dataset check
        self.datasetAvailable = any("dataset:" in tag for tag in tags)

        # Code check
        self.codeAvailable = any("library_name:" in tag for tag in tags)

        # Scoring logic
        if self.datasetAvailable and self.codeAvailable:
            self.score = 1.0
        elif self.datasetAvailable or self.codeAvailable:
            self.score = 0.5
        else:
            self.score = 0.0

        return self.score