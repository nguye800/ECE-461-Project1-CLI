from __future__ import annotations

from dataclasses import dataclass
from src.classes.Metric import Metric

@dataclass
class Size(Metric):
    def __init__(self, metricName="Size", metricWeighting=0.1, sizeScore=0.0):
        super().__init__(metricName, 0, metricWeighting)
        self.sizeScore = sizeScore
        self.modelSizeGB = 0.0

    def setSize(self, file_sizes: list[int]):
        """
        Compute model size score.
        file_sizes: list of file sizes in bytes (from Hugging Face API 'siblings')
        """
        if not file_sizes:
            self.sizeScore = 0.0
            return

        total_size_bytes = sum(file_sizes)
        self.modelSizeGB = total_size_bytes / (1024.0 ** 3)

        if self.modelSizeGB < 1:
            self.sizeScore = 1.0
        elif self.modelSizeGB < 10:
            self.sizeScore = 0.5
        else:
            self.sizeScore = 0.0

    def getSize(self) -> float:
        return self.sizeScore

    def getModelSizeGB(self) -> float:
        return self.modelSizeGB