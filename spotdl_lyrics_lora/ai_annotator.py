"""Fast AI annotation and lyrics structuring module for ACE-Step 1.5 LoRA dataset preparation.

Supports tiny local models (Ollama, LM Studio, Transformers) and cloud APIs (Gemini, OpenAI).
"""

import json
import os
import re
from typing import Dict, Any, Optional
import requests

PROMPT_TEMPLATE = """You are an audio AI dataset annotator. Analyze this track and output metadata for ACE-Step 1.5 LoRA fine-tuning.

Track:
- Title: {title}
- Artist: {artist}
- BPM: {bpm}
- Key: {keyscale}
- Lyrics:
{lyrics}

Generate a valid JSON object matching this exact schema:
{{
    "caption": "Rich, descriptive studio caption (genre, subgenre, rhythm, instruments, vocals, vibe, tempo, key) for diffusion model training",
    "structured_lyrics": "The full lyrics with [Intro], [Verse 1], [Chorus], [Bridge], [Outro] section tags on separate lines without timestamps",
    "genre": "Precise genre / subgenre",
    "language": "Two-letter ISO 639-1 code (pt, es, en, ja, fr, de, it, etc.)"
}}
Respond ONLY with the raw JSON object.
"""

_TRANSFORMERS_CACHE: Dict[str, Any] = {}

LANG_NAME_TO_CODE = {
    "portuguese": "pt", "português": "pt", "pt": "pt",
    "spanish": "es", "español": "es", "es": "es",
    "english": "en", "inglês": "en", "en": "en",
    "japanese": "ja", "ja": "ja",
    "korean": "ko", "ko": "ko",
    "chinese": "zh", "zh": "zh",
    "french": "fr", "fr": "fr",
    "german": "de", "de": "de",
    "italian": "it", "it": "it",
}


def _normalize_structured_lyrics(val: Any) -> str:
    """Normalize structured lyrics output from list/dict/string into clean text."""
    if isinstance(val, list):
        out = []
        for item in val:
            if isinstance(item, dict):
                for k, v in item.items():
                    tag = k if k.startswith("[") else f"[{k}]"
                    out.append(tag)
                    out.append(str(v).strip())
                    out.append("")
            else:
                out.append(str(item).strip())
        return "\n".join(out).strip()
    if isinstance(val, dict):
        out = []
        for k, v in val.items():
            tag = k if k.startswith("[") else f"[{k}]"
            out.append(tag)
            out.append(str(v).strip())
            out.append("")
        return "\n".join(out).strip()
    if isinstance(val, str):
        cleaned = re.sub(r"\s*(\[[a-zA-Z0-9\s\-]+\])\s*", r"\n\n\1\n", val)
        return "\n".join(l.strip() for l in cleaned.splitlines() if l.strip())
    return ""


def _extract_json_from_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON object from raw model text output."""
    data = None
    try:
        data = json.loads(raw_text.strip())
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                pass

    if isinstance(data, dict):
        if "structured_lyrics" in data:
            data["structured_lyrics"] = _normalize_structured_lyrics(data["structured_lyrics"])
        if "language" in data and isinstance(data["language"], str):
            lang_lower = data["language"].strip().lower()
            data["language"] = LANG_NAME_TO_CODE.get(lang_lower, lang_lower[:2])
        return data
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
            return _extract_json_from_response(resp.json().get("response", ""))
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
            return _extract_json_from_response(resp.json()["choices"][0]["message"]["content"])
    except Exception:
        pass
    return None


def call_transformers_pipeline(
    prompt: str,
    model_id: str = "Qwen/Qwen2.5-0.5B-Instruct",
) -> Optional[Dict[str, Any]]:
    """Run an in-process tiny model cached in CUDA GPU memory."""
    try:
        import torch
        from transformers import pipeline
        global _TRANSFORMERS_CACHE
        if model_id not in _TRANSFORMERS_CACHE:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            device_map = "auto" if torch.cuda.is_available() else None
            _TRANSFORMERS_CACHE[model_id] = pipeline(
                "text-generation",
                model=model_id,
                torch_dtype=dtype,
                device_map=device_map,
            )
        pipe = _TRANSFORMERS_CACHE[model_id]
        messages = [
            {"role": "system", "content": "You are a music metadata assistant. Respond ONLY in valid JSON."},
            {"role": "user", "content": prompt}
        ]
        out = pipe(messages, max_new_tokens=500, temperature=0.2)
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
        lyrics=lyrics[:2500] if lyrics else "(Instrumental / No Lyrics)",
    )

    if provider == "transformers":
        m = model or "Qwen/Qwen2.5-0.5B-Instruct"
        res = call_transformers_pipeline(prompt, model_id=m)
        if res:
            return res

    if provider in ("local", "ollama") or (provider == "auto" and local_url):
        url = local_url or "http://localhost:11434"
        m = model or "qwen2.5:0.5b"
        if ":11434" in url:
            res = call_ollama_api(prompt, model=m, base_url=url)
        else:
            res = call_local_openai_api(prompt, base_url=url, model=m)
        if res:
            return res

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

    return None
