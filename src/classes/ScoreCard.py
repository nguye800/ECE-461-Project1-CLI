from __future__ import annotations

from dataclasses import dataclass
import AvailableDatasetAndCode, BusFactor, CodeQuality, DatasetQuality, License, Metric, PerformanceClaims, RampUpTime, Size

@dataclass
class ScoreCard:
    def __init__(self, url):
        # Each metric is a field; defaults provided so you can construct empty and fill later
        self.busFactor = BusFactor()
        self.busFactor.setNumContributors(url)
        self.datasetQuality = DatasetQuality()
        self.size = Size()
        self.license = License()
        self.rampUpTime = RampUpTime()
        self.performanceClaims = PerformanceClaims()
        self.codeQuality = CodeQuality()
        self.availableDatasetAndCode = AvailableDatasetAndCode()

    def setTotalScore(self):
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

    def printTotalScore(self):
        print(f"Overall Score: {self.totalScore}")
    
    def printSubscores(self):
        print("Submetric Scores: \n" \
        f"Size: {self.size.getMetricScore()}\n" \
        f"License: {self.license.getMetricScore()}\n" \
        f"Ramp Up Time: {self.rampUpTime.getMetricScore()}\n" \
        f"Bus Factor: {self.busFactor.getMetricScore()}\n" \
        f"Available Dataset and Code Score: {self.availableDatasetandCode.getMetricScore()}\n" \
        f"Dataset Quality: {self.datasetQuality.getMetricScore()}\n" \
        f"Code Quality: {self.codeQuality.getMetricScore()}\n" \
        f"Performance Claims: {self.performanceClaims.getMetricScore()}\n")