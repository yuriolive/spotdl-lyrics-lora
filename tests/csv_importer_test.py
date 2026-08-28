"""Unit tests for csv_importer module."""

import unittest
import tempfile
from pathlib import Path

from spotdl_lyrics_lora.csv_importer import (
    load_key_bpm_csv,
    find_and_load_csv,
)


class TestCsvImporter(unittest.TestCase):
    """Test suite for Key-BPM-Finder CSV importing."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_load_key_bpm_csv(self):
        csv_file = self.tmp_path / "key_bpm.csv"
        csv_content = (
            "File,Artist,Title,BPM,Key,Camelot\n"
            "song1.wav,Artist1,Title1,128,A minor,8A\n"
            "song2.mp3,Artist2,Title2,140,D major,10B\n"
        )
        csv_file.write_text(csv_content, encoding="utf-8")

        res = load_key_bpm_csv(str(csv_file))
        self.assertIn("song1.wav", res)
        self.assertIn("song1", res)
        self.assertEqual(res["song1.wav"]["bpm"], 128)
        self.assertEqual(res["song1.wav"]["keyscale"], "A minor")
        self.assertEqual(res["song1.wav"]["camelot"], "8A")

        self.assertEqual(res["song2.mp3"]["bpm"], 140)
        self.assertEqual(res["song2.mp3"]["keyscale"], "D major")

    def test_find_and_load_csv_in_folder(self):
        csv_file = self.tmp_path / "dataset_bpm.csv"
        csv_file.write_text("File,BPM,Key\ntrack.mp3,130,C major\n", encoding="utf-8")

        res = find_and_load_csv(str(self.tmp_path))
        self.assertIn("track.mp3", res)
        self.assertEqual(res["track.mp3"]["bpm"], 130)


if __name__ == "__main__":
    unittest.main()
