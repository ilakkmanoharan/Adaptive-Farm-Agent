import time

_last_time = 0
_turn = 0
_animals = 0
_harvest_goods = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _animals, _harvest_goods
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now
    _turn += 1

    money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    ripe_crops = obs.get("ripe_crops", []) or []
    num_plots = obs.get("num_plots", 0)
    animals = obs.get("animals", _animals)
    _animals = animals
    goods = sum(inventory.values()) if isinstance(inventory, dict) else 0
    if goods > 0:
        _harvest_goods = goods

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "WEED", "plot": plot_id}

    if ripe_crops:
        crop = ripe_crops[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        return {"action": "HARVEST", "plot": plot_id}

    if _harvest_goods > 0:
        n = _harvest_goods
        _harvest_goods = 0
        return {"action": "PLACE", "item": "harvest", "n": n}

    if money >= 120 and animals < 4:
        _animals += 1
        return {"action": "BUY", "item": "animal", "n": 1}

    if money >= 80 and num_plots < 6:
        return {"action": "BUY", "item": "land", "n": 1}

    if money < 50 and animals >= 3 and _harvest_goods == 0:
        return {"action": "PASS"}

    return {"action": "PASS"}
