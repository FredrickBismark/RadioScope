"""Main application window for RadioScope."""
import asyncio
from functools import partial

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QStackedWidget, QFrame, QScrollArea,
    QApplication, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QShortcut, QKeySequence

from core.player import RadioPlayer
from core.database import Database
from core.stations import StationAggregator, Station
from core.config import MOOD_PRESETS, DEFAULT_VOLUME
from ui.theme import STYLESHEET
from ui.station_list import StationList
from ui.player_bar import PlayerBar
from ui.ai_panel import AIPanel


class StationFetcher(QThread):
    """Background thread for fetching stations."""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, aggregator, query="", tags="", top=False):
        super().__init__()
        self.aggregator = aggregator
        self.query = query
        self.tags = tags
        self.top = top

    def run(self):
        loop = asyncio.new_event_loop()
        try:
            if self.top:
                stations = loop.run_until_complete(self.aggregator.top_stations(limit=40))
            else:
                stations = loop.run_until_complete(
                    self.aggregator.search(query=self.query, tags=self.tags, limit=40)
                )
            self.finished.emit(stations)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RadioScope — Human-curated · AI-navigated")
        self.setMinimumSize(900, 650)
        self.resize(1000, 720)

        # Core components
        self.db = Database()
        self.player = RadioPlayer()
        self.aggregator = StationAggregator()
        self._current_stations = []
        self._current_station = None
        self._favorites_set = set()
        self._ai_accumulated_stations = []
        self._fetcher = None

        # Load favorites from DB
        for fav in self.db.get_favorites():
            self._favorites_set.add(fav["station_uuid"])

        # Build UI
        self._build_ui()
        self._connect_signals()
        self._setup_shortcuts()

        # Initial load
        self._fetch_top_stations()

    def _build_ui(self):
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(
            "QFrame { background: rgba(10,10,15,0.9); border-bottom: 1px solid rgba(255,255,255,0.05); }"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(10)

        self.logo_icon = QLabel("◉")
        self.logo_icon.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #ff8c32;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff8c32, stop:1 #cc4a10);
                border-radius: 16px;
                min-width: 32px; max-width: 32px;
                min-height: 32px; max-height: 32px;
                padding-left: 4px;
            }
        """)
        logo_layout.addWidget(self.logo_icon)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title_label = QLabel("RadioScope")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #ff9f55;"
        )
        title_layout.addWidget(title_label)
        subtitle = QLabel("HUMAN-CURATED · AI-NAVIGATED")
        subtitle.setObjectName("sectionHeader")
        subtitle.setStyleSheet("font-size: 9px; color: rgba(255,255,255,0.25); letter-spacing: 2px;")
        title_layout.addWidget(subtitle)
        logo_layout.addLayout(title_layout)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("discover", "◎ Discover"),
            ("ai", "◆ AI Tuner"),
            ("favorites", "★ Favorites"),
            ("songs", "♪ Songs"),
        ]
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setProperty("active", key == "discover")
            btn.clicked.connect(partial(self._switch_view, key))
            header_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        root_layout.addWidget(header)

        # ── Content area ────────────────────────────────────
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()

        # ── Discover page ──
        discover_page = QWidget()
        discover_layout = QVBoxLayout(discover_page)
        discover_layout.setContentsMargins(0, 0, 0, 0)
        discover_layout.setSpacing(16)

        # Search bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search stations by name...")
        self.search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_input, stretch=1)

        search_btn = QPushButton("Search")
        search_btn.setObjectName("accentButton")
        search_btn.clicked.connect(self._on_search)
        search_row.addWidget(search_btn)
        discover_layout.addLayout(search_row)

        # Mood chips
        mood_header = QLabel("QUICK TUNE")
        mood_header.setObjectName("sectionHeader")
        discover_layout.addWidget(mood_header)

        mood_flow = QHBoxLayout()
        mood_flow.setSpacing(6)
        self.mood_buttons = []
        for mood in MOOD_PRESETS:
            btn = QPushButton(f"{mood['icon']} {mood['label']}")
            btn.setObjectName("moodChip")
            btn.clicked.connect(partial(self._on_mood, mood))
            mood_flow.addWidget(btn)
            self.mood_buttons.append((btn, mood))
        mood_flow.addStretch()

        # Wrap mood chips in scroll
        mood_scroll_widget = QWidget()
        mood_scroll_widget.setLayout(mood_flow)
        mood_scroll = QScrollArea()
        mood_scroll.setWidget(mood_scroll_widget)
        mood_scroll.setWidgetResizable(True)
        mood_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        mood_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        mood_scroll.setFixedHeight(42)
        mood_scroll.setFrameShape(QFrame.Shape.NoFrame)
        discover_layout.addWidget(mood_scroll)

        # Station list
        self.discover_list = StationList()
        discover_layout.addWidget(self.discover_list, stretch=1)

        self.stack.addWidget(discover_page)

        # ── AI Tuner page ──
        ai_page = QWidget()
        ai_layout = QVBoxLayout(ai_page)
        ai_layout.setContentsMargins(0, 0, 0, 0)
        ai_layout.setSpacing(16)

        self.ai_panel = AIPanel()
        ai_layout.addWidget(self.ai_panel)

        self.ai_station_list = StationList()
        ai_layout.addWidget(self.ai_station_list, stretch=1)

        self.stack.addWidget(ai_page)

        # ── Favorites page ──
        favorites_page = QWidget()
        fav_layout = QVBoxLayout(favorites_page)
        fav_layout.setContentsMargins(0, 0, 0, 0)
        fav_layout.setSpacing(16)

        self.fav_header = QLabel("SAVED STATIONS")
        self.fav_header.setObjectName("sectionHeader")
        fav_layout.addWidget(self.fav_header)

        self.favorites_list = StationList()
        fav_layout.addWidget(self.favorites_list, stretch=1)

        self.stack.addWidget(favorites_page)

        # ── Liked songs page ──
        songs_page = QWidget()
        songs_layout = QVBoxLayout(songs_page)
        songs_layout.setContentsMargins(0, 0, 0, 0)
        songs_layout.setSpacing(16)

        self.songs_header = QLabel("LIKED SONGS")
        self.songs_header.setObjectName("sectionHeader")
        songs_layout.addWidget(self.songs_header)

        self.songs_scroll = QScrollArea()
        self.songs_scroll.setWidgetResizable(True)
        self.songs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.songs_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.songs_container = QWidget()
        self.songs_container_layout = QVBoxLayout(self.songs_container)
        self.songs_container_layout.setContentsMargins(0, 0, 8, 0)
        self.songs_container_layout.setSpacing(6)
        self.songs_container_layout.addStretch()
        self.songs_scroll.setWidget(self.songs_container)

        songs_layout.addWidget(self.songs_scroll, stretch=1)
        self.stack.addWidget(songs_page)

        content_layout.addWidget(self.stack, stretch=1)
        root_layout.addWidget(content_area, stretch=1)

        # ── Player bar ──────────────────────────────────────
        self.player_bar = PlayerBar()
        root_layout.addWidget(self.player_bar)

        # ── Status bar (error messages) ─────────────────────
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                background: rgba(255,60,60,0.1); border-top: 1px solid rgba(255,60,60,0.2);
                color: #ff8888; font-size: 12px; padding: 8px 20px;
                font-family: 'JetBrains Mono', monospace;
            }
        """)
        self.status_label.setVisible(False)
        root_layout.addWidget(self.status_label)

    def _connect_signals(self):
        # Player signals
        self.player.metadata_changed.connect(self._on_metadata)
        self.player.state_changed.connect(self._on_player_state)
        self.player.error_occurred.connect(self._show_error)

        # Station lists
        for lst in [self.discover_list, self.favorites_list, self.ai_station_list]:
            lst.play_station.connect(self._play_station)
            lst.toggle_favorite.connect(self._toggle_favorite)

        # Player bar
        self.player_bar.play_pause_clicked.connect(self._toggle_play)
        self.player_bar.stop_clicked.connect(self._stop)
        self.player_bar.like_clicked.connect(self._like_current_song)
        self.player_bar.volume_changed.connect(self._set_volume)

        # AI panel
        self.ai_panel.search_requested.connect(self._on_ai_search)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self._toggle_play)
        QShortcut(QKeySequence("S"), self, self._stop)
        QShortcut(QKeySequence("F"), self, self._toggle_favorite_current)
        QShortcut(QKeySequence("L"), self, self._like_current_song)
        QShortcut(QKeySequence("Ctrl+F"), self, self.search_input.setFocus)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("+"), self, lambda: self._adjust_volume(5))
        QShortcut(QKeySequence("-"), self, lambda: self._adjust_volume(-5))

    # ── Navigation ──────────────────────────────────────────

    def _switch_view(self, key):
        pages = {"discover": 0, "ai": 1, "favorites": 2, "songs": 3}
        self.stack.setCurrentIndex(pages.get(key, 0))

        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if key == "favorites":
            self._refresh_favorites()
        elif key == "songs":
            self._refresh_liked_songs()

    # ── Station fetching ────────────────────────────────────

    def _fetch_top_stations(self):
        self._fetch(top=True)

    def _on_search(self):
        query = self.search_input.text().strip()
        if query:
            self._fetch(query=query)

    def _on_mood(self, mood):
        # Update mood chip visual state
        for btn, m in self.mood_buttons:
            btn.setProperty("active", m["label"] == mood["label"])
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._fetch(tags=mood["tags"])

    def _fetch(self, query="", tags="", top=False):
        self._fetcher = StationFetcher(self.aggregator, query=query, tags=tags, top=top)
        self._fetcher.finished.connect(self._on_stations_loaded)
        self._fetcher.error.connect(self._show_error)
        self._fetcher.start()

    @pyqtSlot(list)
    def _on_stations_loaded(self, stations):
        self._current_stations = stations
        current_id = ""
        if self._current_station:
            current_id = self._current_station.id if hasattr(self._current_station, 'id') else ""
        self.discover_list.set_stations(
            stations, current_id=current_id, favorites=self._favorites_set
        )

    def _on_ai_search(self, term, search_type):
        """Handle search request from AI panel — accumulate results."""
        fetcher = StationFetcher(self.aggregator, query=term if search_type != "tag" else "", tags=term if search_type == "tag" else "")
        fetcher.finished.connect(self._on_ai_stations_loaded)
        fetcher.error.connect(self._show_error)
        fetcher.start()
        # Keep reference to avoid GC
        if not hasattr(self, '_ai_fetchers'):
            self._ai_fetchers = []
        self._ai_fetchers.append(fetcher)

    @pyqtSlot(list)
    def _on_ai_stations_loaded(self, stations):
        # Accumulate and deduplicate
        seen = {s.id if hasattr(s, 'id') else s.get('id', '') for s in self._ai_accumulated_stations}
        for s in stations:
            sid = s.id if hasattr(s, 'id') else s.get('id', '')
            if sid not in seen:
                seen.add(sid)
                self._ai_accumulated_stations.append(s)

        current_id = ""
        if self._current_station:
            current_id = self._current_station.id if hasattr(self._current_station, 'id') else ""
        self.ai_station_list.set_stations(
            self._ai_accumulated_stations[:25],
            current_id=current_id,
            favorites=self._favorites_set,
        )

    # ── Playback ────────────────────────────────────────────

    def _play_station(self, station):
        # Normalize to Station object if needed
        if isinstance(station, dict):
            url = station.get("url_resolved", station.get("url", ""))
            s = Station(
                id=station.get("stationuuid", station.get("station_uuid", station.get("id", ""))),
                name=station.get("name", ""),
                url=url,
                tags=station.get("tags", ""),
                country=station.get("country", ""),
                bitrate=station.get("bitrate", 0),
                source=station.get("source", ""),
            )
        else:
            s = station

        self._current_station = s
        self.player_bar.set_playing(s.name)
        self.player.play_url(s.url, station=s)
        self.db.log_play(s.id, s.name)

        # Update station lists
        self.discover_list.update_playing(s.id)
        self.ai_station_list.update_playing(s.id)
        self.favorites_list.update_playing(s.id)

    def _toggle_play(self):
        if self.player.is_playing:
            self.player.toggle_pause()
            self.player_bar.set_paused()
        elif self._current_station:
            self.player.toggle_pause()
            self.player_bar.set_resumed()

    def _stop(self):
        self.player.stop()
        self._current_station = None
        self.player_bar.set_stopped()
        self.discover_list.update_playing("")
        self.ai_station_list.update_playing("")
        self.favorites_list.update_playing("")

    def _set_volume(self, value):
        self.player.volume = value

    def _adjust_volume(self, delta):
        new_vol = max(0, min(100, self.player.volume + delta))
        self.player.volume = new_vol
        self.player_bar.volume_slider.setValue(new_vol)

    # ── Metadata ────────────────────────────────────────────

    @pyqtSlot(object)
    def _on_metadata(self, now_playing):
        self.player_bar.update_metadata(now_playing)

    @pyqtSlot(str)
    def _on_player_state(self, state):
        if state == "error":
            self.player_bar.set_stopped()

    # ── Favorites ───────────────────────────────────────────

    def _toggle_favorite(self, station):
        if isinstance(station, dict):
            sid = station.get("stationuuid", station.get("station_uuid", station.get("id", "")))
        else:
            sid = station.id if hasattr(station, 'id') else ""

        if sid in self._favorites_set:
            self._favorites_set.discard(sid)
            self.db.remove_favorite(sid)
        else:
            self._favorites_set.add(sid)
            d = station.to_dict() if hasattr(station, 'to_dict') else station
            self.db.add_favorite(d)

        # Refresh visible lists
        current_id = self._current_station.id if self._current_station else ""
        self.discover_list.set_stations(
            self._current_stations, current_id=current_id, favorites=self._favorites_set
        )

    def _toggle_favorite_current(self):
        if self._current_station:
            self._toggle_favorite(self._current_station)

    def _refresh_favorites(self):
        favs = self.db.get_favorites()
        self._favorites_set = {f["station_uuid"] for f in favs}

        # Convert DB rows to pseudo-station dicts for the list
        stations = []
        for f in favs:
            stations.append({
                "stationuuid": f["station_uuid"],
                "name": f["name"],
                "url_resolved": f["url"],
                "tags": f.get("tags", ""),
                "country": f.get("country", ""),
                "bitrate": f.get("bitrate", 0),
                "source": f.get("source", ""),
            })

        current_id = self._current_station.id if self._current_station else ""
        self.favorites_list.set_stations(stations, current_id=current_id, favorites=self._favorites_set)
        self.fav_header.setText(f"SAVED STATIONS · {len(favs)}")
        self.nav_buttons["favorites"].setText(f"★ Favorites ({len(favs)})" if favs else "★ Favorites")

    # ── Liked Songs ─────────────────────────────────────────

    def _like_current_song(self):
        np = self.player.now_playing
        if not np or not np.station_name:
            return

        self.db.add_liked_song(
            title=np.title or np.raw_meta or np.station_name,
            artist=np.artist,
            station_name=np.station_name,
            station_uuid=self._current_station.id if self._current_station else "",
            tags=self._current_station.tags if self._current_station else "",
        )

        count = len(self.db.get_liked_songs())
        self.nav_buttons["songs"].setText(f"♪ Songs ({count})" if count else "♪ Songs")

    def _refresh_liked_songs(self):
        songs = self.db.get_liked_songs()
        self.songs_header.setText(f"LIKED SONGS · {len(songs)}")

        # Clear existing
        while self.songs_container_layout.count() > 1:
            item = self.songs_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not songs:
            empty = QLabel("♪\n\nHit the heart on the now-playing bar to save songs.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: rgba(255,255,255,0.2); padding: 60px; font-size: 14px;")
            self.songs_container_layout.insertWidget(0, empty)
            return

        for song in songs:
            card = QFrame()
            card.setStyleSheet("""
                QFrame { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
                         border-radius: 8px; padding: 4px; }
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(14, 10, 14, 10)

            info = QVBoxLayout()
            title_text = song.get("title", "Unknown")
            if song.get("artist"):
                title_text = f"{song['artist']} — {song['title']}"
            title_lbl = QLabel(title_text)
            title_lbl.setObjectName("stationName")
            info.addWidget(title_lbl)

            meta_parts = [song.get("station_name", "")]
            if song.get("detected_at"):
                meta_parts.append(song["detected_at"][:16])
            meta_lbl = QLabel(" · ".join(p for p in meta_parts if p))
            meta_lbl.setObjectName("stationMeta")
            info.addWidget(meta_lbl)

            card_layout.addLayout(info, stretch=1)

            del_btn = QPushButton("×")
            del_btn.setStyleSheet("border: none; color: rgba(255,255,255,0.2); font-size: 16px;")
            del_btn.clicked.connect(partial(self._delete_liked_song, song["id"]))
            card_layout.addWidget(del_btn)

            self.songs_container_layout.insertWidget(self.songs_container_layout.count() - 1, card)

    def _delete_liked_song(self, song_id):
        self.db.remove_liked_song(song_id)
        self._refresh_liked_songs()

    # ── Errors ──────────────────────────────────────────────

    def _show_error(self, msg):
        self.status_label.setText(msg)
        self.status_label.setVisible(True)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))

    # ── Cleanup ─────────────────────────────────────────────

    def closeEvent(self, event):
        self.player.cleanup()
        self.db.close()
        event.accept()
