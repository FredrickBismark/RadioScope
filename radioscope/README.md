# RadioScope

**Human-curated internet radio with AI-powered station discovery.**

RadioScope is a Python/PyQt6 desktop internet radio player for Linux. It aggregates stations from multiple open directories — radio-browser.info (30,000+ stations) and SomaFM (30+ channels) — and uses Claude AI as a natural language station navigator. No algorithmic playlists. Just real human-curated radio with an intelligent tuner.

## Features

- **Multi-source station aggregator** — Pulls live from radio-browser.info and SomaFM, deduplicates by URL, and sorts by popularity. Sources are modular — add new directories by subclassing `StationSource`.
- **AI Station Navigator** — Describe a mood, activity, or vibe in plain English. Claude translates it into genre tags and SomaFM channel IDs, then the aggregator finds matching stations. The AI never touches the audio pipeline.
- **12 mood presets** — Quick Tune chips for instant genre browsing: Deep Focus, Night Drive, Jazz Club, Punk Energy, Soul & Funk, World Sounds, Classical, Lo-Fi Chill, Metal, Indie, Blues, Techno.
- **Live ICY metadata** — Polls VLC every 3 seconds for stream metadata. Parses "Artist - Title" format from ICY tags and displays what's currently playing.
- **Favorites & liked songs** — Persistent SQLite storage for station presets and song history. Like any currently-playing song with one click or the `L` key. Favorites sync across sessions.
- **Play history** — Every station play is logged with timestamp for later review.
- **Station cache** — Caches search results in SQLite with a 6-hour TTL to reduce API calls.
- **Dark theme** — Custom-designed dark UI with an orange accent palette. All styling lives in a single stylesheet (`ui/theme.py`).
- **Keyboard-driven** — Full hotkey support for hands-free operation.

## Requirements

- Linux (targeted at Linux Mint 21/22, Ubuntu-compatible)
- Python 3.10+
- VLC media player (`sudo apt install vlc`)
- Anthropic API key (optional — AI features only)

## Quick Start

### Automated setup

```bash
cd radioscope
chmod +x setup.sh
./setup.sh
```

The setup script checks for Python and VLC, creates a virtual environment, installs dependencies, initializes `.env` from the template, and creates the `data/` directory.

### Manual setup

```bash
cd radioscope

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Enable AI station discovery
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env

# Run
python main.py
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `S` | Stop |
| `F` | Toggle favorite on current station |
| `L` | Like current song |
| `+` / `-` | Volume up / down (5% steps) |
| `Ctrl+F` | Focus search bar |
| `Ctrl+Q` | Quit |

## UI Overview

RadioScope has four pages accessible from the header navigation:

- **Discover** — Search by name, browse by mood preset, or see top stations. Station cards show name, genre tags, country, bitrate, codec, and source.
- **AI Tuner** — Natural language station finder. Type a description and Claude returns curated search terms. Includes example prompts to get started.
- **Favorites** — Saved stations with play counts and last-played timestamps.
- **Songs** — Liked songs detected from ICY metadata, with artist, title, station, and detection time.

The **now-playing bar** appears at the bottom during playback, showing the current track, station name, playback controls, a like button, and a volume slider.

## Architecture

```
radioscope/
├── main.py              # Entry point — PyQt6 app bootstrap with HiDPI support
├── requirements.txt     # PyQt6, python-vlc, aiohttp, anthropic, python-dotenv
├── setup.sh             # First-time setup script (Python, VLC, venv, deps, .env)
├── core/
│   ├── config.py        # Paths, API keys/URLs, player defaults, mood presets
│   ├── player.py        # VLC stream player + ICY metadata polling (3s interval)
│   ├── stations.py      # StationSource ABC, RadioBrowserSource, SomaFMSource, StationAggregator
│   ├── database.py      # SQLite: favorites, liked_songs, play_history, station_cache
│   └── ai_tuner.py      # Anthropic API — prompt to JSON {searches, somafm_channels}
├── ui/
│   ├── main_window.py   # MainWindow, StationFetcher thread, navigation, signal wiring
│   ├── station_list.py  # StationCard + StationList (scrollable card list)
│   ├── player_bar.py    # Now-playing bar with controls and volume slider
│   ├── ai_panel.py      # AI prompt input, suggestion chips, AIWorker thread
│   └── theme.py         # COLORS dict + single STYLESHEET string (dark + orange accent)
└── data/
    └── radioscope.db    # SQLite database (auto-created, gitignored)
```

## Adding Station Sources

Station sources are modular. Each source subclasses `StationSource` in `core/stations.py`:

```python
class MySource(StationSource):
    name = "My Radio Directory"

    async def search(self, query: str = "", tags: str = "", limit: int = 30) -> list[Station]:
        # Fetch and return list of Station objects
        ...

    async def top_stations(self, limit: int = 30) -> list[Station]:
        # Return most popular stations
        ...
```

Then add an instance to `StationAggregator.__init__()` in `self.sources`. The aggregator calls all sources in parallel with `asyncio.gather`, deduplicates by URL, and sorts by `click_count`.

## How the AI Tuner Works

1. User types a natural language prompt (e.g., "late night coding, dark and electronic")
2. `AIPanel` dispatches the prompt to `AIWorker` (QThread) which calls `ai_tuner.get_recommendation_sync()`
3. `ai_tuner` sends the prompt to Claude Sonnet with a system prompt that returns JSON: `{explanation, searches, somafm_channels}`
4. `MainWindow` receives the parsed searches and fires `StationFetcher` threads for each tag/query
5. Results accumulate and deduplicate in the AI station list

The AI never streams audio or builds playlists. It translates vibes into search terms that the existing aggregator executes.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | >= 6.6.0 | GUI framework |
| python-vlc | >= 3.0.18 | VLC bindings for stream playback |
| aiohttp | >= 3.9.0 | Async HTTP for station directory APIs |
| anthropic | >= 0.40.0 | Claude API client (optional) |
| python-dotenv | >= 1.0.0 | `.env` file loading |

System dependency: VLC (`sudo apt install vlc`). python-vlc is just Python bindings — the actual VLC runtime must be installed separately.

## License

MIT
