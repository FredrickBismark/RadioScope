"""Application configuration and constants."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "radioscope.db"

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Radio Browser API — use multiple mirrors for reliability
RADIO_BROWSER_MIRRORS = [
    "https://de1.api.radio-browser.info",
    "https://nl1.api.radio-browser.info",
    "https://at1.api.radio-browser.info",
]

# SomaFM
SOMAFM_API = "https://somafm.com/channels.json"

# Player defaults
DEFAULT_VOLUME = 70  # 0-100
METADATA_POLL_INTERVAL_MS = 3000

# AI config
AI_MODEL = "claude-sonnet-4-20250514"
AI_MAX_TOKENS = 1024

# Mood presets
MOOD_PRESETS = [
    {"label": "Deep Focus", "tags": "ambient,electronic,chillout", "icon": "◉"},
    {"label": "Night Drive", "tags": "synthwave,retrowave,electronic", "icon": "◈"},
    {"label": "Jazz Club", "tags": "jazz,smooth jazz,bebop", "icon": "♪"},
    {"label": "Punk Energy", "tags": "punk,hardcore,rock", "icon": "⚡"},
    {"label": "Soul & Funk", "tags": "soul,funk,r&b", "icon": "◎"},
    {"label": "World Sounds", "tags": "world,reggae,african", "icon": "◆"},
    {"label": "Classical", "tags": "classical,opera,symphony", "icon": "♫"},
    {"label": "Lo-Fi Chill", "tags": "lofi,chillhop,downtempo", "icon": "◇"},
    {"label": "Metal", "tags": "metal,heavy metal,death metal", "icon": "⬥"},
    {"label": "Indie", "tags": "indie,alternative,indie rock", "icon": "△"},
    {"label": "Blues", "tags": "blues,delta blues,chicago blues", "icon": "♬"},
    {"label": "Techno", "tags": "techno,minimal,industrial", "icon": "▣"},
]
