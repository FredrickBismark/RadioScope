# RadioScope 🔊

**Human-curated internet radio with AI-powered station discovery.**

RadioScope aggregates thousands of internet radio stations from multiple open directories and uses AI to help you navigate them by mood, activity, or vibe. No algorithmic playlists — just real human-curated radio with an intelligent tuner.

## Features

- **Multi-source station directory** — Pulls from radio-browser.info (30,000+ stations), with architecture ready for SomaFM, Icecast, and more
- **AI Station Navigator** — Describe what you want in natural language, Claude finds matching stations
- **Live stream metadata** — Parses ICY metadata to show what's currently playing
- **Favorites & liked songs** — Persistent SQLite storage for your station presets and song history
- **Song recognition** — Logs detected songs with timestamps for later lookup/download
- **Stream quality info** — Bitrate, codec, and reliability indicators
- **Keyboard-driven** — Full hotkey support for hands-free operation

## Requirements

- Linux (tested on Linux Mint 21/22)
- Python 3.10+
- VLC media player installed (`sudo apt install vlc`)
- Anthropic API key (for AI features — optional)

## Quick Start

```bash
# 1. Clone and enter directory
cd radioscope

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set your Anthropic API key for AI features
export ANTHROPIC_API_KEY="sk-ant-..."
# Or create a .env file:
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env

# 5. Run
python main.py
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `S` | Stop |
| `N` | Next station (in current list) |
| `P` | Previous station |
| `F` | Toggle favorite |
| `L` | Like current song |
| `+` / `-` | Volume up / down |
| `Ctrl+F` | Focus search |
| `Ctrl+Q` | Quit |

## Architecture

```
radioscope/
├── main.py                 # Entry point
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── player.py           # VLC-based stream player + ICY metadata
│   ├── stations.py         # Multi-source station aggregator
│   ├── database.py         # SQLite persistence
│   ├── ai_tuner.py         # Anthropic API integration
│   └── config.py           # App configuration
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── station_list.py     # Station list widget
│   ├── player_bar.py       # Now-playing bar
│   ├── ai_panel.py         # AI tuner panel
│   └── theme.py            # Dark theme and styling
├── data/
│   └── radioscope.db       # SQLite database (auto-created)
└── assets/
    └── icon.png
```

## Adding Station Sources

Station sources are modular. See `core/stations.py` — each source implements the `StationSource` base class with a `search()` method. To add a new source:

```python
class MySource(StationSource):
    name = "My Radio Directory"

    async def search(self, query=None, tags=None, limit=30):
        # Fetch and return list of Station objects
        ...
```

## License

MIT — do whatever you want with it.
