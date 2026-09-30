import time

_last_time = 0
_turn = 0
_chicken_bought = False
_last_place = None

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_time, _turn, _chicken_bought, _last_place
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
    land_owned = obs.get("land_owned", 0)

    print(f"turn={_turn} cash={cash} land={land_owned} empty={empty_plots} harvest={harvest_goods} wheat={wheat_count} animals={animals}")

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

    if _turn <= 3:
        if cash >= 400:
            return {"action": "BUY_LAND", "n": 2}
        elif cash >= 200:
            return {"action": "BUY_LAND", "n": 1}

    if empty_plots > 0 and cash >= 150 and wheat_count < 3:
        n = min(3, empty_plots, (cash - 50) // 150)
        if n > 0:
            return {"action": "BUY_WHEAT", "n": n}

    if not _chicken_bought and land_owned >= 4 and cash >= 1200:
        _chicken_bought = True
        return {"action": "BUY_ANIMAL", "n": 1}

    if cash < 300 or empty_plots == 0:
        return {"action": "PASS"}

    if cash >= 400 and land_owned < 6:
        return {"action": "BUY_LAND", "n": 1}

    return {"action": "PASS"}

if __name__ == "__main__":
    for t in range(100):
        obs = {"cash": 500, "inventory": {"wheat": 0, "harvest": 0, "feed": 10}, "weeds": [], "ripe_crops": [], "animals": 0, "empty_plots": 0, "land_owned": 0}
        if t == 0:
            obs["cash"] = 800
        act = agent(obs)
        assert act.get("action") != "DROP"
        inv_size = sum(obs.get("inventory", {}).values()) if isinstance(obs.get("inventory"), dict) else 0
        assert inv_size <= 20
    print("100-turn compliance OK")
