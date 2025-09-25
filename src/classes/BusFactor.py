from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric
from ..utils.get_metadata import getCollaborators
import math

@dataclass
class BusFactor(Metric):
    def __init__(self, metricName="Bus Factor", metricWeighting = 0.1):
        super().__init__(metricName, 0, metricWeighting)

    def setNumContributors(self, url):
        avg, std, authors = getCollaborators(url, n=200)
        evenness = 1.0 / (1.0 + (std / avg)**2) # rewards balanced contribution, penalizes concentration
        saturation_coeff = 5
        groupsize = 1 - math.exp((-1.0 / avg) / saturation_coeff)
        self.NumContributors = evenness * groupsize

    def getNumContributors(self) -> int:
        return self.NumContributors