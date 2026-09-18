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
    inventory = obs.get("inventory", {})
    weeds = obs.get("weeds", [])
    harvest_ready = obs.get("harvest_ready", [])
    animals = obs.get("animals", 0)
    empty_tiles = obs.get("empty_tiles", [])
    wheat = inventory.get("wheat", 0)
    shed_capacity = obs.get("shed_capacity", 10)
    shed_used = sum(inventory.values()) if isinstance(inventory, dict) else 0
    free_plot = len(empty_tiles) > 0
    seeds = wheat

    if weeds:
        return {"action": "REMOVE"}
    if harvest_ready:
        n = harvest_ready[0] if harvest_ready else 1
        return {"action": ["PLACE", n]}
    if animals == 0 and money >= 50:
        return {"action": "BUY_ANIMAL"}
    if animals > 0 and inventory.get("feed", 0) > 0:
        return {"action": "FEED"}
    if seeds == 0 and money >= 10:
        return {"action": "BUY_WHEAT"}
    if free_plot and seeds >= 1:
        return {"action": "PLANT"}
    if money >= 10:
        return {"action": "BUY_WHEAT"}
    return {"action": "PASS"}

def _run_test():
    buy_animal_count = 0
    plant_count = 0
    for turn in range(100):
        obs = {
            "turn": turn + 1,
            "money": 150 if turn < 5 else (90 if turn == 20 else 50),
            "inventory": {"wheat": 0, "feed": 5} if turn == 15 else {"wheat": 3, "feed": 5},
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
            if a == "BUY_ANIMAL":
                if obs["animals"] >= 1:
                    return False
                buy_animal_count += 1
            if a == "BUY_WHEAT" and (obs["inventory"].get("wheat", 0) >= 1 or len(obs.get("empty_tiles", [])) == 0):
                pass
            if a == "PLANT":
                plant_count += 1
    return buy_animal_count == 1 and plant_count >= 2

if __name__ == "__main__":
    print(_run_test())
