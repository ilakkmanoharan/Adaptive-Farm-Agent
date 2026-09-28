import time

_last_time = 0
_turn = 0
_harvest_goods = 0
_wheat = 0
_num_plots = 0
_weeds_present = False

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _harvest_goods, _wheat, _num_plots, _weeds_present
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
    _num_plots = num_plots
    _weeds_present = len(weeds) > 0

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

    if _wheat == 0 and money >= 120:
        return {"action": "BUY", "item": "wheat", "n": 3}

    if _num_plots < 4 and money >= 80:
        return {"action": "BUY", "item": "land", "n": 1}

    return {"action": "PASS"}

if __name__ == "__main__":
    for t in range(200):
        obs = {"money": 200, "inventory": {"wheat": 0, "harvest": 1}, "weeds": [], "ripe_crops": [], "num_plots": 3, "animals": 0}
        act = agent(obs)
        assert act.get("action") != "DROP"
        if act.get("action") == "BUY" and act.get("item") == "animal":
            assert False
        if act.get("action") == "BUY" and act.get("item") == "wheat":
            assert obs["money"] >= 120 and obs.get("inventory", {}).get("wheat", 0) == 0
    print("200-turn compliance OK")
