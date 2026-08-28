"""Fast AI annotation and lyrics structuring module for ACE-Step 1.5 LoRA dataset preparation.

Supports tiny local models (Ollama, LM Studio, Transformers) and cloud APIs (Gemini, OpenAI).
"""

import json
import os
import re
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


def _extract_json_from_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON object from raw model text output."""
    try:
        return json.loads(raw_text.strip())
    except Exception:
        pass
    # Search for markdown fenced json or bracketed substring
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return None


def call_ollama_api(
    prompt: str,
    model: str = "qwen2.5:0.5b",
    base_url: str = "http://localhost:11434",
    timeout: int = 45,
) -> Optional[Dict[str, Any]]:
    """Call a local Ollama server running a tiny model (e.g. qwen2.5:0.5b, llama3.2:1b)."""
    url = f"{base_url.rstrip('/')}/api/generate"
    body = {"model": model, "prompt": prompt, "format": "json", "stream": False}
    try:
        resp = requests.post(url, json=body, timeout=timeout)
        if resp.status_code == 200:
            raw_response = resp.json().get("response", "")
            return _extract_json_from_response(raw_response)
    except Exception:
        pass
    return None


def call_local_openai_api(
    prompt: str,
    base_url: str = "http://localhost:1234/v1",
    model: str = "local-model",
    timeout: int = 45,
) -> Optional[Dict[str, Any]]:
    """Call a local OpenAI-compatible server (LM Studio, vLLM, LocalAI, Jan)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    try:
        resp = requests.post(url, json=body, timeout=timeout)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            return _extract_json_from_response(content)
    except Exception:
        pass
    return None


def call_transformers_pipeline(
    prompt: str,
    model_id: str = "Qwen/Qwen2.5-0.5B-Instruct",
) -> Optional[Dict[str, Any]]:
    """Run an in-process tiny model directly using HuggingFace Transformers."""
    try:
        from transformers import pipeline
        pipe = pipeline("text-generation", model=model_id, max_new_tokens=512, device_map="auto")
        messages = [{"role": "user", "content": prompt}]
        out = pipe(messages)
        content = out[0]["generated_text"][-1]["content"]
        return _extract_json_from_response(content)
    except Exception:
        return None


def call_gemini_api(prompt: str, api_key: str, model: str = "gemini-2.5-flash", timeout: int = 15) -> Optional[Dict[str, Any]]:
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
            return _extract_json_from_response(text)
    except Exception:
        pass
    return None


def call_openai_api(prompt: str, api_key: str, model: str = "gpt-4o-mini", timeout: int = 15) -> Optional[Dict[str, Any]]:
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
            return _extract_json_from_response(resp.json()["choices"][0]["message"]["content"])
    except Exception:
        pass
    return None


def call_openrouter_api(prompt: str, api_key: str, model: str = "google/gemini-2.5-flash", timeout: int = 15) -> Optional[Dict[str, Any]]:
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
            return _extract_json_from_response(resp.json()["choices"][0]["message"]["content"])
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
    local_url: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Enrich song metadata and structure lyrics using local or cloud AI models."""
    prompt = PROMPT_TEMPLATE.format(
        title=title,
        artist=artist,
        bpm=bpm or "Unknown",
        keyscale=keyscale or "Unknown",
        bpm_or_null=bpm if bpm else "null",
        keyscale_or_null=keyscale if keyscale else "",
        lyrics=lyrics[:3000] if lyrics else "(Instrumental / No Lyrics)",
    )

    # 1. Local Ollama or local OpenAI-compatible server
    if provider in ("local", "ollama") or (provider == "auto" and local_url):
        url = local_url or "http://localhost:11434"
        m = model or "qwen2.5:0.5b"
        if ":11434" in url:
            res = call_ollama_api(prompt, model=m, base_url=url)
        else:
            res = call_local_openai_api(prompt, base_url=url, model=m)
        if res:
            return res

    # 2. In-process Transformers
    if provider == "transformers":
        m = model or "Qwen/Qwen2.5-0.5B-Instruct"
        res = call_transformers_pipeline(prompt, model_id=m)
        if res:
            return res

    # 3. Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if (provider in ("auto", "gemini")) and gemini_key:
        m = model or "gemini-2.5-flash"
        res = call_gemini_api(prompt, gemini_key, model=m)
        if res:
            return res

    # 4. OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if (provider in ("auto", "openai")) and openai_key:
        m = model or "gpt-4o-mini"
        res = call_openai_api(prompt, openai_key, model=m)
        if res:
            return res

    # 5. OpenRouter
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if (provider in ("auto", "openrouter")) and openrouter_key:
        m = model or "google/gemini-2.5-flash"
        res = call_openrouter_api(prompt, openrouter_key, model=m)
        if res:
            return res

    return None
