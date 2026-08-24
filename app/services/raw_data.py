"""Local storage for unmodified provider responses."""

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]


class RawMarketDataStore:
    """Save provider tables and request details in a local directory."""

    def __init__(self, directory: Path = Path("data/raw")) -> None:
        self.directory = directory

    def save(
        self,
        ticker: str,
        frame: pd.DataFrame,
        metadata: dict[str, str],
    ) -> None:
        """Save one raw table and its metadata."""
        self.directory.mkdir(parents=True, exist_ok=True)
        safe_ticker = re.sub(r"[^A-Za-z0-9_.-]", "_", ticker)
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        base = self.directory / f"{safe_ticker}_{stamp}"
        frame.to_csv(base.with_suffix(".csv"))
        base.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True),
            encoding="utf-8",
        )
