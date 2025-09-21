from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

@dataclass
class CodeQuality(Metric):
    def __init__(self, metricName="Code Quality", metricWeighting=0.1):
        super().__init__(metricName, 0, metricWeighting)