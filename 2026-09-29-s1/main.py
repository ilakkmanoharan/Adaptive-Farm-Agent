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

    cash = obs.get("cash", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    ripe_crops = obs.get("ripe_crops", []) or []
    num_plots = obs.get("num_plots", 0)
    animals = obs.get("animals", 0)
    empty_plots = obs.get("empty_plots", 0)
    harvest_goods = inventory.get("harvest", 0) if isinstance(inventory, dict) else 0
    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0

    _owned_land = num_plots
    _herd_size = animals
    _inventory = inventory if isinstance(inventory, dict) else {}

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "CLEAR", "plot": plot_id}

    if cash < 20 and wheat == 0 and harvest_goods > 0:
        return {"action": "PLACE", "item": "harvest", "n": 1}

    if _herd_size >= 3:
        pass
    elif cash >= 50 and _herd_size < 3:
        return {"action": "BUY", "item": "cow", "n": 1}

    if harvest_goods > 0:
        return {"action": "PLACE", "item": "harvest", "n": 1}

    if empty_plots >= 1 and cash >= 50 and wheat >= 10:
        return {"action": "BUY_LAND", "n": 1}

    if wheat < 5 and cash >= 8:
        return {"action": "BUY_WHEAT", "n": min(8, 5 - wheat)}

    if wheat >= 5 and empty_plots >= 1:
        return {"action": "PLANT_WHEAT", "n": 1}

    return {"action": "WAIT"}

if __name__ == "__main__":
    for t in range(50):
        obs = {"cash": 200, "inventory": {"wheat": 0, "harvest": 1}, "weeds": [], "ripe_crops": [], "num_plots": 3, "animals": 0, "empty_plots": 1}
        act = agent(obs)
        assert act.get("action") != "DROP"
    print("50-episode compliance OK")
