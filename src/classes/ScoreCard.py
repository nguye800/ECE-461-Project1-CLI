from __future__ import annotations

from dataclasses import dataclass

@dataclass
class ScoreCard:
    def __init__(self, busFactor, datasetQuality, size, license, rampUpTime, performanceClaims, codeQuality, availableDatasetandCode):
        # Each metric is a field; defaults provided so you can construct empty and fill later
        self.busFactor = busFactor
        self.datasetQuality = datasetQuality
        self.size = size
        self.license = license
        self.rampUpTime = rampUpTime
        self.performanceClaims = performanceClaims
        self.codeQuality = codeQuality
        self.availableDatasetAndCode = availableDatasetandCode

        self.totalScore = 0
        self.totalScore += self.busFactor.getMetricScore() * self.busFactor.getWeighting()
        self.totalScore += self.datasetQuality.getMetricScore() * self.datasetQuality.getWeighting()
        self.totalScore += self.size.getMetricScore() * self.size.getWeighting()
        self.totalScore += self.rampUpTime.getMetricScore() * self.rampUpTime.getWeighting()
        self.totalScore += self.license.getMetricScore() * self.license.getWeighting()
        self.totalScore += self.performanceClaims.getMetricScore() * self.performanceClaims.getWeighting()
        self.totalScore += self.codeQuality.getMetricScore() * self.codeQuality.getWeighting()
        self.totalScore += self.availableDatasetandCode.getMetricScore() * self.availableDatasetandCode.getWeighting()

    def getTotalScore(self) -> float:
        return self.totalScore