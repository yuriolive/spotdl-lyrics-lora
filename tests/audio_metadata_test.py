"""Unit tests for audio_metadata module."""

import unittest
from unittest.mock import patch

from spotdl_lyrics_lora.audio_metadata import (
    parse_filename_metadata,
    find_companion_lrc,
    get_audio_info,
)


class TestAudioMetadata(unittest.TestCase):
    """Test suite for audio metadata extraction."""

    def test_parse_filename_artist_and_title(self):
        meta = parse_filename_metadata("Anitta - Funk Rave.mp3")
        self.assertEqual(meta["artist"], "Anitta")
        self.assertEqual(meta["title"], "Funk Rave")

    def test_parse_filename_multiple_artists(self):
        meta = parse_filename_metadata("Anitta, MC Ryan SP - Vai Vendo.mp3")
        self.assertEqual(meta["artist"], "Anitta, MC Ryan SP")
        self.assertEqual(meta["title"], "Vai Vendo")

    def test_parse_filename_title_only(self):
        meta = parse_filename_metadata("MySpecialTrack.wav")
        self.assertEqual(meta["artist"], "")
        self.assertEqual(meta["title"], "MySpecialTrack")

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.read_text")
    def test_find_companion_lrc_success(self, mock_read, mock_is_file):
        mock_is_file.return_value = True
        mock_read.return_value = "[00:01.00] Line 1"

        lrc_text = find_companion_lrc("C:/music/track1.mp3")
        self.assertEqual(lrc_text, "[00:01.00] Line 1")


if __name__ == "__main__":
    unittest.main()
