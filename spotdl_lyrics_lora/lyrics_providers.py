"""Lyrics provider sources for fetching lyrics from multiple online services."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import requests

USER_AGENT = "SpotDL-Lyrics-LoRA/0.1.0 (https://github.com/yuriolive/spotdl-lyrics-lora)"


class LyricsSource(ABC):
    """Abstract base class for online lyrics sources."""

    @abstractmethod
    def fetch_lyrics(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        duration: Optional[int] = None,
    ) -> Optional[str]:
        """Fetch raw lyrics text for a track."""
        pass


class LRCLibSource(LyricsSource):
    """Fetch lyrics from LRCLIB API (supports exact match and search)."""

    def __init__(self, base_url: str = "https://lrclib.net/api", timeout: int = 12):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_lyrics(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        duration: Optional[int] = None,
    ) -> Optional[str]:
        if not title:
            return None
        headers = {"User-Agent": USER_AGENT}

        params: Dict[str, Any] = {"track_name": title}
        if artist:
            params["artist_name"] = artist
        if album:
            params["album_name"] = album
        if duration:
            params["duration"] = duration

        try:
            resp = requests.get(
                f"{self.base_url}/get", params=params, headers=headers, timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                lyrics = data.get("plainLyrics") or data.get("syncedLyrics")
                if lyrics:
                    return lyrics
        except Exception:
            pass

        primary_artist = artist.split("/")[0].split(",")[0].strip() if artist else ""
        search_params: Dict[str, str] = {"track_name": title}
        if primary_artist:
            search_params["artist_name"] = primary_artist

        try:
            resp = requests.get(
                f"{self.base_url}/search", params=search_params, headers=headers, timeout=self.timeout
            )
            if resp.status_code == 200:
                results = resp.json()
                if isinstance(results, list):
                    for item in results:
                        lyrics = item.get("plainLyrics") or item.get("syncedLyrics")
                        if lyrics:
                            return lyrics
        except Exception:
            pass

        return None


class LyricsOVHSource(LyricsSource):
    """Fetch lyrics from Lyrics.ovh API."""

    def __init__(self, base_url: str = "https://api.lyrics.ovh/v1", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_lyrics(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        duration: Optional[int] = None,
    ) -> Optional[str]:
        if not title or not artist:
            return None
        primary_artist = artist.split("/")[0].split(",")[0].strip()
        encoded_artist = primary_artist.replace(" ", "+")
        encoded_title = title.replace(" ", "+")
        url = f"{self.base_url}/{encoded_artist}/{encoded_title}"

        try:
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                lyrics = data.get("lyrics")
                if lyrics:
                    return lyrics.strip()
        except Exception:
            pass
        return None


class SyncedLyricsPackageSource(LyricsSource):
    """Fetch lyrics via syncedlyrics package (NetEase, Musixmatch, Megalobiz, Genius)."""

    def fetch_lyrics(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        duration: Optional[int] = None,
    ) -> Optional[str]:
        try:
            import syncedlyrics
            query = f"{title} {artist}".strip()
            return syncedlyrics.search(query, enhanced=False)
        except Exception:
            return None


def fetch_lyrics_multi_source(
    title: str,
    artist: str = "",
    album: str = "",
    duration: Optional[int] = None,
    sources: Optional[List[LyricsSource]] = None,
) -> Optional[str]:
    """Try fetching lyrics across registered sources in priority order."""
    if sources is None:
        sources = [LRCLibSource(), SyncedLyricsPackageSource(), LyricsOVHSource()]

    for source in sources:
        try:
            lyrics = source.fetch_lyrics(title, artist=artist, album=album, duration=duration)
            if lyrics and lyrics.strip():
                return lyrics.strip()
        except Exception:
            continue
    return None
