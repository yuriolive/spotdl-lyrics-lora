"""CSV metadata importer for Key-BPM-Finder and DJ software exports."""

import csv
from pathlib import Path
from typing import Dict, Any, Optional


def parse_bpm_value(raw: str) -> Optional[int]:
    """Parse numeric BPM value from string."""
    try:
        val = float(raw.strip())
        return int(round(val)) if val > 0 else None
    except Exception:
        return None


def load_key_bpm_csv(csv_path: str) -> Dict[str, Dict[str, Any]]:
    """Parse a Key-BPM-Finder or metadata CSV file."""
    p = Path(csv_path)
    if not p.is_file():
        return {}

    mapping: Dict[str, Dict[str, Any]] = {}
    try:
        with open(p, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                norm = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                filename = norm.get("file") or norm.get("filename") or norm.get("title", "")
                if not filename:
                    continue

                bpm_str = norm.get("bpm") or norm.get("tempo", "")
                key_str = norm.get("key") or norm.get("keyscale") or norm.get("initialkey", "")
                camelot_str = norm.get("camelot", "")
                caption_str = norm.get("caption") or norm.get("description", "")

                meta = {
                    "bpm": parse_bpm_value(bpm_str),
                    "keyscale": key_str if key_str else None,
                    "camelot": camelot_str if camelot_str else None,
                    "caption": caption_str if caption_str else None,
                }
                mapping[filename] = meta
                mapping[Path(filename).stem] = meta
    except Exception:
        pass
    return mapping


def find_and_load_csv(folder_dir: str) -> Dict[str, Dict[str, Any]]:
    """Scan a dataset folder for any Key-BPM-Finder or metadata CSV file."""
    path = Path(folder_dir)
    if not path.is_dir():
        return {}

    for f in path.glob("*.csv"):
        data = load_key_bpm_csv(str(f))
        if data:
            return data
    return {}
