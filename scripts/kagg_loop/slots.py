"""Map America/Chicago wall-clock time to today's 1–5 submit slot."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .config import SLOT_HOURS, TIMEZONE


def now_local(now: datetime | None = None) -> datetime:
    tz = ZoneInfo(TIMEZONE)
    if now is None:
        return datetime.now(tz)
    if now.tzinfo is None:
        return now.replace(tzinfo=tz)
    return now.astimezone(tz)


def slot_for(now: datetime | None = None) -> tuple[date, int]:
    """Return (local_date, slot 1–5) for the current or given time.

    Before 4am the slot is yesterday's 5 (logs-only window). Callers that
    submit should pass --slot or wait until 4am.
    """
    local = now_local(now)
    hour = local.hour
    chosen = None
    for i, start in enumerate(SLOT_HOURS, start=1):
        if hour >= start:
            chosen = i
    if chosen is None:
        # 0:00–3:59 → previous calendar day's last slot
        return local.date() - timedelta(days=1), 5
    return local.date(), chosen


def is_submit_hour(now: datetime | None = None) -> bool:
    local = now_local(now)
    return local.hour in SLOT_HOURS
