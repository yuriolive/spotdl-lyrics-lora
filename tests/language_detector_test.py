"""Unit tests for language_detector module."""

import unittest

from spotdl_lyrics_lora.language_detector import detect_language


class TestLanguageDetector(unittest.TestCase):
    """Test suite for lyrics language detection."""

    def test_detect_portuguese(self):
        text = "No chão novinha, jogando a bunda pra trás com você não para"
        self.assertEqual(detect_language(text), "pt")

    def test_detect_spanish(self):
        text = "Encuéntrame en el trópico por los lados de Punta Cana con la cura"
        self.assertEqual(detect_language(text), "es")

    def test_detect_english(self):
        text = "Walking down the empty street echoes dancing at my feet tonight with you"
        self.assertEqual(detect_language(text), "en")

    def test_detect_japanese(self):
        text = "ナユタン星からの物体Y あなたと私"
        self.assertEqual(detect_language(text), "ja")

    def test_detect_korean(self):
        text = "안녕하세요 오늘 밤에"
        self.assertEqual(detect_language(text), "ko")


if __name__ == "__main__":
    unittest.main()
