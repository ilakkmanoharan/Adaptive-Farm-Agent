import sys

_last_action = None
_animal_count = 0
_planted_count = 0

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return _safe_pass(obs)

def _safe_pass(obs):
    return {"action": "PASS"}

def _agent_impl(obs, config=None):
    global _last_action, _animal_count, _planted_count
    money = obs.get("money", 0)
    inventory = obs.get("inventory", {})
    weeds = obs.get("weeds", [])
    harvest_ready = obs.get("harvest_ready", [])
    empty_tiles = obs.get("empty_tiles", [])
    animals = obs.get("animals", _animal_count)
    wheat_seed = inventory.get("wheat", 0) if isinstance(inventory, dict) else 0
    grain = inventory.get("grain", 0) if isinstance(inventory, dict) else 0
    feed = inventory.get("feed", 0) if isinstance(inventory, dict) else 0
    _animal_count = animals

    if weeds:
        _last_action = "WEED"
        return {"action": "WEED", "plot": weeds[0]}
    if harvest_ready:
        n = grain
        if n > 0:
            _last_action = "PLACE"
            return {"action": "PLACE", "item": "grain", "n": n}
    if animals < 3 and feed >= 3 and money >= 50:
        _last_action = "BUY"
        return {"action": "BUY", "item": "animal", "n": 1}
    if wheat_seed >= 1 and len(empty_tiles) >= 1:
        _last_action = "PLANT"
        _planted_count += 1
        return {"action": "PLANT", "item": "wheat", "plot": empty_tiles[0]}
    if wheat_seed == 0 and len(empty_tiles) >= 1 and money >= 10:
        _last_action = "BUY"
        return {"action": "BUY", "item": "wheat", "n": min(2, len(empty_tiles))}
    if _planted_count >= 2 and money >= 100:
        _last_action = "BUY"
        return {"action": "BUY", "item": "land", "n": 1}
    _last_action = "PASS"
    return {"action": "PASS"}

def _run_test():
    drop_count = 0
    animal_buys = 0
    wheat_buys = 0
    weed_count = 0
    place_count = 0
    for turn in range(100):
        obs = {
            "turn": turn + 1,
            "money": 200,
            "inventory": {"wheat": min(turn, 4), "grain": 5, "feed": 10},
            "weeds": [3] if turn == 5 else [],
            "harvest_ready": [0] if turn == 10 else [],
            "empty_tiles": [0, 1, 2, 3],
            "animals": min(turn // 20, 2),
        }
        act = agent(obs)
        if isinstance(act, dict):
            a = act.get("action")
            if a == "DROP":
                drop_count += 1
            if a == "BUY" and act.get("item") == "animal":
                animal_buys += 1
            if a == "BUY" and act.get("item") == "wheat":
                wheat_buys += 1
            if a == "WEED":
                weed_count += 1
            if a == "PLACE":
                place_count += 1
    return (drop_count == 0 and animal_buys <= 3 and wheat_buys <= 3 and weed_count >= 1 and place_count >= 1)

if __name__ == "__main__":
    print(_run_test())
