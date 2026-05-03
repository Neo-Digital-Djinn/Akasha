from __future__ import annotations

from ..models import LunarContext


def build_lunar_context(timestamp_utc: str, latitude: float, longitude: float) -> LunarContext:
    # Still intentionally conservative in V2.
    return LunarContext(
        moon_phase=None,
        moon_illumination_pct=None,
    )
