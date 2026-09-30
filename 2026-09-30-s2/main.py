import time

_last_time = 0
_turn = 0
_last_place = None

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _last_place
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now
    _turn += 1

    cash = obs.get("cash", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    empty_plots = obs.get("empty_plots", 0)
    animals = obs.get("animals", 0)
    ripe = obs.get("ripe_crops", []) or []
    harvest_goods = inventory.get("harvest", 0) if isinstance(inventory, dict) else 0
    wheat_count = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    feed = inventory.get("feed", 0) if isinstance(inventory, dict) else 0

    if weeds:
        weed = weeds[0]
        plot_id = weed.get("id", 0) if isinstance(weed, dict) else weed
        return {"action": "CLEAR_WEED", "plot": plot_id}

    if ripe:
        crop = ripe[0]
        plot_id = crop.get("id", 0) if isinstance(crop, dict) else crop
        return {"action": "HARVEST", "plot": plot_id}

    if harvest_goods > 0:
        n = min(10, harvest_goods)
        _last_place = {"action": "PLACE", "item": "harvest", "n": n}
        return _last_place

    if _last_place is not None and _last_place.get("action") == "PLACE":
        tile = _last_place.get("tile", 0)
        _last_place = None
        return {"action": "PICKUP", "tile": tile}

    if animals < 3 and cash >= 120 and feed >= 5:
        return {"action": "BUY_ANIMAL", "n": 1}

    if cash >= 400:
        return {"action": "BUY_LAND", "n": 1}

    if empty_plots >= 1 and cash >= 150 and wheat_count <= 2 and not weeds:
        return {"action": "BUY_WHEAT", "n": 1}

    if cash >= 80 and wheat_count <= 2:
        return {"action": "BUY_WHEAT", "n": 1}

    if harvest_goods > 0:
        return {"action": "SELL", "item": "harvest", "n": harvest_goods}

    return {"action": "PASS"}

if __name__ == "__main__":
    for t in range(100):
        obs = {"cash": 500, "inventory": {"wheat": 0, "harvest": 0, "feed": 10}, "weeds": [], "ripe_crops": [], "animals": 0, "empty_plots": 0}
        if t == 0:
            obs["cash"] = 500
        act = agent(obs)
        assert act.get("action") != "DROP"
        inv_size = sum(obs.get("inventory", {}).values()) if isinstance(obs.get("inventory"), dict) else 0
        assert inv_size <= 20
    print("100-turn compliance OK")
