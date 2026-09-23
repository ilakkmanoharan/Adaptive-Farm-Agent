import time

_last_action = None
_last_time = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _last_time
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now

    money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    empty_tiles = obs.get("empty_tiles", []) or []
    harvest_ready = obs.get("harvest_ready", []) or []

    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0
    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0

    if weeds:
        weed_plot = max(weeds, key=lambda w: w.get("weed_level", 0) if isinstance(w, dict) else 0)
        plot_id = weed_plot.get("id", 0) if isinstance(weed_plot, dict) else weed_plot
        _last_action = "CLEAR"
        return {"action": "CLEAR", "plot": plot_id}

    harvest_goods = []
    if grain > 0: harvest_goods.append(("grain", grain))
    if eggs > 0: harvest_goods.append(("eggs", eggs))
    if milk > 0: harvest_goods.append(("milk", milk))
    if harvest_goods:
        item, qty = harvest_goods[0]
        _last_action = "PLACE"
        return {"action": "PLACE", "item": item, "n": qty}

    if empty_tiles and wheat >= 1:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    if money >= 12 and wheat < 1 and empty_tiles:
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": 1}

    if not empty_tiles and money >= 150:
        _last_action = "EXPAND"
        return {"action": "EXPAND", "n": 1}

    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture s5 ready")
