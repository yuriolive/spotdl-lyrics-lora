"""Lyrics structural tagger for ACE-Step 1.5 LoRA training.

Inserts musical section tags ([Intro], [Verse 1], [Chorus], [Bridge], [Outro])
into plain lyrics using repetition analysis or local/cloud AI models.
"""

import re
from typing import List
from spotdl_lyrics_lora.lyrics_cleaner import is_structural_tag


def has_structural_tags(text: str) -> bool:
    """Check if lyrics text already contains structural section tags."""
    for line in text.splitlines():
        if is_structural_tag(line):
            return True
    return False


def group_into_stanzas(lines: List[str]) -> List[List[str]]:
    """Group lines into stanzas based on empty line breaks or 4-line blocks."""
    stanzas: List[List[str]] = []
    current: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                stanzas.append(current)
                current = []
        else:
            current.append(stripped)

    if current:
        stanzas.append(current)

    if len(stanzas) == 1 and len(stanzas[0]) > 8:
        all_lines = stanzas[0]
        stanzas = []
        chunk_size = 4
        for i in range(0, len(all_lines), chunk_size):
            stanzas.append(all_lines[i : i + chunk_size])

    return stanzas


def normalize_stanza_text(stanza: List[str]) -> str:
    """Join and normalize stanza lines for repetition matching."""
    return " ".join(re.sub(r"[^\w\s]", "", l.lower()) for l in stanza).strip()


def structure_lyrics_heuristically(text: str) -> str:
    """Analyze stanzas and repetition patterns to insert [Verse], [Chorus], etc."""
    if not text or not text.strip():
        return ""

    if has_structural_tags(text):
        return text.strip() + "\n"

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return ""

    stanzas = group_into_stanzas(text.splitlines())
    if not stanzas:
        return text.strip() + "\n"

    norm_stanzas = [normalize_stanza_text(s) for s in stanzas]
    counts: dict = {}
    for norm in norm_stanzas:
        if norm:
            counts[norm] = counts.get(norm, 0) + 1

    chorus_norm = None
    max_rep = 1
    for norm, count in counts.items():
        if count > max_rep and len(norm.split()) >= 4:
            max_rep = count
            chorus_norm = norm

    verse_num = 1
    output_lines: List[str] = []

    for i, stanza in enumerate(stanzas):
        norm = norm_stanzas[i]
        is_first = (i == 0)
        is_last = (i == len(stanzas) - 1)

        if is_first and len(stanza) <= 3 and norm != chorus_norm:
            tag = "[Intro]"
        elif norm == chorus_norm and chorus_norm is not None:
            tag = "[Chorus]"
        elif is_last and (len(stanza) <= 4 or norm != chorus_norm and len(stanzas) > 3):
            tag = "[Outro]"
        elif i > 1 and len(stanzas) > 4 and i == len(stanzas) - 2 and norm != chorus_norm:
            tag = "[Bridge]"
        else:
            tag = f"[Verse {verse_num}]"
            verse_num += 1

        output_lines.append(tag)
        output_lines.extend(stanza)
        output_lines.append("")

    while output_lines and not output_lines[-1]:
        output_lines.pop()

    return "\n".join(output_lines) + "\n"
