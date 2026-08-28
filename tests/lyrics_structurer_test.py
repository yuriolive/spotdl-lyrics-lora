"""Unit tests for lyrics_structurer module."""

import unittest

from spotdl_lyrics_lora.lyrics_structurer import (
    has_structural_tags,
    group_into_stanzas,
    structure_lyrics_heuristically,
)


class TestLyricsStructurer(unittest.TestCase):
    """Test suite for structural tag insertion."""

    def test_has_structural_tags(self):
        self.assertTrue(has_structural_tags("[Verse 1]\nLine 1\n[Chorus]\nLine 2"))
        self.assertFalse(has_structural_tags("Just a regular line 1\nLine 2"))

    def test_structure_lyrics_heuristically(self):
        plain_lyrics = (
            "Look at what you cannot have\n"
            "Boss bitch, mulher mala, mala\n"
            "\n"
            "Pásala, chócala, sácala, tómala\n"
            "Sá-sá-sácala, tómala\n"
            "\n"
            "Got that sauce\n"
            "No me haga hablar\n"
            "\n"
            "Pásala, chócala, sácala, tómala\n"
            "Sá-sá-sácala, tómala\n"
            "\n"
            "Sá-sá-sá-sá-sá-sá\n"
        )
        structured = structure_lyrics_heuristically(plain_lyrics)
        self.assertIn("[Chorus]", structured)
        self.assertIn("[Intro]", structured)
        self.assertIn("[Outro]", structured)

    def test_already_structured_unchanged(self):
        already = "[Verse]\nLine 1\n[Chorus]\nLine 2\n"
        self.assertEqual(structure_lyrics_heuristically(already), already)


if __name__ == "__main__":
    unittest.main()
