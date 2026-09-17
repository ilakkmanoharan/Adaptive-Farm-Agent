import collections
import json

def safe_pass(obs):
    try:
        farms = obs.get("farms", [])
        player = int(obs.get("player", 0) or 0)
        me = farms[player] if player < len(farms) else {}
        n_hands = len(me.get("hands", []))
    except Exception:
        n_hands = 0
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(n_hands)], "market": []}

def agent(obs, config=None):
    try:
        farms = obs.get("farms", [])
        player = int(obs.get("player", 0) or 0)
        me = farms[player] if player < len(farms) else {}
        cash = int(me.get("cash", 0) or 0)
        land = me.get("land", [])
        land_count = len([t for t in land if t and t.get("kind") != "WEED"])
        inv = me.get("inventory", {})
        harvest_goods = {k: v for k, v in inv.items() if k in ("WHEAT", "MELON", "STRAWBERRY") and v > 0}
        acts = []
        if harvest_goods:
            item = next(iter(harvest_goods))
            n = min(harvest_goods[item], 5)
            acts.append(["PLACE", item, n])
        elif cash >= 10 and land_count < 3:
            acts.append(["BUY_SEED", "WHEAT", 1])
        elif any(t and t.get("kind") == "WEED" for t in land):
            acts.append(["DIG"])
        else:
            acts.append(["PASS"])
        farmer_act = acts[0] if acts else ["PASS"]
        n_hands = len(me.get("hands", []))
        hand_acts = [["PASS"] for _ in range(n_hands)]
        return {"farmer": farmer_act, "hands": hand_acts, "market": []}
    except Exception:
        return safe_pass(obs)
