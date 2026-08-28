"""Dataset validator for ACE-Step 1.5 LoRA training data."""

import os
from pathlib import Path
from typing import Dict, Any, List

from spotdl_lyrics_lora.audio_metadata import AUDIO_EXTENSIONS
from spotdl_lyrics_lora.lyrics_cleaner import TIMESTAMP_PATTERN, METADATA_HEADER_PATTERN


def validate_lyrics_file(lyrics_path: Path) -> Dict[str, Any]:
    """Validate a single .lyrics.txt file for common formatting issues."""
    errors: List[str] = []
    if not lyrics_path.exists():
        return {"valid": False, "lines_count": 0, "errors": ["File does not exist"]}

    try:
        content = lyrics_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"valid": False, "lines_count": 0, "errors": ["Not valid UTF-8 encoding"]}

    if not content.strip():
        return {"valid": False, "lines_count": 0, "errors": ["Lyrics file is empty"]}

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    for i, line in enumerate(lines, 1):
        if TIMESTAMP_PATTERN.search(line):
            errors.append(f"Line {i} contains unstripped timestamp: {line}")
        if METADATA_HEADER_PATTERN.match(line):
            errors.append(f"Line {i} contains unstripped LRC header: {line}")

    return {
        "valid": len(errors) == 0,
        "lines_count": len(lines),
        "errors": errors,
    }


def validate_dataset_folder(dataset_dir: str) -> Dict[str, Any]:
    """Validate an entire folder for ACE-Step 1.5 LoRA training readiness."""
    path = Path(dataset_dir).resolve()
    if not path.is_dir():
        raise NotADirectoryError(f"Directory not found: {dataset_dir}")

    audio_files = sorted(
        f for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    )

    report: Dict[str, Any] = {
        "total_audio": len(audio_files),
        "valid_pairs": 0,
        "missing_lyrics": [],
        "invalid_lyrics": {},
        "with_json_annotation": 0,
    }

    for audio in audio_files:
        lyrics_file = path / f"{audio.stem}.lyrics.txt"
        json_file = path / f"{audio.stem}.json"

        if json_file.exists():
            report["with_json_annotation"] += 1

        if not lyrics_file.exists():
            report["missing_lyrics"].append(audio.name)
            continue

        val = validate_lyrics_file(lyrics_file)
        if val["valid"]:
            report["valid_pairs"] += 1
        else:
            report["invalid_lyrics"][lyrics_file.name] = val["errors"]

    return report


def print_validation_report(report: Dict[str, Any]) -> None:
    """Print human-readable validation summary."""
    print("=" * 60)
    print("ACE-Step 1.5 LoRA Dataset Validation Report")
    print("=" * 60)
    print(f"Total Audio Files:        {report['total_audio']}")
    print(f"Valid Training Pairs:     {report['valid_pairs']}")
    print(f"JSON Annotations:         {report['with_json_annotation']}")
    print(f"Missing Lyrics:           {len(report['missing_lyrics'])}")
    print(f"Invalid Lyrics Files:     {len(report['invalid_lyrics'])}")
    print("-" * 60)

    if report["missing_lyrics"]:
        print("Missing lyrics for:")
        for name in report["missing_lyrics"]:
            print(f"  - {name}")

    if report["invalid_lyrics"]:
        print("\nFormatting issues:")
        for name, errs in report["invalid_lyrics"].items():
            print(f"  - {name}:")
            for e in errs:
                print(f"      * {e}")

    if report["valid_pairs"] == report["total_audio"] and report["total_audio"] > 0:
        print("\n[SUCCESS] Dataset is 100% ready for LoRA fine-tuning!")
    print("=" * 60)
