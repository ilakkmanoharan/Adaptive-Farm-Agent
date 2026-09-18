import sys
import random

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return _safe_pass(obs)

def _safe_pass(obs):
    return {"action": "PASS"}

def _agent_impl(obs, config=None):
    money = obs.get("money", 0)
    owned_land = obs.get("owned_land", [])
    inventory = obs.get("inventory", {})
    weeds = obs.get("weeds", [])
    harvest_ready = obs.get("harvest_ready", [])
    animals = obs.get("animals", 0)
    empty_tiles = obs.get("empty_tiles", [])
    shed_capacity = obs.get("shed_capacity", 10)
    shed_used = sum(inventory.values()) if isinstance(inventory, dict) else 0

    if money >= 120 and len(owned_land) <= 3:
        return {"action": "BUY_LAND"}
    if weeds:
        return {"action": "WEED"}
    if harvest_ready:
        if shed_used >= shed_capacity:
            return {"action": ["PICKUP", "PLACE", 1]}
        return {"action": "PICKUP"}
    if animals < 2 and money >= 80:
        return {"action": "BUY_CHICKEN"}
    if empty_tiles and inventory.get("wheat", 0) > 0:
        return {"action": "PLANT_WHEAT"}
    if inventory.get("wheat", 0) == 0 and empty_tiles and len(owned_land) > 0:
        return {"action": "BUY_WHEAT"}
    return {"action": "PASS"}

def _run_test():
    for turn in range(50):
        obs = {
            "turn": turn + 1,
            "money": 150 if turn == 5 else (90 if turn == 20 else 50),
            "owned_land": [0, 1] if turn < 10 else [0, 1, 2, 3],
            "inventory": {"wheat": 0} if turn == 15 else {"wheat": 3},
            "weeds": [3] if turn == 8 else [],
            "harvest_ready": [1] if turn == 25 else [],
            "animals": 1 if turn > 30 else 0,
            "empty_tiles": [4] if turn % 3 == 0 else [],
            "shed_capacity": 5,
        }
        act = agent(obs)
        if isinstance(act, dict):
            a = act.get("action")
            if a == "DROP" or (isinstance(a, list) and "DROP" in a):
                return False
            if a == "BUY_CHICKEN" and obs["animals"] >= 2:
                return False
    return True

if __name__ == "__main__":
    _run_test()
