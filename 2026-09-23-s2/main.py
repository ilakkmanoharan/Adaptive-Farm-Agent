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
    animals = obs.get("animals", []) or []

    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0

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

    free_plots = len(empty_tiles)
    if money >= 50 and len(animals) == 0:
        _last_action = "BUY"
        return {"action": "BUY", "item": "chicken", "n": 1}

    if money >= 10 and wheat == 0 and free_plots > 0:
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": 1}

    if wheat >= 1 and free_plots > 0:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-23-s2 ready")
