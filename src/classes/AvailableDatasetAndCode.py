from __future__ import annotations

from dataclasses import dataclass
from src.classes.Metric import Metric

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