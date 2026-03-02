"""SQLite persistence for favorites, liked songs, and station cache."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from core.config import DB_PATH


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS favorites (
                station_uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                tags TEXT DEFAULT '',
                country TEXT DEFAULT '',
                bitrate INTEGER DEFAULT 0,
                codec TEXT DEFAULT '',
                homepage TEXT DEFAULT '',
                favicon TEXT DEFAULT '',
                source TEXT DEFAULT 'radio-browser',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                play_count INTEGER DEFAULT 0,
                last_played TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS liked_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT DEFAULT '',
                station_name TEXT DEFAULT '',
                station_uuid TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                downloaded INTEGER DEFAULT 0,
                download_path TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_uuid TEXT NOT NULL,
                station_name TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS station_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    # ── Favorites ──────────────────────────────────────────────

    def add_favorite(self, station: dict):
        self.conn.execute("""
            INSERT OR REPLACE INTO favorites
            (station_uuid, name, url, tags, country, bitrate, codec, homepage, favicon, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            station.get("stationuuid", station.get("id", "")),
            station.get("name", ""),
            station.get("url_resolved", station.get("url", "")),
            station.get("tags", ""),
            station.get("country", ""),
            station.get("bitrate", 0),
            station.get("codec", ""),
            station.get("homepage", ""),
            station.get("favicon", ""),
            station.get("source", "radio-browser"),
        ))
        self.conn.commit()

    def remove_favorite(self, station_uuid: str):
        self.conn.execute("DELETE FROM favorites WHERE station_uuid = ?", (station_uuid,))
        self.conn.commit()

    def get_favorites(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM favorites ORDER BY added_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def is_favorite(self, station_uuid: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM favorites WHERE station_uuid = ?", (station_uuid,)
        ).fetchone()
        return row is not None

    def increment_play_count(self, station_uuid: str):
        self.conn.execute("""
            UPDATE favorites SET play_count = play_count + 1, last_played = ?
            WHERE station_uuid = ?
        """, (datetime.now().isoformat(), station_uuid))
        self.conn.commit()

    # ── Liked Songs ────────────────────────────────────────────

    def add_liked_song(self, title: str, artist: str = "", station_name: str = "",
                       station_uuid: str = "", tags: str = "") -> int:
        cursor = self.conn.execute("""
            INSERT INTO liked_songs (title, artist, station_name, station_uuid, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (title, artist, station_name, station_uuid, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_liked_songs(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM liked_songs ORDER BY detected_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def remove_liked_song(self, song_id: int):
        self.conn.execute("DELETE FROM liked_songs WHERE id = ?", (song_id,))
        self.conn.commit()

    def mark_downloaded(self, song_id: int, path: str):
        self.conn.execute(
            "UPDATE liked_songs SET downloaded = 1, download_path = ? WHERE id = ?",
            (path, song_id)
        )
        self.conn.commit()

    # ── Play History ───────────────────────────────────────────

    def log_play(self, station_uuid: str, station_name: str):
        self.conn.execute("""
            INSERT INTO play_history (station_uuid, station_name)
            VALUES (?, ?)
        """, (station_uuid, station_name))
        self.conn.commit()

    def get_play_history(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM play_history ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]

    # ── Station Cache ──────────────────────────────────────────

    def cache_stations(self, key: str, stations: list[dict], max_age_hours: int = 6):
        self.conn.execute("""
            INSERT OR REPLACE INTO station_cache (cache_key, data, cached_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(stations), datetime.now().isoformat()))
        self.conn.commit()

    def get_cached_stations(self, key: str, max_age_hours: int = 6) -> list[dict] | None:
        row = self.conn.execute(
            "SELECT data, cached_at FROM station_cache WHERE cache_key = ?", (key,)
        ).fetchone()
        if not row:
            return None
        cached_at = datetime.fromisoformat(row["cached_at"])
        if (datetime.now() - cached_at).total_seconds() > max_age_hours * 3600:
            return None
        return json.loads(row["data"])

    def close(self):
        self.conn.close()
