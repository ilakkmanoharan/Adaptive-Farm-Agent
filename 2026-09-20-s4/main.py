import sys
import time

_last_action = None
_animals = 0
_weed_count = 0
_turn = 0
_last_time = 0
_cow_bought = False

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _animals, _weed_count, _turn, _last_time, _cow_bought
    now = time.time()
    if _last_time > 0 and now - _last_time > 1.0:
        _last_time = now
        return {"action": "PASS"}
    _last_time = now
    _turn = obs.get("turn", 0)
    money = obs.get("money", 0)
    inventory = obs.get("inventory", {}) or {}
    weeds = obs.get("weeds", []) or []
    harvest_ready = obs.get("harvest_ready", []) or []
    empty_tiles = obs.get("empty_tiles", []) or []
    animals = obs.get("animals", 0)
    wheat_seed = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    feed = inventory.get("feed", 0) if isinstance(inventory, dict) else 0
    _animals = animals
    _weed_count = len(weeds)
    tilled_empty = len([t for t in empty_tiles if t.get("tilled", False)]) if empty_tiles else 0

    if _turn == 1 and animals == 0 and money >= 50:
        _last_action = "BUY"
        _cow_bought = True
        return {"action": "BUY", "item": "cow", "n": 1}
    if weeds:
        _last_action = "WEED"
        return {"action": "WEED", "plot": weeds[0]}
    if grain > 0:
        _last_action = "SELL"
        return {"action": "SELL", "item": "grain", "n": grain}
    if feed > 0:
        _last_action = "SELL"
        return {"action": "SELL", "item": "feed", "n": feed}
    if harvest_ready:
        item = harvest_ready[0].get("item", "grain")
        _last_action = "PLACE"
        return {"action": "PLACE", "item": item, "n": 1}
    if animals < 3 and money >= 120:
        _last_action = "BUY"
        return {"action": "BUY", "item": "cow", "n": 1}
    if tilled_empty > 0 and wheat_seed == 0 and money >= 10:
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": 1}
    if tilled_empty > 0 and wheat_seed >= 1:
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": empty_tiles[0]}
    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture s4 ready")
