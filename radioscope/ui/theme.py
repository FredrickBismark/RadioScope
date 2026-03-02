"""Dark theme and styling for RadioScope."""

# Color palette
COLORS = {
    "bg_dark": "#0a0a0f",
    "bg_mid": "#111118",
    "bg_light": "#1a1a24",
    "bg_card": "#15151e",
    "bg_hover": "#1e1e2a",
    "accent": "#ff8c32",
    "accent_light": "#ff9f55",
    "accent_dark": "#e85d20",
    "accent_dim": "rgba(255, 140, 50, 0.15)",
    "text": "#e8e0d6",
    "text_secondary": "rgba(255, 255, 255, 0.5)",
    "text_dim": "rgba(255, 255, 255, 0.3)",
    "border": "rgba(255, 255, 255, 0.06)",
    "border_accent": "rgba(255, 140, 50, 0.3)",
    "error": "#ff6666",
    "success": "#66cc88",
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text']};
    font-family: 'Noto Sans', 'Cantarell', 'Ubuntu', sans-serif;
    font-size: 13px;
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 140, 50, 0.2);
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(255, 140, 50, 0.4);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

/* Input fields */
QLineEdit, QTextEdit {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS['text']};
    font-size: 13px;
    selection-background-color: rgba(255, 140, 50, 0.3);
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {COLORS['border_accent']};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 18px;
    color: {COLORS['text_secondary']};
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_accent']};
    color: {COLORS['accent_light']};
}}
QPushButton:pressed {{
    background-color: rgba(255, 140, 50, 0.1);
}}

QPushButton#accentButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLORS['accent']}, stop:1 {COLORS['accent_dark']});
    border: none;
    color: white;
    font-weight: 600;
}}
QPushButton#accentButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLORS['accent_light']}, stop:1 {COLORS['accent']});
}}

/* Tab-style nav buttons */
QPushButton#navButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 16px;
    color: {COLORS['text_dim']};
}}
QPushButton#navButton:hover {{
    color: {COLORS['text_secondary']};
}}
QPushButton#navButton[active="true"] {{
    background-color: {COLORS['accent_dim']};
    border-color: {COLORS['border_accent']};
    color: {COLORS['accent_light']};
}}

/* Mood preset chips */
QPushButton#moodChip {{
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 12px;
    color: {COLORS['text_secondary']};
}}
QPushButton#moodChip:hover {{
    border-color: {COLORS['border_accent']};
    color: {COLORS['accent_light']};
}}
QPushButton#moodChip[active="true"] {{
    background-color: rgba(255, 140, 50, 0.15);
    border-color: {COLORS['border_accent']};
    color: {COLORS['accent_light']};
}}

/* Station cards */
QFrame#stationCard {{
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 4px;
}}
QFrame#stationCard:hover {{
    background-color: rgba(255, 255, 255, 0.04);
    border-color: {COLORS['border_accent']};
}}

/* Play button in station card */
QPushButton#playButton {{
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    font-size: 14px;
    color: white;
}}
QPushButton#playButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLORS['accent']}, stop:1 {COLORS['accent_dark']});
}}
QPushButton#playButton[playing="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLORS['accent']}, stop:1 {COLORS['accent_dark']});
}}

/* Favorite button */
QPushButton#favButton {{
    background: transparent;
    border: none;
    font-size: 18px;
    color: {COLORS['text_dim']};
    min-width: 30px;
}}
QPushButton#favButton[favorited="true"] {{
    color: {COLORS['accent']};
}}

/* Now playing bar */
QFrame#nowPlayingBar {{
    background-color: rgba(15, 15, 22, 0.95);
    border-top: 1px solid {COLORS['border_accent']};
}}

/* Volume slider */
QSlider::groove:horizontal {{
    background: rgba(255, 255, 255, 0.1);
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {COLORS['accent']};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {COLORS['accent']};
    border-radius: 2px;
}}

/* Labels */
QLabel#sectionHeader {{
    color: {COLORS['text_dim']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}}
QLabel#stationName {{
    color: {COLORS['text']};
    font-size: 13px;
    font-weight: 600;
    font-family: 'JetBrains Mono', 'Fira Code', 'Noto Sans Mono', monospace;
}}
QLabel#stationMeta {{
    color: {COLORS['text_dim']};
    font-size: 11px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Noto Sans Mono', monospace;
}}
QLabel#nowPlayingTitle {{
    color: {COLORS['accent_light']};
    font-size: 14px;
    font-weight: 600;
    font-family: 'JetBrains Mono', 'Fira Code', 'Noto Sans Mono', monospace;
}}
QLabel#aiExplanation {{
    color: rgba(255, 255, 255, 0.65);
    font-size: 13px;
    padding: 12px 16px;
    background-color: rgba(255, 140, 50, 0.06);
    border: 1px solid rgba(255, 140, 50, 0.12);
    border-radius: 10px;
}}
"""
