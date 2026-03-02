"""Now-playing bar — shows current station, metadata, playback controls."""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider,
)
from PyQt6.QtCore import pyqtSignal, Qt


class PlayerBar(QFrame):
    """Bottom bar showing current playback with controls."""
    play_pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    like_clicked = pyqtSignal()
    volume_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nowPlayingBar")
        self.setFixedHeight(70)
        self.setVisible(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(16)

        # Play/Pause button
        self.play_btn = QPushButton("❚❚")
        self.play_btn.setObjectName("playButton")
        self.play_btn.setProperty("playing", True)
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)
        layout.addWidget(self.play_btn)

        # Station & song info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)

        self.station_label = QLabel("Not playing")
        self.station_label.setObjectName("nowPlayingTitle")
        info_layout.addWidget(self.station_label)

        self.song_label = QLabel("")
        self.song_label.setObjectName("stationMeta")
        info_layout.addWidget(self.song_label)

        layout.addLayout(info_layout, stretch=1)

        # Like button
        self.like_btn = QPushButton("♡")
        self.like_btn.setObjectName("favButton")
        self.like_btn.setToolTip("Like current song")
        self.like_btn.clicked.connect(self.like_clicked.emit)
        layout.addWidget(self.like_btn)

        # Volume
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(8)
        self.volume_icon = QLabel("🔊")
        self.volume_icon.setFixedWidth(20)
        volume_layout.addWidget(self.volume_icon)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(90)
        self.volume_slider.valueChanged.connect(self._on_volume_change)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)

        # Stop button
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_clicked.emit)
        layout.addWidget(stop_btn)

    def _on_volume_change(self, value):
        if value == 0:
            self.volume_icon.setText("🔇")
        elif value < 50:
            self.volume_icon.setText("🔉")
        else:
            self.volume_icon.setText("🔊")
        self.volume_changed.emit(value)

    def set_playing(self, station_name: str):
        self.setVisible(True)
        self.station_label.setText(station_name)
        self.song_label.setText("Tuning in...")
        self.play_btn.setText("❚❚")
        self.play_btn.setProperty("playing", True)

    def set_paused(self):
        self.play_btn.setText("▶")
        self.play_btn.setProperty("playing", False)

    def set_resumed(self):
        self.play_btn.setText("❚❚")
        self.play_btn.setProperty("playing", True)

    def set_stopped(self):
        self.setVisible(False)

    def update_metadata(self, now_playing):
        """Update displayed metadata from NowPlaying object."""
        if now_playing.artist and now_playing.title:
            self.station_label.setText(now_playing.title)
            self.song_label.setText(f"{now_playing.artist} · {now_playing.station_name}")
        elif now_playing.raw_meta:
            self.station_label.setText(now_playing.raw_meta)
            self.song_label.setText(now_playing.station_name)
        else:
            self.station_label.setText(now_playing.station_name)
            self.song_label.setText("Listening...")
