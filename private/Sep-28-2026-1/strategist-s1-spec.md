**Kaggriculture Submission Spec – 2026-09-28-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no market resolution observed).
- No opponents faced; no W/L data or bank values available from replays.
- Previous submission (56625236 / 2026-09-27-s5) has zero live ladder history.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (full inventory dump) instead of targeted PLACE n on harvest goods only. This loses all unsold items and prevents scoring.
- **Herd size**: No cap on animal purchases; animals cannot be sold, so excess animals permanently block inventory slots and action economy.
- **Wheat buys**: Unconditional wheat purchases every turn regardless of current inventory or land state.
- **Weeds**: No weed-clearing action scheduled; weeds block land use and reduce effective planting area.
- **Land timing**: Planting and harvesting not sequenced with market resolution; actions after purchase are wasted because player actions resolve before market.

### 3. Exact s1 policy table vs previous bot

| Situation                          | Previous bot (2026-09-27-s5)          | s1 policy (2026-09-28-s1)                          |
|------------------------------------|---------------------------------------|----------------------------------------------------|
| Harvest goods in inventory         | DROP                                  | PLACE n (only the harvested goods)                 |
| Animal count ≥ 4                   | Buy more animals                      | Never buy animals                                  |
| Wheat in inventory < 3 and land free | Buy wheat every turn                | Buy wheat only if land is clear and no weeds       |
| Weeds present on any tile          | Ignore                                | Clear weeds first (priority over planting)         |
| Land available and no weeds        | Plant immediately                     | Plant only after weeds cleared and wheat ≥ 3       |
| Any other item                     | —                                     | Hold unless it is a harvest good → PLACE           |

### 4. Task priority
1. Implement deterministic rule engine in `main.py` that follows the s1 policy table exactly.
2. Add simple state tracking for inventory counts, animal count, weed flags, and free land tiles (stdlib only).
3. Enforce hard cap: never issue animal buy when count ≥ 4.
4. Replace every DROP with conditional PLACE n for harvest goods.
5. Add weed-clear action before any plant action.
6. Local test harness that runs 100 deterministic turns and checks policy compliance.

### 5. Local acceptance gates before Kaggle upload
- 100-turn simulation completes with zero DROP calls.
- Animal count never exceeds 3.
- Wheat is bought only when free land > 0 and weeds == 0.
- All harvest goods are placed via PLACE n (never left in inventory at turn end).
- No syntax/runtime errors under Python 3.11 stdlib only.
- Total lines ≤ 250, single file `main.py`.

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or learned parameters.
- No multi-file structure or external dependencies.
- No coin maximization heuristics beyond the policy table.