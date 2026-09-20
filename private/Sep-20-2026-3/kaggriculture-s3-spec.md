# Kaggriculture Submission 3 Specification
Date: 2026-09-20 · Slot: s3 · Folder: `2026-09-20-s3/`

Previous Kaggle id: 56391878
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-20-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (fresh bot, rating starts at 600).
- Bank: None observed (no completed episodes).
- No opponent data available. Previous submission (56391878) also has zero recorded games. All policy changes are therefore pre-emptive and based on known failure modes of the prior bot in 2026-09-20-s2.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: previous bot issued DROP on every failed sell attempt, emptying the entire shed instead of using targeted PLACE.
- **Herd size**: over-purchased animals early, locking capital with no sell path (animals cannot be sold).
- **Wheat buys**: bought wheat seed every turn regardless of existing inventory or land availability.
- **Weeds**: never cleared weeds before planting, causing zero-yield turns.
- **Land timing**: planted on day 1 of new land without waiting for clear/weed-free state; harvested too late, missing market window.
- No use of PLACE n for harvested goods; relied on implicit sell that failed.

### 3. Exact s3 policy table vs previous bot

| State (checked in order)                  | s3 Action (main.py)                  | Previous bot behaviour          | Reason |
|-------------------------------------------|--------------------------------------|----------------------------------|--------|
| Weeds present on any owned land           | CLEAR_WEED on first weeded tile      | Plant anyway                     | Zero yield otherwise |
| Shed has harvest goods (any qty)          | PLACE 1 (repeat until shed empty)    | DROP or nothing                  | Avoid total inventory loss |
| No clear land available                   | BUY_LAND (max 1 per turn)            | Buy multiple animals             | Land is the bottleneck |
| Clear land exists + wheat seed ≥ 1        | PLANT_WHEAT on first clear tile      | Plant wheat every turn           | Only plant when land ready |
| Wheat seed == 0 and cash ≥ 10             | BUY_WHEAT_SEED (max 3)               | Buy every turn                   | Prevent over-buy |
| Animals == 0 and cash ≥ 50 and land ≥ 2   | BUY_ANIMAL (max 1)                   | Buy animals first                | Limit herd to 1 until profitable |
| Cash < 10 and shed empty                  | SELL (any non-animal item)           | No explicit sell                 | Force liquidation |
| All above false                           | WAIT                                 | Random buys                      | Safe default |

Policy is evaluated once per turn in the listed order. Only one action type is emitted per turn.

### 4. Task priority
1. Implement the exact state machine above in `2026-09-20-s3/main.py` using only stdlib.
2. Add minimal state tracking (current land status, shed contents, cash, animal count) via simple dicts/lists.
3. Ensure no DROP is ever emitted.
4. Add 1-second actTimeout guard (simple time check before action).
5. Produce a single runnable `main.py` that reads stdin and writes one action line.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs without import errors or external packages.
- 100 consecutive turns execute without emitting DROP.
- Herd size never exceeds 1 in any simulated 50-turn trace.
- At least one PLACE action is emitted when shed contains goods.
- No wheat purchase when seed count > 0.
- Code contains only stdlib (no numpy, pandas, etc.).

### 6. Non-goals
- No opponent modelling or shop denial.
- No reinforcement learning or learned parameters.
- No multi-file structure.
- No complex pathfinding or inventory optimisation beyond the table above.
- No handling of rare edge cases not listed in the policy table.
