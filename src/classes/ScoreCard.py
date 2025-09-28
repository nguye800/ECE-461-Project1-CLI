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
from src.utils.get_metadata import get_model_metadata
import time

@dataclass
class ScoreCard:
    def __init__(self, url):
        t0 = time.perf_counter_ns()
        # Each metric is a field; defaults provided so you can construct empty and fill later
        self.busFactor = BusFactor()
        self.busFactor.setNumContributors(url)
        self.datasetQuality = DatasetQuality()
        self.datasetQuality.metricScore, self.datasetQuality.metricLatency = self.datasetQuality.computeDatasetQuality(url)
        self.size = Size()
        self.size.setSize(url)        
        self.license = License()
        self.license.metricScore, self.license.metricLatency = self.license.evaluate(url)
        self.rampUpTime = RampUpTime()
        readme_text = get_github_readme(url)
        self.rampUpTime.setRampUpTime(readme_text=readme_text)
        self.performanceClaims = PerformanceClaims()
        self.performanceClaims.metricScore, self.performanceClaims.metricLatency = self.performanceClaims.evaluate(url)
        self.codeQuality = CodeQuality()
        self.codeQuality.metricScore, self.codeQuality.metricLatency = self.codeQuality.evaluate(url)
        self.availableDatasetAndCode = AvailableDatasetAndCode()
        self.availableDatasetAndCode.metricScore, self.availableDatasetAndCode.metricLatency = self.availableDatasetAndCode.score_dataset_and_code_availability(url)
        self.latency = (time.perf_counter_ns() - t0) // 1_000_000

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
    
    def getLatency(self) -> int:
        return self.latency

    def printTotalScore(self):
        print(f"net_score {self.totalScore}\n"\
              f"net_score_latency {self.latency}")
    
    def printSubscores(self):
        print("Submetric Scores: \n" \
        f"size_score {self.size.getMetricScore()}\n" \
        f"size_score_latency {self.size.getLatency()}\n" \
        f"license {self.license.getMetricScore()}\n" \
        f"license_latency {self.license.getLatency()}\n" \
        f"ramp_up_time {self.rampUpTime.getMetricScore()}\n" \
        f"ramp_up_time_latency {self.rampUpTime.getLatency()}\n" \
        f"bus_factor {self.busFactor.getMetricScore()}\n" \
        f"bus_factor_latency {self.busFactor.getLatency()}\n" \
        f"dataset_and_code_score {self.availableDatasetAndCode.getMetricScore()}\n" \
        f"dataset_and_code_score_latency {self.availableDatasetAndCode.getLatency()}\n" \
        f"dataset_quality {self.datasetQuality.getMetricScore()}\n" \
        f"dataset_quality_latency {self.datasetQuality.getLatency()}\n" \
        f"code_quality {self.codeQuality.getMetricScore()}\n" \
        f"code_quality_latency {self.codeQuality.getLatency()}\n" \
        f"performance_claims {self.performanceClaims.getMetricScore()}\n"\
        f"performance_claims_latency {self.performanceClaims.getLatency()}\n")