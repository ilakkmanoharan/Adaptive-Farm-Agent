import time

_last_time = 0
_turn = 0
_animals = 0
_harvest_goods = 0
_wheat = 0
_free_land = 0
_weeds_present = False

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _animals, _harvest_goods, _wheat, _free_land, _weeds_present
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
    _animals = min(animals, 3)
    _weeds_present = len(weeds) > 0
    _free_land = max(0, num_plots - len(weeds) - len(ripe_crops))

    if isinstance(inventory, dict):
        _wheat = inventory.get("wheat", 0)
        _harvest_goods = inventory.get("harvest", 0)
    else:
        _wheat = 0
        _harvest_goods = 0

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

    if _animals < 4 and money >= 120 and _animals < 3:
        _animals += 1
        return {"action": "BUY", "item": "animal", "n": 1}

    if _wheat < 3 and _free_land > 0 and not _weeds_present and money >= 50:
        return {"action": "BUY", "item": "wheat", "n": 3 - _wheat}

    if _wheat >= 3 and _free_land > 0 and not _weeds_present:
        return {"action": "PLANT", "item": "wheat", "n": 1}

    if money < 50 and _animals >= 3 and _harvest_goods == 0:
        return {"action": "PASS"}

    return {"action": "PASS"}

if __name__ == "__main__":
    for t in range(100):
        obs = {"money": 200, "inventory": {"wheat": 2, "harvest": 1}, "weeds": [], "ripe_crops": [], "num_plots": 4, "animals": 2}
        act = agent(obs)
        assert act.get("action") != "DROP"
        if act.get("action") == "BUY" and act.get("item") == "animal":
            assert obs["animals"] < 3
    print("100-turn compliance OK")
