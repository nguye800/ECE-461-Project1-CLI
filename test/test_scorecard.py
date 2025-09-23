import importlib

class DummyMetric:
    def __init__(self, score, wt):
        self._s, self._w = score, wt
    def getMetricScore(self):
        return self._s
    def getWeighting(self):
        return self._w

def test_scorecard_weighted_sum():
    ScoreCard = importlib.import_module("src.classes.ScoreCard").ScoreCard
    bf = DummyMetric(0.9, 0.1)
    dq = DummyMetric(0.7, 0.2)
    sz = DummyMetric(0.5, 0.1)
    lic= DummyMetric(1.0, 0.1)
    ru = DummyMetric(0.6, 0.2)
    pc = DummyMetric(0.4, 0.1)
    cq = DummyMetric(0.8, 0.1)
    ac = DummyMetric(0.3, 0.1)

    sc = ScoreCard(bf, dq, sz, lic, ru, pc, cq, ac)

    # Expected weighted sum
    expected = sum(m.getMetricScore() * m.getWeighting()
                   for m in [bf,dq,sz,lic,ru,pc,cq,ac])
    assert hasattr(sc, "totalScore"), "ScoreCard must set totalScore"
    assert abs(sc.totalScore - expected) < 1e-9
