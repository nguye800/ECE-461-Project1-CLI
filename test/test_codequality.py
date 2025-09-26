from src.classes.CodeQuality import CodeQuality

def test_codequality_smoke_precomputed(capsys):
    m = CodeQuality()
    score, latency = m.evaluate(code_text=None, precomputed_score=0.5)

    print(f"code_quality={score:.3f}, latency_s={latency:.6f}")

    assert 0.0 <= score <= 1.0
    assert m.codeQuality == score
    assert m.metricScore == score
    assert latency >= 0.0
