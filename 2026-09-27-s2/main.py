import time

_last_time = 0
_harvested_wheat = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _harvested_wheat
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
    num_plots = obs.get("num_plots", 0)
    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    land_count = num_plots

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "WEED", "plot": plot_id}

    if ripe_crops:
        crop = ripe_crops[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        _harvested_wheat += 1
        return {"action": "HARVEST", "plot": plot_id}

    if _harvested_wheat > 0:
        n = _harvested_wheat
        _harvested_wheat = 0
        return {"action": "PLACE", "item": "wheat", "n": n}

    if wheat >= 1 and empty_tiles:
        plot = empty_tiles[0]
        plot_id = plot.get("id", 0) if isinstance(plot, dict) else plot
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    if money >= 200 and land_count < 3:
        return {"action": "BUY", "item": "land", "n": 1}

    if money >= 10 and wheat < 5 and land_count > 0:
        return {"action": "BUY", "item": "wheat", "n": 1}

    return {"action": "PASS"}
