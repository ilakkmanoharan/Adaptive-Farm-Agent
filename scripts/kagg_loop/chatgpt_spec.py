"""Ask Grok (preferred) or Cursor for the next-submission spec. OpenAI is optional last resort."""

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

HEURISTIC = (
    "# Heuristic next-spec (no LLM)\n\n"
    "Keep the previous bot's crash wrapper. Never DROP; use PLACE item n for harvest.\n"
    "Reserve pastures; sheep-first then cows; BUY_PRODUCT WHEAT so shed+carried >= herd+4.\n"
    "Delay land until day>=10 and bank>=5000. Plant cap workers*3. Water before planting more.\n"
    "Fix any thrash (PICKUP/DROP loops) and feed escapes from the latest briefing if present.\n"
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
    body, source = ask_strategist(
        day=day,
        slot=slot,
        code_folder=code_folder,
        briefing_text=briefing_text,
        prev_code_dir=prev_code_dir,
        prev_kaggle_id=prev_kaggle_id,
    )
    (spec_dir / ("strategist-s%s-spec.md" % slot)).write_text(body, encoding="utf-8")
    # Keep legacy filename so older tooling still finds a draft.
    (spec_dir / ("chatgpt-s%s-spec.md" % slot)).write_text(body, encoding="utf-8")
    merged = _merge_spec(
        day=day,
        slot=slot,
        code_folder=code_folder,
        body=body,
        source=source,
        prev_kaggle_id=prev_kaggle_id,
    )
    out = spec_dir / ("kaggriculture-s%s-spec.md" % slot)
    out.write_text(merged, encoding="utf-8")
    print("strategist source:", source)
    return out


def ask_strategist(
    *,
    day: date,
    slot: int,
    code_folder: str,
    briefing_text: str,
    prev_code_dir: str | None,
    prev_kaggle_id: int | None,
) -> tuple[str, str]:
    user = _user_prompt(
        day=day,
        slot=slot,
        code_folder=code_folder,
        briefing_text=briefing_text,
        prev_code_dir=prev_code_dir,
        prev_kaggle_id=prev_kaggle_id,
    )

    # 1) Grok / xAI
    try:
        text = _chat_completions(
            url="https://api.x.ai/v1/chat/completions",
            key=secret("XAI_API_KEY"),
            model=_env_model("KAGG_LOOP_GROK_MODEL", "grok-3"),
            user=user,
        )
        if text:
            return text, "grok"
    except Exception as exc:
        print("grok strategist failed:", exc)

    # 2) Cursor cloud one-shot (optional)
    try:
        text = _cursor_strategist(user)
        if text:
            return text, "cursor"
    except Exception as exc:
        print("cursor strategist failed:", exc)

    # 3) OpenAI only if credits exist — never abort the loop on 429
    try:
        text = _chat_completions(
            url="https://api.openai.com/v1/chat/completions",
            key=secret("OPENAI_API_KEY"),
            model=_env_model("KAGG_LOOP_OPENAI_MODEL", "gpt-4o"),
            user=user,
        )
        if text:
            return text, "openai"
    except Exception as exc:
        print("openai strategist skipped:", exc)

    return HEURISTIC + "\n## Briefing excerpt\n\n```\n%s\n```\n" % briefing_text[:6000], "heuristic"


def ask_chatgpt(**kwargs) -> str:
    """Back-compat wrapper."""
    text, _source = ask_strategist(**kwargs)
    return text


def _user_prompt(
    *,
    day: date,
    slot: int,
    code_folder: str,
    briefing_text: str,
    prev_code_dir: str | None,
    prev_kaggle_id: int | None,
) -> str:
    return f"""Kaggriculture next submission plan.
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


def _env_model(name: str, default: str) -> str:
    import os

    return (os.environ.get(name) or default).strip()


def _chat_completions(*, url: str, key: str | None, model: str, user: str) -> str | None:
    if not key:
        return None
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def _cursor_strategist(user: str) -> str | None:
    key = secret("CURSOR_API_KEY")
    if not key:
        return None
    from cursor_sdk import Agent, AgentOptions, CloudAgentOptions

    prompt = SYSTEM + "\n\n" + user + "\n\nReply with the markdown spec only."
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=key,
            model="composer-2.5",
            cloud=CloudAgentOptions(repos=[]),
        ),
    )
    if getattr(result, "status", None) == "error":
        return None
    text = getattr(result, "result", None) or ""
    return text.strip() or None


def _merge_spec(
    *,
    day: date,
    slot: int,
    code_folder: str,
    body: str,
    source: str,
    prev_kaggle_id: int | None,
) -> str:
    return (
        "# Kaggriculture Submission %s Specification\n"
        "Date: %s · Slot: s%s · Folder: `%s/`\n\n"
        "Previous Kaggle id: %s\n"
        "Sources: pulled live episodes + strategist (`%s`).\n\n"
        "%s\n"
    ) % (slot, day.isoformat(), slot, code_folder, prev_kaggle_id, source, body.strip())
