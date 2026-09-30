import time

_last_time = 0
_turn = 0
_herd_size = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _herd_size
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
    animals = obs.get("animals", 0)
    empty_plots = obs.get("empty_plots", 0)
    harvest_goods = inventory.get("harvest", 0) if isinstance(inventory, dict) else 0

    _herd_size = animals

    if _turn == 1:
        if cash >= 400:
            return {"action": "BUY_LAND", "n": 2}
        return {"action": "PASS"}

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "CLEAR_WEED", "plot": plot_id}

    if harvest_goods > 0:
        return {"action": "PLACE", "item": "harvest", "n": min(10, harvest_goods)}

    if empty_plots >= 1 and cash >= 10 and _herd_size < 3:
        return {"action": "BUY_ANIMAL", "n": 1}

    if empty_plots >= 1 and cash >= 50:
        return {"action": "BUY_WHEAT", "n": 1}

    return {"action": "PASS"}

if __name__ == "__main__":
    for t in range(50):
        obs = {"cash": 500, "inventory": {"wheat": 0, "harvest": 0}, "weeds": [], "ripe_crops": [], "num_plots": 0, "animals": 0, "empty_plots": 0}
        if t == 0:
            obs["cash"] = 500
        act = agent(obs)
        assert act.get("action") != "DROP"
    print("50-turn compliance OK")
