from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

@dataclass
class RampUpTime(Metric):
    def __init__(self, metricName="Ramp Up Time", metricWeighting=0.1, rampUpTime=0.0):
        super().__init__(metricName, 0, metricWeighting)
        self.rampUpTime = rampUpTime
        
    def getRampUpTime(self) -> float:
        return self.rampUpTime