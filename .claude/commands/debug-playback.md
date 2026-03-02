Debug a radio stream playback issue.

1. Ask me to describe the problem (no audio, wrong station, metadata not showing, etc.)
2. Read `core/player.py` to understand the VLC integration and metadata polling
3. Check common issues:
   - Is the stream URL valid and responding? Test with: `python -c "import vlc; p=vlc.MediaPlayer('URL'); p.play()"`
   - Is VLC installed system-wide? `which vlc`
   - Is the stream format supported? Check codec in station data
   - Are ICY metadata headers present? Some streams don't send them
   - Is the metadata poll timer running? Check `METADATA_POLL_INTERVAL_MS` in config
4. If it's a SomaFM issue, check if the .pls URL needs resolution to a direct stream
5. Propose a fix, implement it, and test
