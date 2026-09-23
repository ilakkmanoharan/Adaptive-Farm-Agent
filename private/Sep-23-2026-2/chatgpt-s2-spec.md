**Kaggriculture Submission Spec – 2026-09-23-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission, no episodes completed).
- Mean bank: None (no scored games).
- Starting rating: 600.
- No opponent data available. Previous submission (56484201) also has zero recorded games.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP on harvest goods. Rule: never use DROP. Use `PLACE item n` only for harvested goods.
- **Herd size**: No animals purchased or managed; inventory stayed empty.
- **Wheat buys**: No wheat seed purchases timed to growth cycles.
- **Weeds**: No weeding actions observed.
- **Land timing**: No land purchases or planting timing relative to market resolution.
- General: Player actions must resolve before market; unsold inventory scores zero.

### 3. Exact s2 policy table vs previous bot

| Situation                        | s1 (previous) behaviour          | s2 policy (new)                                      |
|----------------------------------|----------------------------------|------------------------------------------------------|
| Harvest goods in inventory       | DROP                             | `PLACE item n` (n = count)                           |
| Wheat seed available in shop     | Ignore                           | Buy 1 wheat seed if money ≥ 10 and no wheat growing  |
| Empty plot + wheat seed owned    | Skip                             | Plant wheat immediately                              |
| Weeds present on any plot        | Ignore                           | Weed one plot per turn until clear                   |
| Money ≥ 50 + no animals          | Ignore                           | Buy 1 chicken (if available)                         |
| Chicken owned + no feed          | —                                | Buy wheat seed to feed later                         |
| Any other item                   | Random/ignore                    | Hold only harvest goods; sell nothing (animals unsellable) |
| End of turn with goods           | DROP or hold                     | PLACE goods only; never DROP                         |

### 4. Task priority
1. Implement core loop with `PLACE` instead of `DROP`.
2. Add wheat buy + plant logic on empty plots.
3. Add weed removal when weeds detected.
4. Add single chicken purchase when money ≥ 50.
5. Ensure all actions respect player-before-market order.
6. Keep code in single `main.py` using only stdlib.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without exception or timeout (>1s).
- Never calls DROP.
- Performs at least one `PLACE`, one wheat buy, one plant, and one weed action in test runs.
- Bank never goes negative.
- Code fits in one `main.py` file with no external dependencies.

### 6. Non-goals
- No RL or learning.
- No opponent shop interference.
- No multi-file structure.
- No animal selling logic.
- No complex inventory management beyond wheat/chicken basics.