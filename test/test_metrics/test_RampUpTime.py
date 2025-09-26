import pytest
from src.classes.RampUpTime import RampUpTime

class DummyLLM:
    """Fake LLM to avoid making real API calls."""
    def __init__(self, reply="1.0"):
        self.reply = reply
    def main(self, text):
        return self.reply

def test_precomputed_score():
    ramp = RampUpTime()
    ramp.setRampUpTime(precomputed_score=0.5)
    assert ramp.getRampUpTime() == 0.5

def test_llm_scoring_good_readme():
    ramp = RampUpTime()
    ramp.llm = DummyLLM("1.0")
    ramp.setRampUpTime(readme_text="This is a README with clear setup instructions...")
    assert ramp.getRampUpTime() == 1.0

def test_llm_scoring_moderate_readme():
    ramp = RampUpTime()
    ramp.llm = DummyLLM("0.5")
    ramp.setRampUpTime(readme_text="Some README content, not great")
    assert ramp.getRampUpTime() == 0.5

def test_llm_scoring_bad_readme():
    ramp = RampUpTime()
    ramp.llm = DummyLLM("0.0") 
    ramp.setRampUpTime(readme_text="")
    assert ramp.getRampUpTime() == 0.0

def test_no_inputs_defaults_to_zero():
    ramp = RampUpTime()
    ramp.setRampUpTime()
    assert ramp.getRampUpTime() == 0.0