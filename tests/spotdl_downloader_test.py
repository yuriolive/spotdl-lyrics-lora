"""Unit tests for spotdl_downloader module."""

import unittest
from unittest.mock import patch, MagicMock

from spotdl_lyrics_lora.spotdl_downloader import (
    is_spotdl_installed,
    download_tracks,
)


class TestSpotdlDownloader(unittest.TestCase):
    """Test suite for spotdl wrapper."""

    @patch("shutil.which", return_value="/usr/local/bin/spotdl")
    def test_is_spotdl_installed_true(self, mock_which):
        self.assertTrue(is_spotdl_installed())

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_is_spotdl_installed_python_module(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(is_spotdl_installed())

    @patch("spotdl_lyrics_lora.spotdl_downloader.is_spotdl_installed", return_value=False)
    def test_download_tracks_not_installed_raises(self, mock_installed):
        with self.assertRaises(RuntimeError):
            download_tracks("https://open.spotify.com/track/123", "/tmp/out")


if __name__ == "__main__":
    unittest.main()
