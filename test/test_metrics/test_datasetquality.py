import unittest
from src.classes.DatasetQuality import DatasetQuality

class TestDatasetQuality(unittest.TestCase):
    def test_no_dataset(self):
        metric = DatasetQuality("dummy")
        metric.datasetEntries = 0
        self.assertEqual(metric.evaluate(), 0.0)

    def test_small_dataset(self):
        metric = DatasetQuality("dummy")
        metric.datasetEntries = 100
        metric.likes = 2
        metric.downloads = 50
        metric.license = "apache-2.0"
        self.assertGreater(metric.evaluate(), 0.0)

    def test_large_dataset(self):
        metric = DatasetQuality("dummy")
        metric.datasetEntries = 1_000_000
        metric.likes = 500
        metric.downloads = 100_000
        metric.license = "apache-2.0"
        self.assertEqual(metric.evaluate(), 1.0)
