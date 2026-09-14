"""Persisted per-day slot bookkeeping."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from .config import STATE_FILE


def load() -> dict[str, Any]:
    if not STATE_FILE.is_file():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save(data: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def day_key(day: date) -> str:
    return day.isoformat()


def slot_record(data: dict[str, Any], day: date, slot: int) -> dict[str, Any] | None:
    return (data.get(day_key(day)) or {}).get(str(slot))


def next_unused_slot(day: date, data: dict[str, Any] | None = None) -> int | None:
    """First of 1–5 for this Chicago day that has no kaggle_id yet."""
    data = load() if data is None else data
    day_map = data.get(day_key(day)) or {}
    for slot in (1, 2, 3, 4, 5):
        rec = day_map.get(str(slot)) or {}
        if not rec.get("kaggle_id"):
            return slot
    return None


def mark(day: date, slot: int, **fields: Any) -> dict[str, Any]:
    data = load()
    day_map = data.setdefault(day_key(day), {})
    rec = day_map.setdefault(str(slot), {})
    rec.update(fields)
    save(data)
    return rec


def latest_kaggle_id() -> int | None:
    data = load()
    best = None
    best_key = ()
    for day_s, slots in data.items():
        if not isinstance(slots, dict):
            continue
        for slot_s, rec in slots.items():
            if not isinstance(rec, dict):
                continue
            kid = rec.get("kaggle_id")
            if not kid:
                continue
            key = (day_s, int(slot_s))
            if key >= best_key:
                best_key = key
                best = int(kid)
    return best
