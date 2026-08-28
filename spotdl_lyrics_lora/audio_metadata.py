"""Audio metadata and embedded lyrics extractor for LoRA data preparation."""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".aiff", ".opus", ".m4a"}


def _decode_id3_text(data: bytes, enc_byte: int) -> str:
    """Decode ID3 text frame byte payload according to the encoding flag."""
    if enc_byte == 0:
        return data.decode("latin1", errors="ignore").rstrip("\x00")
    if enc_byte == 1:
        return data.decode("utf-16", errors="ignore").rstrip("\x00")
    if enc_byte == 2:
        return data.decode("utf-16-be", errors="ignore").rstrip("\x00")
    if enc_byte == 3:
        return data.decode("utf-8", errors="ignore").rstrip("\x00")
    return data.decode("utf-8", errors="ignore").rstrip("\x00")


def parse_id3_tags(file_path: str) -> Dict[str, Any]:
    """Parse ID3v2 metadata frames from an MP3 file."""
    meta: Dict[str, Any] = {}
    if not os.path.exists(file_path):
        return meta

    try:
        with open(file_path, "rb") as f:
            header = f.read(10)
            if len(header) < 10 or header[:3] != b"ID3":
                return meta
            ver_major = header[3]
            tag_size = (
                ((header[6] & 0x7F) << 21)
                | ((header[7] & 0x7F) << 14)
                | ((header[8] & 0x7F) << 7)
                | (header[9] & 0x7F)
            )
            tag_data = f.read(tag_size)

        idx = 0
        while idx + 10 <= len(tag_data):
            frame_id = tag_data[idx:idx + 4].decode("latin1", errors="ignore")
            if not frame_id.isalnum() or frame_id == "\x00\x00\x00\x00":
                break
            if ver_major == 4:
                frame_size = (
                    ((tag_data[idx + 4] & 0x7F) << 21)
                    | ((tag_data[idx + 5] & 0x7F) << 14)
                    | ((tag_data[idx + 6] & 0x7F) << 7)
                    | (tag_data[idx + 7] & 0x7F)
                )
            else:
                frame_size = int.from_bytes(tag_data[idx + 4:idx + 8], "big")
            idx += 10
            frame_body = tag_data[idx:idx + frame_size]
            idx += frame_size

            if len(frame_body) > 1:
                enc = frame_body[0]
                raw = frame_body[1:]
                if frame_id == "TIT2":
                    meta["title"] = _decode_id3_text(raw, enc)
                elif frame_id == "TPE1":
                    meta["artist"] = _decode_id3_text(raw, enc)
                elif frame_id == "TALB":
                    meta["album"] = _decode_id3_text(raw, enc)
                elif frame_id == "TCON":
                    meta["genre"] = _decode_id3_text(raw, enc)
                elif frame_id in ("TDRC", "TYER"):
                    meta["year"] = _decode_id3_text(raw, enc)
                elif frame_id == "WOAS":
                    meta["spotify_url"] = frame_body.decode("latin1", errors="ignore").rstrip("\x00")
                elif frame_id == "USLT" and len(frame_body) > 5:
                    meta["embedded_lyrics"] = _decode_id3_text(frame_body[4:], enc)
    except Exception:
        pass
    return meta


def parse_filename_metadata(file_path: str) -> Dict[str, str]:
    """Extract artist and title fallback from filename (e.g. 'Artist - Title.mp3')."""
    stem = Path(file_path).stem
    parts = re.split(r"\s+-\s+", stem, maxsplit=1)
    if len(parts) == 2:
        return {"artist": parts[0].strip(), "title": parts[1].strip()}
    return {"artist": "", "title": stem.strip()}


def find_companion_lrc(file_path: str) -> Optional[str]:
    """Find and return text from a companion LRC file if one exists."""
    p = Path(file_path)
    candidates = [
        p.with_suffix(".lrc"),
        p.parent / f"{p.stem}.lyrics.lrc",
        p.parent / f"{p.stem}.lyrics.txt",
        p.parent / f"{p.stem}.txt",
    ]
    for c in candidates:
        if c.is_file() and c.suffix.lower() == ".lrc":
            try:
                return c.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
    return None


def get_audio_info(file_path: str) -> Dict[str, Any]:
    """Extract complete track metadata and available lyrics for an audio file."""
    info = parse_id3_tags(file_path)
    fn_info = parse_filename_metadata(file_path)

    if not info.get("title"):
        info["title"] = fn_info.get("title", "")
    if not info.get("artist"):
        info["artist"] = fn_info.get("artist", "")

    info["companion_lrc"] = find_companion_lrc(file_path)
    return info
