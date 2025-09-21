# test_chat_prompt.py
import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

from src.chatgpt_api import openaiAPI


class ChatPromptTests(unittest.TestCase):
    @patch("builtins.print")
    @patch("chat_prompt.OpenAI")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_success(self, mparse, mOpenAI, mprint):
        # Arrange
        mparse.return_value = mock.Mock(prompt="Hello", model="gpt-4.1-mini")

        fake_response = MagicMock()
        fake_choice = MagicMock()
        fake_choice.message.content = "Mocked response"
        fake_response.choices = [fake_choice]

        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_response
        mOpenAI.return_value = fake_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "FAKEKEY"}):
            api = openaiAPI()
            api.main()

        # Assert OpenAI was called correctly
        mOpenAI.assert_called_once_with(api_key="FAKEKEY")
        fake_client.chat.completions.create.assert_called_once_with(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": "Hello"}],
        )
        # Assert print was called with the mocked response
        mprint.assert_called_once_with("Mocked response")

    @patch("argparse.ArgumentParser.parse_args")
    def test_main_missing_api_key_raises(self, mparse):
        mparse.return_value = mock.Mock(prompt="Hi", model="gpt-4.1-mini")
        with patch.dict(os.environ, {}, clear=True):  # No OPENAI_API_KEY
            api = openaiAPI()
            with self.assertRaises(RuntimeError) as ctx:
                api.main()
            self.assertIn("Missing OPENAI_API_KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
