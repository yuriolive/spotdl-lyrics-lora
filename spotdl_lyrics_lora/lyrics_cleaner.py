"""Lyrics cleaning utilities for ACE-Step 1.5 LoRA dataset preparation.

This module provides functions to sanitize raw LRC or plain text lyrics
by stripping timestamps and metadata while preserving structural tags.
"""

import re
from typing import List

TIMESTAMP_PATTERN = re.compile(r"\[\d{1,2}:\d{2}(?:\.\d{1,3})?\]")
INLINE_TIMESTAMP_PATTERN = re.compile(r"<\d{1,2}:\d{2}(?:\.\d{1,3})?>")
METADATA_HEADER_PATTERN = re.compile(
    r"^\[(ar|al|ti|au|length|by|offset|re|ve|id):.*\]$", re.IGNORECASE
)
STRUCTURAL_TAGS = {
    "intro", "verse", "chorus", "bridge", "outro", "hook",
    "pre-chorus", "post-chorus", "solo", "instrumental", "drop", "refrain"
}


def is_structural_tag(text: str) -> bool:
    """Check if a line or bracketed tag represents a musical structure tag."""
    stripped = text.strip()
    match = re.match(r"^\[([a-zA-Z0-9\s\-]+)\]$", stripped)
    if not match:
        return False
    tag_name = match.group(1).strip().lower().split()[0]
    return tag_name in STRUCTURAL_TAGS


def clean_lrc_line(line: str) -> str:
    """Remove timestamps and extraneous markers from a single LRC line."""
    stripped = line.strip()
    if not stripped or METADATA_HEADER_PATTERN.match(stripped):
        return ""

    if is_structural_tag(stripped):
        return stripped

    cleaned = TIMESTAMP_PATTERN.sub("", stripped)
    cleaned = INLINE_TIMESTAMP_PATTERN.sub("", cleaned)
    return cleaned.strip()


def clean_lrc_content(lines: List[str]) -> List[str]:
    """Clean a list of LRC lines, stripping timestamps and removing empty lines."""
    result: List[str] = []
    for line in lines:
        cleaned = clean_lrc_line(line)
        if cleaned:
            result.append(cleaned)

    while result and not result[-1]:
        result.pop()
    while result and not result[0]:
        result.pop(0)

    return result


def clean_lyrics_text(raw_text: str) -> str:
    """Convert raw lyrics string (LRC or plain) into ACE-Step 1.5 formatted lyrics."""
    if not raw_text or not raw_text.strip():
        return ""

    lines = raw_text.splitlines()
    cleaned_lines = clean_lrc_content(lines)
    if not cleaned_lines:
        return ""

    return "\n".join(cleaned_lines) + "\n"
