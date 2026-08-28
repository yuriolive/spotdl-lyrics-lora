# 🎵 SpotDL Lyrics & LoRA Dataset Preparation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Automated toolkit to download tracks via **SpotDL**, clean and format timestamp-free lyrics, and extract musical metadata (**BPM, Key/Scale, Time Signature, and Captions**) specifically formatted for **ACE-Step 1.5 LoRA training**.

---

## ⚡ Features

- 🎧 **SpotDL Integration**: Programmatically download tracks, albums, and playlists directly from Spotify URLs or search queries.
- 📝 **Timestamp-Free Lyrics Cleaning**: Strips LRC timestamps (`[mm:ss.xx]`, `[mm:ss.xxx]`, `<mm:ss.xx>`) and metadata headers while preserving musical structure tags (`[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`).
- 🌐 **Multi-Source Lyrics Fallback**: Queries **LRCLIB** (free, exact match & search) and **Lyrics.ovh** automatically when embedded lyrics or companion `.lrc` files are missing.
- ⚡ **Zero-AI DSP Mode (`--auto-analyze`)**:
  - **BPM**: Onset energy flux & autocorrelation via `scipy`/`numpy` in **~0.1s**.
  - **Key & Scale**: 12-chroma pitch class STFT correlated against 24 Krumhansl-Kessler harmonic profiles in **~0.1s**.
  - **Acoustic Mood**: RMS energy and spectral brightness dynamically categorize vibe (`punchy, high-energy`, `warm, bass-heavy`, `bright synth`, `driving`).
  - **Language Detection**: Deterministic script & stopword analysis (`pt`, `es`, `en`, `ja`, `zh`, `ko`, `fr`, `de`, `it`).
- 🤖 **Fast AI Enrichment Mode (`--use-ai`)**:
  - Optional Gemini Flash / GPT-4o-mini / OpenRouter integration for AI section structuring and studio diffusion captions.
- 📊 **Key-BPM-Finder CSV Auto-Importer**: Drag-and-drop CSV exports from [Key-BPM-Finder](https://vocalremover.org/key-bpm-finder) or DJ software.
- 🔍 **Dataset Validator (`--validate`)**: Audits dataset readiness and checks formatting before starting LoRA fine-tuning.

---

## 📦 Installation

Using [`uv`](https://docs.astral.sh/uv/) (Recommended):

```bash
# Clone the repository
git clone https://github.com/yuriolive/spotdl-lyrics-lora.git
cd spotdl-lyrics-lora

# Install dependencies
uv sync
```

Or with standard `pip`:

```bash
pip install -e .
```

*Note: Ensure `ffmpeg` is installed on your system if you plan to download audio files with SpotDL.*

---

## 🚀 Quick Start

### 1. Zero-AI Mode (Offline & Fast)
Process an existing directory of audio files (`.mp3`, `.wav`, `.flac`, `.ogg`, `.opus`, `.m4a`):

```bash
uv run spotdl-lora --dir ./my_music --auto-analyze --overwrite
```

### 2. Download from Spotify & Prepare Dataset
Download a Spotify playlist and generate clean `.lyrics.txt` + `.json` annotations in one step:

```bash
uv run spotdl-lora --download "https://open.spotify.com/playlist/..." --output ./dataset --auto-analyze
```

### 3. Fast AI Mode (Gemini Flash / OpenAI)
Add structural section tags (`[Verse]`, `[Chorus]`) and studio-grade diffusion captions:

```bash
export GEMINI_API_KEY="your-api-key"
uv run spotdl-lora --dir ./my_music --use-ai --ai-provider gemini --overwrite
```

### 4. Validate Dataset Readiness
Verify that all audio files have matching, clean lyrics and valid metadata:

```bash
uv run spotdl-lora --validate ./my_music
```

---

## 📋 Generated File Structure

Each audio track is paired with ACE-Step 1.5 compliant training files:

```
dataset/
├── song1.mp3               # Audio track
├── song1.lyrics.txt        # Clean lyrics without timestamps
├── song1.json              # Annotations (BPM, Key, Caption, Language)
└── song1.caption.txt       # Natural language description
```

#### Example `song1.json`:
```json
{
    "caption": "A high-energy, fast-paced, punchy, high-energy Brazilian funk track in G minor at 143 BPM performed by Anitta/PEDRO SAMPAIO, titled 'NO CHÃO NOVINHA', featuring Portuguese vocals.",
    "bpm": 143,
    "keyscale": "G minor",
    "timesignature": "4",
    "language": "pt"
}
```

---

## 💻 Python Library Usage

```python
from spotdl_lyrics_lora import (
    process_folder,
    process_audio_file,
    download_and_prepare,
    analyze_audio_features,
    validate_dataset_folder,
)

# 1. Process all songs in a directory
created = process_folder("./funk-pop", auto_analyze=True, overwrite=True)

# 2. Extract acoustic DSP features directly (< 0.2s)
features = analyze_audio_features("./funk-pop/track.mp3")
print(features)
# {'bpm': 136, 'keyscale': 'B major', 'timesignature': '4', 'mood_tags': ['punchy, high-energy']}

# 3. Download and prepare from Spotify
download_and_prepare("https://open.spotify.com/track/...", output_dir="./dataset", auto_analyze=True)

# 4. Audit dataset health
report = validate_dataset_folder("./dataset")
```

---

## 🛠️ CLI Options Reference

| Flag | Description | Default |
| :--- | :--- | :--- |
| `-d, --dir` | Directory containing audio files to process | `None` |
| `-f, --file` | Path to a single audio file to process | `None` |
| `--download` | Spotify URL (track, album, playlist) or search query | `None` |
| `-o, --output` | Destination directory for output files | Same as audio |
| `--auto-analyze` | Zero-AI detection of BPM, Key, Time Signature, and Captions | `False` |
| `--use-ai` | Use fast AI model for section tagging & captions | `False` |
| `--ai-provider` | AI provider (`gemini`, `openai`, `openrouter`, `auto`) | `auto` |
| `--json` | Generate `.json` & `.caption.txt` metadata files | `False` |
| `--overwrite` | Overwrite existing output files | `False` |
| `--format` | Audio format for downloads (`mp3`, `flac`, `wav`, `opus`) | `mp3` |
| `--validate` | Run validation audit on a dataset directory | `None` |

---

## 🧪 Running Tests

```bash
uv run python -m unittest discover -s tests -p "*_test.py"
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
