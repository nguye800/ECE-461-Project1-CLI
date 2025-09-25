from __future__ import annotations


import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse


from .Metric import Metric
from src.utils.hf_api import hfAPI
from src.utils.llm_api import llmAPI



#helper functions
_GENAI_SYSTEM_INSTRUCTIONS = """\
You are a strict compliance scorer for open-source model licenses.


Your task: Read the README (free text) and METADATA (JSON) for a model, infer the most likely license,
and compute a license_score in [0,1] using ONLY the rubric below. If information conflicts, prefer an
explicit SPDX ID or LICENSE text in README/metadata over badges or hearsay.


Rubric to compute license_score (clamp to [0,1]) relative to LGPL-2.1 compatibility needs:
1) Compatibility (0..1):
   - 1.0: Permissive or weak-copyleft compatible with LGPL-2.1, e.g. MIT, BSD-2/3, Apache-2.0,
          LGPL-2.1/3.0, MPL-2.0, CC-BY-4.0 (for weights/data), OpenRAIL-M **if commercial use allowed**.
   - 0.0: Non-commercial/research-only (e.g., CC-BY-NC, RAIL-NC), AGPL-3.0 (strong copyleft over network),
          or custom terms that restrict commercial redistribution.
   - 0.3: Unclear/unknown (no reliable license).
2) Return your best normalized SPDX-like license identifier (lowercase, e.g., 'mit','apache-2.0','lgpl-3.0',
   'mpl-2.0','gpl-3.0','agpl-3.0','cc-by-4.0','cc-by-nc-4.0','cc0-1.0','openrail-m','proprietary','no-license').


Output STRICTLY the following JSON (no prose, no markdown):


{
  "license_normalized": "<string>",
  "license_score": <float 0..1>,
  "reason": "<one short sentence explaining the scoring choice>"
}
"""


def _safe_json(obj: object) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"


@dataclass
class License(Metric):


    def __init__(self, metricName: str = "license", metricWeighting: float = 0.10) -> None:
        super().__init__(metricName, 0.0, metricWeighting)
       
        self._logger = logging.getLogger(__name__)
        self.licenseType: str = "unknown"
        self.reason: str = ""


    def getLicenseType(self) -> str:
        return self.licenseType


    def evaluate(
        self,
        model_id_or_url: str,
        *,
        readme_text: Optional[str] = None,
        metadata_json: Optional[dict] = None,
    ) -> Tuple[float, int]:
       
        t0 = time.perf_counter()
        score: float = 0.3  # default "unclear"
        self.licenseType = "unknown"
        self.reason = ""


        try:
            #acquire inputs (fetch only)
            if readme_text is None or metadata_json is None:
                try:
                    api = hfAPI()
                    if readme_text is None:
                        readme_text = api.get_readme(model_id_or_url) or ""
                    if metadata_json is None:
                        raw_info = api.get_info(model_id_or_url, as_raw_json=False)


                        if isinstance(raw_info, dict) and "data" in raw_info and isinstance(raw_info["data"], dict):
                            metadata_json = raw_info["data"]
                        elif isinstance(raw_info, dict):
                            metadata_json = raw_info
                        else:
                            metadata_json = {}


                except Exception as fetch_err:
                    #if fetching fails, still ask GenAI with whatever we have.
                    self._logger.debug("Fetch failed, continuing with partial inputs: %s", fetch_err)
                    readme_text = readme_text or ""
                    metadata_json = metadata_json or {}


            #strict genai promp
            user_payload = {
                "README": readme_text or "",
                "METADATA": metadata_json or {},
            }


            prompt = _GENAI_SYSTEM_INSTRUCTIONS + "\n\nINPUT:\n" + _safe_json(user_payload)
            


            #genai call
            client = llmAPI()
            provider_json = client.main(prompt)


            parsed_outer = None
            try:
                parsed_outer = json.loads(provider_json)
            except Exception:
                parsed_outer = None


            content_str: Optional[str] = None
            if isinstance(parsed_outer, dict) and "choices" in parsed_outer:
                content_str = (
                    (parsed_outer.get("choices") or [{}])[0].get("message") or {}
                ).get("content")
            else:
                content_str = provider_json


            result = {}
            try:
                result = json.loads(content_str or "{}")
            except Exception:
                result = {}


            #extract results, clamp, assign
            lic = result.get("license_normalized")
            sc = result.get("license_score")
            rsn = result.get("reason")


            if isinstance(lic, str) and lic.strip():
                self.licenseType = lic.strip().lower()
            else:
                self.licenseType = "unknown"


            try:
                score = float(sc)
            except Exception:
                score = 0.3


            # clamp to [0,1]
            if score < 0.0:
                score = 0.0
            elif score > 1.0:
                score = 1.0


            if isinstance(rsn, str):
                self.reason = rsn.strip()


            self.metricScore = score
            self._logger.debug(
                "GenAI license result: license=%s score=%.2f reason=%s",
                self.licenseType, score, self.reason
            )


        except Exception as e:
            self._logger.debug("License evaluate error: %s", e)


        latency_ms = int(round((time.perf_counter() - t0) * 1000.0))
        return score, latency_ms
