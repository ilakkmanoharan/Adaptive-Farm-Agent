"""Upload main.py to Kaggle and resolve the new submission id."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .config import COMPETITION


def submit(main_py: Path, message: str) -> dict[str, Any]:
    from kaggle.api.kaggle_api_extended import KaggleApi

    if not main_py.is_file():
        raise SystemExit("nothing to submit: %s" % main_py)
    api = KaggleApi()
    api.authenticate()
    before = {getattr(s, "ref", None) for s in (api.competition_submissions(COMPETITION) or [])}
    api.competition_submit(str(main_py), message, COMPETITION)
    new_id = None
    desc = message
    status = "unknown"
    score = None
    for _ in range(12):
        time.sleep(2)
        for s in api.competition_submissions(COMPETITION) or []:
            ref = getattr(s, "ref", None)
            if ref and ref not in before:
                new_id = int(ref)
                desc = getattr(s, "description", message)
                status = str(getattr(s, "status", ""))
                score = getattr(s, "publicScore", None)
                break
        if new_id:
            break
    return {
        "kaggle_id": new_id,
        "description": desc,
        "status": status,
        "publicScore": score,
        "file": str(main_py),
        "message": message,
    }
