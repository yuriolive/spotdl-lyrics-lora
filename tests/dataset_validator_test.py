"""Unit tests for dataset_validator module."""

import unittest
import tempfile
from pathlib import Path

from spotdl_lyrics_lora.dataset_validator import (
    validate_lyrics_file,
    validate_dataset_folder,
)


class TestDatasetValidator(unittest.TestCase):
    """Test suite for dataset validation."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_validate_lyrics_file_clean(self):
        f = self.tmp_path / "song.lyrics.txt"
        f.write_text("[Intro]\nFirst line\n[Chorus]\nSecond line\n", encoding="utf-8")
        res = validate_lyrics_file(f)
        self.assertTrue(res["valid"])
        self.assertEqual(res["lines_count"], 4)
        self.assertEqual(len(res["errors"]), 0)

    def test_validate_lyrics_file_with_unstripped_timestamps(self):
        f = self.tmp_path / "song.lyrics.txt"
        f.write_text("[00:12.34] Unstripped line\n", encoding="utf-8")
        res = validate_lyrics_file(f)
        self.assertFalse(res["valid"])
        self.assertTrue(any("timestamp" in e for e in res["errors"]))

    def test_validate_dataset_folder(self):
        (self.tmp_path / "track1.mp3").write_bytes(b"audio")
        (self.tmp_path / "track1.lyrics.txt").write_text("Line 1\nLine 2", encoding="utf-8")
        (self.tmp_path / "track2.wav").write_bytes(b"audio")

        report = validate_dataset_folder(str(self.tmp_path))
        self.assertEqual(report["total_audio"], 2)
        self.assertEqual(report["valid_pairs"], 1)
        self.assertIn("track2.wav", report["missing_lyrics"])


if __name__ == "__main__":
    unittest.main()
