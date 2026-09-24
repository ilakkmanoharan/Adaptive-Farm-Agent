**Kaggriculture Submission Spec – 2026-09-24-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, no episodes played yet).
- Starting rating: 600.
- No bank or opponent data available. Previous submission (56524254) also has zero recorded games.

### 2. Root causes we must fix
- Previous bot performed no actions or only invalid ones, resulting in zero scoring inventory.
- Must eliminate any DROP usage (forbidden).
- Must avoid PICKUP thrash on the same tile.
- Must maintain a small, stable herd (max 3 animals) without over-purchasing.
- Must buy wheat seed only when land is already prepared and empty.
- Must clear weeds before planting.
- Must respect action-before-market ordering and 1-second actTimeout.

### 3. Exact s3 policy table vs previous bot

| Situation                          | s2 behaviour (previous) | s3 behaviour (new) |
|------------------------------------|-------------------------|--------------------|
| Empty fertile land, no weeds       | Do nothing              | BUY wheat_seed, then PLACE 1 |
| Weeds present on land              | Do nothing              | PLOW (or equivalent weed clear) |
| Ripe crop on land                  | Do nothing              | HARVEST then PLACE n (n = count) |
| 0 animals, ≥2 empty pens           | Do nothing              | BUY chicken (max 3 total) |
| Animal inventory >0                | —                       | Never sell (animals unsellable) |
| Any other tile                     | Do nothing              | MOVE toward nearest empty fertile land |
| Inventory full of harvest goods    | —                       | PLACE n on empty shed tile |

All decisions are deterministic if-then rules. No loops, no recursion.

### 4. Task priority
1. Implement core action loop with 1-second timeout guard.
2. Add land/weed/plant/harvest/place logic per policy table.
3. Add minimal herd logic (buy up to 3 chickens only).
4. Remove every DROP reference.
5. Add simple MOVE toward target when idle.
6. Local test harness (see section 5).

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without raising or timing out.
- Never emits DROP.
- Ends with ≥1 item in shed (via PLACE) and herd size ≤3.
- No wheat purchase unless land is empty and weed-free.
- Single file `main.py` using only Python stdlib.

### 6. Non-goals
- No opponent interaction or shop denial.
- No machine learning or parameter search.
- No multi-file structure.
- No complex pathfinding or inventory optimisation beyond the policy table.