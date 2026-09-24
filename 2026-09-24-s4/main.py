import time

_last_action = None
_last_time = 0
_place_queue = []
_skip_count = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _last_time, _place_queue, _skip_count
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now

    money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    empty_tiles = obs.get("empty_tiles", []) or []
    plots = obs.get("plots", []) or []
    ripe_crops = obs.get("ripe_crops", []) or []
    shed_tiles = obs.get("shed_tiles", []) or []
    day = obs.get("day", 0)
    episode_length = obs.get("episode_length", 100)

    wheat = inventory.get("wheat_seed", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0
    chickens = inventory.get("chicken", 0) if isinstance(inventory, dict) else 0
    cows = inventory.get("cow", 0) if isinstance(inventory, dict) else 0
    animal_count = chickens + cows

    held_item = obs.get("held_item")
    market_open = obs.get("market_open", False)

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        _last_action = "PICKUP"
        _skip_count = 0
        return {"action": "PICKUP", "plot": plot_id}

    if ripe_crops:
        crop = ripe_crops[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        _last_action = "PICKUP"
        _skip_count = 0
        return {"action": "PICKUP", "plot": plot_id}

    if held_item and held_item in ("grain", "eggs", "milk"):
        if shed_tiles:
            tile_id = shed_tiles[0].get("id", 0) if isinstance(shed_tiles[0], dict) else shed_tiles[0]
            _last_action = "PLACE"
            _skip_count = 0
            return {"action": "PLACE", "item": held_item, "n": 1, "plot": tile_id}
        _last_action = "PASS"
        _skip_count += 1
        return {"action": "PASS"}

    if held_item == "wheat_seed" and empty_tiles and day < 0.8 * episode_length:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "PLACE"
        _skip_count = 0
        return {"action": "PLACE", "item": "wheat_seed", "n": 1, "plot": plot_id}

    empty_tilled = len([t for t in empty_tiles if t.get("tilled", False)]) if empty_tiles else 0
    if money >= 20 and wheat < 1 and empty_tilled >= 1:
        _last_action = "BUY"
        _skip_count = 0
        return {"action": "BUY", "item": "wheat_seed", "n": 1}

    if money >= 80 and animal_count < 1 and (grain + eggs + milk) > 0:
        _last_action = "BUY"
        _skip_count = 0
        return {"action": "BUY", "item": "chicken", "n": 1}

    if market_open and (grain + eggs + milk) > 0:
        sell_item = "grain" if grain > 0 else ("eggs" if eggs > 0 else "milk")
        _last_action = "SELL"
        _skip_count = 0
        return {"action": "SELL", "item": sell_item, "n": 1}

    if not any([weeds, ripe_crops, held_item]):
        _last_action = "PASS"
        _skip_count += 1
        if _skip_count > 3:
            _skip_count = 0
        return {"action": "PASS"}

    _last_action = "PASS"
    _skip_count = 0
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-24-s4 ready")
