"""SpotDL Lyrics & LoRA Dataset Preparation Toolkit for ACE-Step 1.5.

Automated audio downloading, timestamp-free lyrics cleaning, and metadata annotation.
"""

from spotdl_lyrics_lora.pipeline import (
    process_audio_file,
    process_folder,
    download_and_prepare,
)
from spotdl_lyrics_lora.lyrics_cleaner import clean_lyrics_text
from spotdl_lyrics_lora.audio_analyzer import analyze_audio_features
from spotdl_lyrics_lora.caption_generator import generate_caption
from spotdl_lyrics_lora.dataset_validator import validate_dataset_folder

__version__ = "0.1.0"
__all__ = [
    "process_audio_file",
    "process_folder",
    "download_and_prepare",
    "clean_lyrics_text",
    "analyze_audio_features",
    "generate_caption",
    "validate_dataset_folder",
]
