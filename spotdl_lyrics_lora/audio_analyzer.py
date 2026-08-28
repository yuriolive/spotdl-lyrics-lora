"""Fast DSP audio feature analyzer for ACE-Step 1.5 LoRA preparation."""

from typing import Dict, Any, List
import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d
from scipy.signal import correlate

MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def estimate_bpm_from_signal(signal: np.ndarray, sample_rate: float) -> int:
    """Estimate track tempo (BPM) using energy onset flux and autocorrelation."""
    hop = int(sample_rate * 0.02)
    win_size = hop * 2
    if len(signal) <= win_size:
        return 120

    frames = np.lib.stride_tricks.sliding_window_view(np.abs(signal), win_size)[::hop]
    energy = np.mean(frames, axis=1)
    diff = np.maximum(0, np.diff(energy))
    smooth_filter = max(1, int(sample_rate / hop * 3))
    diff = np.maximum(0, diff - uniform_filter1d(diff, size=smooth_filter))

    corr = correlate(diff, diff, mode="full")
    corr = corr[len(corr) // 2 :]

    fps = sample_rate / hop
    min_lag = int(60 * fps / 220)
    max_lag = int(60 * fps / 55)

    if max_lag <= min_lag or len(corr) < max_lag:
        return 120

    best_lag = min_lag + int(np.argmax(corr[min_lag:max_lag]))
    return int(round(60 * fps / best_lag))


def estimate_key_from_signal(signal: np.ndarray, sample_rate: float) -> str:
    """Estimate musical key and scale via 12-chroma pitch class correlation."""
    n_fft = 2048
    hop = 1024
    if len(signal) < n_fft:
        return "C major"

    stft_frames = np.lib.stride_tricks.sliding_window_view(signal, n_fft)[::hop]
    window = np.hanning(n_fft)
    spec = np.abs(np.fft.rfft(stft_frames * window, axis=1))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)

    chroma = np.zeros(12)
    mask = (freqs >= 65.4) & (freqs <= 2093.0)
    spec_mean = spec.mean(axis=0)

    for f, mag in zip(freqs[mask], spec_mean[mask]):
        midi = int(round(69 + 12 * np.log2(f / 440.0)))
        chroma[midi % 12] += mag

    if chroma.sum() > 0:
        chroma /= chroma.sum()

    best_corr = -999.0
    best_key = "C major"

    for i in range(12):
        maj_prof = np.roll(MAJOR_PROFILE, i) / MAJOR_PROFILE.sum()
        score_maj = float(np.corrcoef(chroma, maj_prof)[0, 1])
        if score_maj > best_corr:
            best_corr = score_maj
            best_key = f"{PITCH_NAMES[i]} major"

        min_prof = np.roll(MINOR_PROFILE, i) / MINOR_PROFILE.sum()
        score_min = float(np.corrcoef(chroma, min_prof)[0, 1])
        if score_min > best_corr:
            best_corr = score_min
            best_key = f"{PITCH_NAMES[i]} minor"

    return best_key


def estimate_acoustic_mood(signal: np.ndarray, sample_rate: float) -> List[str]:
    """Derive acoustic descriptors from RMS energy and spectral brightness."""
    rms = float(np.sqrt(np.mean(signal**2)))
    n_fft = 1024
    if len(signal) > n_fft:
        windowed = signal[:n_fft * (len(signal) // n_fft)].reshape(-1, n_fft)
        spec = np.abs(np.fft.rfft(windowed, axis=1))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
        centroid = float(np.sum(freqs * spec.mean(axis=0)) / (np.sum(spec.mean(axis=0)) + 1e-8))
    else:
        centroid = 1500.0

    moods: List[str] = []
    if rms > 0.15:
        moods.append("punchy, high-energy")
    elif rms > 0.08:
        moods.append("driving, rhythmic")
    else:
        moods.append("mellow, dynamic")

    if centroid > 2000:
        moods.append("bright synth and percussion")
    elif centroid < 1000:
        moods.append("warm, bass-heavy")

    return moods


def analyze_audio_features(file_path: str) -> Dict[str, Any]:
    """Zero-AI audio feature extraction for an audio file."""
    try:
        data, sr = sf.read(file_path, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)

        target_sr = 11025
        factor = max(1, sr // target_sr)
        y = data[::factor]
        eff_sr = sr / factor

        return {
            "bpm": estimate_bpm_from_signal(y, eff_sr),
            "keyscale": estimate_key_from_signal(y, eff_sr),
            "timesignature": "4",
            "mood_tags": estimate_acoustic_mood(y, eff_sr),
        }
    except Exception:
        return {
            "bpm": 120,
            "keyscale": "C major",
            "timesignature": "4",
            "mood_tags": ["rhythmic"],
        }
