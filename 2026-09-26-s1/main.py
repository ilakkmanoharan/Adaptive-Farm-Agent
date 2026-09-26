import time

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
    day = obs.get("day", 0)

    wheat_seed = inventory.get("wheat_seed", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "WEED", "plot": plot_id}

    if wheat_seed >= 1 and empty_tiles:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        return {"action": "PLACE", "item": "wheat_seed", "n": 1, "plot": plot_id}

    if grain > 0 and shed_tiles:
        tile_id = shed_tiles[0].get("id", 0) if isinstance(shed_tiles[0], dict) else shed_tiles[0]
        n = grain
        return {"action": "PLACE", "item": "grain", "n": n, "plot": tile_id}

    if grain > 0:
        return {"action": "SELL", "item": "grain", "n": grain}

    if money >= 50 and wheat_seed < 10 and day < 3:
        return {"action": "BUY", "item": "wheat_seed", "n": 10}

    if money >= 50 and wheat_seed == 0:
        return {"action": "BUY", "item": "wheat_seed", "n": 10}

    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-26-s1 ready")
