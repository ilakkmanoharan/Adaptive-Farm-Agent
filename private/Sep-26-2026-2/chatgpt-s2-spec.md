**Kaggriculture Submission Spec – 2026-09-26-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed since previous submission 56572897).
- Starting rating: 600 (new-bot default). No wins/losses recorded, so no bank or opponent data available.
- No observed opponents, no observed final banks, no observed loss patterns.

### 2. Root causes we must fix
- Previous bot used `DROP` (entire inventory) on multiple turns, destroying sellable goods.
- Herd size never exceeded 1 animal; no consistent breeding or feed loop.
- Wheat purchased every turn regardless of existing inventory or land state.
- Weeds left on field for 3+ turns, blocking planting.
- Land timing: actions taken after market close, so purchases arrived too late for same-turn planting.
- No `PLACE item n` logic; goods remained in inventory instead of being sold.

### 3. Exact s2 policy table vs previous bot

| Situation                          | s1 (previous) behaviour          | s2 behaviour                                      | Priority |
|------------------------------------|----------------------------------|---------------------------------------------------|----------|
| Inventory has harvest goods        | DROP or hold                     | `PLACE item n` for every harvest good             | 1        |
| Field has weeds                    | Ignore                           | `WEED` until clear, then plant                    | 1        |
| No animals and ≥3 wheat in shed    | Buy wheat                        | Buy 1 animal if money ≥ animal cost               | 2        |
| Animal present and feed available  | Do nothing                       | `FEED` animal                                     | 2        |
| Empty field, no weeds, seeds ready | Buy wheat                        | `PLANT` if seeds in inventory, else buy 1 wheat   | 3        |
| Harvest ready                      | Hold                             | `HARVEST` then `PLACE` on next turn               | 1        |
| Money < 50 and no goods            | Buy wheat                        | `IDLE` (preserve rating)                          | 4        |
| Any other state                    | Random / buy wheat               | `IDLE`                                            | 5        |

All actions use only documented stdlib calls. Never emit `DROP`.

### 4. Task priority
1. Replace every `DROP` with `PLACE item n` logic.
2. Add weed-clear + plant sequence.
3. Add minimal 1-animal herd + feed loop.
4. Add harvest-then-place sell path.
5. Add money guard (`IDLE` when <50).
6. Remove all wheat-buy spam.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs to completion with no exceptions under 1 s per turn for 50 simulated turns.
- No `DROP` token appears in any output line.
- At least one `PLACE`, one `HARVEST`, one `WEED`, and one `FEED` appear in a 30-turn test log.
- Final inventory is empty at end of test run (goods placed/sold).
- Code remains single-file `main.py` using only Python stdlib.

### 6. Non-goals
- No opponent modelling or shop denial.
- No reinforcement learning or parameter search.
- No multi-file structure or external data.
- No attempt to maximise coins (rating only).