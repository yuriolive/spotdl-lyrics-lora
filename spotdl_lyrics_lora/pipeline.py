"""Pipeline orchestrator for SpotDL audio downloading and LoRA lyrics preparation."""

import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from spotdl_lyrics_lora.ai_annotator import enrich_metadata_with_ai
from spotdl_lyrics_lora.audio_analyzer import analyze_audio_features
from spotdl_lyrics_lora.audio_metadata import AUDIO_EXTENSIONS, get_audio_info
from spotdl_lyrics_lora.caption_generator import generate_caption
from spotdl_lyrics_lora.csv_importer import find_and_load_csv
from spotdl_lyrics_lora.language_detector import detect_language
from spotdl_lyrics_lora.lyrics_cleaner import clean_lyrics_text
from spotdl_lyrics_lora.lyrics_providers import fetch_lyrics_multi_source
from spotdl_lyrics_lora.spotdl_downloader import download_tracks


def process_audio_file(
    audio_path: str,
    output_dir: Optional[str] = None,
    overwrite: bool = False,
    generate_json: bool = False,
    auto_analyze: bool = False,
    use_ai: bool = False,
    ai_provider: str = "auto",
    csv_metadata: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Process an audio file to generate ACE-Step 1.5 lyrics and dynamic annotations."""
    audio_p = Path(audio_path).resolve()
    if not audio_p.is_file():
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        return None

    target_dir = Path(output_dir).resolve() if output_dir else audio_p.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    lyrics_file = target_dir / f"{audio_p.stem}.lyrics.txt"
    meta = get_audio_info(str(audio_p))
    raw_lyrics = meta.get("companion_lrc") or meta.get("embedded_lyrics")

    if not raw_lyrics and (not lyrics_file.exists() or overwrite):
        raw_lyrics = fetch_lyrics_multi_source(
            title=meta.get("title", ""), artist=meta.get("artist", ""), album=meta.get("album", "")
        )

    cleaned_lyrics = ""
    if raw_lyrics:
        cleaned_lyrics = clean_lyrics_text(raw_lyrics)
    elif lyrics_file.exists():
        cleaned_lyrics = lyrics_file.read_text(encoding="utf-8", errors="ignore")

    csv_info = (csv_metadata or {}).get(audio_p.name) or (csv_metadata or {}).get(audio_p.stem) or {}
    bpm_val = csv_info.get("bpm")
    key_val = csv_info.get("keyscale")
    camelot_val = csv_info.get("camelot")
    ts_val = "4"
    mood_tags = []

    if auto_analyze and (bpm_val is None or key_val is None):
        features = analyze_audio_features(str(audio_p))
        bpm_val = bpm_val or features.get("bpm")
        key_val = key_val or features.get("keyscale")
        ts_val = features.get("timesignature", "4")
        mood_tags = features.get("mood_tags", [])

    ai_data = None
    if use_ai:
        ai_data = enrich_metadata_with_ai(
            title=meta.get("title", audio_p.stem),
            artist=meta.get("artist", ""),
            lyrics=cleaned_lyrics,
            bpm=bpm_val,
            keyscale=key_val,
            provider=ai_provider,
        )
        if ai_data and ai_data.get("structured_lyrics"):
            cleaned_lyrics = clean_lyrics_text(ai_data["structured_lyrics"])

    if cleaned_lyrics and (not lyrics_file.exists() or overwrite):
        lyrics_file.write_text(cleaned_lyrics, encoding="utf-8")
        print(f"  [Saved Lyrics]  -> {lyrics_file.name}")

    if generate_json:
        json_file = target_dir / f"{audio_p.stem}.json"
        caption_file = target_dir / f"{audio_p.stem}.caption.txt"

        lang = (ai_data or {}).get("language") or detect_language(cleaned_lyrics or meta.get("title", ""))
        genre = (ai_data or {}).get("genre") or meta.get("genre") or ("Brazilian funk" if "funk" in str(target_dir).lower() else None)
        caption = (ai_data or {}).get("caption") or csv_info.get("caption") or generate_caption(
            title=meta.get("title", audio_p.stem),
            artist=meta.get("artist"),
            bpm=bpm_val,
            keyscale=key_val,
            timesignature=ts_val,
            genre=genre,
            language=lang,
            mood_tags=mood_tags,
        )

        if not json_file.exists() or overwrite:
            tpl = {
                "caption": caption,
                "bpm": bpm_val,
                "keyscale": key_val,
                "timesignature": ts_val,
                "language": lang,
            }
            if camelot_val:
                tpl["camelot"] = camelot_val
            json_file.write_text(json.dumps(tpl, indent=4, ensure_ascii=False), encoding="utf-8")
            caption_file.write_text(caption, encoding="utf-8")
            print(f"  [Saved Annot.]  -> {json_file.name} ({bpm_val} BPM, {key_val}, {lang})")

    return str(lyrics_file) if lyrics_file.exists() else None


def process_folder(
    input_dir: str,
    output_dir: Optional[str] = None,
    overwrite: bool = False,
    generate_json: bool = False,
    auto_analyze: bool = False,
    use_ai: bool = False,
    ai_provider: str = "auto",
) -> List[str]:
    """Process all audio files in a directory."""
    in_path = Path(input_dir).resolve()
    if not in_path.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")

    audio_files = sorted(f for f in in_path.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS)
    if not audio_files:
        print(f"No audio files found in: {input_dir}")
        return []

    csv_data = find_and_load_csv(str(in_path))
    if csv_data:
        print(f"Loaded metadata for {len(csv_data)} track(s) from CSV")

    print(f"Found {len(audio_files)} audio file(s) in {in_path.name}")
    created = []
    for i, audio in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] {audio.name}")
        out = process_audio_file(
            str(audio), output_dir, overwrite, generate_json, auto_analyze, use_ai, ai_provider, csv_data
        )
        if out:
            created.append(out)
    return created


def download_and_prepare(
    query_or_url: str,
    output_dir: str,
    audio_format: str = "mp3",
    overwrite: bool = False,
    generate_json: bool = False,
    auto_analyze: bool = False,
    use_ai: bool = False,
    ai_provider: str = "auto",
) -> List[str]:
    """Download tracks via spotdl and generate ACE-Step 1.5 lyrics and metadata."""
    audio_files = download_tracks(query_or_url, output_dir, audio_format)
    created = []
    for p in audio_files:
        out = process_audio_file(
            p, output_dir, overwrite, generate_json, auto_analyze, use_ai, ai_provider
        )
        if out:
            created.append(out)
    return created
