"""Dynamic caption synthesis engine for ACE-Step 1.5 LoRA training datasets."""

from typing import Optional, List


def get_tempo_description(bpm: Optional[int]) -> str:
    """Return a descriptive tempo phrase based on BPM."""
    if not bpm:
        return "mid-tempo"
    if bpm < 80:
        return "slow, atmospheric"
    if bpm < 105:
        return "laid-back groove"
    if bpm < 125:
        return "rhythmic, upbeat"
    if bpm < 145:
        return "high-energy, fast-paced"
    return "fast, intense tempo"


def generate_caption(
    title: str,
    artist: Optional[str] = None,
    bpm: Optional[int] = None,
    keyscale: Optional[str] = None,
    timesignature: str = "4",
    genre: Optional[str] = None,
    language: Optional[str] = None,
    mood_tags: Optional[List[str]] = None,
) -> str:
    """Dynamically synthesize a training caption from acoustic and metadata features."""
    tempo_phrase = get_tempo_description(bpm)
    genre_str = genre.strip() if genre and genre.strip() else "music"

    descriptors = [tempo_phrase]
    if mood_tags:
        descriptors.extend([m for m in mood_tags if m])
    mood_part = ", ".join(dict.fromkeys(descriptors))

    parts = [f"A {mood_part} {genre_str} track"]

    if keyscale:
        parts.append(f"in {keyscale}")
    if bpm:
        parts.append(f"at {bpm} BPM")
    if timesignature and timesignature != "4":
        parts.append(f"with {timesignature}/4 time signature")

    caption = " ".join(parts)

    details = []
    if artist:
        if any(sep in artist for sep in [",", "/", "feat.", "ft.", "&"]):
            details.append(f"performed by {artist}")
        else:
            details.append(f"by {artist}")
    if title:
        details.append(f"titled '{title}'")

    if details:
        caption += f" {', '.join(details)}"

    lang_names = {
        "pt": "Portuguese",
        "es": "Spanish",
        "en": "English",
        "ja": "Japanese",
        "zh": "Chinese",
        "ko": "Korean",
        "fr": "French",
        "de": "German",
        "it": "Italian",
    }
    if language and language in lang_names:
        caption += f", featuring {lang_names[language]} vocals"

    return caption.strip() + "."
