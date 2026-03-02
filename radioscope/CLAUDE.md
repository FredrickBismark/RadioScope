# RadioScope

## About
Python/PyQt6 desktop internet radio player for Linux. Aggregates human-curated stations from multiple open directories (radio-browser.info, SomaFM) and uses Claude AI as an intelligent station navigator — not an algorithmic playlist builder, but a knowledgeable guide to real radio.

## Tech Stack
- **Language:** Python 3.10+
- **GUI:** PyQt6
- **Audio:** python-vlc (requires system VLC: `sudo apt install vlc`)
- **Async HTTP:** aiohttp
- **Database:** SQLite (via stdlib sqlite3)
- **AI:** Anthropic Python SDK (optional, for AI tuner)
- **Config:** python-dotenv for .env loading
- **OS Target:** Linux Mint (primary), Ubuntu-compatible

## Project Structure
```
radioscope/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── .env                 # API keys (gitignored)
├── core/
│   ├── config.py        # Constants, paths, API URLs, mood presets
│   ├── player.py        # VLC stream player + ICY metadata extraction
│   ├── stations.py      # Multi-source station aggregator (modular sources)
│   ├── database.py      # SQLite persistence (favorites, liked songs, history)
│   └── ai_tuner.py      # Anthropic API integration for station recommendations
├── ui/
│   ├── main_window.py   # Main app window, navigation, signal wiring
│   ├── station_list.py  # Scrollable station card list widget
│   ├── player_bar.py    # Now-playing bar with controls
│   ├── ai_panel.py      # AI natural language station finder
│   └── theme.py         # Dark theme stylesheet and color palette
├── data/
│   └── radioscope.db    # SQLite database (auto-created, gitignored)
└── assets/              # Icons, images (future)
```

## Commands
- **Run app:** `python main.py` (from project root, with venv active)
- **Install deps:** `pip install -r requirements.txt`
- **Activate venv:** `source venv/bin/activate`
- **Create venv:** `python3 -m venv venv`

## Architecture Decisions
- **Station sources are modular.** Each source subclasses `StationSource` in `core/stations.py` with `search()` and `top_stations()` methods. `StationAggregator` combines all sources, deduplicates by URL, and sorts by popularity.
- **Player uses VLC via python-vlc.** This handles the widest range of stream codecs and formats. ICY metadata is polled every 3 seconds via VLC's media meta API.
- **AI is a translator, not an algorithm.** `ai_tuner.py` takes natural language, returns search terms and SomaFM channel IDs. The aggregator executes the actual searches. The AI never touches the audio pipeline.
- **All persistence goes through `Database` class.** No raw SQL elsewhere. Tables: favorites, liked_songs, play_history, station_cache.
- **Qt signals bridge async to sync.** Station fetching and AI calls run in QThread workers. Results emit signals consumed by the main thread.

## Code Style
- Type hints on function signatures
- Docstrings on classes and public methods
- No wildcard imports
- f-strings for formatting
- dataclasses for data containers (see `Station`, `NowPlaying`)
- PyQt6 signals/slots pattern for UI updates
- snake_case for functions/variables, PascalCase for classes

## Known Limitations & TODOs
- SomaFM source returns .pls playlist URLs — VLC handles these but a proper PLS parser would be more robust
- No song fingerprinting yet (planned: Chromaprint/AcoustID integration)
- No download capability for liked songs yet (planned: yt-dlp matching)
- Metadata extraction depends on ICY tags in the stream — not all stations provide them
- No Icecast/xiph.org directory source yet
- Station cache TTL is 6 hours, not configurable from UI
- No system tray integration yet

## Important Notes
- API key is optional — the app works fully without AI features. Set `ANTHROPIC_API_KEY` in `.env` to enable the AI tuner.
- VLC must be installed system-wide (`sudo apt install vlc`). python-vlc is just bindings.
- The `data/` directory is auto-created. `radioscope.db` should not be committed.
- All UI styling is in `ui/theme.py` via a single Qt stylesheet string. Colors are in the `COLORS` dict.
