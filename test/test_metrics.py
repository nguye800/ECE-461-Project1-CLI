import importlib

def test_metric_base_getters():
    Metric = importlib.import_module("src.classes.Metric").Metric
    m = Metric(metricName="X", metricScore=0.3, metricWeighting=0.2)
    assert m.getMetricName() == "X"
    assert m.getMetricScore() == 0.3
    assert m.getWeighting() == 0.2

def test_concrete_metric_stores_values():
    BusFactor = importlib.import_module("src.classes.BusFactor").BusFactor
    License = importlib.import_module("src.classes.License").License
    Size = importlib.import_module("src.classes.Size").Size

    bf = BusFactor(numContributors=5)
    assert bf.getNumContributors() == 5

    lic = License(licenseType="LGPL-2.1")
    assert lic.getLicenseType() == "LGPL-2.1"

    sz = Size(size=123.4)
    assert abs(sz.getSize() - 123.4) < 1e-9
