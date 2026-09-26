**Kaggriculture s4 Submission Spec**

**Folder:** `2026-09-26-s4/`  
**Target file:** `main.py` (single stdlib file, <400 LOC)  
**Previous:** 56584779 (2026-09-26-s3)  
**Current record:** 0W-0T-0L (no episodes yet)

### 1. Ladder facts from these games
- Record: 0W-0T-0L
- Mean bank: None (no completed episodes)
- No opponents observed yet. Skill rating starts at 600. No data on who beat us or how.

### 2. Root causes we must fix (from s3 replay patterns)
- **DROP/PICKUP thrash**: s3 used DROP on harvest goods, dumping entire inventory and losing scoring items. Fix: never emit DROP; only use PLACE n for harvested goods.
- **Herd size**: Over-purchased animals early; animals cannot be sold and block shed space. Fix: cap total animals at 2 (one cow + one chicken max) and only buy after land is producing.
- **Wheat buys**: Bought wheat seed every turn regardless of soil state. Fix: buy wheat seed only when current wheat count == 0 and a free plot exists.
- **Weeds**: Ignored weed growth on plots, losing land productivity. Fix: check for weeds on every plot each turn and prioritize hoe action on any weeded plot.
- **Land timing**: Delayed first land purchase until turn 8+. Fix: buy first land plot on turn 1 if bank >= 50.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behavior (previous)          | s4 behavior (new)                                      | Action emitted |
|------------------------------------|---------------------------------|--------------------------------------------------------|----------------|
| Turn 1, bank >= 50                 | Idle / buy seed                 | Buy land plot                                          | BUY LAND       |
| Any weeded plot                    | Ignore                          | Hoe the lowest-index weeded plot                       | HOE n          |
| Wheat count == 0 and free plot     | Buy wheat every turn            | Buy exactly 1 wheat seed                               | BUY WHEAT      |
| Harvested good in inventory        | DROP                            | PLACE n (specific harvested item)                      | PLACE n        |
| Bank >= 80 and animals < 2         | Buy animal                      | Buy only if wheat production stable (wheat >= 3)       | BUY COW / CHICKEN |
| No free action possible            | Random                          | SELL lowest-value harvested good if inventory > 6      | SELL n         |
| Animals >= 3                       | Continue buying                 | Never buy more animals                                 | —              |

All other actions (PLOW, PLANT, WATER, etc.) remain identical to s3 unless overridden by the table above. Never emit DROP.

### 4. Task priority (implementation order in main.py)
1. Add `never_drop` guard + replace all DROP with PLACE n logic.
2. Implement weed scan + HOE priority at start of action selection.
3. Add land purchase on turn 1 and wheat buy guard (count == 0).
4. Add animal cap (max 2) with production check.
5. Add minimal inventory management (SELL when > 6 items).
6. Wire the policy table into the existing turn loop.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns with no exceptions and no DROP action emitted.
- Produces at least one harvested good placed in shed by turn 15.
- Maintains ≤ 2 animals at all times.
- No wheat purchase when wheat count > 0.
- Executes in < 0.8 s per turn (actTimeout = 1 s).

### 6. Non-goals
- No RL or learning.
- No opponent shop denial or market manipulation.
- No multi-file structure.
- No new environment APIs or simulation code.