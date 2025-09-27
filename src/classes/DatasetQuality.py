from __future__ import annotations
from dataclasses import dataclass
from Metric import Metric
from src.utils.hf_api import get_info
import math
import json

@dataclass
class DatasetQuality(Metric):
    def __init__(self, metricName="Dataset Quality", metricWeighting = 0.1, datasetShape=(0), datasetEntries=0):
        super().__init__(metricName, 0, metricWeighting)
        self.datasetShape = datasetShape
        self.datasetEntries = datasetEntries
    
    
    def computeDatasetQuality(url: str) -> float:
        """
        Compute a dataset quality score between 0 and 1 based on likes, downloads, and license.
        """
        # Fetch model card JSON
        modelInfoStr = get_info(url, printCLI=False)  # assuming get_info is imported
        modelInfo = json.loads(modelInfoStr)

        data = modelInfo.get("data", {})
        cardData = data.get("cardData", {})

        # Extract relevant fields
        likes = data.get("likes", 0)
        downloads = data.get("downloads", 0)
        license_str = cardData.get("license", None)


        # Weak signal: popularity / community validation
        likes_score = math.log(likes + 1) / math.log(5000 + 1)  # normalize roughly
        
        # Proxy for dataset usefulness / adoption
        downloads_score = math.log(downloads + 1) / math.log(1000000 + 1)
        
        # License quality: open > restricted > unknown
        if license_str is None:
            license_score = 0.2
        elif any(x in license_str.lower() for x in ["mit","apache","cc0","cc-by"]):
            license_score = 1.0
        elif "research" in license_str.lower():
            license_score = 0.8
        else:
            license_score = 0.5

        # Weighted sum
        total_score = 0.3 * likes_score + 0.4 * downloads_score + 0.3 * license_score

        # Clamp between 0 and 1
        return round(min(total_score, 1.0), 3)