from __future__ import annotations

from dataclasses import dataclass
from Metric import Metric
from utils.llm_api import llmAPI

@dataclass
class RampUpTime(Metric):
    def __init__(self, metricName="Ramp Up Time", metricWeighting=0.1, rampUpTime=0.0):
        super().__init__(metricName, 0, metricWeighting)
        self.rampUpTime = rampUpTime
        self.llm = llmAPI()

    def _score_readme_with_llm(self, readme_text: str) -> float:
        """Send README text to Purdue’s LLM and return 0.0, 0.5, or 1.0."""
        prompt = f"""
        Evaluate the documentation quality of an open-source machine learning project.
        The goal is to rate how quickly a new engineer could understand and use the project based on its README.

        Read the README text below and assign one of the following scores:
        - 1.0 = Excellent documentation (clear setup instructions, examples, usage details, dependencies, etc.)
        - 0.5 = Moderate documentation (some instructions exist, but incomplete or unclear)
        - 0.0 = Poor documentation (very little or no usable information)

        README text:
        ---
        {readme_text[:8000]}
        ---

        Answer with only the numeric score (1.0, 0.5, or 0.0).
        """

        response_text = self.llm.main(prompt)

        if "1.0" in response_text:
            return 1.0
        elif "0.5" in response_text:
            return 0.5
        elif "0.0" in response_text:
            return 0.0
        else:
            return 0.0

    def setRampUpTime(self, readme_text: str | None = None, precomputed_score: float | None = None):
        """
        Set ramp-up time score either from:
        - precomputed_score (manual value for testing), or
        - raw readme_text (evaluated by LLM).
        """
        if precomputed_score is not None:
            self.rampUpTime = precomputed_score
        elif readme_text is not None:
            self.rampUpTime = self._score_readme_with_llm(readme_text)
        else:
            self.rampUpTime = 0.0

    def getRampUpTime(self) -> float:
        return self.rampUpTime

