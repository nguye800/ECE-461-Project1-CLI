from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import time

from src.classes.Metric import Metric
from src.utils.llm_api import llmAPI

_PROMPT = """You are evaluating CODE QUALITY (style & maintainability).
Consider consistency, naming, modularity, comments/docstrings, type hints, tests/CI hints, and readability.
Rate on this discrete scale and reply with ONLY one number: 1.0, 0.5, or 0.0.

CODE (may be partial):
---
{code}
---

README (optional context):
---
{readme}
---
"""

@dataclass
class CodeQuality(Metric):
    def __init__(self, metricName="Code Quality", metricWeighting=0.1):
        super().__init__(metricName, 0, metricWeighting)

        self.codeQuality: float = 0.0
        self.llm = llmAPI()

    def _score_with_llm(self, code_text: str, readme_text: str) -> float:
        prompt = _PROMPT.format(code=(code_text or "")[:6000], readme=(readme_text or "")[:6000])
        resp = self.llm.main(prompt)  #plain text like "1.0" / "0.5" / "0.0"
        if "1.0" in resp: return 1.0 #high quality
        if "0.5" in resp: return 0.5 #avg quality
        if "0.0" in resp: return 0.0 #low quality
        return 0.0

    #computing code quality score and returns score and latency 
    def evaluate(
        self,
        *,
        code_text: Optional[str] = None,
        readme_text: Optional[str] = None,
        precomputed_score: Optional[float] = None,
    ) -> Tuple[float, float]:
        t0 = time.perf_counter()
        try:
            if precomputed_score is not None:
                score = float(precomputed_score)
            elif code_text:  #GenAI
                score = self._score_with_llm(code_text, readme_text or "")
            else:
                score = 0.0
        finally:
            score = max(0.0, min(1.0, float(score)))
            self.codeQuality = score
            self.metricScore = score
            latency = time.perf_counter() - t0
        return score, latency
