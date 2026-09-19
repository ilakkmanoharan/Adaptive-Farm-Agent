import sys
import random

_last_action = None

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return _safe_pass(obs)

def _safe_pass(obs):
    return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action
    money = obs.get("money", 0)
    inventory = obs.get("inventory", {})
    weeds = obs.get("weeds", [])
    harvest_ready = obs.get("harvest_ready", [])
    empty_tiles = obs.get("empty_tiles", [])
    shed_capacity = obs.get("shed_capacity", 10)
    shed_used = sum(inventory.values()) if isinstance(inventory, dict) else 0
    seeds = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    goods = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    wheat_cost = 10

    if weeds:
        _last_action = "WEED"
        return {"action": "WEED"}
    if harvest_ready:
        _last_action = "HARVEST"
        return {"action": "HARVEST"}
    if goods > 0:
        n = min(goods, shed_capacity - shed_used)
        if n > 0:
            _last_action = "PLACE"
            return {"action": "PLACE", "item": "grain", "n": n}
    if len(empty_tiles) > 0 and seeds > 0:
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat"}
    if len(empty_tiles) > 0 and seeds == 0 and money >= wheat_cost:
        buy_n = min(3, max(1, (money // wheat_cost)))
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": buy_n}
    if _last_action == "PLACE":
        _last_action = "WAIT"
        return {"action": "WAIT"}
    _last_action = "WAIT"
    return {"action": "WAIT"}

def _run_test():
    place_count = 0
    for turn in range(10):
        obs = {
            "turn": turn + 1,
            "money": 100,
            "inventory": {"wheat": 3, "grain": 2},
            "weeds": [],
            "harvest_ready": [],
            "empty_tiles": [0, 1, 2],
            "shed_capacity": 10,
        }
        act = agent(obs)
        if isinstance(act, dict):
            a = act.get("action")
            if a == "DROP" or (isinstance(a, list) and "DROP" in a):
                return False
            if a == "PLACE":
                place_count += 1
    return place_count >= 1

if __name__ == "__main__":
    print(_run_test())
