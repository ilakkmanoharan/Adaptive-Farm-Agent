# Kaggriculture Submission 1 Specification
Date: 2026-09-24 · Slot: s1 · Folder: `2026-09-24-s1/`

Previous Kaggle id: 56511466
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-24-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed since last submission).
- Starting rating: 600 (new bot reset).
- No opponent data available. No observed wins, losses, or bank values.
- Previous submission (56511466) produced no rated games.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (entire inventory) instead of targeted PLACE. This must be eliminated.
- **Herd size**: No animal management logic; animals cannot be sold so over-purchase wastes turns and space.
- **Wheat buys**: No timing or quantity control; bought without checking land or season.
- **Weeds**: No weeding action scheduled; weeds reduce yield on planted tiles.
- **Land timing**: No early land purchase or expansion; stayed on initial tiles too long.
- All fixes must fit in one stdlib main.py with 1 s actTimeout.

### 3. Exact s1 policy table vs previous bot

| Situation                          | Previous bot                          | s1 policy (new)                                      |
|------------------------------------|---------------------------------------|------------------------------------------------------|
| Harvest goods in inventory         | DROP (entire)                         | PLACE item n (only the harvested stack)              |
| Empty hands, weeds present         | Ignore                                | WEED nearest weed tile                               |
| No wheat seed, land available      | Buy 1 wheat seed every turn           | Buy wheat seed only if < 3 seeds and ≥ 2 empty tiles |
| Animal in shop                     | Buy if money > 100                    | Never buy animals (cannot sell)                      |
| Land available and money ≥ 200     | Never buy land                        | Buy 1 land tile if current tiles ≤ 4                 |
| Multiple harvest goods             | PLACE all at once                     | PLACE one stack per turn, oldest first               |
| No action possible                 | Idle                                  | MOVE to nearest empty or weed tile                   |

### 4. Task priority
1. Remove all DROP calls; replace with PLACE n.
2. Add simple weed scan + WEED action.
3. Add land purchase check (money ≥ 200 and tiles ≤ 4).
4. Add wheat seed purchase guard (max 3 seeds, require empty tiles).
5. Block all animal purchases.
6. Implement basic tile counting and inventory stack tracking.

### 5. Local acceptance gates before Kaggle upload
- main.py runs without syntax/runtime errors for 100 turns.
- No DROP appears in source.
- At least one WEED and one PLACE executed in a 50-turn local run.
- Wheat seed count never exceeds 3.
- No animal purchase code path exists.
- Code uses only stdlib (no external imports).

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No complex crop rotation or season tracking.
- No inventory scoring logic beyond PLACE.
