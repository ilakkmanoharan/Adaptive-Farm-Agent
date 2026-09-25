import time

_last_time = 0
_animal_buys = 0
_skip_count = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _animal_buys, _skip_count
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
    episode_length = obs.get("episode_length", 100)
    market_open = obs.get("market_open", False)

    wheat = inventory.get("wheat_seed", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0
    chickens = inventory.get("chicken", 0) if isinstance(inventory, dict) else 0
    cows = inventory.get("cow", 0) if isinstance(inventory, dict) else 0
    animal_count = chickens + cows
    harvest_goods = grain + eggs + milk

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        _skip_count = 0
        return {"action": "WEED", "plot": plot_id}

    if ripe_crops:
        crop = ripe_crops[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        _skip_count = 0
        return {"action": "PICKUP", "plot": plot_id}

    if harvest_goods > 0 and shed_tiles:
        item = "grain" if grain > 0 else ("eggs" if eggs > 0 else "milk")
        tile_id = shed_tiles[0].get("id", 0) if isinstance(shed_tiles[0], dict) else shed_tiles[0]
        n = inventory.get(item, 1)
        _skip_count = 0
        return {"action": "PLACE", "item": item, "n": n, "plot": tile_id}

    if wheat > 0 and empty_tiles and day < 0.8 * episode_length:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _skip_count = 0
        return {"action": "PLACE", "item": "wheat_seed", "n": 1, "plot": plot_id}

    if money >= 120 and wheat >= 8 and len(empty_tiles) < 3:
        _skip_count = 0
        return {"action": "TILL"}

    if money >= 30 and wheat == 0 and len(empty_tiles) > 0 and day < 0.8 * episode_length:
        _skip_count = 0
        return {"action": "BUY", "item": "wheat_seed", "n": 1}

    if money >= 200 and animal_count < 4 and _animal_buys < 4 and harvest_goods >= 3:
        _animal_buys += 1
        _skip_count = 0
        return {"action": "BUY", "item": "chicken", "n": 1}

    if market_open and harvest_goods > 0:
        item = "grain" if grain > 0 else ("eggs" if eggs > 0 else "milk")
        _skip_count = 0
        return {"action": "SELL", "item": item, "n": harvest_goods}

    _skip_count += 1
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-25-s2 ready")
