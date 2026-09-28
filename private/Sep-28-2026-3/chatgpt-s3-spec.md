**Kaggriculture Submission Spec – 2026-09-28-s3**

**Folder:** `2026-09-28-s3/`  
**Target file:** `main.py` (single stdlib file, <1 s per turn)  
**Previous:** 56648124 (2026-09-28-s2)

### 1. Ladder facts
- Record: 0W-0T-0L (new slot, no rated games yet).
- Starting rating: 600.
- No bank or opponent data available. All policy changes are therefore defensive and self-contained.

### 2. Root causes to fix (from s2 replay patterns)
- Repeated PICKUP/DROP thrash on harvest goods instead of direct PLACE.
- Herd size left at 0–1 (no reliable animal income).
- Over-purchase of wheat seed when land is not yet cleared.
- Weeds left on field for multiple turns.
- Land purchase timed after market instead of before planting window.
- Inventory left unsold at end of episode (0 score contribution).

### 3. Exact s3 policy table (vs s2)

| State condition                          | s2 behaviour                  | s3 behaviour                                      | Action sequence (priority order) |
|------------------------------------------|-------------------------------|---------------------------------------------------|----------------------------------|
| Weeds present on any owned tile          | Ignore / buy seed             | Clear first                                       | `WEED` nearest weed tile        |
| Empty field + wheat seed ≥ 1             | Buy more wheat                | Plant immediately                                 | `PLANT` wheat                   |
| Harvest ready (any crop)                 | PICKUP then later PLACE       | Direct sell                                       | `PLACE item n` (n = harvest)    |
| Gold ≥ 50 and herd size = 0              | Skip                          | Buy 1 chicken                                     | `BUY` chicken                   |
| Gold ≥ 120 and owned land < 4            | Buy land after market         | Buy land on first turn of cycle                   | `BUY` land (cheapest)           |
| Inventory value > 0 and market open      | Hold                          | Sell all non-animal goods                         | `SELL` all                      |
| No action possible                       | Idle                          | Idle                                              | `PASS`                          |

Animals are never sold. DROP is never used.

### 4. Task priority (implement in this order)
1. Weed removal before any purchase or plant.
2. Direct `PLACE` on harvest instead of PICKUP.
3. One-time chicken purchase when gold ≥ 50 and herd = 0.
4. Land purchase on turn 1 if gold ≥ 120 and land < 4.
5. Wheat planting only on cleared land.
6. End-of-episode sell of all non-animal inventory.

### 5. Local acceptance gates (run before any upload)
- `python main.py` completes 50 random episodes with zero `DROP` calls and zero PICKUP on harvest goods.
- Herd size ≥ 1 by turn 30 in ≥ 80 % of episodes.
- Weeds cleared within 1 turn of appearance.
- Final inventory value = 0 in ≥ 90 % of episodes (all sold).
- No action exceeds 200 ms wall time.

### 6. Non-goals
- No opponent modelling or shop blocking.
- No RL or learned parameters.
- No multi-file structure.
- No new environment APIs.

Implement the policy table as a simple if-elif chain in `main.py` using only standard library. Keep state tracking minimal (owned land count, herd size, weed positions, current inventory).