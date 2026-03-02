Review the codebase and suggest improvements.

1. Read through all Python files in `core/` and `ui/`
2. Check for:
   - Missing type hints or docstrings
   - Error handling gaps (especially network calls and VLC operations)
   - Signal/slot connections that could leak or cause crashes
   - Threading issues (async operations running on the main thread)
   - UI responsiveness problems (blocking calls)
   - Dead code or unused imports
3. Prioritize issues by severity: crashes > data loss > UX problems > code quality
4. Propose fixes with rationale
5. Implement approved fixes incrementally, testing between changes
