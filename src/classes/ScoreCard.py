from __future__ import annotations

from dataclasses import dataclass
from src.classes.AvailableDatasetAndCode import AvailableDatasetAndCode
from src.classes.BusFactor import BusFactor
from src.classes.CodeQuality import CodeQuality
from src.classes.DatasetQuality import DatasetQuality
from src.classes.License import License
from src.classes.PerformanceClaims import PerformanceClaims
from src.classes.RampUpTime import RampUpTime
from src.classes.Size import Size
from src.utils.get_metadata import get_github_readme

@dataclass
class ScoreCard:
    def __init__(self, url):
        # Each metric is a field; defaults provided so you can construct empty and fill later
        self.busFactor = BusFactor()
        self.busFactor.setNumContributors(url)
        self.datasetQuality = DatasetQuality()
        self.datasetQuality.metricScore = self.datasetQuality.computeDatasetQuality(url)
        self.size = Size()
        self.size.setSize(url)
        self.license = License()
        self.license.metricScore = self.license.evaluate(url)
        self.rampUpTime = RampUpTime()
        readme_text = get_github_readme(url)
        self.rampUpTime.setRampUpTime(readme_text=readme_text)
        self.performanceClaims = PerformanceClaims()
        self.performanceClaims.metricScore = self.performanceClaims.evaluate(url)
        self.codeQuality = CodeQuality()
        self.codeQuality.metricScore = self.codeQuality.evaluate(url)
        self.availableDatasetAndCode = AvailableDatasetAndCode()
        self.availableDatasetAndCode.metricScore = self.availableDatasetAndCode.score_dataset_and_code_availability(url)

    def setTotalScore(self):
        self.totalScore = 0
        self.totalScore += self.busFactor.getMetricScore() * self.busFactor.getWeighting()
        self.totalScore += self.datasetQuality.getMetricScore() * self.datasetQuality.getWeighting()
        self.totalScore += self.size.getMetricScore() * self.size.getWeighting()
        self.totalScore += self.rampUpTime.getMetricScore() * self.rampUpTime.getWeighting()
        self.totalScore += self.license.getMetricScore() * self.license.getWeighting()
        self.totalScore += self.performanceClaims.getMetricScore() * self.performanceClaims.getWeighting()
        self.totalScore += self.codeQuality.getMetricScore() * self.codeQuality.getWeighting()
        self.totalScore += self.availableDatasetAndCode.getMetricScore() * self.availableDatasetAndCode.getWeighting()
        self.totalScore = round(self.totalScore, 3)

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
        f"Available Dataset and Code Score: {self.availableDatasetAndCode.getMetricScore()}\n" \
        f"Dataset Quality: {self.datasetQuality.getMetricScore()}\n" \
        f"Code Quality: {self.codeQuality.getMetricScore()}\n" \
        f"Performance Claims: {self.performanceClaims.getMetricScore()}\n")