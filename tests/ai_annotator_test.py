"""Unit tests for ai_annotator module."""

import unittest
from unittest.mock import patch, MagicMock

from spotdl_lyrics_lora.ai_annotator import (
    call_ollama_api,
    call_local_openai_api,
    call_gemini_api,
    call_openai_api,
    enrich_metadata_with_ai,
)


class TestAiAnnotator(unittest.TestCase):
    """Test suite for fast AI annotation module with tiny local models."""

    @patch("requests.post")
    def test_call_ollama_api_success(self, mock_post):
        """Test calling local Ollama server."""
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "response": '{"caption": "Local Qwen 0.5B funk caption", "genre": "Funk", "language": "pt"}'
        }
        mock_post.return_value = mock_resp

        res = call_ollama_api("prompt", model="qwen2.5:0.5b")
        self.assertIsNotNone(res)
        self.assertEqual(res["caption"], "Local Qwen 0.5B funk caption")
        self.assertEqual(res["genre"], "Funk")

    @patch("requests.post")
    def test_call_local_openai_api_success(self, mock_post):
        """Test calling local OpenAI-compatible server (LM Studio / vLLM)."""
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"caption": "Local LM Studio pop track"}'}}]
        }
        mock_post.return_value = mock_resp

        res = call_local_openai_api("prompt", base_url="http://localhost:1234/v1")
        self.assertIsNotNone(res)
        self.assertEqual(res["caption"], "Local LM Studio pop track")

    @patch("requests.post")
    def test_call_gemini_api_success(self, mock_post):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"caption": "High-energy Brazilian funk", "genre": "Funk Carioca", "language": "pt"}'
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        res = call_gemini_api("prompt", "dummy_key")
        self.assertIsNotNone(res)
        self.assertEqual(res["caption"], "High-energy Brazilian funk")

    @patch.dict("os.environ", {}, clear=True)
    def test_enrich_metadata_no_keys_returns_none(self):
        res = enrich_metadata_with_ai("Title", "Artist", "Lyrics")
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
