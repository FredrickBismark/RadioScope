"""AI Tuner panel — natural language station discovery."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from core.ai_tuner import get_recommendation_sync, AIRecommendation


class AIWorker(QThread):
    """Background thread for AI API calls."""
    finished = pyqtSignal(object)

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        result = get_recommendation_sync(self.prompt)
        self.finished.emit(result)


class AIPanel(QWidget):
    """AI station navigator panel."""
    search_requested = pyqtSignal(str, str)  # (query, tags)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header
        header = QLabel("AI STATION NAVIGATOR")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        desc = QLabel(
            "Describe what you're in the mood for — an activity, a feeling, a vibe — "
            "and the AI will find human-curated stations that match."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 13px; margin-bottom: 4px;")
        layout.addWidget(desc)

        # Input area
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            'e.g. "Late night coding session, something dark and electronic '
            'but not too aggressive" or "3am drive through empty desert highways"'
        )
        self.prompt_input.setMaximumHeight(80)
        self.prompt_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        input_row.addWidget(self.prompt_input, stretch=1)

        self.search_btn = QPushButton("Find\nStations")
        self.search_btn.setObjectName("accentButton")
        self.search_btn.setFixedSize(90, 70)
        self.search_btn.clicked.connect(self._on_search)
        input_row.addWidget(self.search_btn)

        layout.addLayout(input_row)

        # AI response
        self.response_label = QLabel()
        self.response_label.setObjectName("aiExplanation")
        self.response_label.setWordWrap(True)
        self.response_label.setVisible(False)
        layout.addWidget(self.response_label)

        # Suggestion chips
        self.suggestions_widget = QWidget()
        suggestions_layout = QVBoxLayout(self.suggestions_widget)
        suggestions_layout.setContentsMargins(0, 0, 0, 0)
        suggestions_layout.setSpacing(8)

        suggestions_header = QLabel("TRY ASKING FOR...")
        suggestions_header.setObjectName("sectionHeader")
        suggestions_layout.addWidget(suggestions_header)

        suggestions = [
            "Something for a rainy Sunday morning with coffee",
            "Music for soldering electronics at 2am",
            "Stations that play obscure 70s prog rock deep cuts",
            "Background for reading cyberpunk novels",
            "High energy for a late-night workout",
        ]
        for text in suggestions:
            btn = QPushButton(f'"{text}"')
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left; padding: 10px 14px; border-radius: 8px;
                    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
                    color: rgba(255,255,255,0.35); font-size: 12px;
                }
                QPushButton:hover {
                    border-color: rgba(255,140,50,0.3); color: rgba(255,255,255,0.55);
                }
            """)
            btn.clicked.connect(lambda checked, t=text: self._fill_prompt(t))
            suggestions_layout.addWidget(btn)

        layout.addWidget(self.suggestions_widget)
        layout.addStretch()

    def _fill_prompt(self, text):
        self.prompt_input.setPlainText(text)
        self.prompt_input.setFocus()

    def _on_search(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.search_btn.setText("Tuning...")
        self.search_btn.setEnabled(False)
        self.response_label.setVisible(False)

        self._worker = AIWorker(prompt)
        self._worker.finished.connect(self._on_result)
        self._worker.start()

    @pyqtSlot(object)
    def _on_result(self, rec: AIRecommendation):
        self.search_btn.setText("Find\nStations")
        self.search_btn.setEnabled(True)

        if rec.error:
            self.response_label.setText(f"⚠ {rec.error}")
            self.response_label.setVisible(True)
            return

        if rec.explanation:
            self.response_label.setText(f"◆ {rec.explanation}")
            self.response_label.setVisible(True)

        self.suggestions_widget.setVisible(False)

        # Emit searches for the main window to execute
        for term in rec.searches:
            self.search_requested.emit(term, "tag")

        # Also emit SomaFM channel searches
        for ch in rec.somafm_channels:
            self.search_requested.emit(ch, "somafm")

    def reset(self):
        self.prompt_input.clear()
        self.response_label.setVisible(False)
        self.suggestions_widget.setVisible(True)
