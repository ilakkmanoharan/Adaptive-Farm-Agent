"""Minimal official-env harness for local first-submission tests."""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

spec = importlib.util.spec_from_file_location("kaggriculture_env", os.path.join(HERE, "kaggriculture.py"))
envmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(envmod)

from main import agent  # noqa: E402


def _obs(player):
    o = SimpleNamespace()
    o.player = player
    o.farms = []
    o.private = {}
    o.market = {}
    o.town = {}
    o.day = 0
    o.hour = 0
    o.step = 0
    return o


def _state(player):
    s = SimpleNamespace()
    s.observation = _obs(player)
    s.action = {"farmer": ["PASS"], "hands": [], "market": []}
    s.status = "ACTIVE"
    s.reward = 0.0
    return s


def _cfg(**kwargs):
    defaults = dict(
        episodeSteps=720,
        boardSize=10,
        startingMoney=3000,
        maxMarketOrdersPerTurn=10,
        turnsPerDay=24,
        shedCapacity=100,
        weedSpawnChance=0.005,
        townShopUnlockInterval=3,
        townShopSellInterval=4,
        townCenterSellInterval=24,
        seed=None,
        farmHandCostMult=1,
        marketParams={},
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _env(seed=None):
    e = SimpleNamespace()
    e.configuration = _cfg(seed=seed)
    e.done = False
    e.info = {}
    return e


def _obs_dict(s):
    o = s.observation
    return {
        "player": o.player,
        "day": getattr(o, "day", 0),
        "hour": getattr(o, "hour", 0),
        "step": getattr(o, "step", 0),
        "farms": o.farms,
        "market": o.market,
        "town": o.town,
        "private": o.private,
    }


def run_episode(agent0, agent1, seed=1, debug=False):
    env = _env(seed)
    state = [_state(0), _state(1)]
    envmod.interpreter(state, env)
    state[0].observation.step = 0
    state[1].observation.step = 0

    agents = [agent0, agent1]
    for step in range(int(env.configuration.episodeSteps)):
        if any(s.status != "ACTIVE" for s in state):
            break
        for i, s in enumerate(state):
            s.observation.step = step
            s.observation.day = step // 24
            s.observation.hour = step % 24
            s.action = agents[i](_obs_dict(s))
        envmod.interpreter(state, env)
        nxt = step + 1
        state[0].observation.step = nxt
        state[1].observation.step = nxt

    banks = [float(state[0].observation.farms[i]["money"]) for i in range(2)]
    statuses = [s.status for s in state]
    return banks, statuses


def load_named(name):
    if name == "us":
        return agent
    if name == "starter":
        return envmod.starter_agent
    if name == "random":
        return envmod.random_agent
    if name == "pass":
        return envmod.pass_agent
    raise SystemExit("unknown agent %s" % name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--opp", default="starter")
    p.add_argument("--seeds", type=int, default=2)
    p.add_argument("--seat", default="both", choices=("0", "1", "both"))
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()
    if args.debug:
        os.environ["KAGG_DEBUG"] = "1"

    wins = ties = losses = crashes = 0
    margins = []
    seats = (0, 1) if args.seat == "both" else (int(args.seat),)
    for seed in range(args.seeds):
        for seat in seats:
            us = load_named("us")
            opp = load_named(args.opp)
            pair = [us, opp] if seat == 0 else [opp, us]
            try:
                banks, statuses = run_episode(pair[0], pair[1], seed=1000 + seed * 10 + seat, debug=args.debug)
            except Exception as exc:
                crashes += 1
                print("CRASH seed=%s seat=%s %s" % (seed, seat, exc))
                if args.debug:
                    raise
                continue
            ours = banks[seat]
            theirs = banks[1 - seat]
            margins.append(ours - theirs)
            if ours > theirs:
                wins += 1
            elif ours < theirs:
                losses += 1
            else:
                ties += 1
            print(
                "seed=%s seat=%s us=%.0f opp=%.0f margin=%+.0f status=%s"
                % (seed, seat, ours, theirs, ours - theirs, statuses)
            )
    n = max(1, wins + ties + losses)
    print(
        "vs %s  W-T-L %s-%s-%s  win=%.0f%%  mean_margin=%+.0f  crashes=%s"
        % (args.opp, wins, ties, losses, 100.0 * wins / n, (sum(margins) / len(margins) if margins else 0), crashes)
    )


if __name__ == "__main__":
    main()
