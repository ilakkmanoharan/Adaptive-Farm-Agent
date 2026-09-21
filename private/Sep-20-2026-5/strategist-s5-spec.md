**Kaggriculture s5 Submission Spec**

**Folder:** `2026-09-20-s5/`  
**Base:** `2026-09-20-s4` (id 56403810)  
**Goal:** First non-zero W/L/T record on live ladder. Single-file `main.py` only.

### 1. Ladder facts
- Record: 0W-0T-0L  
- Mean bank: None (no episodes completed)  
- No opponent data available. All new bots start at 600 rating. No wins/losses recorded yet.

### 2. Root causes to fix
- Previous bot performed unnecessary PICKUP/DROP cycles on harvest goods (violates “never DROP” rule).  
- Herd size never exceeded 1 animal; no consistent milk/egg production.  
- Bought wheat seeds every turn regardless of land state or existing inventory.  
- No weed removal logic; weeds blocked planting on multiple tiles.  
- Land timing: actions taken after market resolution instead of before; missed early planting windows.  
- Inventory left unsold at end of episodes (scores 0).

### 3. Exact s5 policy table (vs s4)

| Situation                          | s4 behaviour                  | s5 behaviour                                      | Priority |
|------------------------------------|-------------------------------|---------------------------------------------------|----------|
| Empty fertile tile + wheat seeds ≥1 | Buy wheat if money > 50      | PLANT wheat if seeds > 0 else BUY 1 wheat        | 1        |
| Tile has mature crop               | PICKUP then sometimes DROP   | PICKUP then PLACE 1 (never DROP)                 | 1        |
| Weeds on any tile                  | Ignore                       | REMOVE weed (highest priority if present)        | 1        |
| Money ≥ 120 and no animal          | Never bought                 | BUY 1 chicken (if none) or 1 cow                 | 2        |
| Animal present + product ready     | Ignored                      | COLLECT product                                  | 1        |
| Product in inventory               | Held or dropped              | SELL all product every turn                      | 1        |
| No fertile land left               | Did nothing                  | BUY land only if money ≥ 200 and no other action | 3        |
| Turn with no other action          | Random buy                   | BUY wheat seed (max 2)                           | 3        |

All actions resolve before market. Use PLACE n only for harvested goods. Never call DROP.

### 4. Task priority (implement order)
1. Weed removal + correct PICKUP/PLACE flow  
2. Basic wheat planting loop with seed buy guard  
3. Single animal purchase + COLLECT logic  
4. Sell every product every turn  
5. Minimal land buy only when idle and cash-rich  
6. Add simple turn counter to avoid late-game idling

### 5. Local acceptance gates (before upload)
- Runs 50 episodes with 0 crashes and actTimeout < 800 ms.  
- Produces ≥ 3 sales per episode on average.  
- Maintains ≥ 1 animal after turn 8 in ≥ 70 % of episodes.  
- Zero uses of DROP in all test logs.  
- Final inventory value = 0 at episode end in ≥ 80 % of runs.  
- Code remains single-file stdlib only.

### 6. Non-goals
- No opponent modeling or shop denial.  
- No multi-animal herd management beyond 1.  
- No crop rotation or advanced timing.  
- No RL or learned parameters.  
- No multi-file structure.