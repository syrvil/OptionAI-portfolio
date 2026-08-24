"""Small replaceable filesystem cache used by analysis agents."""

import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any


class FileCache:
    """Store JSON values locally with a caller-selected freshness period."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def path_for(self, *parts: str) -> Path:
        """Return a stable hashed path for cache key parts."""
        key = hashlib.sha256("|".join(parts).encode()).hexdigest()
        return self.directory / f"{key}.json"

    def read(
        self,
        path: Path,
        analysis_date: date,
        *,
        ttl_override: timedelta | None = None,
    ) -> dict[str, Any] | None:
        """Read a fresh JSON object, returning none for missing/invalid data."""
        if not path.exists():
            return None
        today = datetime.now(UTC).date()
        is_current_trading_day = analysis_date >= today and analysis_date.weekday() < 5
        ttl = ttl_override or (
            timedelta(hours=1) if is_current_trading_day else timedelta(days=1)
        )
        if datetime.now().timestamp() - path.stat().st_mtime > ttl.total_seconds():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return None
        return value if isinstance(value, dict) else None

    def write(self, path: Path, value: dict[str, Any]) -> None:
        """Write a JSON object to the cache directory."""
        self.directory.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2), encoding="utf-8")
