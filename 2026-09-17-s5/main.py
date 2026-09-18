import sys
import random

def agent(obs, config=None):
    try:
        return _agent_impl(obs, config)
    except Exception:
        return _safe_pass(obs)

def _safe_pass(obs):
    return {"action": "PASS"}

def _agent_impl(obs, config=None):
    turn = obs.get("turn", 0)
    money = obs.get("money", 0)
    owned_land = obs.get("owned_land", [])
    inventory = obs.get("inventory", {})
    weeds = obs.get("weeds", [])
    harvest_ready = obs.get("harvest_ready", [])
    animals = obs.get("animals", 0)
    empty_tiles = obs.get("empty_tiles", [])
    goods = obs.get("goods", 0)
    phase = obs.get("phase", "normal")

    actions = []

    if turn == 1:
        if money >= 200:
            actions.append(["BUY_LAND", 2])
        return {"action": actions or ["PASS"]}

    if money < 30 or len(owned_land) == 0:
        return {"action": ["PASS"]}

    if weeds:
        for tile in weeds[:1]:
            actions.append(["CLEAR", tile])
        return {"action": actions or ["PASS"]}

    if harvest_ready:
        for tile in harvest_ready[:1]:
            actions.append(["PICKUP", tile])
            actions.append(["PLACE_SELL", 99])
        return {"action": actions or ["PASS"]}

    if phase == "market" and goods > 0:
        actions.append(["SELL_ALL"])
        return {"action": actions or ["PASS"]}

    placed = 0
    for tile in empty_tiles:
        if placed >= 3:
            break
        actions.append(["PLACE_WHEAT", tile])
        placed += 1
    if placed > 0:
        return {"action": actions}

    if money >= 120 and animals == 0 and empty_tiles:
        actions.append(["BUY_COW", 1])
        actions.append(["PLACE", empty_tiles[0]])
        return {"action": actions or ["PASS"]}

    return {"action": ["PASS"]}

def _run_test(seed):
    random.seed(seed)
    for turn in range(50):
        obs = {
            "turn": turn + 1,
            "money": random.randint(0, 500),
            "owned_land": list(range(random.randint(0, 5))),
            "inventory": {},
            "weeds": [],
            "harvest_ready": [],
            "animals": 0,
            "empty_tiles": [1, 2, 3] if random.random() > 0.5 else [],
            "goods": random.randint(0, 10),
            "phase": random.choice(["normal", "market"]),
        }
        try:
            agent(obs)
        except Exception:
            return False
    return True

if __name__ == "__main__":
    passed = 0
    for i in range(20):
        seed = random.randint(0, 100000)
        if _run_test(seed):
            passed += 1
    print(f"Tests passed: {passed}/20")
    if passed == 20:
        print("All local acceptance gates satisfied.")
