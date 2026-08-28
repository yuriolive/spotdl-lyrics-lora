"""Fast AI annotation and lyrics structuring module for ACE-Step 1.5 LoRA dataset preparation."""

import json
import os
from typing import Dict, Any, Optional
import requests

PROMPT_TEMPLATE = """You are a music AI dataset annotator. Analyze this song to produce ACE-Step 1.5 LoRA training metadata.

Track Info:
- Title: {title}
- Artist: {artist}
- Detected BPM: {bpm}
- Detected Key: {keyscale}
- Raw Lyrics:
{lyrics}

Generate a valid JSON object matching this schema:
{{
    "caption": "A concise, descriptive caption (style, instruments, mood, vocals, tempo, key) for audio diffusion training",
    "structured_lyrics": "The full lyrics with clean [Intro], [Verse], [Chorus], [Bridge], [Outro] tags, without timestamps",
    "genre": "Precise primary genre / style",
    "bpm": {bpm_or_null},
    "keyscale": "{keyscale_or_null}",
    "language": "ISO 639-1 code (e.g. pt, es, en, ja)"
}}
Respond ONLY with the JSON object.
"""


def call_gemini_api(
    prompt: str,
    api_key: str,
    model: str = "gemini-2.5-flash",
    timeout: int = 15,
) -> Optional[Dict[str, Any]]:
    """Call Google Gemini API for fast structured JSON response."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
        if resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception:
        pass
    return None


def call_openai_api(
    prompt: str,
    api_key: str,
    model: str = "gpt-4o-mini",
    timeout: int = 15,
) -> Optional[Dict[str, Any]]:
    """Call OpenAI API for structured JSON response."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
        if resp.status_code == 200:
            text = resp.json()["choices"][0]["message"]["content"]
            return json.loads(text)
    except Exception:
        pass
    return None


def call_openrouter_api(
    prompt: str,
    api_key: str,
    model: str = "google/gemini-2.5-flash",
    timeout: int = 15,
) -> Optional[Dict[str, Any]]:
    """Call OpenRouter API for structured JSON response."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/yuriolive/spotdl-lyrics-lora",
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
        if resp.status_code == 200:
            text = resp.json()["choices"][0]["message"]["content"]
            return json.loads(text)
    except Exception:
        pass
    return None


def enrich_metadata_with_ai(
    title: str,
    artist: str,
    lyrics: str,
    bpm: Optional[int] = None,
    keyscale: Optional[str] = None,
    provider: str = "auto",
    model: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Enrich song metadata and structure lyrics using a fast AI model."""
    prompt = PROMPT_TEMPLATE.format(
        title=title,
        artist=artist,
        bpm=bpm or "Unknown",
        keyscale=keyscale or "Unknown",
        bpm_or_null=bpm if bpm else "null",
        keyscale_or_null=keyscale if keyscale else "",
        lyrics=lyrics[:3000] if lyrics else "(Instrumental / No Lyrics)",
    )

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if (provider in ("auto", "gemini")) and gemini_key:
        m = model or "gemini-2.5-flash"
        res = call_gemini_api(prompt, gemini_key, model=m)
        if res:
            return res

    openai_key = os.environ.get("OPENAI_API_KEY")
    if (provider in ("auto", "openai")) and openai_key:
        m = model or "gpt-4o-mini"
        res = call_openai_api(prompt, openai_key, model=m)
        if res:
            return res

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if (provider in ("auto", "openrouter")) and openrouter_key:
        m = model or "google/gemini-2.5-flash"
        res = call_openrouter_api(prompt, openrouter_key, model=m)
        if res:
            return res

    return None
