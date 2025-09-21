from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

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