Add a new station source to RadioScope.

1. Read `core/stations.py` to understand the `StationSource` base class and the `Station` dataclass
2. Ask me which radio directory or API to integrate (e.g., Icecast/xiph.org, TuneIn, Internet-Radio.com)
3. Create a new class subclassing `StationSource` with:
   - `name` class attribute
   - `async search(query, tags, limit)` method
   - `async top_stations(limit)` method
   - `_normalize()` method to convert API responses to `Station` objects
4. Register the new source in `StationAggregator.__init__()` sources list
5. Test the new source by running a search and verifying results have valid URLs
6. Update CLAUDE.md if the source has any quirks worth documenting
