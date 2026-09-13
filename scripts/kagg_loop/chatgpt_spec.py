"""Ask ChatGPT for the next-submission spec from the log briefing."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from .config import secret

SYSTEM = (
    "You are the strategist for a Kaggriculture Kaggle simulation team. "
    "The live ladder is W/L/T skill rating, not coins. New bots start at 600 and "
    "drop when they lose. Unsold inventory does not score. Player actions resolve "
    "before market (cannot use a seed/animal/hire bought this turn). "
    "DROP dumps the ENTIRE inventory into the shed — never recommend DROP; use "
    "PLACE item n for harvest goods only. Animals cannot be sold. actTimeout is 1s. "
    "Write a concrete next-submission spec the coding agent can implement in one "
    "stdlib main.py. Do not invent env APIs."
)


def write_specs(
    spec_dir: Path,
    *,
    day: date,
    slot: int,
    code_folder: str,
    briefing_text: str,
    prev_code_dir: str | None,
    prev_kaggle_id: int | None,
) -> Path:
    spec_dir.mkdir(parents=True, exist_ok=True)
    chatgpt_md = ask_chatgpt(
        day=day,
        slot=slot,
        code_folder=code_folder,
        briefing_text=briefing_text,
        prev_code_dir=prev_code_dir,
        prev_kaggle_id=prev_kaggle_id,
    )
    (spec_dir / ("chatgpt-s%s-spec.md" % slot)).write_text(chatgpt_md, encoding="utf-8")
    merged = _merge_spec(
        day=day,
        slot=slot,
        code_folder=code_folder,
        chatgpt_md=chatgpt_md,
        prev_kaggle_id=prev_kaggle_id,
    )
    out = spec_dir / ("kaggriculture-s%s-spec.md" % slot)
    out.write_text(merged, encoding="utf-8")
    return out


def ask_chatgpt(
    *,
    day: date,
    slot: int,
    code_folder: str,
    briefing_text: str,
    prev_code_dir: str | None,
    prev_kaggle_id: int | None,
) -> str:
    key = secret("OPENAI_API_KEY")
    if not key:
        return (
            "# ChatGPT unavailable\n\nOPENAI_API_KEY missing. "
            "Keep the previous bot's crash wrapper, never DROP, reserve pastures, "
            "sheep-first, buy market wheat so shed+carried >= herd+4, delay land "
            "until day>=10 and bank>=5000, plant cap workers*3.\n"
        )

    user = f"""Kaggriculture next submission plan.
Date: {day.isoformat()}  slot: {slot}/5  implement folder: `{code_folder}/`
Previous Kaggle submission id: {prev_kaggle_id}
Previous code folder: {prev_code_dir}

Live episode briefing (from official replays):
{briefing_text}

Write a markdown spec with:
1. Ladder facts from these games (W/L, banks, who beat us and how)
2. Root causes we must fix (be specific: DROP/PICKUP thrash, herd size, wheat buys, weeds, land timing)
3. Exact s{slot} policy table vs the previous bot
4. Task priority
5. Local acceptance gates before Kaggle upload
6. Non-goals

Keep it implementable in one main.py. No RL, no opponent shop denial."""

    body = {
        "model": "gpt-4o",
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")[:800]
        raise SystemExit("OpenAI HTTP %s: %s" % (exc.code, err)) from exc
    return payload["choices"][0]["message"]["content"]


def _merge_spec(*, day: date, slot: int, code_folder: str, chatgpt_md: str, prev_kaggle_id: int | None) -> str:
    return (
        "# Kaggriculture Submission %s Specification\n"
        "Date: %s · Slot: s%s · Folder: `%s/`\n\n"
        "Previous Kaggle id: %s\n"
        "Sources: pulled live episodes + ChatGPT (`gpt-4o`).\n\n"
        "%s\n"
    ) % (slot, day.isoformat(), slot, code_folder, prev_kaggle_id, chatgpt_md.strip())
