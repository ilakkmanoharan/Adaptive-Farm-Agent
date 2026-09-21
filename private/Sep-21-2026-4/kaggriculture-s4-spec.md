# Kaggriculture Submission 4 Specification
Date: 2026-09-21 · Slot: s4 · Folder: `2026-09-21-s4/`

Previous Kaggle id: 56441842
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s4 Submission Spec**

**Date:** 2026-09-21 slot 4/5  
**Folder:** `2026-09-21-s4/`  
**Target file:** `main.py` (single stdlib file, <1s per turn)  
**Previous:** submission 56441842 (2026-09-21-s3)

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no completed episodes yet).
- Mean bank: None (no scoring data).
- No opponents observed; ladder position still at default 600.
- No W/L/T deltas or bank values available from replays.

### 2. Root causes we must fix
- Previous bot performed repeated PICKUP/DROP cycles on harvest goods instead of direct PLACE n.
- Herd size never exceeded 1–2 animals; no consistent wheat purchase timing.
- Weeds accumulated on unplanted tiles; land timing left fields idle after harvest.
- Inventory left unsold at episode end (no scoring).
- No explicit rule to avoid DROP entirely.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behaviour (previous)          | s4 behaviour (new)                                      |
|------------------------------------|----------------------------------|---------------------------------------------------------|
| Empty field + wheat in inventory   | PICKUP then later DROP           | PLACE wheat n on empty field                            |
| Harvest ready                      | PICKUP                           | PLACE harvest n directly into shed (never DROP)         |
| Bank ≥ 20 and no wheat seed        | Buy 1 wheat seed                 | Buy 2 wheat seeds                                       |
| Bank ≥ 50 and herd < 3             | Skip                             | Buy 1 animal (max herd 3)                               |
| Weeds present on any tile          | Ignore                           | Clear one weed per turn if no higher-priority action    |
| Field empty after harvest          | Idle                             | Buy/place wheat seed immediately                        |
| Inventory > 0 at end of turn       | Hold                             | Sell all sellable goods before end of turn              |
| Any other state                    | Default loop                     | Follow priority order: sell → place harvest → plant → buy wheat → buy animal → clear weed |

### 4. Task priority
1. Replace all DROP usage with PLACE item n (highest).
2. Add wheat purchase rule (bank ≥ 20 → buy 2).
3. Add animal purchase rule (bank ≥ 50 and herd < 3).
4. Add weed-clearing rule when no planting/selling action available.
5. Add end-of-turn sell-all logic.
6. Ensure single main.py with only stdlib (no external deps).

### 5. Local acceptance gates before Kaggle upload
- Run 20 local episodes; final inventory must be 0 in ≥ 18 episodes.
- Herd size must reach exactly 3 in ≥ 15 episodes.
- No DROP action logged in any run.
- Average wheat seeds planted per episode ≥ 4.
- Turn time < 0.8 s in all local runs.
- Code must be one file `main.py` using only stdlib.

### 6. Non-goals
- No opponent shop interaction or denial.
- No RL or learned policy.
- No multi-file structure.
- No changes to land purchase timing beyond the rules above.
- No new data structures beyond simple counters and lists.
