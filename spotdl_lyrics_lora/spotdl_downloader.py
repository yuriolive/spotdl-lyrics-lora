"""SpotDL integration wrapper for downloading audio tracks."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".opus", ".m4a", ".aac"}


def is_spotdl_installed() -> bool:
    """Check if spotdl executable or python module is available."""
    if shutil.which("spotdl") is not None:
        return True
    try:
        res = subprocess.run(
            [sys.executable, "-m", "spotdl", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        return res.returncode == 0
    except Exception:
        return False


def get_spotdl_cmd() -> List[str]:
    """Get the command prefix to execute spotdl."""
    if shutil.which("spotdl") is not None:
        return ["spotdl"]
    return [sys.executable, "-m", "spotdl"]


def download_tracks(
    query_or_url: str,
    output_dir: str,
    audio_format: str = "mp3",
) -> List[str]:
    """Download audio tracks from Spotify URL or search query using spotdl."""
    if not is_spotdl_installed():
        raise RuntimeError(
            "spotdl is not installed or not found in PATH. "
            "Install it via: pip install spotdl"
        )

    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    existing_files = {
        f.resolve()
        for f in out_path.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTS
    }

    cmd = get_spotdl_cmd() + [
        "download",
        query_or_url,
        "--output",
        str(out_path),
        "--format",
        audio_format,
    ]

    print(f"Running spotdl download for: {query_or_url}")
    result = subprocess.run(cmd, cwd=str(out_path), text=True)

    if result.returncode != 0:
        raise RuntimeError(f"spotdl download failed with return code {result.returncode}")

    current_files = {
        f.resolve()
        for f in out_path.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTS
    }
    new_or_updated = sorted(str(p) for p in (current_files - existing_files))

    if not new_or_updated:
        return sorted(str(p) for p in current_files)

    return new_or_updated
