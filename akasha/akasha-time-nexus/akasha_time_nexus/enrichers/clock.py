from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from ..models import ClockContext


def _season(day_of_year: int) -> str:
    if 80 <= day_of_year < 172:
        return "spring"
    if 172 <= day_of_year < 264:
        return "summer"
    if 264 <= day_of_year < 355:
        return "autumn"
    return "winter"


def build_clock_context(timestamp_utc: str, timezone_name: str = "UTC") -> ClockContext:
    dt_utc = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00")).astimezone(UTC)
    tz = ZoneInfo(timezone_name)
    dt_local = dt_utc.astimezone(tz)

    return ClockContext(
        utc=dt_utc.isoformat(),
        local=dt_local.isoformat(),
        timezone_name=timezone_name,
        day_of_week=dt_local.strftime("%A"),
        day_of_year=int(dt_local.strftime("%j")),
        season=_season(int(dt_local.strftime("%j"))),
        hour_local=dt_local.hour,
        is_weekend=dt_local.weekday() >= 5,
    )
