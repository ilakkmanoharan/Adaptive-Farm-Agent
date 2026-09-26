# Kaggriculture Submission 3 Specification
Date: 2026-09-26 · Slot: s3 · Folder: `2026-09-26-s3/`

Previous Kaggle id: 56579754
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-26-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating starts at 600).
- No completed episodes yet; mean bank = None (no scoring data).
- Previous bot (56579754) also had 0W-0T-0L on first upload.
- No opponent data available. All future matches will be against established bots (rating 650–900 range).

### 2. Root causes we must fix
- **DROP abuse**: Previous bot used DROP, which empties the entire inventory. Never use DROP.
- **No harvest placement**: Crops/eggs reached inventory but were never placed with `PLACE item n`, so they never scored.
- **Herd size**: Started with 0 animals; no `BUY` of chickens or cows executed.
- **Wheat buys**: No `BUY Wheat` calls, so no planting feedstock.
- **Weeds/land timing**: No `WEED` or `BUY Land` actions; land remained fallow.
- **Action ordering**: Player actions must resolve before market; bot must issue all buys/plants/places in the same turn before market tick.

### 3. Exact s3 policy table vs previous bot

| Situation                  | s2 (previous) behaviour          | s3 behaviour                                      |
|----------------------------|----------------------------------|---------------------------------------------------|
| Turn 1                     | Do nothing                       | `BUY Chicken 2`, `BUY Wheat 10`                   |
| Inventory has Wheat        | Nothing                          | `PLANT Wheat 5` (if land available)               |
| Chicken produces egg       | Nothing                          | `PLACE Egg 1` (repeat for all eggs)               |
| Inventory has produce      | DROP or idle                     | `PLACE` every harvest item; never DROP            |
| Cash >= 300                | Idle                             | `BUY Cow 1`                                       |
| Weeds present              | Ignore                           | `WEED` once per turn if any                       |
| No land left               | Idle                             | `BUY Land 1` (only after first chicken + 5 wheat) |
| End of turn                | —                                | Always end with `PLACE` for any unsold goods      |

### 4. Task priority (implement in order)
1. Replace all `DROP` with `PLACE item n` for every harvest good.
2. Add initial `BUY Chicken 2` + `BUY Wheat 10` on turn 1.
3. Add `PLANT Wheat n` when wheat in inventory and land exists.
4. Add `PLACE` loop for eggs and any future produce every turn.
5. Add `BUY Cow 1` once cash ≥ 300.
6. Add single `WEED` and conditional `BUY Land 1` after basic loop works.
7. Keep total code inside one `main.py` using only stdlib.

### 5. Local acceptance gates before Kaggle upload
- Runs 50 turns without crashing or using DROP.
- Produces at least 3 placed items (eggs or wheat) by turn 30.
- Bank never goes negative.
- No external libraries or env API inventions.
- Single file `2026-09-26-s3/main.py` passes `python -m pyright` and runs in <1s per turn.

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No complex crop rotation or late-game optimization.
