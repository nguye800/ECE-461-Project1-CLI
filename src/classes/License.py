from __future__ import annotations

import json
import logging
import time
from typing import Dict, Optional, Tuple, Any

from src.classes.Metric import Metric
from src.utils.llm_api import llmAPI


class License(Metric):
    def __init__(self, metricName: str = "License", metricWeighting: float = 0.1) -> None:
        super().__init__(metricName, 0.0, metricWeighting)
        self.license: float = 0.0     
        self.llm = llmAPI()            

    def evaluate(
        self,
        *,
        readme_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, float]:
        t0 = time.perf_counter()

        #GenAI prompt
        system = (
            "You are a licensing analyst. Score license compatibility relative to LGPL-2.1.\n"
            "Respond with ONLY a single JSON object:\n"
            '  { "license_score": number in [0,1],'
            '    "license_normalized": string,'
            '    "reason": string }\n'
            "Scoring:\n"
            "  1.0: MIT, BSD-2/3, Apache-2.0, LGPL-2.1/3.0, MPL-2.0, CC-BY-4.0 (weights), OpenRAIL-M (commercial OK)\n"
            "  0.0: Non-commercial (e.g., CC-BY-NC, RAIL-NC), AGPL-3.0, custom terms restricting commercial redistribution\n"
            "  0.3: Unclear/unknown\n"
            "Prefer explicit SPDX IDs or LICENSE links."
        )
        payload = {"README": readme_text or "", "METADATA": metadata or {}}
        prompt = system + "\n\nINPUT:\n" + json.dumps(payload, ensure_ascii=False)

        #GenAI call
        score = 0.3        #default for unclear
        try:
            resp = self.llm.main(prompt)
            if isinstance(resp, str):
                resp = json.loads(resp)
            if isinstance(resp, dict):
                score = float(resp.get("license_score", score))
        except Exception as e:
            logging.exception("License.evaluate GenAI error: %s", e)

        #clamp + store on the metric object
        score = max(0.0, min(1.0, score))
        self.license = score
        self.metricScore = score

        latency = time.perf_counter() - t0
        return score, latency
