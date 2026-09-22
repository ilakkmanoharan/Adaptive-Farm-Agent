import time

_last_action = None
_turn = 0
_last_time = 0
_last_expand_turn = -6
_money = 0
_wheat = 0
_feed = 0
_cows = 0
_chickens = 0
_grain = 0
_eggs = 0
_milk = 0
_owned_land = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _turn, _last_time, _last_expand_turn, _money, _wheat, _feed, _cows, _chickens, _grain, _eggs, _milk, _owned_land
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
    _wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    _feed = inventory.get("feed", 0) if isinstance(inventory, dict) else 0
    _grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    _eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    _milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0
    _cows = obs.get("cows", 0)
    _chickens = obs.get("chickens", 0)
    _owned_land = len(empty_tiles) if empty_tiles else 0

    if weeds:
        weed_plot = max(weeds, key=lambda w: w.get("weed_level", 0) if isinstance(w, dict) else 0)
        plot_id = weed_plot.get("id", 0) if isinstance(weed_plot, dict) else weed_plot
        _last_action = "CLEAR"
        return {"action": "CLEAR", "plot": plot_id}

    harvest_goods = []
    if _grain > 0: harvest_goods.append(("grain", _grain))
    if _eggs > 0: harvest_goods.append(("eggs", _eggs))
    if _milk > 0: harvest_goods.append(("milk", _milk))
    if harvest_goods:
        item, qty = harvest_goods[0]
        _last_action = "PLACE"
        return {"action": "PLACE", "item": item, "n": 1}

    if _money >= 12 and _wheat < 8 and not harvest_ready:
        buy_n = min(4, 8 - _wheat)
        if buy_n > 0:
            _last_action = "BUY"
            return {"action": "BUY", "item": "wheat", "n": buy_n}

    if _money >= 25 and _cows < 3 and _feed >= 4:
        _last_action = "BUY"
        return {"action": "BUY", "item": "cow", "n": 1}

    if _money >= 15 and _chickens < 5 and _feed >= 3:
        _last_action = "BUY"
        return {"action": "BUY", "item": "chicken", "n": 1}

    if harvest_ready:
        plot_id = harvest_ready[0].get("id", 0) if isinstance(harvest_ready[0], dict) else harvest_ready[0]
        _last_action = "HARVEST"
        return {"action": "HARVEST", "plot": plot_id}

    if empty_tiles and _wheat >= 1:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    if _money >= 40 and _owned_land < 12 and (_turn - _last_expand_turn) >= 6:
        _last_expand_turn = _turn
        _last_action = "EXPAND"
        return {"action": "EXPAND", "n": 1}

    if _feed < 3 and _money >= 6:
        _last_action = "BUY"
        return {"action": "BUY", "item": "feed", "n": 6}

    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture s3 ready")
