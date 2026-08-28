"""Unit tests for caption_generator module."""

import unittest

from spotdl_lyrics_lora.caption_generator import (
    get_tempo_description,
    generate_caption,
)


class TestCaptionGenerator(unittest.TestCase):
    """Test suite for deterministic rule-based caption generation."""

    def test_get_tempo_description(self):
        self.assertEqual(get_tempo_description(70), "slow, atmospheric")
        self.assertEqual(get_tempo_description(120), "rhythmic, upbeat")
        self.assertEqual(get_tempo_description(140), "high-energy, fast-paced")

    def test_generate_caption_complete(self):
        caption = generate_caption(
            title="Funk Rave",
            artist="Anitta",
            bpm=136,
            keyscale="B major",
            timesignature="4",
            genre="Brazilian funk",
            language="pt",
            mood_tags=["punchy, high-energy", "bright synth and percussion"],
        )
        self.assertIn("136 BPM", caption)
        self.assertIn("B major", caption)
        self.assertIn("Anitta", caption)
        self.assertIn("Funk Rave", caption)
        self.assertIn("Portuguese vocals", caption)
        self.assertTrue(caption.endswith("."))


if __name__ == "__main__":
    unittest.main()
