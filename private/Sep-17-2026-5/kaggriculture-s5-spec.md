# Kaggriculture Submission 5 Specification
Date: 2026-09-17 · Slot: s5 · Folder: `2026-09-17-s5/`

Previous Kaggle id: 56315733
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s5 Submission Spec**

**Folder:** `2026-09-17-s5/`  
**Base:** previous `2026-09-17-s4` (id 56315733)  
**Goal:** first working ladder bot that plants, harvests, and sells without thrash or illegal actions. Single-file `main.py` only.

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed yet)
- Starting rating: 600
- Bank: unknown (no data)
- No opponents observed; no loss patterns available

### 2. Root causes we must fix
- Previous bot likely performed repeated PICKUP/DROP on same tiles (inventory thrash)
- No deterministic planting schedule → idle land or missed growth windows
- Over-purchase of wheat seeds without corresponding land or time to grow
- No weed clearing before planting
- Animals bought but never fed/placed, wasting money
- No sell logic at market phase (unsold inventory scores 0)

### 3. Exact s5 policy table vs previous bot

| Situation (checked in order) | s5 action | Change from s4 |
|------------------------------|-----------|----------------|
| Turn 1 | BUY 2 LAND | New |
| Any empty owned land tile | PLACE WHEAT (max 3 per turn) | New deterministic rule |
| Weeds visible on owned land | CLEAR tile | New |
| Harvest ready on owned land | PICKUP then PLACE SELL 99 | Fixed (was thrashing) |
| Inventory has goods at market phase | SELL all | New |
| Money ≥ 120 and no animals | BUY 1 COW, PLACE on empty land | New |
| Money < 30 or no land left | PASS | Safety |
| Any other case | PASS | Default |

- Never call DROP.
- Never buy more than 3 seeds per turn.
- Never buy animals after turn 8.
- All actions use only stdlib; no env APIs beyond documented actions.

### 4. Task priority
1. Implement the exact policy table above in one `main.py`
2. Add minimal state tracking (owned land count, current inventory, last action per tile) using only dicts/lists
3. Ensure every action is legal before issuing (enough money, tile empty, etc.)
4. Add simple turn counter and early-game vs late-game switch
5. Local test harness that runs 20 random seeds without exceptions

### 5. Local acceptance gates before Kaggle upload
- `python main.py` completes 50 turns with zero exceptions on 3 different seeds
- At least 2 successful harvests + sells observed in logs
- No PICKUP without matching prior PLACE on same tile
- Final inventory sold or zero at end of episode
- Bank never goes negative
- File remains single `main.py` < 400 lines

### 6. Non-goals
- No opponent modeling or shop denial
- No machine learning or parameter search
- No complex pathfinding or multi-turn planning
- No animal breeding logic
- No handling of rare events beyond the policy table

Implement the policy table first; everything else is defensive checks only.
