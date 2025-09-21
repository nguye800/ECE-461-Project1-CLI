# test_hf_api.py
import json
import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch

import requests

import src.hf_api


class ParseHfUrlTests(unittest.TestCase):
    def test_parse_model_urls(self):
        cases = {
            # plain repo ids
            "bert-base-uncased": ("model", "bert-base-uncased"),
            "someuser/somerepo": ("model", "someuser/somerepo"),
            # http(s) URLs, 1-part and 2-part
            "https://huggingface.co/bert-base-uncased": ("model", "bert-base-uncased"),
            "https://huggingface.co/someuser/somerepo": ("model", "someuser/somerepo"),
            # extra path segments should be ignored for the repo id
            "https://huggingface.co/bert-base-uncased/tree/main": ("model", "bert-base-uncased"),
            "https://huggingface.co/someuser/somerepo/tree/main": ("model", "someuser/somerepo"),
            "https://huggingface.co/someuser/somerepo/blob/main/file": ("model", "someuser/somerepo"),
            "https://huggingface.co/someuser/somerepo/resolve/main/model.safetensors": ("model", "someuser/somerepo"),
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(hf_api.parse_hf_url(url), expected)

    def test_parse_dataset_urls(self):
        cases = {
            "datasets/squad": ("dataset", "squad"),
            "https://huggingface.co/datasets/squad": ("dataset", "squad"),
            "https://huggingface.co/datasets/user/name": ("dataset", "user/name"),
            "https://huggingface.co/datasets/name/tree/main": ("dataset", "name"),
            "https://huggingface.co/datasets/user/name/tree/main": ("dataset", "user/name"),
            # Handle unusual double "datasets"
            "https://huggingface.co/datasets/datasets/squad": ("dataset", "squad"),
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(hf_api.parse_hf_url(url), expected)

    def test_parse_invalid_host_raises(self):
        with self.assertRaises(ValueError):
            hf_api.parse_hf_url("https://example.com/bert-base-uncased")

    def test_parse_missing_path_raises(self):
        with self.assertRaises(ValueError):
            hf_api.parse_hf_url("https://huggingface.co/")

    def test_parse_whitespace_repo_raises(self):
        with self.assertRaises(ValueError):
            hf_api.parse_hf_url("https://huggingface.co/user/my repo")


class BuildApiUrlTests(unittest.TestCase):
    def test_build_api_url_model(self):
        self.assertEqual(
            hf_api.build_api_url("model", "bert-base-uncased"),
            "https://huggingface.co/api/models/bert-base-uncased",
        )

    def test_build_api_url_dataset(self):
        self.assertEqual(
            hf_api.build_api_url("dataset", "squad"),
            "https://huggingface.co/api/datasets/squad",
        )

    def test_build_api_url_bad_kind_raises(self):
        with self.assertRaises(ValueError):
            hf_api.build_api_url("weird", "x")


class FetchJsonTests(unittest.TestCase):
    class _Resp:
        def __init__(self, status_code=200, payload=None, text="", url=""):
            self.status_code = status_code
            self._payload = payload if payload is not None else {}
            self.text = text
            self.url = url

        def json(self):
            return self._payload

        def raise_for_status(self):
            if self.status_code >= 400:
                err = requests.HTTPError(f"{self.status_code} error for {self.url}")
                # Attach a response object like requests does
                err.response = self
                raise err

    @patch("requests.get")
    def test_fetch_json_ok_without_token(self, mget):
        resp = self._Resp(200, {"ok": True})
        mget.return_value = resp
        out = hf_api.fetch_json("https://huggingface.co/api/models/bert-base-uncased", token=None)
        self.assertEqual(out, {"ok": True})
        # Headers include Accept but not Authorization
        called_headers = mget.call_args.kwargs["headers"]
        self.assertIn("Accept", called_headers)
        self.assertNotIn("Authorization", called_headers)

    @patch("requests.get")
    def test_fetch_json_ok_with_token_header(self, mget):
        resp = self._Resp(200, {"ok": True})
        mget.return_value = resp
        out = hf_api.fetch_json("https://huggingface.co/api/models/bert-base-uncased", token="ABC")
        self.assertEqual(out, {"ok": True})
        called_headers = mget.call_args.kwargs["headers"]
        self.assertEqual(called_headers.get("Authorization"), "Bearer ABC")

    @patch("requests.get")
    def test_fetch_json_dataset_404_fallback_last_segment(self, mget):
        # First call: 404 on owner/name
        first = self._Resp(status_code=404, payload={"detail": "Not found"}, url="https://huggingface.co/api/datasets/user/name")
        # Second call: 200 when trying just the last segment "name"
        second = self._Resp(status_code=200, payload={"id": "name"}, url="https://huggingface.co/api/datasets/name")
        mget.side_effect = [first, second]

        out = hf_api.fetch_json("https://huggingface.co/api/datasets/user/name", token=None)
        self.assertEqual(out, {"id": "name"})
        self.assertEqual(mget.call_count, 2)
        # Ensure the second URL is the base + last segment
        _, second_kwargs = mget.call_args
        self.assertTrue(second.url.endswith("/api/datasets/name"))

    @patch("requests.get")
    def test_fetch_json_raises_http_error(self, mget):
        bad = self._Resp(status_code=500, text="boom", url="https://huggingface.co/api/models/x")
        mget.return_value = bad
        with self.assertRaises(requests.HTTPError):
            hf_api.fetch_json("https://huggingface.co/api/models/x", token=None)


class MainCliTests(unittest.TestCase):
    @patch("builtins.print")
    @patch("requests.get")
    def test_main_success_prints_json(self, mget, mprint):
        # Mock network JSON
        class _R(FetchJsonTests._Resp):
            pass

        mget.return_value = _R(200, {"hello": "world"})
        argv = ["hf_api.py", "https://huggingface.co/bert-base-uncased"]
        with patch.object(sys, "argv", argv):
            hf_api.main()

        # Ensure we printed exactly one JSON blob that contains our data and _requested keys
        self.assertTrue(mprint.called)
        printed = "".join(str(args[0]) for args, _ in mprint.call_args_list)
        blob = json.loads(printed)
        self.assertIn("_requested", blob)
        self.assertEqual(blob["data"], {"hello": "world"})
        self.assertEqual(blob["_requested"]["kind"], "model")
        self.assertEqual(blob["_requested"]["repo_id"], "bert-base-uncased")

    @patch("sys.stderr")
    def test_main_bad_url_exits_2(self, mstderr):
        argv = ["hf_api.py", "https://example.com/not-hf"]
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as ctx:
                hf_api.main()
        self.assertEqual(ctx.exception.code, 2)
        # Ensure an error message was printed to stderr
        self.assertTrue(mstderr.write.called or mstderr.buffer)

    @patch("requests.get")
    def test_main_http_error_exits_1(self, mget):
        # Make the underlying fetch_json raise HTTPError
        class _R(FetchJsonTests._Resp):
            pass

        bad = _R(status_code=500, text="boom", url="https://huggingface.co/api/models/x")
        mget.return_value = bad
        argv = ["hf_api.py", "https://huggingface.co/x"]
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as ctx:
                hf_api.main()
        self.assertEqual(ctx.exception.code, 1)

    @patch("requests.get")
    def test_main_network_error_exits_1(self, mget):
        mget.side_effect = requests.RequestException("no internet")
        argv = ["hf_api.py", "https://huggingface.co/x"]
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as ctx:
                hf_api.main()
        self.assertEqual(ctx.exception.code, 1)

    @patch.dict(os.environ, {"HF_TOKEN": "ENV_TOKEN"}, clear=False)
    @patch("requests.get")
    def test_main_uses_env_token_when_flag_missing(self, mget):
        # Check that Authorization header is present (env var path)
        class _R(FetchJsonTests._Resp):
            pass

        mget.return_value = _R(200, {"ok": True})
        argv = ["hf_api.py", "https://huggingface.co/bert-base-uncased"]
        with patch.object(sys, "argv", argv):
            hf_api.main()
        headers = mget.call_args.kwargs["headers"]
        self.assertEqual(headers.get("Authorization"), "Bearer ENV_TOKEN")


if __name__ == "__main__":
    unittest.main()
