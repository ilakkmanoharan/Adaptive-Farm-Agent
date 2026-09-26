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
    animals = obs.get("animals", []) or []
    day = obs.get("day", 0)
    eggs = inventory.get("egg", 0) if isinstance(inventory, dict) else 0
    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "WEED", "plot": plot_id}

    if ripe_crops:
        crop = ripe_crops[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        return {"action": "HARVEST", "plot": plot_id}

    if day == 0:
        if money >= 120:
            return {"action": "BUY", "item": "chicken", "n": 2}
        if money >= 50:
            return {"action": "BUY", "item": "wheat", "n": 10}

    if wheat > 0 and empty_tiles:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        n = min(5, wheat)
        return {"action": "PLANT", "item": "wheat", "n": n, "plot": plot_id}

    if eggs > 0 and shed_tiles:
        tile_id = shed_tiles[0].get("id", 0) if isinstance(shed_tiles[0], dict) else shed_tiles[0]
        return {"action": "PLACE", "item": "egg", "n": eggs, "plot": tile_id}

    if money >= 300:
        return {"action": "BUY", "item": "cow", "n": 1}

    if money >= 100 and len(animals) < 3:
        return {"action": "BUY", "item": "chicken", "n": 1}

    if money >= 50 and wheat < 5:
        return {"action": "BUY", "item": "wheat", "n": 5}

    if money < 50 and eggs == 0 and wheat == 0:
        return {"action": "IDLE"}

    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-26-s3 ready")
