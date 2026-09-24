import time

_last_action = None
_last_time = 0
_place_queue = []

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _last_time, _place_queue
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
    tiles_count = len(plots) if plots else 1

    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0

    harvest_items = []
    if grain > 0:
        harvest_items.append(("grain", grain))
    if eggs > 0:
        harvest_items.append(("eggs", eggs))
    if milk > 0:
        harvest_items.append(("milk", milk))

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        _last_action = "WEED"
        return {"action": "WEED", "plot": plot_id}

    if harvest_items:
        item, n = harvest_items[0]
        if item not in _place_queue:
            _place_queue.append(item)
        if _place_queue:
            place_item = _place_queue[0]
            _place_queue.pop(0)
            _last_action = "PLACE"
            return {"action": "PLACE", "item": place_item, "n": 1}

    if money >= 200 and tiles_count <= 4:
        _last_action = "BUY"
        return {"action": "BUY", "item": "land", "n": 1}

    empty_count = len(empty_tiles)
    if money >= 10 and wheat < 3 and empty_count >= 2:
        buy_n = min(3 - wheat, money // 10)
        if buy_n > 0:
            _last_action = "BUY"
            return {"action": "BUY", "item": "wheat", "n": buy_n}

    if wheat >= 1 and empty_tiles:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    if empty_tiles:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "MOVE"
        return {"action": "MOVE", "plot": plot_id}
    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        _last_action = "MOVE"
        return {"action": "MOVE", "plot": plot_id}

    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-24-s1 ready")
