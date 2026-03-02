"""Multi-source internet radio station aggregator.

Pulls stations from multiple open directories and normalizes them
into a common Station format. Sources are modular — add new ones
by subclassing StationSource.
"""
import asyncio
import random
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

import aiohttp

from core.config import RADIO_BROWSER_MIRRORS, SOMAFM_API


@dataclass
class Station:
    """Normalized station object used throughout the app."""
    id: str = ""
    name: str = ""
    url: str = ""
    tags: str = ""
    country: str = ""
    bitrate: int = 0
    codec: str = ""
    homepage: str = ""
    favicon: str = ""
    source: str = ""
    votes: int = 0
    click_count: int = 0
    description: str = ""

    # Aliases for compatibility with radio-browser API field names
    @property
    def stationuuid(self):
        return self.id

    @property
    def url_resolved(self):
        return self.url

    def to_dict(self) -> dict:
        d = asdict(self)
        d["stationuuid"] = self.id
        d["url_resolved"] = self.url
        return d


class StationSource(ABC):
    """Base class for station directory sources."""
    name: str = "Unknown"

    @abstractmethod
    async def search(self, query: str = "", tags: str = "", limit: int = 30) -> list[Station]:
        ...

    @abstractmethod
    async def top_stations(self, limit: int = 30) -> list[Station]:
        ...


class RadioBrowserSource(StationSource):
    """Community Radio Browser — radio-browser.info (30,000+ stations)."""
    name = "Radio Browser"

    def __init__(self):
        self.mirrors = list(RADIO_BROWSER_MIRRORS)

    def _get_base_url(self) -> str:
        return random.choice(self.mirrors)

    async def _fetch(self, session: aiohttp.ClientSession, path: str, params: dict = None) -> list[dict]:
        url = f"{self._get_base_url()}/json{path}"
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return []

    def _normalize(self, raw: list[dict]) -> list[Station]:
        stations = []
        for r in raw:
            if not r.get("url_resolved") or not r.get("name"):
                continue
            stations.append(Station(
                id=r.get("stationuuid", ""),
                name=r.get("name", "").strip(),
                url=r.get("url_resolved", ""),
                tags=r.get("tags", ""),
                country=r.get("country", ""),
                bitrate=r.get("bitrate", 0),
                codec=r.get("codec", ""),
                homepage=r.get("homepage", ""),
                favicon=r.get("favicon", ""),
                source="radio-browser",
                votes=r.get("votes", 0),
                click_count=r.get("clickcount", 0),
            ))
        return stations

    async def search(self, query: str = "", tags: str = "", limit: int = 30) -> list[Station]:
        async with aiohttp.ClientSession() as session:
            params = {
                "limit": str(limit),
                "order": "clickcount",
                "reverse": "true",
                "hidebroken": "true",
            }
            if tags:
                tag_list = [t.strip() for t in tags.split(",")]
                tag = random.choice(tag_list)
                raw = await self._fetch(session, f"/stations/bytag/{tag}", params)
            elif query:
                raw = await self._fetch(session, f"/stations/byname/{query}", params)
            else:
                raw = await self._fetch(session, f"/stations/topclick/{limit}")
            return self._normalize(raw)

    async def top_stations(self, limit: int = 30) -> list[Station]:
        async with aiohttp.ClientSession() as session:
            raw = await self._fetch(session, f"/stations/topclick/{limit}")
            return self._normalize(raw)


class SomaFMSource(StationSource):
    """SomaFM — listener-supported, commercial-free internet radio."""
    name = "SomaFM"

    async def _fetch_channels(self, session: aiohttp.ClientSession) -> list[dict]:
        try:
            async with session.get(SOMAFM_API, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("channels", [])
        except Exception:
            pass
        return []

    def _normalize(self, channels: list[dict]) -> list[Station]:
        stations = []
        for ch in channels:
            # SomaFM provides multiple stream qualities — pick highest quality MP3
            playlists = ch.get("playlists", [])
            url = ""
            bitrate = 0
            for pl in playlists:
                if pl.get("format") == "mp3" and pl.get("quality", "") == "highest":
                    url = pl.get("url", "")
                    break
            if not url and playlists:
                url = playlists[0].get("url", "")

            # SomaFM playlist URLs are .pls — extract direct stream
            # For now store the pls URL; the player can handle it
            if not url:
                continue

            stations.append(Station(
                id=f"somafm-{ch.get('id', '')}",
                name=f"SomaFM: {ch.get('title', '')}",
                url=url,
                tags=ch.get("genre", ""),
                country="USA",
                bitrate=bitrate,
                codec="mp3",
                homepage=f"https://somafm.com/{ch.get('id', '')}/",
                favicon=ch.get("xlimage", ch.get("image", "")),
                source="somafm",
                description=ch.get("description", ""),
                click_count=ch.get("listeners", 0),
            ))
        return stations

    async def search(self, query: str = "", tags: str = "", limit: int = 30) -> list[Station]:
        async with aiohttp.ClientSession() as session:
            channels = await self._fetch_channels(session)
            stations = self._normalize(channels)

            if query:
                q = query.lower()
                stations = [s for s in stations if q in s.name.lower() or q in s.tags.lower() or q in s.description.lower()]
            if tags:
                tag_set = {t.strip().lower() for t in tags.split(",")}
                stations = [s for s in stations if any(t in s.tags.lower() for t in tag_set)]

            return stations[:limit]

    async def top_stations(self, limit: int = 30) -> list[Station]:
        async with aiohttp.ClientSession() as session:
            channels = await self._fetch_channels(session)
            stations = self._normalize(channels)
            stations.sort(key=lambda s: s.click_count, reverse=True)
            return stations[:limit]


class StationAggregator:
    """Aggregates results from multiple station sources."""

    def __init__(self):
        self.sources: list[StationSource] = [
            RadioBrowserSource(),
            SomaFMSource(),
        ]

    async def search(self, query: str = "", tags: str = "", limit: int = 30) -> list[Station]:
        tasks = [src.search(query=query, tags=tags, limit=limit) for src in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_stations = []
        seen_urls = set()
        for result in results:
            if isinstance(result, Exception):
                continue
            for station in result:
                if station.url not in seen_urls:
                    seen_urls.add(station.url)
                    all_stations.append(station)

        # Sort by click count / popularity
        all_stations.sort(key=lambda s: s.click_count, reverse=True)
        return all_stations[:limit]

    async def top_stations(self, limit: int = 30) -> list[Station]:
        tasks = [src.top_stations(limit=limit) for src in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_stations = []
        seen_urls = set()
        for result in results:
            if isinstance(result, Exception):
                continue
            for station in result:
                if station.url not in seen_urls:
                    seen_urls.add(station.url)
                    all_stations.append(station)

        all_stations.sort(key=lambda s: s.click_count, reverse=True)
        return all_stations[:limit]
