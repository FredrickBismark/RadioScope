"""Station list widget — displays a scrollable list of station cards."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt


class StationCard(QFrame):
    """Single station card widget."""
    play_clicked = pyqtSignal(object)
    favorite_clicked = pyqtSignal(object)

    def __init__(self, station, is_playing=False, is_favorite=False, parent=None):
        super().__init__(parent)
        self.station = station
        self.setObjectName("stationCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # Play button
        self.play_btn = QPushButton("❚❚" if is_playing else "▶")
        self.play_btn.setObjectName("playButton")
        self.play_btn.setProperty("playing", is_playing)
        self.play_btn.clicked.connect(lambda: self.play_clicked.emit(self.station))
        layout.addWidget(self.play_btn)

        # Station info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name = station.name if hasattr(station, 'name') else station.get("name", "Unknown")
        name_label = QLabel(name)
        name_label.setObjectName("stationName")
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout.addWidget(name_label)

        # Build meta string
        tags = station.tags if hasattr(station, 'tags') else station.get("tags", "")
        country = station.country if hasattr(station, 'country') else station.get("country", "")
        bitrate = station.bitrate if hasattr(station, 'bitrate') else station.get("bitrate", 0)
        source = station.source if hasattr(station, 'source') else station.get("source", "")

        meta_parts = []
        if tags:
            meta_parts.append(" · ".join(t.strip() for t in tags.split(",")[:3]))
        if country:
            meta_parts.append(country)
        if bitrate and bitrate > 0:
            meta_parts.append(f"{bitrate}kbps")
        if source:
            meta_parts.append(source)

        meta_label = QLabel(" · ".join(meta_parts) or "Internet Radio")
        meta_label.setObjectName("stationMeta")
        info_layout.addWidget(meta_label)

        layout.addLayout(info_layout, stretch=1)

        # Favorite button
        self.fav_btn = QPushButton("★" if is_favorite else "☆")
        self.fav_btn.setObjectName("favButton")
        self.fav_btn.setProperty("favorited", is_favorite)
        self.fav_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.station))
        layout.addWidget(self.fav_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.play_clicked.emit(self.station)
        super().mousePressEvent(event)


class StationList(QWidget):
    """Scrollable list of station cards."""
    play_station = pyqtSignal(object)
    toggle_favorite = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_station_id = None
        self._favorites = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 8, 0)
        self.container_layout.setSpacing(6)
        self.container_layout.addStretch()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self._empty_label = QLabel("No stations found")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: rgba(255,255,255,0.2); padding: 60px; font-size: 14px;")
        self._empty_label.setVisible(False)
        layout.addWidget(self._empty_label)

    def set_stations(self, stations: list, current_id: str = None, favorites: set = None):
        """Replace the station list."""
        if current_id is not None:
            self._current_station_id = current_id
        if favorites is not None:
            self._favorites = favorites

        # Clear existing
        while self.container_layout.count() > 1:  # keep stretch
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._empty_label.setVisible(len(stations) == 0)

        for station in stations:
            sid = station.id if hasattr(station, 'id') else station.get("stationuuid", station.get("station_uuid", ""))
            is_playing = sid == self._current_station_id
            is_fav = sid in self._favorites

            card = StationCard(station, is_playing=is_playing, is_favorite=is_fav)
            card.play_clicked.connect(self.play_station.emit)
            card.favorite_clicked.connect(self.toggle_favorite.emit)
            self.container_layout.insertWidget(self.container_layout.count() - 1, card)

    def update_playing(self, station_id: str):
        """Update which station shows as playing."""
        self._current_station_id = station_id
        for i in range(self.container_layout.count()):
            item = self.container_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), StationCard):
                card = item.widget()
                sid = card.station.id if hasattr(card.station, 'id') else card.station.get("stationuuid", "")
                playing = sid == station_id
                card.play_btn.setText("❚❚" if playing else "▶")
                card.play_btn.setProperty("playing", playing)
                card.play_btn.style().unpolish(card.play_btn)
                card.play_btn.style().polish(card.play_btn)
