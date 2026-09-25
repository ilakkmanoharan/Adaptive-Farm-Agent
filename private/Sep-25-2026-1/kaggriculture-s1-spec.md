# Kaggriculture Submission 1 Specification
Date: 2026-09-25 · Slot: s1 · Folder: `2026-09-25-s1/`

Previous Kaggle id: 56536518
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-25-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission on ladder).
- Mean bank: None (no episodes completed).
- Starting rating: 600.
- No opponent data available. Previous submission (56536518) also has zero recorded games.

### 2. Root causes we must fix
- Previous bot (2026-09-24-s5) had no functional harvest-to-market loop.
- Risk of DROP/PICKUP thrash on every turn (explicitly forbidden).
- No herd-size control (animals cannot be sold, so over-purchase locks capital).
- No wheat seed purchase discipline (buy only when land is ready).
- No weed handling or land timing (planting on weeded/untimed plots wastes turns).
- Inventory left unsold at end of episode (scores 0).

### 3. Exact s1 policy table vs previous bot

| Situation                          | 2026-09-24-s5 behaviour          | 2026-09-25-s1 behaviour (new)                          |
|------------------------------------|----------------------------------|-------------------------------------------------------|
| No land owned                      | Do nothing                       | Buy 1 land if bank ≥ 120                              |
| Land owned, weeds present          | Ignore                           | Hire 1 worker to clear weeds (max 1 per turn)         |
| Land ready, no wheat               | Buy wheat randomly               | Buy wheat seeds only if land is clear and bank ≥ 30   |
| Wheat ready to harvest             | —                                | Harvest then immediately PLACE item 1 (never DROP)    |
| Harvest goods in inventory         | Hold or DROP                     | PLACE all harvest goods to market every turn          |
| Bank ≥ 200 and no animals          | Buy animals freely               | Buy at most 2 animals total (sheep or cows)           |
| Bank < 80                          | Buy anything                     | Only buy wheat seeds or clear weeds                   |
| Turn limit approaching             | —                                | Sell everything via PLACE; no new purchases           |

### 4. Task priority
1. Implement land/weed/wheat/PLACE loop (core scoring path).
2. Add minimal herd cap (max 2 animals).
3. Add bank guards to prevent negative balance.
4. Remove any DROP usage.
5. Single-file main.py only.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without exception or timeout (>1s).
- Never calls DROP.
- Never buys >2 animals.
- Always uses PLACE for harvested goods.
- Ends with inventory == 0 on at least 80% of simulated episodes.
- Bank never goes negative.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No complex crop rotation or animal breeding logic.
