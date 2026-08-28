"""Unit tests for ai_annotator module."""

import unittest
from unittest.mock import patch, MagicMock

from spotdl_lyrics_lora.ai_annotator import (
    call_gemini_api,
    call_openai_api,
    enrich_metadata_with_ai,
)


class TestAiAnnotator(unittest.TestCase):
    """Test suite for fast AI annotation module."""

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
        self.assertEqual(res["genre"], "Funk Carioca")

    @patch("requests.post")
    def test_call_openai_api_success(self, mock_post):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '{"caption": "Pop track in C major"}'}}]
        }
        mock_post.return_value = mock_resp

        res = call_openai_api("prompt", "dummy_key")
        self.assertIsNotNone(res)
        self.assertEqual(res["caption"], "Pop track in C major")

    @patch.dict("os.environ", {}, clear=True)
    def test_enrich_metadata_no_keys_returns_none(self):
        res = enrich_metadata_with_ai("Title", "Artist", "Lyrics")
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
