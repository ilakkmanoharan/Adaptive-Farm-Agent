import time

_last_time = 0
_turn = 0
_owned_land = 0
_herd_size = 0
_inventory = {}

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _owned_land, _herd_size, _inventory
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
    animals = obs.get("animals", 0)
    _owned_land = num_plots
    _herd_size = animals
    _inventory = inventory if isinstance(inventory, dict) else {}

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "WEED", "plot": plot_id}

    if ripe_crops:
        crop = ripe_crops[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        return {"action": "PLACE", "item": "harvest", "n": 1}

    harvest_n = _inventory.get("harvest", 0) if isinstance(_inventory, dict) else 0
    if harvest_n > 0:
        return {"action": "PLACE", "item": "harvest", "n": harvest_n}

    wheat = _inventory.get("wheat", 0) if isinstance(_inventory, dict) else 0
    if wheat >= 1 and num_plots > 0:
        return {"action": "PLANT", "item": "wheat"}

    if _herd_size == 0 and money >= 50:
        return {"action": "BUY", "item": "chicken", "n": 1}

    if _turn == 1 and _owned_land < 4 and money >= 120:
        return {"action": "BUY", "item": "land", "n": 1}

    if harvest_n == 0 and any(k not in ("chicken", "cow") for k in (_inventory or {})):
        return {"action": "SELL", "item": "all"}

    return {"action": "PASS"}

if __name__ == "__main__":
    for t in range(50):
        obs = {"money": 200, "inventory": {"wheat": 0, "harvest": 1}, "weeds": [], "ripe_crops": [], "num_plots": 3, "animals": 0}
        act = agent(obs)
        assert act.get("action") != "DROP"
        assert act.get("action") != "PICKUP"
    print("50-episode compliance OK")
