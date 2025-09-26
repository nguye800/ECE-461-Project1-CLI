import math
from src.classes.License import License

def test_license(capsys):
    m = License()
    score, latency = m.evaluate(readme_text="MIT License\nPermission is hereby granted...", metadata=None)
    print(f"License score={score:.3f}, latency_ms={latency*1000:.1f}")
    assert 0.0 <= score <= 1.0
    assert latency >= 0.0

#python -m pytest -q -s test\test_license.py
