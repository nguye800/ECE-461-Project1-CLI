# License Testing
import math
from src.classes.License import License

def test_license(capsys):
    m = License()
    score, latency = m.evaluate("owner/repo")
    print(f"License score={score:.3f}, latency_ms={latency*1000:.1f}")
    assert 0.0 <= score <= 1.0
    assert latency >= 0.0
