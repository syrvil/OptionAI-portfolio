import os
from datetime import UTC, date, datetime, timedelta

from app.services.cache import FileCache


def test_weekend_analysis_uses_daily_cache_ttl(tmp_path, monkeypatch) -> None:
    cache = FileCache(tmp_path)
    path = cache.path_for("weekend")
    cache.write(path, {"value": "cached"})
    old_time = datetime.now().timestamp() - timedelta(hours=2).total_seconds()
    os.utime(path, (old_time, old_time))

    monkeypatch.setattr(
        "app.services.cache.datetime",
        type(
            "FixedDateTime",
            (datetime,),
            {
                "now": classmethod(
                    lambda cls, tz=None: datetime(2026, 8, 15, tzinfo=UTC)
                )
            },
        ),
    )

    assert cache.read(path, date(2026, 8, 15)) == {"value": "cached"}
