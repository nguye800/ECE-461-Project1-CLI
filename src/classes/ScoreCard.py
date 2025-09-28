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
import json
from urllib.parse import urlparse

@dataclass
class ScoreCard:
    def __init__(self, url):
        t0 = time.perf_counter_ns()
        self.modelName = self.getName(url)
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
    
    def getName(self, url: str) -> str:
        p = urlparse(url)
        parts = [seg for seg in p.path.split("/") if seg]
        if len(parts) < 2:
            raise ValueError("Invalid HF URL; expected https://huggingface.co/<owner>/<repo>")
        return parts[1]

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
    
    def printScores(self):
        rec = {
            "name":self.modelName,
            "category":"MODEL",  # e.g., "MODEL" | "DATASET" | "CODE"

            "net_score":self.totalScore,
            "net_score_latency":self.latency,  # or your real overall latency

            "ramp_up_time":float(self.rampUpTime.getMetricScore()),
            "ramp_up_time_latency":int(self.rampUpTime.getLatency()),

            "bus_factor":float(self.busFactor.getMetricScore()),
            "bus_factor_latency":int(self.busFactor.getLatency()),

            "performance_claims":float(self.performanceClaims.getMetricScore()),
            "performance_claims_latency":int(self.performanceClaims.getLatency()),

            "license":float(self.license.getMetricScore()),
            "license_latency":int(self.license.getLatency()),

            # Spec says: object mapping hardware types -> floats
            "size_score":float(self.size.getMetricScore()),
            "size_score_latency":int(self.size.getLatency()),

            "dataset_and_code_score":float(self.availableDatasetAndCode.getMetricScore()),
            "dataset_and_code_score_latency":int(self.availableDatasetAndCode.getLatency()),

            "dataset_quality":float(self.datasetQuality.getMetricScore()),
            "dataset_quality_latency":int(self.datasetQuality.getLatency()),

            "code_quality":float(self.codeQuality.getMetricScore()),
            "code_quality_latency": int(self.codeQuality.getLatency()),
        }

        # NDJSON: one JSON object per line (no pretty-printing)
        print(json.dumps(rec, ensure_ascii=False, separators=(",", ":")))