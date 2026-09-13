"""Paths, competition constants, and secret loading. Never print secret values."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

COMPETITION = "kaggriculture"
US_NAME = "Ilakk manoharan"
TIMEZONE = "America/Chicago"
# Last calendar day we still submit (final deadline Sep 30, 2026).
LAST_SUBMIT_DATE = date(2026, 9, 30)
ENTRY_DEADLINE = date(2026, 9, 23)

SLOT_HOURS = (4, 7, 10, 13, 15)  # local 4am, 7am, 10am, 1pm, 3pm
MAX_SUBMITS_PER_DAY = 5

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / "private"
KEYS_FILE = PRIVATE / "api-keys" / "api-keys.md"
STATE_FILE = PRIVATE / "loop_state.json"
LOCAL_ENV = ROOT / "2026-09-12" / "_local_env"


def _parse_key_file(name: str) -> str | None:
    if not KEYS_FILE.is_file():
        return None
    for raw in KEYS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith(name + "="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


def secret(name: str) -> str | None:
    env = os.environ.get(name)
    if env and env.strip():
        return env.strip()
    return _parse_key_file(name)


def require_secret(name: str) -> str:
    value = secret(name)
    if not value:
        raise SystemExit(
            "missing %s (set the env var or add it to private/api-keys/api-keys.md)" % name
        )
    return value


def spec_dir(day: date, slot: int) -> Path:
    label = day.strftime("%b-%d-%Y")  # Sep-13-2026
    return PRIVATE / ("%s-%s" % (label, slot))


def code_dir(day: date, slot: int) -> Path:
    return ROOT / ("%s-s%s" % (day.isoformat(), slot))


def github_repo_url() -> str | None:
    explicit = os.environ.get("KAGG_LOOP_REPO_URL") or os.environ.get("GITHUB_REPO_URL")
    if explicit:
        return explicit.rstrip(".git")
    slug = os.environ.get("GITHUB_REPOSITORY")
    if slug:
        return "https://github.com/%s" % slug
    return None
