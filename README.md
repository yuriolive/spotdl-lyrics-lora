# 🎵 SpotDL Lyrics & LoRA Dataset Preparation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Automated toolkit to download tracks via **SpotDL**, clean and format timestamp-free lyrics, and extract musical metadata (**BPM, Key/Scale, Time Signature, and Captions**) specifically formatted for **ACE-Step 1.5 LoRA training**.

---

## ⚡ Multi-Tier Architecture

| Mode | Engine | Speed | Requirements | Features |
| :--- | :--- | :--- | :--- | :--- |
| **Zero-AI Mode** | DSP Signal Analysis | **~0.1s / song** | **100% offline & free** | Exact BPM, Key/scale, RMS energy, and acoustic mood |
| **Tiny Local Model** | Ollama / LM Studio / Transformers (`qwen2.5:0.5b`, `llama3.2:1b`) | **~0.5s / song** | **100% offline & local** (Zero API keys) | Adds `[Verse]` / `[Chorus]` section tags & studio captions |
| **Fast Cloud AI** | Gemini 2.5 Flash / GPT-4o-mini | **~1.5s / song** | `GEMINI_API_KEY` / `OPENAI_API_KEY` | Deep multimodal genre understanding & diffusion captions |

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
- 🦙 **Tiny Local Model Integration (`--ai-provider ollama` / `--ai-provider local`)**:
  - Run ultra-lightweight models (e.g. `qwen2.5:0.5b`, `llama3.2:1b`, `smollm2:1.7b`, `phi3:mini`) locally via Ollama, LM Studio, or vLLM to structure lyrics without needing any internet connection or cloud API keys.
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

### 1. Zero-AI Mode (Fastest, 100% Local & Free)
Process an existing directory of audio files (`.mp3`, `.wav`, `.flac`, `.ogg`, `.opus`, `.m4a`):

```bash
uv run spotdl-lora --dir ./my_music --auto-analyze --overwrite
```

### 2. Tiny Local Model (Ollama / Local LLM)
Structure lyrics into `[Verse]`/`[Chorus]` and generate descriptions using a tiny local model:

```bash
# Example with Ollama running Qwen 0.5B (takes < 0.5 GB RAM)
# 1. Run model: ollama run qwen2.5:0.5b
# 2. Run spotdl-lora:
uv run spotdl-lora --dir ./my_music --use-ai --ai-provider ollama --local-model qwen2.5:0.5b --overwrite
```

### 3. Fast Cloud AI Mode (Gemini Flash / OpenAI)
```bash
export GEMINI_API_KEY="your-api-key"
uv run spotdl-lora --dir ./my_music --use-ai --ai-provider gemini --overwrite
```

### 4. Download from Spotify & Prepare Dataset
Download a Spotify playlist and generate clean `.lyrics.txt` + `.json` annotations in one step:

```bash
uv run spotdl-lora --download "https://open.spotify.com/playlist/..." --output ./dataset --auto-analyze
```

### 5. Validate Dataset Readiness
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

# 1. Process all songs with Zero-AI DSP
created = process_folder("./funk-pop", auto_analyze=True, overwrite=True)

# 2. Process with local Ollama model
created = process_folder("./funk-pop", use_ai=True, ai_provider="ollama", local_model="qwen2.5:0.5b", overwrite=True)

# 3. Extract acoustic DSP features directly (< 0.2s)
features = analyze_audio_features("./funk-pop/track.mp3")
print(features)
# {'bpm': 136, 'keyscale': 'B major', 'timesignature': '4', 'mood_tags': ['punchy, high-energy']}

# 4. Download and prepare from Spotify
download_and_prepare("https://open.spotify.com/track/...", output_dir="./dataset", auto_analyze=True)
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
| `--use-ai` | Use AI model for section tagging & captions | `False` |
| `--ai-provider` | AI provider (`ollama`, `local`, `transformers`, `gemini`, `openai`, `openrouter`) | `auto` |
| `--local-model` | Local model name (e.g. `qwen2.5:0.5b`, `llama3.2:1b`) | `qwen2.5:0.5b` |
| `--local-url` | Local server URL (e.g. `http://localhost:11434`, `http://localhost:1234/v1`) | `http://localhost:11434` |
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
