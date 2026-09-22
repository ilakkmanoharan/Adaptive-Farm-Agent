import time

_last_action = None
_turn = 0
_last_time = 0
_money = 0
_wheat_seeds = 0
_owned_land = 0
_grain = 0
_animals = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _turn, _last_time, _money, _wheat_seeds, _owned_land, _grain, _animals
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now
    _turn = obs.get("turn", 0)
    _money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    harvest_ready = obs.get("harvest_ready", []) or []
    empty_tiles = obs.get("empty_tiles", []) or []
    animals_list = obs.get("animals", []) or []
    plots = obs.get("plots", []) or []
    _wheat_seeds = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    _grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    _owned_land = len(empty_tiles) if empty_tiles else 0
    _animals = len(animals_list) if animals_list else 0
    tilled_empty = len([t for t in empty_tiles if isinstance(t, dict) and t.get("tilled", False)]) if empty_tiles else 0

    if _grain > 0:
        _last_action = "PLACE"
        return {"action": "PLACE", "item": "grain", "n": _grain}

    if harvest_ready:
        _last_action = "PLACE"
        return {"action": "PLACE", "item": "grain", "n": 1}

    if weeds:
        weed_plot = max(weeds, key=lambda w: w.get("weed_level", 0) if isinstance(w, dict) else 0)
        plot_id = weed_plot.get("id", 0) if isinstance(weed_plot, dict) else weed_plot
        _last_action = "WEED"
        return {"action": "WEED", "plot": plot_id}

    if _animals >= 2:
        pass
    elif _animals < 2 and _money >= 50:
        _last_action = "BUY"
        return {"action": "BUY", "item": "animal", "n": 1}

    if _money >= 120 and len(empty_tiles) >= 2 and _wheat_seeds >= 4:
        _last_action = "BUY"
        return {"action": "BUY", "item": "land", "n": 1}

    if _money >= 80 and _wheat_seeds < 6 and len(empty_tiles) > 0 and not weeds:
        buy_n = min(5, 10 - _wheat_seeds)
        if buy_n > 0:
            _last_action = "BUY"
            return {"action": "BUY", "item": "wheat", "n": buy_n}

    if _grain == 0 and len(inventory) > 0 and _money < 40:
        for item, qty in inventory.items():
            if item != "wheat" and qty > 0:
                _last_action = "SELL"
                return {"action": "SELL", "item": item, "n": qty}

    if empty_tiles and _wheat_seeds >= 1:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else 0
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    if _money >= 20 and _wheat_seeds < 5:
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": 1}

    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture s5 ready")
