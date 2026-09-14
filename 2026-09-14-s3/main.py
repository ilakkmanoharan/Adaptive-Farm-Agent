"""Kaggriculture submission 3 — 2026-09-12-s3.

Fixes s2 shed thrash (never DROP the whole bag), reserves pastures,
scales sheep first, and buys wheat for feed. Crash-safe protocol unchanged.
"""

from __future__ import annotations

import os
from collections import Counter

LOCAL_DEBUG = os.environ.get("KAGG_DEBUG") == "1"

SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
ANIMAL_STRUCTURE = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
MAX_YIELD_DAY = {"WHEAT": 4, "CARROT": 3, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
ONGOING = {"WHEAT": False, "CARROT": False, "TOMATO": True, "STRAWBERRY": True, "MELON": False}
LAND_PRICES = (1000, 2000, 4000)
PRODUCTS = (
    "MELON", "MILK", "WOOL", "STRAWBERRY", "EGG", "TOMATO", "CARROT",
    "FERTILIZER", "WHEAT",
)
BASE_PRICE = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100,
}
PREMIUM = {"MELON", "MILK", "WOOL", "STRAWBERRY"}
MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}

TARGET_COWS = 4
TARGET_SHEEP = 10
TARGET_MELONS = 8
TARGET_STRAWBERRY = 20
TARGET_WHEAT_TILES = 10
MAX_HANDS = 10
PASTURE_RESERVE = 8
SHED_CAP = 100
BOARD = 10
TURNS_PER_DAY = 24
EPISODE_STEPS = 720

# Process memory is fine within one episode; claims are rebuilt if missing.
_claims = {}
_last_key = None


def getv(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        pass
    return getattr(obj, key, default)


def as_map(obj):
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    try:
        return dict(obj)
    except Exception:
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_")}


def as_list(obj):
    if obj is None:
        return []
    if isinstance(obj, (list, tuple)):
        return list(obj)
    try:
        return list(obj)
    except Exception:
        return []


def tile_kind(tile):
    if tile is None or tile == "LOCKED":
        return tile
    return getv(tile, "kind")


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def shed_tiles(board=BOARD):
    h = board // 2
    return ((h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h))


def nearest_shed(pos, board=BOARD):
    spots = shed_tiles(board)
    return min(spots, key=lambda p: (manhattan(pos, p), p[1], p[0]))


def is_shed_adj(pos, board=BOARD):
    return tuple(pos) in set(shed_tiles(board))


def hire_cost(n_already):
    a, b = 1, 1
    for _ in range(n_already):
        a, b = b, a + b
    return a


def step_toward(pos, target):
    x, y = pos
    tx, ty = target
    dx, dy = tx - x, ty - y
    if dx == 0 and dy == 0:
        return ["PASS"]
    if abs(dx) > abs(dy) or (abs(dx) == abs(dy) and dx != 0):
        return ["EAST"] if dx > 0 else ["WEST"]
    return ["SOUTH"] if dy > 0 else ["NORTH"]


def inv_count(inv):
    return sum(int(v or 0) for v in as_map(inv).values())


def inv_get(inv, item):
    return int(as_map(inv).get(item, 0) or 0)


class World:
    __slots__ = (
        "obs", "player", "day", "hour", "step", "remain", "me", "priv",
        "tiles", "money", "farmer", "hands", "quads", "hires",
        "shed", "seeds", "invs", "prices", "units", "board",
    )

    def __init__(self, obs):
        self.obs = obs
        self.player = int(getv(obs, "player", 0) or 0)
        self.day = int(getv(obs, "day", 0) or 0)
        self.hour = int(getv(obs, "hour", 0) or 0)
        raw_step = getv(obs, "step", None)
        self.step = int(raw_step) if raw_step is not None else self.day * TURNS_PER_DAY + self.hour
        self.remain = max(0, EPISODE_STEPS - self.step - 2)
        farms = as_list(getv(obs, "farms", []))
        self.me = farms[self.player] if self.player < len(farms) else {}
        self.priv = getv(obs, "private", {}) or {}
        self.tiles = as_list(getv(self.me, "tiles", []))
        self.board = len(self.tiles) if self.tiles else BOARD
        self.money = float(getv(self.me, "money", 0) or 0)
        self.farmer = tuple(as_list(getv(self.me, "farmer", [4, 4]))[:2] or [4, 4])
        self.hands = [tuple(as_list(p)[:2]) for p in as_list(getv(self.me, "hands", []))]
        self.quads = as_list(getv(self.me, "unlocked_quadrants", ["NW"]))
        self.hires = int(getv(self.me, "hires_today", 0) or 0)
        self.shed = as_map(getv(self.priv, "shed", {}))
        self.seeds = as_map(getv(self.priv, "seeds", {}))
        self.invs = [as_map(x) for x in as_list(getv(self.priv, "inventories", [{}]))]
        while len(self.invs) < 1 + len(self.hands):
            self.invs.append({})
        prices = getv(getv(obs, "market", {}), "prices", {})
        self.prices = as_map(prices)
        self.units = [("F", self.farmer, self.invs[0])]
        for i, pos in enumerate(self.hands):
            inv = self.invs[i + 1] if i + 1 < len(self.invs) else {}
            self.units.append(("H%d" % i, pos, inv))

    def tile(self, x, y):
        if y < 0 or y >= len(self.tiles):
            return "LOCKED"
        row = as_list(self.tiles[y])
        if x < 0 or x >= len(row):
            return "LOCKED"
        return row[x]

    def iter_tiles(self):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(as_list(row)):
                yield x, y, tile

    def seed(self, crop):
        return int(self.seeds.get(crop, 0) or 0)

    def shed_n(self, item):
        return int(self.shed.get(item, 0) or 0)

    def price(self, item):
        return int(self.prices.get(item, BASE_PRICE.get(item, 1)) or 1)

    def shed_used(self):
        return sum(int(v or 0) for v in self.shed.values())


def classify(w):
    plants, animals, weeds, empty, structures = [], [], [], [], []
    wheat_tiles = melon_tiles = strawberry_tiles = 0
    cows = sheep = geese = 0
    unfed_risk = []
    unwater_risk = []
    for x, y, tile in w.iter_tiles():
        if tile == "LOCKED":
            continue
        if tile is None:
            empty.append((x, y))
            continue
        kind = tile_kind(tile)
        if kind == "WEED":
            weeds.append((x, y, tile))
        elif kind == "PLANT":
            plants.append((x, y, tile))
            crop = getv(tile, "crop")
            if crop == "WHEAT":
                wheat_tiles += 1
            elif crop == "MELON":
                melon_tiles += 1
            elif crop == "STRAWBERRY":
                strawberry_tiles += 1
            if not getv(tile, "watered_today") and int(getv(tile, "consecutive_unwatered", 0) or 0) >= 1:
                unwater_risk.append((x, y, tile))
        elif kind in ("COOP", "PASTURE"):
            animal = getv(tile, "animal")
            if animal:
                animals.append((x, y, tile))
                if animal == "COW":
                    cows += 1
                elif animal == "SHEEP":
                    sheep += 1
                elif animal == "GOOSE":
                    geese += 1
                if not getv(tile, "fed_today") and int(getv(tile, "consecutive_unfed", 0) or 0) >= 1:
                    unfed_risk.append((x, y, tile))
            else:
                structures.append((x, y, tile))
    return {
        "plants": plants,
        "animals": animals,
        "weeds": weeds,
        "empty": empty,
        "structures": structures,
        "wheat_tiles": wheat_tiles,
        "melon_tiles": melon_tiles,
        "strawberry_tiles": strawberry_tiles,
        "cows": cows,
        "sheep": sheep,
        "geese": geese,
        "unwater_risk": unwater_risk,
        "unfed_risk": unfed_risk,
    }


def desired_hands(w, farm):
    load = len(farm["plants"]) + 3 * len(farm["animals"]) + len(farm["weeds"])
    if w.day <= 1:
        target = 6
    elif w.day <= 6:
        target = 8
    else:
        target = 10
    target = min(MAX_HANDS, max(target, (load + 4) // 5))
    if w.money < 180:
        target = min(target, 4)
    return target


def last_plant_ok(w, crop):
    if crop == "MELON":
        return w.day <= 18
    if crop == "STRAWBERRY":
        return w.day <= 18
    if crop == "WHEAT":
        return w.day <= 25
    return w.day <= 12


def plantable_empty(w, farm):
    blocked = set(shed_tiles(w.board))
    return [p for p in farm["empty"] if p not in blocked]


def max_plants(w, farm):
    workers = 1 + max(len(w.hands), min(MAX_HANDS, desired_hands(w, farm)))
    return min(24, max(10, workers * 3))


def sellable_counts(w, farm, inv):
    """Harvest goods that may go to the shed. Never includes animals or reserved wheat."""
    out = {}
    for item, n in as_map(inv).items():
        n = int(n or 0)
        if n <= 0 or item in ANIMAL_COST:
            continue
        if item == "WHEAT":
            continue
        out[item] = n
    return out


def deposit_action(inv, farm, w):
    goods = sellable_counts(w, farm, inv)
    if not goods:
        return None
    item = max(goods, key=lambda k: (k in PREMIUM, goods[k], k))
    return ["PLACE", item, goods[item]]


def pending_animals(w):
    out = []
    for animal in ("COW", "SHEEP", "GOOSE"):
        n = w.shed_n(animal) + sum(inv_get(inv, animal) for _, _, inv in w.units)
        if n > 0:
            out.append(animal)
    return out


def harvest_ready(w, tile):
    crop = getv(tile, "crop")
    age = w.day - int(getv(tile, "planted_day", 0) or 0)
    yield_u = int(getv(tile, "yield_units", 0) or 0)
    if yield_u <= 0:
        return False
    if age < FIRST_YIELD.get(crop, 2):
        return False
    if w.remain <= 30 or w.day >= 28:
        return True
    if ONGOING.get(crop):
        return True
    return age >= MAX_YIELD_DAY.get(crop, 4)


def decaying(w, tile):
    mls = int(getv(tile, "max_lifespan_step", -1) or -1)
    return mls >= 0 and w.step >= mls and int(getv(tile, "yield_units", 0) or 0) > 0


def phase(w):
    if w.day >= 28 or w.remain <= 36:
        return "LIQUIDATE"
    if w.day >= 25:
        return "HARVEST"
    if w.day >= 13:
        return "PRODUCE"
    if w.day >= 5:
        return "EXPAND"
    return "OPEN"


def plan_market(w, farm):
    orders = []
    cash = w.money
    ph = phase(w)
    endgame = ph in ("HARVEST", "LIQUIDATE")
    herd = farm["cows"] + farm["sheep"] + farm["geese"]
    days_left = max(1, 29 - w.day)
    reserve = 0 if (endgame and herd == 0) else herd * min(days_left, 3) + (0 if endgame else 2)

    def afford(cost):
        nonlocal cash
        if cash >= cost:
            cash -= cost
            return True
        return False

    # 1. Emergency liquidity: sell anything if we cannot hire/plant.
    if cash < 40:
        for item in PRODUCTS:
            n = w.shed_n(item)
            if item == "WHEAT":
                n = max(0, n - reserve)
            if n > 0:
                orders.append(["SELL", item, n])
                break

    # 2. Attractive / time-sensitive sales from the shed.
    used = w.shed_used()
    tight = used >= 70 or endgame
    for item in PRODUCTS:
        n = w.shed_n(item)
        if n <= 0:
            continue
        if item == "WHEAT":
            n = max(0, n - reserve)
            if n <= 0:
                continue
        px = w.price(item)
        base = BASE_PRICE.get(item, 1)
        if endgame or tight:
            take = n
        elif item in PREMIUM:
            if px <= 1:
                take = n  # already on the floor
            elif px >= int(base * 0.55):
                take = min(n, 4)
            else:
                take = min(n, 2)
        else:
            if px >= max(8, int(base * 0.45)) or used >= 50:
                take = n
            else:
                take = min(n, 3)
        if take > 0:
            orders.append(["SELL", item, take])

    # 3. Feed purchase — winners buy wheat rather than starve the herd.
    wheat_have = w.shed_n("WHEAT") + sum(inv_get(inv, "WHEAT") for _, _, inv in w.units)
    unfed = sum(1 for _x, _y, t in farm["animals"] if not getv(t, "fed_today"))
    feed_want = (herd + 4) if herd else 0
    if wheat_have < feed_want and cash >= w.price("WHEAT"):
        buy_n = min(max(4, feed_want - wheat_have), 12)
        cost = w.price("WHEAT") * buy_n
        if afford(cost):
            orders.append(["BUY_PRODUCT", "WHEAT", buy_n])

    # 4. Sheep first, then cows. One unplaced animal in the pipeline.
    pending_cows = w.shed_n("COW") + sum(inv_get(inv, "COW") for _, _, inv in w.units)
    pending_sheep = w.shed_n("SHEEP") + sum(inv_get(inv, "SHEEP") for _, _, inv in w.units)
    pending = pending_cows + pending_sheep
    space_ok = len(plantable_empty(w, farm)) + len(farm["structures"]) >= 1
    if (not endgame) and w.day <= 22 and pending <= 1 and space_ok:
        cash_floor = 200 if w.day <= 1 else 350
        if farm["sheep"] + pending_sheep < TARGET_SHEEP and cash >= ANIMAL_COST["SHEEP"] + cash_floor:
            if afford(ANIMAL_COST["SHEEP"]):
                orders.append(["BUY_ANIMAL", "SHEEP", 1])
        elif farm["sheep"] >= 2 and farm["cows"] + pending_cows < TARGET_COWS and cash >= ANIMAL_COST["COW"] + cash_floor:
            if afford(ANIMAL_COST["COW"]):
                orders.append(["BUY_ANIMAL", "COW", 1])

    # 5. Land only after melon cash; never while broke.
    extras = max(0, len(w.quads) - 1)
    if extras < 1 and not endgame and w.day >= 10 and w.money >= 5000:
        cost = LAND_PRICES[0]
        if cash >= cost + 400 and len(plantable_empty(w, farm)) <= 4:
            if afford(cost):
                orders.append(["BUY_LAND"])

    # 6. Hire every morning up to the labor target.
    target = desired_hands(w, farm)
    already = w.hires
    have = len(w.hands)
    while have + (len([o for o in orders if o[0] == "HIRE"])) < target and already < 12:
        cost = hire_cost(already)
        if cash < cost + 40:
            break
        cash -= cost
        already += 1
        orders.append(["HIRE"])

    seed_orders = []
    melon_cap = 4 if w.day <= 3 else TARGET_MELONS
    if last_plant_ok(w, "MELON") and ph != "LIQUIDATE" and farm["melon_tiles"] + w.seed("MELON") < melon_cap:
        n = min(3 if w.day <= 1 else 1, melon_cap - farm["melon_tiles"] - w.seed("MELON"))
        n = min(n, int(cash // SEED_COST["MELON"]) if cash >= SEED_COST["MELON"] + 80 else 0)
        if n > 0 and afford(SEED_COST["MELON"] * n):
            seed_orders.append(["BUY_SEED", "MELON", n])
    empties = len(plantable_empty(w, farm))
    if last_plant_ok(w, "STRAWBERRY") and w.day >= 3 and ph != "LIQUIDATE" and empties >= 4:
        have_b = farm["strawberry_tiles"] + w.seed("STRAWBERRY")
        if have_b < TARGET_STRAWBERRY and cash >= SEED_COST["STRAWBERRY"] + 200:
            n = min(2, TARGET_STRAWBERRY - have_b, int((cash - 200) // SEED_COST["STRAWBERRY"]))
            if n > 0 and afford(SEED_COST["STRAWBERRY"] * n):
                seed_orders.append(["BUY_SEED", "STRAWBERRY", n])
    if last_plant_ok(w, "WHEAT") and ph != "LIQUIDATE":
        want = 4 if farm["wheat_tiles"] < TARGET_WHEAT_TILES else 1
        have_s = w.seed("WHEAT")
        if have_s < want:
            n = min(want - have_s, 6, int(cash // SEED_COST["WHEAT"]) if cash >= SEED_COST["WHEAT"] else 0)
            if n > 0 and afford(SEED_COST["WHEAT"] * n):
                seed_orders.append(["BUY_SEED", "WHEAT", n])

    sells = [o for o in orders if o[0] == "SELL"][:3]
    feed_buys = [o for o in orders if o[0] == "BUY_PRODUCT"]
    commits = [o for o in orders if o[0] in ("BUY_ANIMAL", "BUY_LAND")]
    hires = [o for o in orders if o[0] == "HIRE"]
    out = []
    for group in (sells, feed_buys, seed_orders, commits, hires):
        out.extend(group)
    return out[:10]


def plant_choice(w, farm):
    if phase(w) in ("HARVEST", "LIQUIDATE"):
        return None
    if len(farm["plants"]) >= max_plants(w, farm):
        return None
    herd = farm["cows"] + farm["sheep"] + farm["geese"]
    need_pasture = max(0, PASTURE_RESERVE - herd - len(farm["structures"]))
    if len(plantable_empty(w, farm)) <= need_pasture:
        return None
    if last_plant_ok(w, "MELON") and farm["melon_tiles"] < TARGET_MELONS and w.seed("MELON") > 0:
        return "MELON"
    wheat_need = TARGET_WHEAT_TILES if herd < 6 else min(8, TARGET_WHEAT_TILES)
    if last_plant_ok(w, "WHEAT") and w.seed("WHEAT") > 0 and farm["wheat_tiles"] < wheat_need:
        return "WHEAT"
    if last_plant_ok(w, "STRAWBERRY") and farm["strawberry_tiles"] < TARGET_STRAWBERRY and w.seed("STRAWBERRY") > 0:
        return "STRAWBERRY"
    return None


def local_action(w, farm, pos, inv, reserved_seeds):
    """Best action on the tile we already stand on, or None."""
    x, y = pos
    tile = w.tile(x, y)
    kind = tile_kind(tile)

    if kind == "PLANT":
        crop = getv(tile, "crop")
        watered = bool(getv(tile, "watered_today"))
        unwatered = int(getv(tile, "consecutive_unwatered", 0) or 0)
        if not watered and unwatered >= 1:
            return (9000, ["WATER"])
        if harvest_ready(w, tile) or decaying(w, tile):
            return (7800, ["HARVEST"])
        if not watered:
            return (6200, ["WATER"])
        if (
            inv_get(inv, "FERTILIZER") > 0
            and int(getv(tile, "fertilized_until_day", -1) or -1) < w.day
            and crop in ("MELON", "WHEAT", "STRAWBERRY")
        ):
            age = w.day - int(getv(tile, "planted_day", 0) or 0)
            if crop == "STRAWBERRY" and 8 <= age <= 16:
                return (4100, ["FERTILIZE"])
            window = (MAX_YIELD_DAY.get(crop, 4) + 1) // 2
            if crop != "STRAWBERRY" and window <= age <= MAX_YIELD_DAY.get(crop, 4):
                return (4100, ["FERTILIZE"])
        return None

    if kind in ("COOP", "PASTURE") and getv(tile, "animal"):
        animal = getv(tile, "animal")
        fed = bool(getv(tile, "fed_today"))
        unfed = int(getv(tile, "consecutive_unfed", 0) or 0)
        held = int(getv(tile, "yield_units", 0) or 0)
        if not fed and inv_get(inv, "WHEAT") > 0:
            return (9500 if unfed >= 1 else 8200, ["FEED"])
        if held > 0 and (held >= 4 or w.day >= 27 or phase(w) == "LIQUIDATE"):
            return (7600, ["HARVEST"])
        if getv(tile, "fertilizer_available"):
            return (7000, ["COLLECT_FERTILIZER"])
        if held > 0:
            return (6800, ["HARVEST"])
        if fed and not getv(tile, "cared_today") and w.day <= 27:
            return (5600, ["CARE"])
        # Place is N/A; structure occupied.
        return None

    if kind in ("COOP", "PASTURE") and not getv(tile, "animal"):
        for animal, struct in ANIMAL_STRUCTURE.items():
            if struct == kind and inv_get(inv, animal) > 0:
                return (7400, ["PLACE", animal])
        return None

    if kind == "WEED":
        return (5000, ["DIG"])

    if tile is None:
        if (x, y) not in set(shed_tiles(w.board)):
            for animal, struct in (("COW", "PASTURE"), ("SHEEP", "PASTURE"), ("GOOSE", "COOP")):
                if inv_get(inv, animal) > 0:
                    return (8400, ["BUILD_%s" % struct])
            crop = plant_choice(w, farm)
            if crop and reserved_seeds.get(crop, 0) < w.seed(crop):
                return (5400, ["PLANT", crop])
        return None

    return None


def need_deposit(w, farm, inv):
    """True only when we have harvest goods to PLACE — never wheat or animals."""
    goods = sellable_counts(w, farm, inv)
    if not goods:
        return False
    if phase(w) == "LIQUIDATE":
        return True
    n = sum(goods.values())
    if n >= 3:
        return True
    if w.hour >= 20:
        return False
    if w.shed_used() >= 90:
        return False
    return n >= 1 and w.hour <= 18


def build_targets(w, farm):
    """Global scored targets: (score, x, y, tag). Higher is more urgent."""
    targets = []
    for x, y, tile in farm["plants"]:
        watered = bool(getv(tile, "watered_today"))
        unwatered = int(getv(tile, "consecutive_unwatered", 0) or 0)
        if not watered and unwatered >= 1:
            targets.append((9000, x, y, "water_survive"))
        elif harvest_ready(w, tile) or decaying(w, tile):
            targets.append((7800, x, y, "harvest_plant"))
        elif not watered:
            targets.append((6200, x, y, "water_yield"))

    for x, y, tile in farm["animals"]:
        fed = bool(getv(tile, "fed_today"))
        unfed = int(getv(tile, "consecutive_unfed", 0) or 0)
        held = int(getv(tile, "yield_units", 0) or 0)
        if not fed:
            targets.append((9500 if unfed >= 1 else 8200, x, y, "feed"))
        if held > 0:
            targets.append((7600 if held >= 4 or w.day >= 27 else 6800, x, y, "harvest_animal"))
        if getv(tile, "fertilizer_available"):
            targets.append((7000, x, y, "fert"))
        if fed and not getv(tile, "cared_today") and w.day <= 27:
            targets.append((5600, x, y, "care"))

    for x, y, tile in farm["structures"]:
        kind = tile_kind(tile)
        for animal, struct in ANIMAL_STRUCTURE.items():
            if struct == kind and (w.shed_n(animal) > 0 or any(inv_get(inv, animal) for _, _, inv in w.units)):
                targets.append((7400, x, y, "place"))
                break

    for x, y, _tile in farm["weeds"]:
        targets.append((5000, x, y, "dig"))

    crop = plant_choice(w, farm)
    empties = plantable_empty(w, farm)
    if crop and empties:
        ranked = sorted(empties, key=lambda p: (manhattan(p, (4, 4)), p[1], p[0]))
        for x, y in ranked[:6]:
            targets.append((5400, x, y, "plant_%s" % crop))

    carrying_or_shed = bool(pending_animals(w))
    have_empty_struct = bool(farm["structures"])
    if carrying_or_shed and not have_empty_struct and empties and phase(w) not in ("LIQUIDATE",):
        x, y = min(empties, key=lambda p: (manhattan(p, (4, 4)), p[1], p[0]))
        targets.append((8400, x, y, "build"))

    if any(not getv(t, "fed_today") for _x, _y, t in farm["animals"]) and w.shed_n("WHEAT") > 0:
        if all(inv_get(inv, "WHEAT") <= 0 for _, _, inv in w.units):
            targets.append((8800, 4, 4, "pickup"))
    elif any(w.shed_n(a) > 0 for a in ANIMAL_COST):
        targets.append((8700, 4, 4, "pickup"))

    targets.sort(key=lambda t: (-t[0], t[2], t[1], t[3]))
    return targets


def assign(w, farm, targets):
    global _claims, _last_key
    key = (w.player, w.day)
    if _last_key != key:
        _claims = {}
        _last_key = key

    claimed_xy = {}
    assignments = {}
    reserved_seeds = Counter()

    # Validate sticky claims.
    valid_targets = {(x, y): score for score, x, y, _tag in targets}
    for uid, pos, inv in w.units:
        claim = _claims.get(uid)
        if not claim:
            continue
        cx, cy, tag = claim
        if (cx, cy) not in valid_targets and tag not in ("drop", "pickup"):
            _claims.pop(uid, None)
            continue
        # Release if a much more urgent unclaimed job is adjacent-close.
        assignments[uid] = (cx, cy, tag)

    used = set()
    for uid, pos, inv in w.units:
        if uid in assignments:
            used.add(assignments[uid][:2])

    for uid, pos, inv in w.units:
        if uid in assignments:
            continue
        # Prefer carrying-specific work.
        if need_deposit(w, farm, inv):
            tx, ty = nearest_shed(pos, w.board)
            assignments[uid] = (tx, ty, "drop")
            _claims[uid] = assignments[uid]
            continue
        empties = plantable_empty(w, farm)
        if any(inv_get(inv, a) > 0 for a in ANIMAL_COST) and (farm["structures"] or empties):
            structs = [(x, y, t) for x, y, t in farm["structures"]]
            animal = next(a for a in ("COW", "SHEEP", "GOOSE") if inv_get(inv, a) > 0)
            struct = ANIMAL_STRUCTURE[animal]
            match = [(x, y) for x, y, t in structs if tile_kind(t) == struct]
            if match:
                dest = min(match, key=lambda p: (manhattan(pos, p), p[1], p[0]))
            else:
                dest = min(empties, key=lambda p: (manhattan(pos, p), p[1], p[0]))
            assignments[uid] = (dest[0], dest[1], "place")
            _claims[uid] = assignments[uid]
            used.add(dest)
            continue
        if inv_get(inv, "WHEAT") > 0:
            unfed = [(x, y) for x, y, t in farm["animals"] if not getv(t, "fed_today") and (x, y) not in used]
            if unfed:
                dest = min(unfed, key=lambda p: (manhattan(pos, p), p[1], p[0]))
                assignments[uid] = (dest[0], dest[1], "feed")
                _claims[uid] = assignments[uid]
                used.add(dest)
                continue

        best = None
        best_score = -1e9
        for score, x, y, tag in targets:
            if (x, y) in used and tag not in ("shed",):
                continue
            travel = manhattan(pos, (x, y))
            # Feed tasks are useless without wheat unless we are picking up.
            if tag == "feed" and inv_get(inv, "WHEAT") <= 0:
                continue
            adj = score - travel * 35
            if adj > best_score:
                best_score = adj
                best = (x, y, tag)
        if best is None:
            # Pickup wheat / animals at shed if needed.
            if (w.shed_n("WHEAT") > 0 and any(not getv(t, "fed_today") for _x, _y, t in farm["animals"])) or any(
                w.shed_n(a) > 0 for a in ANIMAL_COST
            ):
                dest = nearest_shed(pos, w.board)
                assignments[uid] = (dest[0], dest[1], "pickup")
                _claims[uid] = assignments[uid]
            else:
                assignments[uid] = (pos[0], pos[1], "idle")
        else:
            assignments[uid] = best
            _claims[uid] = best
            if best[2] not in ("shed",):
                used.add(best[:2])
            if best[2].startswith("plant_"):
                reserved_seeds[best[2].split("_", 1)[1]] += 1

    return assignments, reserved_seeds


def unit_action(w, farm, uid, pos, inv, assignment, reserved_seeds, seed_budget):
    if is_shed_adj(pos, w.board):
        unfed = sum(1 for _x, _y, t in farm["animals"] if not getv(t, "fed_today"))
        placed = len(farm["animals"])
        bootstrap = placed < 3 or w.day <= 4
        if unfed > 0 and w.shed_n("WHEAT") > 0 and inv_get(inv, "WHEAT") == 0 and not bootstrap:
            return ["PICKUP", "WHEAT", min(2, unfed, w.shed_n("WHEAT"))]
        if unfed == 0 or bootstrap:
            if w.shed_n("SHEEP") > 0 and inv_get(inv, "SHEEP") == 0:
                return ["PICKUP", "SHEEP", 1]
            if w.shed_n("COW") > 0 and inv_get(inv, "COW") == 0:
                return ["PICKUP", "COW", 1]
            if w.shed_n("GOOSE") > 0 and inv_get(inv, "GOOSE") == 0:
                return ["PICKUP", "GOOSE", 1]
        if unfed > 0 and w.shed_n("WHEAT") > 0 and inv_get(inv, "WHEAT") == 0:
            return ["PICKUP", "WHEAT", min(2, unfed, w.shed_n("WHEAT"))]

    # Endgame recall: deposit harvest goods only — never DROP the bag.
    if phase(w) == "LIQUIDATE" and sellable_counts(w, farm, inv):
        if is_shed_adj(pos, w.board):
            return deposit_action(inv, farm, w) or ["PASS"]
        return step_toward(pos, nearest_shed(pos, w.board))
    if w.remain <= manhattan(pos, nearest_shed(pos, w.board)) + 3 and sellable_counts(w, farm, inv):
        if is_shed_adj(pos, w.board):
            return deposit_action(inv, farm, w) or ["PASS"]
        return step_toward(pos, nearest_shed(pos, w.board))

    # On-tile work wins when it is at least as urgent as the assigned trip.
    local = local_action(w, farm, pos, inv, seed_budget)
    assigned_score = 0
    if assignment:
        ax, ay, tag = assignment
        assigned_score = {
            "water_survive": 9000, "feed": 8200, "harvest_plant": 7800,
            "harvest_animal": 6800, "fert": 7000, "place": 8400, "build": 8400,
            "water_yield": 6200, "care": 5600, "dig": 5000, "drop": 6500,
            "pickup": 6400, "idle": 0,
        }.get(tag, 5400 if tag.startswith("plant_") else 1000)
        if (ax, ay) == tuple(pos) and local:
            act = local[1]
            if act[0] == "PLANT":
                crop = act[1]
                if seed_budget[crop] <= 0:
                    local = None
                else:
                    seed_budget[crop] -= 1
                    return act
            return act
        if local and local[0] >= assigned_score + 400:
            act = local[1]
            if act[0] == "PLANT":
                crop = act[1]
                if seed_budget[crop] > 0:
                    seed_budget[crop] -= 1
                    return act
            else:
                return act

    ax, ay, tag = assignment if assignment else (pos[0], pos[1], "idle")
    if tuple(pos) != (ax, ay):
        return step_toward(pos, (ax, ay))

    # Arrived at assigned tile.
    if tag == "drop" or (need_deposit(w, farm, inv) and is_shed_adj(pos, w.board)):
        if is_shed_adj(pos, w.board):
            act = deposit_action(inv, farm, w)
            if act:
                return act
    if tag in ("pickup", "feed"):
        if is_shed_adj(pos, w.board):
            if w.shed_n("SHEEP") > 0 and inv_get(inv, "SHEEP") == 0:
                return ["PICKUP", "SHEEP", 1]
            if w.shed_n("COW") > 0 and inv_get(inv, "COW") == 0:
                return ["PICKUP", "COW", 1]
            unfed = sum(1 for _x, _y, t in farm["animals"] if not getv(t, "fed_today"))
            if unfed and w.shed_n("WHEAT") > 0 and inv_get(inv, "WHEAT") == 0:
                return ["PICKUP", "WHEAT", min(2, unfed, w.shed_n("WHEAT"))]
    if local:
        act = local[1]
        if act[0] == "PLANT":
            crop = act[1]
            if seed_budget[crop] > 0:
                seed_budget[crop] -= 1
                return act
            return ["PASS"]
        return act
    if tile_kind(w.tile(*pos)) is None:
        crop = plant_choice(w, farm)
        if crop and seed_budget.get(crop, 0) > 0:
            seed_budget[crop] -= 1
            return ["PLANT", crop]
        if any(inv_get(inv, a) > 0 for a in ANIMAL_COST):
            animal = next(a for a in ("COW", "SHEEP", "GOOSE") if inv_get(inv, a) > 0)
            return ["BUILD_%s" % ANIMAL_STRUCTURE[animal]]
    return ["PASS"]


def safe_pass(obs):
    farms = as_list(getv(obs, "farms", []))
    player = int(getv(obs, "player", 0) or 0)
    me = farms[player] if player < len(farms) else {}
    n_hands = len(as_list(getv(me, "hands", [])))
    return {"farmer": ["PASS"], "hands": [["PASS"] for _ in range(n_hands)], "market": []}


def agent_impl(obs, config=None):
    w = World(obs)
    farm = classify(w)
    market = plan_market(w, farm)
    targets = build_targets(w, farm)
    assignments, reserved = assign(w, farm, targets)
    seed_budget = Counter({c: w.seed(c) for c in SEED_COST})
    # reserved is informational; budget is decremented as we emit PLANTs.

    farmer_act = ["PASS"]
    hand_acts = []
    for uid, pos, inv in w.units:
        act = unit_action(w, farm, uid, pos, inv, assignments.get(uid), reserved, seed_budget)
        if not isinstance(act, list) or not act:
            act = ["PASS"]
        if uid == "F":
            farmer_act = act
        else:
            hand_acts.append(act)

    while len(hand_acts) < len(w.hands):
        hand_acts.append(["PASS"])
    hand_acts = hand_acts[: len(w.hands)]

    # Atomic PLANT guard: if we over-subscribed a crop, convert extras to PASS.
    demand = Counter()
    acts = [farmer_act] + hand_acts
    for a in acts:
        if isinstance(a, list) and len(a) >= 2 and a[0] == "PLANT":
            demand[a[1]] += 1
    blocked = {c for c, n in demand.items() if n > w.seed(c)}
    if blocked:
        def scrub(a):
            if isinstance(a, list) and len(a) >= 2 and a[0] == "PLANT" and a[1] in blocked:
                return ["PASS"]
            return a
        farmer_act = scrub(farmer_act)
        hand_acts = [scrub(a) for a in hand_acts]

    clean_market = []
    for order in market:
        if not isinstance(order, list) or not order:
            continue
        clean_market.append(order)
        if len(clean_market) >= 10:
            break

    return {"farmer": farmer_act, "hands": hand_acts, "market": clean_market}


def agent(obs, config=None):
    try:
        return agent_impl(obs, config)
    except Exception:
        if LOCAL_DEBUG:
            raise
        return safe_pass(obs)
