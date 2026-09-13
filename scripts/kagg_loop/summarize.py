"""Compress huge Kaggle replays into a briefing ChatGPT can actually use."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .config import US_NAME


def summarize_logs(log_dir: Path, us_name: str = US_NAME) -> dict[str, Any]:
    episodes_path = log_dir / "episodes.json"
    episode_meta = []
    if episodes_path.is_file():
        episode_meta = json.loads(episodes_path.read_text(encoding="utf-8")).get("episodes") or []

    summaries = []
    for replay_path in sorted(log_dir.glob("*-replay.json")):
        try:
            replay = json.loads(replay_path.read_text(encoding="utf-8"))
        except Exception as exc:
            summaries.append({"file": replay_path.name, "error": str(exc)})
            continue
        summaries.append(_summarize_replay(replay, replay_path.name, us_name))

    wins = losses = ties = 0
    banks = []
    for row in summaries:
        if "error" in row or row.get("us_index") is None:
            continue
        us = row["rewards"][row["us_index"]]
        opp = row["rewards"][1 - row["us_index"]]
        banks.append(us)
        if us > opp:
            wins += 1
        elif us < opp:
            losses += 1
        else:
            ties += 1

    briefing = {
        "record": "%sW-%sT-%sL" % (wins, ties, losses),
        "mean_us_bank": (sum(banks) / len(banks)) if banks else None,
        "episodes_api": episode_meta,
        "summaries": summaries,
    }
    (log_dir / "replay_summary.json").write_text(
        json.dumps(briefing, indent=2), encoding="utf-8"
    )
    return briefing


def briefing_text(briefing: dict[str, Any], limit: int = 24000) -> str:
    """Human-readable compact text for the ChatGPT prompt."""
    lines = [
        "Record: %s  mean our bank: %s" % (briefing.get("record"), briefing.get("mean_us_bank")),
        "",
    ]
    for row in briefing.get("summaries") or []:
        if "error" in row:
            lines.append("ERROR %s %s" % (row.get("file"), row["error"]))
            continue
        names = row.get("names") or ["p0", "p1"]
        rewards = row.get("rewards") or [0, 0]
        ui = row.get("us_index", 0)
        opp = 1 - ui
        result = "WIN" if rewards[ui] > rewards[opp] else ("LOSS" if rewards[ui] < rewards[opp] else "TIE")
        lines.append(
            "Episode %s %s us=%s opp=%s (%s vs %s)"
            % (row.get("episode"), result, rewards[ui], rewards[opp], names[ui], names[opp])
        )
        lines.append(
            "  our actions: %s  opp actions: %s  our PASS-rate=%.3f"
            % (row.get("unit_actions", [0, 0])[ui], row.get("unit_actions", [0, 0])[opp], row.get("pass_rate", [0, 0])[ui])
        )
        lines.append("  our market: %s" % row.get("our_market"))
        lines.append("  opp market: %s" % row.get("opp_market"))
        for snap in row.get("daily") or []:
            if snap.get("day") not in (0, 1, 3, 7, 12, 20, 29):
                continue
            p = (snap.get("players") or [None, None])[ui]
            o = (snap.get("players") or [None, None])[opp]
            if not p:
                continue
            lines.append(
                "  day %s us money=%s herd=%s plants=%s weeds=%s quads=%s | opp money=%s herd=%s plants=%s"
                % (
                    snap.get("day"),
                    p.get("money"),
                    p.get("herd"),
                    p.get("plants"),
                    p.get("weeds"),
                    p.get("quads"),
                    (o or {}).get("money"),
                    (o or {}).get("herd"),
                    (o or {}).get("plants"),
                )
            )
        lines.append("")
    text = "\n".join(lines)
    if len(text) > limit:
        text = text[:limit] + "\n...truncated...\n"
    return text


def _summarize_replay(replay: dict[str, Any], filename: str, us_name: str) -> dict[str, Any]:
    info = replay.get("info") or {}
    agents = info.get("Agents") or []
    names = [a.get("Name") if isinstance(a, dict) else str(a) for a in agents]
    if not names:
        names = list(info.get("TeamNames") or ["p0", "p1"])
    us_index = 0
    for i, name in enumerate(names):
        if us_name.lower() in str(name).lower():
            us_index = i
            break

    steps = replay.get("steps") or []
    unit_counts = [Counter(), Counter()]
    market_counts = [Counter(), Counter()]
    pass_n = [0, 0]
    unit_n = [0, 0]
    daily = []
    snapshot_hours = {0, 23}

    for step_i, pair in enumerate(steps):
        if not isinstance(pair, list) or len(pair) < 2:
            continue
        hour = None
        day = None
        for p, side in enumerate(pair[:2]):
            act = (side or {}).get("action") or {}
            _count_actions(act, unit_counts[p], market_counts[p])
            farmer = act.get("farmer") or ["PASS"]
            hands = act.get("hands") or []
            unit_n[p] += 1 + len(hands)
            if farmer == ["PASS"] or farmer == "PASS":
                pass_n[p] += 1
            pass_n[p] += sum(1 for h in hands if h == ["PASS"] or h == "PASS")
            obs = (side or {}).get("observation") or {}
            hour = obs.get("hour", hour)
            day = obs.get("day", day)
        if hour in snapshot_hours or step_i in (0, len(steps) - 1):
            daily.append(
                {
                    "step": step_i,
                    "day": day,
                    "hour": hour,
                    "players": [_farm_snap((pair[p] or {}).get("observation") or {}, p) for p in (0, 1)],
                }
            )

    rewards = replay.get("rewards") or [0, 0]
    return {
        "file": filename,
        "episode": (info.get("EpisodeId") or replay.get("id")),
        "names": names,
        "rewards": rewards,
        "us_index": us_index,
        "pass_rate": [
            (pass_n[i] / unit_n[i] if unit_n[i] else 0) for i in (0, 1)
        ],
        "unit_actions": unit_n,
        "our_market": dict(market_counts[us_index]),
        "opp_market": dict(market_counts[1 - us_index]),
        "our_units": dict(unit_counts[us_index].most_common(16)),
        "opp_units": dict(unit_counts[1 - us_index].most_common(16)),
        "daily": daily,
    }


def _count_actions(act: dict[str, Any], unit: Counter, market: Counter) -> None:
    farmer = act.get("farmer")
    if isinstance(farmer, list) and farmer:
        unit[str(farmer[0])] += 1
    for hand in act.get("hands") or []:
        if isinstance(hand, list) and hand:
            unit[str(hand[0])] += 1
    for order in act.get("market") or []:
        if isinstance(order, list) and order:
            key = str(order[0])
            if key == "BUY_PRODUCT" and len(order) >= 3:
                market["BUY_PRODUCT " + str(order[1])] += int(order[2] or 0)
            elif key == "BUY_ANIMAL" and len(order) >= 2:
                market["BUY_ANIMAL " + str(order[1])] += int(order[2] if len(order) > 2 else 1)
            elif key == "BUY_SEED" and len(order) >= 2:
                market["BUY_SEED " + str(order[1])] += int(order[2] if len(order) > 2 else 1)
            else:
                market[key] += 1


def _farm_snap(obs: dict[str, Any], player: int) -> dict[str, Any]:
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    plants: Counter = Counter()
    herd: Counter = Counter()
    weeds = empty = empty_struct = 0
    for row in farm.get("tiles") or []:
        for tile in row:
            if tile == "LOCKED":
                continue
            if tile is None:
                empty += 1
                continue
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT":
                plants[tile.get("crop") or "PLANT"] += 1
            elif kind == "WEED":
                weeds += 1
            elif kind in ("COOP", "PASTURE"):
                if tile.get("animal"):
                    herd[tile.get("animal")] += 1
                else:
                    empty_struct += 1
    return {
        "money": farm.get("money"),
        "quads": farm.get("unlocked_quadrants"),
        "plants": dict(plants),
        "herd": dict(herd),
        "weeds": weeds,
        "empty": empty,
        "empty_struct": empty_struct,
        "hands": len(farm.get("hands") or []),
    }
