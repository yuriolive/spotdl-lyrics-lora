"""Unit tests for lyrics_providers module."""

import unittest
from unittest.mock import patch, MagicMock

from spotdl_lyrics_lora.lyrics_providers import (
    LRCLibSource,
    LyricsOVHSource,
    SyncedLyricsPackageSource,
    fetch_lyrics_multi_source,
)


class TestLyricsProviders(unittest.TestCase):
    """Test suite for multi-source lyrics fetching."""

    @patch("requests.get")
    def test_lrclib_exact_get_success(self, mock_get):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "plainLyrics": "Hello world\nThis is a song",
            "syncedLyrics": "[00:01.00] Hello world",
        }
        mock_get.return_value = mock_resp

        source = LRCLibSource()
        lyrics = source.fetch_lyrics(title="Song", artist="Artist")
        self.assertEqual(lyrics, "Hello world\nThis is a song")

    @patch("requests.get")
    def test_lrclib_search_fallback(self, mock_get):
        resp_404 = MagicMock(status_code=404)
        resp_search = MagicMock(status_code=200)
        resp_search.json.return_value = [{"plainLyrics": "Found via search"}]
        mock_get.side_effect = [resp_404, resp_search]

        source = LRCLibSource()
        lyrics = source.fetch_lyrics(title="Song", artist="Artist")
        self.assertEqual(lyrics, "Found via search")

    @patch("requests.get")
    def test_lyrics_ovh_success(self, mock_get):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"lyrics": "Lyrics from OVH"}
        mock_get.return_value = mock_resp

        source = LyricsOVHSource()
        lyrics = source.fetch_lyrics(title="Song", artist="Artist")
        self.assertEqual(lyrics, "Lyrics from OVH")

    @patch.object(LRCLibSource, "fetch_lyrics", return_value=None)
    @patch.object(SyncedLyricsPackageSource, "fetch_lyrics", return_value=None)
    @patch.object(LyricsOVHSource, "fetch_lyrics", return_value="OVH Fallback Lyrics")
    def test_multi_source_fallback(self, mock_ovh, mock_synced, mock_lrclib):
        lyrics = fetch_lyrics_multi_source("Song", "Artist")
        self.assertEqual(lyrics, "OVH Fallback Lyrics")


if __name__ == "__main__":
    unittest.main()
