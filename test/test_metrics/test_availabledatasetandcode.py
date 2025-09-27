import unittest
from src.classes.AvailableDatasetAndCode import AvailableDatasetAndCode

class TestAvailableDatasetAndCode(unittest.TestCase):
    def test_both_available(self):
        metric = AvailableDatasetAndCode("dummy")
        metric.datasetAvailable = True
        metric.codeAvailable = True
        self.assertEqual(metric.evaluate(), 1.0)

    def test_dataset_only(self):
        metric = AvailableDatasetAndCode("dummy")
        metric.datasetAvailable = True
        metric.codeAvailable = False
        self.assertEqual(metric.evaluate(), 0.5)

    def test_code_only(self):
        metric = AvailableDatasetAndCode("dummy")
        metric.datasetAvailable = False
        metric.codeAvailable = True
        self.assertEqual(metric.evaluate(), 0.5)

    def test_none_available(self):
        metric = AvailableDatasetAndCode("dummy")
        metric.datasetAvailable = False
        metric.codeAvailable = False
        self.assertEqual(metric.evaluate(), 0.0)
