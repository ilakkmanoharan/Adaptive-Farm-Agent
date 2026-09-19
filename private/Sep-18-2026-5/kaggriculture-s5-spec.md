# Kaggriculture Submission 5 Specification
Date: 2026-09-18 · Slot: s5 · Folder: `2026-09-18-s5/`

Previous Kaggle id: 56340820
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-18-s5**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating starts at 600)
- Mean bank: None (no episodes completed)
- No opponent data available. Previous submission (56340820) also has zero recorded games.

### 2. Root causes we must fix
- No prior policy exists to compare against; s4 folder contains no runnable logic.
- Must avoid any use of `DROP` (dumps entire inventory).
- Must never sell animals.
- Must respect action-before-market ordering.
- Must keep inventory moving to shed only via `PLACE item n` on harvest goods.
- Must avoid thrashing on pickup/place cycles.
- Must not over-buy wheat or let weeds accumulate.
- Must manage land timing so planting occurs on empty tiles only after harvest.

### 3. Exact s5 policy table vs previous bot

| Situation                          | s5 Action (new)                          | Reason |
|------------------------------------|------------------------------------------|--------|
| Empty tile + wheat in inventory    | PLANT wheat                              | Basic production |
| Ripe wheat on tile                 | HARVEST                                  | Convert to goods |
| Harvest goods in inventory         | PLACE item n (n = count of goods)        | Score points, avoid unsold inventory |
| Empty tile + no wheat              | BUY wheat (min 1, max 3)                 | Controlled restock |
| Weeds present on any tile          | WEED                                     | Prevent tile loss |
| Animal tile ready                  | COLLECT                                  | Only action allowed on animals |
| No safe action                     | WAIT                                     | Prevent invalid moves |
| Any other state                    | WAIT                                     | Default safe action |

Never emit `DROP`, never sell animals, never buy >3 wheat per turn.

### 4. Task priority
1. Implement core loop that reads observation and emits one of: PLANT, HARVEST, PLACE, BUY, WEED, COLLECT, WAIT.
2. Add minimal state tracking for last action to avoid pickup/place thrash.
3. Add simple wheat count guard (≤3).
4. Add weed priority check before planting.
5. Add harvest-before-place ordering.
6. Ensure single-file `main.py` uses only stdlib.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs without import or syntax errors.
- On a 10-turn simulated loop with 3 empty tiles + 2 wheat, bot produces at least one PLACE action.
- No `DROP` string ever appears in output.
- Bank and inventory values remain non-negative across 20 simulated turns.
- Total lines of code ≤ 120.

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or learned parameters.
- No multi-file structure.
- No complex pathfinding or long-term planning beyond the policy table.
- No handling of special events or rare items.
