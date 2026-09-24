import time

_last_action = None
_last_time = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _last_time
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now

    money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    empty_tiles = obs.get("empty_tiles", []) or []
    plots = obs.get("plots", []) or []

    wheat = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    eggs = inventory.get("eggs", 0) if isinstance(inventory, dict) else 0
    milk = inventory.get("milk", 0) if isinstance(inventory, dict) else 0

    active_plots = len([p for p in plots if isinstance(p, dict) and p.get("state") != "empty"]) if plots else 0

    if weeds:
        weed_plot = max(weeds, key=lambda w: w.get("weed_level", 0) if isinstance(w, dict) else 0)
        plot_id = weed_plot.get("id", 0) if isinstance(weed_plot, dict) else weed_plot
        if money >= 5:
            _last_action = "BUY"
            return {"action": "BUY", "item": "weed_killer", "n": 1}
        _last_action = "PASS"
        return {"action": "PASS"}

    if grain > 0:
        _last_action = "SELL"
        return {"action": "SELL", "item": "grain", "n": grain}
    if eggs > 0:
        _last_action = "SELL"
        return {"action": "SELL", "item": "eggs", "n": eggs}
    if milk > 0:
        _last_action = "SELL"
        return {"action": "SELL", "item": "milk", "n": milk}

    if money >= 20 and len(plots) == 0:
        _last_action = "BUY"
        return {"action": "BUY", "item": "land", "n": 1}
    if money >= 10 and wheat < 5:
        buy_n = min(5 - wheat, money // 10)
        if buy_n > 0:
            _last_action = "BUY"
            return {"action": "BUY", "item": "wheat", "n": buy_n}

    if wheat >= 1 and empty_tiles:
        plot_id = empty_tiles[0].get("id", 0) if isinstance(empty_tiles[0], dict) else empty_tiles[0]
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": plot_id}

    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture 2026-09-23-s5 ready")
