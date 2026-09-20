import sys
import time

_last_action = None
_wheat = 0
_feed = 0
_animals = 0
_weed_count = 0
_grain = 0
_land_count = 0
_turn = 0
_last_time = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _wheat, _feed, _animals, _weed_count, _grain, _land_count, _turn, _last_time
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
    _wheat = wheat_seed
    _feed = feed
    _animals = animals
    _grain = grain
    _weed_count = len(weeds)
    _land_count = obs.get("land_count", 4)

    if weeds:
        _last_action = "CLEAR"
        return {"action": "CLEAR", "plot": weeds[0]}
    if grain > 0:
        _last_action = "PLACE"
        return {"action": "PLACE", "item": "grain", "n": 1}
    if len(empty_tiles) == 0:
        if money >= 200:
            _last_action = "BUY"
            return {"action": "BUY", "item": "land", "n": 1}
    if len(empty_tiles) > 0 and wheat_seed >= 1:
        _last_action = "PLANT"
        return {"action": "PLANT", "item": "wheat", "plot": empty_tiles[0]}
    if wheat_seed == 0 and money >= 10:
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": 3}
    if animals == 0 and money >= 50 and _land_count >= 2:
        _last_action = "BUY"
        return {"action": "BUY", "item": "animal", "n": 1}
    if money < 10 and grain == 0:
        _last_action = "SELL"
        return {"action": "SELL", "item": "grain", "n": 1}
    _last_action = "PASS"
    return {"action": "PASS"}

if __name__ == "__main__":
    print("Kaggriculture s3 ready")
