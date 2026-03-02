"""VLC-based internet radio player with ICY metadata extraction.

Uses python-vlc for reliable stream playback and metadata parsing.
ICY metadata (artist/title) is extracted from the stream when available.
"""
import vlc
import time
from dataclasses import dataclass
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.config import DEFAULT_VOLUME, METADATA_POLL_INTERVAL_MS


@dataclass
class NowPlaying:
    """Current track metadata."""
    title: str = ""
    artist: str = ""
    raw_meta: str = ""
    station_name: str = ""
    timestamp: str = ""

    @property
    def display_text(self) -> str:
        if self.artist and self.title:
            return f"{self.artist} — {self.title}"
        if self.raw_meta:
            return self.raw_meta
        return self.station_name or "Unknown"

    @property
    def is_identified(self) -> bool:
        return bool(self.title and self.title != self.station_name)


class RadioPlayer(QObject):
    """Internet radio stream player using VLC.

    Signals:
        metadata_changed(NowPlaying): Emitted when stream metadata updates
        state_changed(str): Emitted on state transitions (playing, paused, stopped, error)
        error_occurred(str): Emitted on playback errors
    """
    metadata_changed = pyqtSignal(object)
    state_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # VLC instance with ICY metadata support
        self.instance = vlc.Instance([
            "--no-video",
            "--no-xlib",
            "--aout=pulse",
            "--network-caching=3000",
            "--live-caching=3000",
            "--http-reconnect",
            "--no-metadata-network-access",
        ])
        self.player = self.instance.media_player_new()
        self._current_media = None
        self._current_station = None
        self._now_playing = NowPlaying()
        self._last_meta = ""

        # Volume (0-100)
        self._volume = DEFAULT_VOLUME
        self.player.audio_set_volume(self._volume)

        # Metadata polling timer
        self._meta_timer = QTimer()
        self._meta_timer.timeout.connect(self._poll_metadata)

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, val: int):
        self._volume = max(0, min(100, val))
        self.player.audio_set_volume(self._volume)

    @property
    def is_playing(self) -> bool:
        return self.player.is_playing()

    @property
    def now_playing(self) -> NowPlaying:
        return self._now_playing

    @property
    def current_station(self):
        return self._current_station

    def play_url(self, url: str, station=None):
        """Start playing a stream URL."""
        self.stop()
        self._current_station = station

        try:
            media = self.instance.media_new(url)
            media.add_option(":network-caching=3000")
            self._current_media = media
            self.player.set_media(media)
            if self.player.play() == -1:
                self.error_occurred.emit("VLC failed to start — check VLC installation")
                self.state_changed.emit("error")
                return

            # Give VLC a moment to connect
            self._now_playing = NowPlaying(
                station_name=station.name if station else "Unknown",
                timestamp=time.strftime("%H:%M:%S"),
            )
            self.metadata_changed.emit(self._now_playing)
            self.state_changed.emit("playing")

            # Start polling for ICY metadata
            self._meta_timer.start(METADATA_POLL_INTERVAL_MS)

        except Exception as e:
            self.error_occurred.emit(f"Playback error: {e}")
            self.state_changed.emit("error")

    def toggle_pause(self):
        """Toggle play/pause."""
        if self.player.is_playing():
            self.player.pause()
            self.state_changed.emit("paused")
        elif self._current_media:
            self.player.play()
            self.state_changed.emit("playing")

    def stop(self):
        """Stop playback and clean up."""
        self._meta_timer.stop()
        self.player.stop()
        self._current_media = None
        self._current_station = None
        self._now_playing = NowPlaying()
        self._last_meta = ""
        self.state_changed.emit("stopped")

    def _poll_metadata(self):
        """Poll VLC for stream metadata updates (ICY tags)."""
        if not self._current_media:
            return

        state = self.player.get_state()
        if state == vlc.State.Error:
            self._meta_timer.stop()
            self.error_occurred.emit("Stream error — bad URL or unsupported format")
            self.state_changed.emit("error")
            return
        if state == vlc.State.Ended:
            self._meta_timer.stop()
            self.state_changed.emit("stopped")
            return
        if not self.player.is_playing():
            return

        media = self.player.get_media()
        if not media:
            return

        # VLC exposes ICY metadata through media meta fields
        title = media.get_meta(vlc.Meta.Title) or ""
        artist = media.get_meta(vlc.Meta.Artist) or ""
        now_playing_meta = media.get_meta(vlc.Meta.NowPlaying) or ""
        description = media.get_meta(vlc.Meta.Description) or ""

        # Build the best available metadata
        raw = now_playing_meta or title or description
        meta_key = f"{artist}|{title}|{raw}"

        if meta_key != self._last_meta and raw:
            self._last_meta = meta_key

            # Parse "Artist - Title" format common in ICY streams
            parsed_artist = artist
            parsed_title = title

            if not parsed_artist and " - " in raw:
                parts = raw.split(" - ", 1)
                parsed_artist = parts[0].strip()
                parsed_title = parts[1].strip()
            elif not parsed_title:
                parsed_title = raw

            self._now_playing = NowPlaying(
                title=parsed_title,
                artist=parsed_artist,
                raw_meta=raw,
                station_name=self._current_station.name if self._current_station else "",
                timestamp=time.strftime("%H:%M:%S"),
            )
            self.metadata_changed.emit(self._now_playing)

    def cleanup(self):
        """Release VLC resources."""
        self._meta_timer.stop()
        self.player.stop()
        self.player.release()
        self.instance.release()
