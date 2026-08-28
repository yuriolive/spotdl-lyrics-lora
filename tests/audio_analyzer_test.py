"""Unit tests for audio_analyzer module."""

import unittest
import numpy as np

from spotdl_lyrics_lora.audio_analyzer import (
    estimate_bpm_from_signal,
    estimate_key_from_signal,
    analyze_audio_features,
)


class TestAudioAnalyzer(unittest.TestCase):
    """Test suite for fast DSP audio feature analyzer."""

    def test_estimate_bpm_synthetic_pulse(self):
        sr = 11025
        duration = 5.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        signal = np.zeros_like(t)

        interval = int(sr * 0.5)
        for idx in range(0, len(signal), interval):
            signal[idx : min(idx + 100, len(signal))] = 1.0

        bpm = estimate_bpm_from_signal(signal, sr)
        self.assertAlmostEqual(bpm, 120, delta=5)

    def test_estimate_key_synthetic_sine(self):
        sr = 11025
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        signal = np.sin(2 * np.pi * 440.0 * t)  # A4

        detected_key = estimate_key_from_signal(signal, sr)
        self.assertIn("A", detected_key)

    def test_analyze_audio_features_fallback(self):
        res = analyze_audio_features("/non/existent/path.mp3")
        self.assertEqual(res["bpm"], 120)
        self.assertEqual(res["timesignature"], "4")


if __name__ == "__main__":
    unittest.main()
