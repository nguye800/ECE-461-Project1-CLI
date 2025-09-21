from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric

@dataclass
class License(Metric):
    def __init__(self, metricName="License", metricWeighting = 0.1, licenseType="Apache 2.0"):
        super().__init__(metricName, 0, metricWeighting)
        self.licenseType = licenseType

    def getLicenseType(self) -> str:
        return self.licenseType