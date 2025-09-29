import unittest
from unittest.mock import patch

from src.classes.CodeQuality import CodeQuality

class LLM10:  # 1.0
    def main(self, prompt: str) -> str:
        return "ok 1.0"

class LLM05:  # 0.5
    def main(self, prompt: str) -> str:
        return "score=0.5"

class LLMBad:  # no valid token
    def main(self, prompt: str) -> str:
        return "N/A"

class TestCodeQuality(unittest.TestCase):

    def test_explicit_github_url_llm10(self):
        m = CodeQuality()
        m.llm = LLM10()  # avoid network
        score, dt_ms = m.evaluate(
            url="https://huggingface.co/some/model",
            githubURL="https://github.com/example/repo"
        )
        self.assertEqual(score, 1.0)
        self.assertIsInstance(dt_ms, int)
        self.assertGreaterEqual(dt_ms, 0)

    @patch("src.classes.CodeQuality.find_github_links", return_value={"https://github.com/example/repo"})
    def test_inferred_links_llm05(self, _):
        m = CodeQuality()
        m.llm = LLM05()
        score, _ = m.evaluate(
            url="https://huggingface.co/google-bert/bert-base-uncased",
            githubURL=None
        )
        self.assertEqual(score, 0.5)

    @patch("src.classes.CodeQuality.find_github_links", return_value=set())
    def test_no_links_returns_zero(self, _):
        m = CodeQuality()
        m.llm = LLM10()  # should not matter—no links path returns 0.0
        score, _ = m.evaluate(url="https://whatever", githubURL=None)
        self.assertEqual(score, 0.0)

    @patch("src.classes.CodeQuality.find_github_links", return_value={"https://github.com/example/repo"})
    def test_invalid_llm_defaults_zero(self, _):
        m = CodeQuality()
        m.llm = LLMBad()
        score, _ = m.evaluate(url="https://whatever", githubURL=None)
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
