"""Unit tests for lyrics_cleaner module."""

import unittest
from spotdl_lyrics_lora.lyrics_cleaner import (
    clean_lrc_line,
    clean_lrc_content,
    clean_lyrics_text,
    is_structural_tag,
)


class TestLyricsCleaner(unittest.TestCase):
    """Test suite for LRC cleaning and formatting."""

    def test_clean_lrc_line_with_timestamp(self):
        line = "[00:13.33] Look at what you cannot have"
        self.assertEqual(clean_lrc_line(line), "Look at what you cannot have")

    def test_clean_lrc_line_with_three_decimal_timestamp(self):
        line = "[01:23.456] This is another line"
        self.assertEqual(clean_lrc_line(line), "This is another line")

    def test_clean_lrc_line_metadata_header(self):
        self.assertEqual(clean_lrc_line("[ar:Anitta]"), "")
        self.assertEqual(clean_lrc_line("[ti:Funk Rave]"), "")
        self.assertEqual(clean_lrc_line("[al:Funk Generation]"), "")
        self.assertEqual(clean_lrc_line("[length:02:45]"), "")

    def test_preserve_structural_tags(self):
        self.assertTrue(is_structural_tag("[Verse 1]"))
        self.assertTrue(is_structural_tag("[Chorus]"))
        self.assertTrue(is_structural_tag("[Intro]"))
        self.assertTrue(is_structural_tag("[Bridge]"))
        self.assertFalse(is_structural_tag("[00:12.34]"))

        self.assertEqual(clean_lrc_line("[Verse 1]"), "[Verse 1]")
        self.assertEqual(clean_lrc_line("[Chorus]"), "[Chorus]")

    def test_clean_lyrics_text_full(self):
        raw_lrc = (
            "[ar:Artist]\n"
            "[ti:Song]\n"
            "\n"
            "[00:01.00] [Intro]\n"
            "[00:05.00] Hello world\n"
            "[00:10.50] Dancing in the rain\n"
        )
        cleaned = clean_lyrics_text(raw_lrc)
        expected = "[Intro]\nHello world\nDancing in the rain\n"
        self.assertEqual(cleaned, expected)

    def test_clean_empty_or_whitespace(self):
        self.assertEqual(clean_lyrics_text(""), "")
        self.assertEqual(clean_lyrics_text("   \n\n  "), "")


if __name__ == "__main__":
    unittest.main()
