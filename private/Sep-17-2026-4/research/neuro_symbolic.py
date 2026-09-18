"""Neuro-symbolic adaptive reasoner — offline intervention lab + embeddable core.

Learns farm world dynamics by intervening on policies, stores discovered
mechanisms as explicit (symbolic) rules with confidence, and plans under
uncertainty via UCB over strategy modes.

Stdlib only. Safe to import from research scripts; a compact twin lives in
the Kaggle main.py for online episode adaptation.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Symbolic mechanisms (explicit causal hypotheses)
# ---------------------------------------------------------------------------

@dataclass
class Mechanism:
    """Discovered / hypothesized causal mechanism with uncertainty."""

    name: str
    cause: str
    effect: str
    # Soft weight in [0, +inf); higher = more trusted for planning.
    weight: float = 1.0
    # Running sufficient stats for online Bayesian-ish updates.
    n: int = 0
    mean_delta: float = 0.0
    m2: float = 0.0  # Welford sum of squares of diffs from mean

    def observe(self, delta: float) -> None:
        """Update from an intervention outcome (delta bank or proxy)."""
        self.n += 1
        d = delta - self.mean_delta
        self.mean_delta += d / self.n
        self.m2 += d * (delta - self.mean_delta)
        # Confidence-weighted trust: positive mean_delta boosts weight.
        conf = self.confidence()
        self.weight = max(0.05, 0.7 * self.weight + 0.3 * (1.0 + self.mean_delta / 5000.0) * conf)

    def variance(self) -> float:
        if self.n < 2:
            return 1e6
        return self.m2 / (self.n - 1)

    def confidence(self) -> float:
        """1 / (1 + stderr) — high when tight estimates."""
        if self.n < 1:
            return 0.1
        se = math.sqrt(self.variance() / max(1, self.n))
        return 1.0 / (1.0 + se / 2000.0)

    def ucb(self, total_pulls: int, c: float = 1.4) -> float:
        """Upper confidence bound for planning under uncertainty."""
        if self.n == 0:
            return 1e9
        bonus = c * math.sqrt(math.log(max(2, total_pulls)) / self.n)
        return self.mean_delta + 5000.0 * bonus  # scale exploration in $


DEFAULT_MECHANISMS: list[Mechanism] = [
    Mechanism("dairy_compounding", "BUY_COW_EARLY", "MILK_BANK", weight=1.5),
    Mechanism("wheat_buffer", "BUY_PRODUCT_WHEAT", "HERD_YIELD", weight=1.2),
    Mechanism("second_land", "BUY_LAND_2", "HERD_CAPACITY", weight=1.1),
    Mechanism("third_land", "BUY_LAND_3", "HERD_CAPACITY", weight=0.8),
    Mechanism("care_feed", "CARE_FEED", "MILK_WOOL_UNITS", weight=1.0),
    Mechanism("strawberry_cash", "STRAWBERRY", "MIDGAME_CASH", weight=0.7),
    Mechanism("sheep_wool", "BUY_SHEEP", "WOOL_BANK", weight=0.5),
    Mechanism("placement_throughput", "PLACE_ANIMALS_FAST", "HERD_ON_TILES", weight=1.3),
]


@dataclass
class BeliefState:
    mechanisms: dict[str, Mechanism] = field(default_factory=dict)
    total_pulls: int = 0
    mode_counts: dict[str, int] = field(default_factory=dict)
    mode_rewards: dict[str, float] = field(default_factory=dict)
    last_money: float | None = None
    last_mode: str | None = None

    @classmethod
    def priors(cls) -> "BeliefState":
        return cls(mechanisms={m.name: Mechanism(**asdict(m)) for m in DEFAULT_MECHANISMS})

    def to_json(self) -> dict[str, Any]:
        return {
            "total_pulls": self.total_pulls,
            "mode_counts": self.mode_counts,
            "mode_rewards": self.mode_rewards,
            "mechanisms": {k: asdict(v) for k, v in self.mechanisms.items()},
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "BeliefState":
        mechs = {k: Mechanism(**v) for k, v in (data.get("mechanisms") or {}).items()}
        return cls(
            mechanisms=mechs or cls.priors().mechanisms,
            total_pulls=int(data.get("total_pulls") or 0),
            mode_counts=dict(data.get("mode_counts") or {}),
            mode_rewards={k: float(v) for k, v in (data.get("mode_rewards") or {}).items()},
        )


# Strategy modes = high-level policies the planner selects under uncertainty.
MODES = (
    "cow_first_dairy",      # buy cow day0, then expand dairy
    "balanced_mix",         # 2 sheep then cows (s3-like)
    "land_rush",            # unlock 3 quads ASAP + dairy
    "wheat_heavy_dairy",    # max market wheat + cows
)


def plan_mode(belief: BeliefState, day: int, hour: int, rng: random.Random | None = None) -> str:
    """Choose a strategy mode via UCB over observed mode rewards + mechanism tips."""
    rng = rng or random.Random((day * 24 + hour) ^ 0xA5A5)
    # Early episode: soft explore using mechanism priors.
    if belief.total_pulls < 3:
        # Bias toward cow_first given strong prior from offline research.
        dairy = belief.mechanisms.get("dairy_compounding")
        land = belief.mechanisms.get("third_land")
        scores = {
            "cow_first_dairy": 3.0 + (dairy.weight if dairy else 0),
            "balanced_mix": 1.5,
            "land_rush": 2.0 + (land.weight if land else 0),
            "wheat_heavy_dairy": 2.2,
        }
        # Weighted sample
        items = list(scores.items())
        weights = [max(0.01, s) for _, s in items]
        return rng.choices([k for k, _ in items], weights=weights, k=1)[0]

    best, best_score = MODES[0], -1e18
    for mode in MODES:
        n = belief.mode_counts.get(mode, 0)
        mean_r = belief.mode_rewards.get(mode, 0.0)
        if n == 0:
            score = 1e9
        else:
            bonus = 1.4 * math.sqrt(math.log(max(2, belief.total_pulls)) / n)
            score = mean_r + 8000.0 * bonus
        if score > best_score:
            best, best_score = mode, score
    return best


def observe_transition(belief: BeliefState, money: float, mode: str | None = None) -> None:
    """Online update after seeing money change (intervention outcome)."""
    if belief.last_money is not None:
        delta = money - belief.last_money
        if belief.last_mode:
            belief.total_pulls += 1
            n = belief.mode_counts.get(belief.last_mode, 0) + 1
            belief.mode_counts[belief.last_mode] = n
            prev = belief.mode_rewards.get(belief.last_mode, 0.0)
            belief.mode_rewards[belief.last_mode] = prev + (delta - prev) / n
            # Map mode → mechanisms lightly.
            mapping = {
                "cow_first_dairy": ["dairy_compounding", "placement_throughput"],
                "balanced_mix": ["sheep_wool", "dairy_compounding"],
                "land_rush": ["second_land", "third_land", "dairy_compounding"],
                "wheat_heavy_dairy": ["wheat_buffer", "dairy_compounding"],
            }
            for name in mapping.get(belief.last_mode, []):
                m = belief.mechanisms.get(name)
                if m:
                    m.observe(delta)
    belief.last_money = money
    if mode is not None:
        belief.last_mode = mode


# ---------------------------------------------------------------------------
# Offline intervention runner (local env)
# ---------------------------------------------------------------------------

def run_episode(agent_fn: Callable, seed: int) -> dict[str, Any]:
    import importlib.util
    import sys
    from pathlib import Path as P

    root = P(__file__).resolve().parents[3]
    local = root / "2026-09-12" / "_local_env"
    sys.path.insert(0, str(local))
    from run_local import _env, _obs_dict, _state, envmod

    env = _env(seed)
    state = [_state(0), _state(1)]
    envmod.interpreter(state, env)
    agents = [agent_fn, envmod.starter_agent]
    for step in range(int(env.configuration.episodeSteps)):
        if any(s.status != "ACTIVE" for s in state):
            break
        for i, s in enumerate(state):
            s.observation.step = step
            s.observation.day = step // 24
            s.observation.hour = step % 24
            s.action = agents[i](_obs_dict(s))
        envmod.interpreter(state, env)
    farm = state[0].observation.farms[0]
    tiles = farm.get("tiles") or []
    cows = sheep = 0
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("animal") == "COW":
                cows += 1
            elif t.get("animal") == "SHEEP":
                sheep += 1
    return {
        "seed": seed,
        "us": float(farm["money"]),
        "opp": float(state[0].observation.farms[1]["money"]),
        "cows": cows,
        "sheep": sheep,
        "quads": len(farm.get("unlocked_quadrants") or [0]),
        "status": [s.status for s in state],
    }


def intervene_compare(
    agents: dict[str, Callable],
    seeds: list[int],
    out_path: Path | None = None,
) -> dict[str, Any]:
    """A/B intervene: run each named agent on the same seeds; update beliefs."""
    belief = BeliefState.priors()
    results: dict[str, list] = {name: [] for name in agents}
    for seed in seeds:
        for name, fn in agents.items():
            r = run_episode(fn, seed)
            results[name].append(r)
            # Treat final bank as intervention reward for that mode label.
            m = belief.mechanisms.get("dairy_compounding")
            if m and r["cows"] >= 4:
                m.observe(r["us"] - 40000.0)
            m2 = belief.mechanisms.get("third_land")
            if m2 and r["quads"] >= 3:
                m2.observe(r["us"] - 50000.0)
            belief.mode_counts[name] = belief.mode_counts.get(name, 0) + 1
            prev = belief.mode_rewards.get(name, 0.0)
            n = belief.mode_counts[name]
            belief.mode_rewards[name] = prev + (r["us"] - prev) / n
            belief.total_pulls += 1

    summary = {
        "per_agent": {
            name: {
                "mean_us": sum(x["us"] for x in rows) / len(rows),
                "mean_cows": sum(x["cows"] for x in rows) / len(rows),
                "mean_quads": sum(x["quads"] for x in rows) / len(rows),
                "wins": sum(1 for x in rows if x["us"] > x["opp"]),
                "runs": rows,
            }
            for name, rows in results.items()
        },
        "belief": belief.to_json(),
        "recommended_mode": plan_mode(belief, day=0, hour=0, rng=random.Random(0)),
    }
    if out_path:
        out_path.write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    print("neuro_symbolic lab — import intervene_compare from research scripts")
