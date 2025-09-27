import unittest
from src.classes.PerformanceClaims import PerformanceClaims

class TestPerformanceClaims(unittest.TestCase):
    def test_no_results(self):
        metric = PerformanceClaims("dummy")
        metric.benchmarks = {"accuracy": 0.0}
        self.assertEqual(metric.evaluate(), 0.0)

    def test_partial_results(self):
        metric = PerformanceClaims("dummy")
        metric.benchmarks = {"accuracy": 0.6}  # below threshold
        self.assertLess(metric.evaluate(), 1.0)

    def test_good_results(self):
        metric = PerformanceClaims("dummy")
        metric.benchmarks = {"accuracy": 0.95}
        self.assertEqual(metric.evaluate(), 1.0)
