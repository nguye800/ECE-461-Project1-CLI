from __future__ import annotations

from dataclasses import dataclass
from src.classes.Metric import Metric
from src.utils.llm_api import llmAPI

@dataclass
class Size(Metric):
    def __init__(self, metricName="Size", metricWeighting=0.1, sizeScore=0.0):
        super().__init__(metricName, 0, metricWeighting)
        self.sizeScore = sizeScore
        self.modelSizeGB = 0.0
        self.paramCount = 0
        self.llm = llmAPI()

    def _score_with_llm(self, model_type: str, param_count: int, file_size_gb: float) -> float:
        """Use Purdue’s LLM to contextualize size scoring."""
        prompt = f"""
        You are evaluating the SIZE metric of a machine learning model.

        Information:
        - Model type: {model_type}
        - Parameter count: {param_count:,}
        - File size (GB): {file_size_gb:.2f}

        Rate the model's size on a scale of:
        - 1.0 = Size is appropriate and easy to handle for this type of model
        - 0.5 = Size is large but still manageable
        - 0.0 = Size is unnecessarily large or difficult to use for most purposes

        Answer with only the numeric score (1.0, 0.5, or 0.0).
        """

        try:
            response_text = self.llm.main(prompt)
            if "1.0" in response_text:
                return 1.0
            elif "0.5" in response_text:
                return 0.5
            elif "0.0" in response_text:
                return 0.0
        except Exception as e:
            print(f"[Size Metric] LLM scoring failed, falling back. Error: {e}")
        return None

    def setSize(self, file_sizes: list[int] | None = None,
                param_count: int | None = None,
                model_type: str = "general"):
        """
        Compute size score.
        - If LLM available → ask it to contextualize.
        - Else fallback to rule-based thresholds.
        """
        if param_count is not None:
            self.paramCount = param_count
            self.modelSizeGB = param_count / 1e9
        elif file_sizes:
            total_size_bytes = sum(file_sizes)
            self.modelSizeGB = total_size_bytes / (1024.0 ** 3)
        else:
            self.sizeScore = 0.0
            return

        score = self._score_with_llm(model_type, self.paramCount, self.modelSizeGB)
        if score is not None:
            self.sizeScore = score
            return

        if self.paramCount > 0:
            if self.paramCount < 1e9:
                self.sizeScore = 1.0
            elif self.paramCount < 10e9:
                self.sizeScore = 0.5
            else:
                self.sizeScore = 0.0
        else:
            if self.modelSizeGB < 1:
                self.sizeScore = 1.0
            elif self.modelSizeGB < 10:
                self.sizeScore = 0.5
            else:
                self.sizeScore = 0.0

    def getSize(self) -> float:
        return self.sizeScore

    def getModelSizeGB(self) -> float:
        return self.modelSizeGB

    def getParamCount(self) -> int:
        return self.paramCount