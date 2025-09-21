from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

@dataclass
class BusFactor(Metric):
    def __init__(self, metricName="Bus Factor", metricWeighting = 0.1, numContributors=0):
        super().__init__(metricName, 0, metricWeighting)
        self.NumContributors = numContributors

    def getNumContributors(self) -> int:
        return self.NumContributors