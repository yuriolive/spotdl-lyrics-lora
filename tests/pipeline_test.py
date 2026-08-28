"""Unit tests for pipeline module."""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from spotdl_lyrics_lora.pipeline import (
    process_audio_file,
    process_folder,
)


class TestPipeline(unittest.TestCase):
    """Test suite for main pipeline."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    @patch("spotdl_lyrics_lora.pipeline.fetch_lyrics_multi_source")
    def test_process_audio_file_success(self, mock_fetch):
        mock_fetch.return_value = "[00:05.00] Hello lyrics\n[00:10.00] Second line"

        dummy_audio = self.tmp_path / "Artist - Track.mp3"
        dummy_audio.write_bytes(b"dummy audio data")

        out_lyrics = process_audio_file(str(dummy_audio))
        self.assertIsNotNone(out_lyrics)
        self.assertTrue(Path(out_lyrics).exists())

        content = Path(out_lyrics).read_text(encoding="utf-8")
        self.assertEqual(content, "Hello lyrics\nSecond line\n")

    @patch("spotdl_lyrics_lora.pipeline.fetch_lyrics_multi_source")
    def test_process_audio_file_with_json(self, mock_fetch):
        mock_fetch.return_value = "Test plain lyrics"

        dummy_audio = self.tmp_path / "Singer - Hit.mp3"
        dummy_audio.write_bytes(b"dummy audio data")

        out_lyrics = process_audio_file(str(dummy_audio), generate_json=True)
        self.assertIsNotNone(out_lyrics)

        json_file = self.tmp_path / "Singer - Hit.json"
        self.assertTrue(json_file.exists())

    @patch("spotdl_lyrics_lora.pipeline.fetch_lyrics_multi_source")
    def test_process_folder_success(self, mock_fetch):
        mock_fetch.return_value = "Song lyrics text"

        (self.tmp_path / "Song1.mp3").write_bytes(b"data1")
        (self.tmp_path / "Song2.wav").write_bytes(b"data2")

        created = process_folder(str(self.tmp_path))
        self.assertEqual(len(created), 2)


if __name__ == "__main__":
    unittest.main()
