import time
import copy

_last_time = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now

    money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    empty_tiles = obs.get("empty_tiles", []) or []
    ripe_crops = obs.get("ripe_crops", []) or []
    shed_tiles = obs.get("shed_tiles", []) or []
    animals = obs.get("animals", 0)
    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    harvest_goods = []
    for k in ["egg", "tomato", "corn"]:
        if inventory.get(k, 0) > 0:
            harvest_goods.append((k, inventory[k]))

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "PLOW", "plot": plot_id}

    if wheat == 0 and len(empty_tiles) > 0:
        return {"action": "BUY", "item": "wheat", "n": 1}

    if harvest_goods and shed_tiles:
        item, n = harvest_goods[0]
        tile_id = shed_tiles[0].get("id", 0) if isinstance(shed_tiles[0], dict) else shed_tiles[0]
        return {"action": "PLACE", "item": item, "n": n, "plot": tile_id}

    if wheat > 0 and empty_tiles:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        n = min(wheat, 5)
        return {"action": "PLANT", "item": "wheat", "n": n, "plot": plot_id}

    if animals >= 3 and money >= 5:
        return {"action": "HIRE", "item": "worker"}

    if money >= 8 and len(empty_tiles) >= 2:
        return {"action": "BUY", "item": "wheat", "n": 2}

    return {"action": "PASS"}

def run_test_harness():
    obs = {
        "money": 20,
        "inventory": {"wheat": 0, "egg": 0},
        "weeds": [],
        "empty_tiles": [{"id": 1}, {"id": 2}],
        "ripe_crops": [],
        "shed_tiles": [{"id": 10}],
        "animals": 0,
        "day": 0,
        "num_plots": 2
    }
    placed = 0
    for turn in range(50):
        action = agent(obs)
        if action.get("action") == "PLACE":
            placed += action.get("n", 0)
            obs["inventory"]["egg"] = 0
        elif action.get("action") == "BUY":
            if action.get("item") == "wheat":
                obs["inventory"]["wheat"] = obs["inventory"].get("wheat", 0) + action.get("n", 1)
                obs["money"] -= 2 * action.get("n", 1)
        elif action.get("action") == "PLANT":
            obs["inventory"]["wheat"] = max(0, obs["inventory"].get("wheat", 0) - action.get("n", 0))
            if obs["empty_tiles"]:
                obs["empty_tiles"].pop(0)
                obs["ripe_crops"].append({"id": 99})
        elif action.get("action") == "PLOW":
            if obs["weeds"]:
                obs["weeds"].pop(0)
        elif action.get("action") == "HIRE":
            obs["animals"] = 0
        if turn % 5 == 0 and obs["empty_tiles"]:
            obs["weeds"].append({"id": 99})
        if turn % 7 == 0:
            obs["animals"] += 1
        if turn % 4 == 0 and obs["ripe_crops"]:
            obs["ripe_crops"].pop(0)
            obs["inventory"]["egg"] = obs["inventory"].get("egg", 0) + 1
    print("Final sellable inventory:", obs.get("inventory", {}))
    print("Placed harvest goods:", placed)

if __name__ == "__main__":
    run_test_harness()
