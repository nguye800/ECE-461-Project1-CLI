from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

@dataclass
class Size(Metric):
    def __init__(self, metricName="Size", metricWeighting = 0.1, size=0.0):
        super().__init__(metricName, 0, metricWeighting)
        self.size = size

    def getSize(self) -> float:
        return self.size