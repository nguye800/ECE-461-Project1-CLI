from __future__ import annotations

from dataclasses import dataclass
from src.classes.Metric import Metric
from src.utils.get_metadata import get_collaborators_github, find_github_links
from src.utils.llm_api import llmAPI
import math
import re

@dataclass
class BusFactor(Metric):
    def __init__(self, metricName="Bus Factor", metricWeighting = 0.1):
        super().__init__(metricName, 0, metricWeighting)

    def setNumContributors(self, url):
        links = find_github_links(url)
        if links:
            avg, std, authors = get_collaborators_github(links[0], n=200)
            evenness = 1.0 / (1.0 + (std / avg) **2) # rewards balanced contribution, penalizes concentration
            saturation_coeff = 5
            groupsize = 1 - math.exp((-1.0 / avg) / saturation_coeff)
            self.NumContributors = len(authors)
            self.metricScore = evenness * groupsize
        else:
            api = llmAPI()
            prompt = "Given this link to a HuggingFace model repository, can you assess the Bus Factor of the model based on size of the organization/members \
                and likelihood that the work for developing this model was evenly split but all contributors. \
                I would like you to return a single value from 0-1 with 1 being perfect bus factor and no risk involved, and 0 being one singular contributor doing all the work. \
                This response should just be the 0-1 value with no other text given."
            response = api.main(f"URL: {url}, instructions: {prompt}")
            content = response["choices"][0]["message"]["content"]
            match = re.search(r"[-+]?\d*\.\d+|\d+", content)
            bus_factor = float(match.group()) if match else None
            self.metricScore = bus_factor

    def getNumContributors(self) -> int:
        return self.NumContributors
    