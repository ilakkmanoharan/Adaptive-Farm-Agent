# Kaggriculture Submission 1 Specification
Date: 2026-09-29 · Slot: s1 · Folder: `2026-09-29-s1/`

Previous Kaggle id: 56654294
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-29-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating starts at 600).
- Mean bank: None (no completed episodes).
- No prior opponents observed. All future matches will be against established bots that already have positive W/L records.

### 2. Root causes we must fix
- Previous bot used `DROP` on harvest turns, dumping entire inventory instead of scoring.
- No herd-size cap → wheat consumption outstripped planting capacity.
- Bought wheat every turn regardless of inventory, causing repeated negative cash.
- No weed-clearing action when `weeds > 0` on owned plots.
- Land purchases occurred before any crop was ready, locking cash with zero production.
- PICKUP/PLACE thrash on the same tile when multiple harvest goods existed.

### 3. Exact s1 policy table vs previous bot

| State condition                          | s1 action (priority order)          | Previous bot behaviour          |
|------------------------------------------|-------------------------------------|---------------------------------|
| `weeds > 0` on any owned plot            | CLEAR weeds                         | ignored                         |
| `cash < 20` and `inventory.wheat == 0`   | SELL any harvest goods (PLACE n)    | bought wheat                    |
| `herd.cows >= 3`                         | do not buy animals                  | bought animals every turn       |
| `inventory.harvest_goods > 0`            | PLACE item n (one at a time)        | DROP                            |
| `plots.empty >= 1` and `cash >= 50`      | BUY_LAND only if `inventory.wheat >= 10` | bought land immediately      |
| `inventory.wheat < 5` and `cash >= 8`    | BUY_WHEAT (max 8)                   | bought wheat every turn         |
| `inventory.wheat >= 5` and `plots.empty` | PLANT_WHEAT                         | did nothing                     |
| none of above                            | WAIT                                | random actions                  |

All actions use only documented API calls. No `DROP` ever issued.

### 4. Task priority
1. Implement state reader + policy table above (single `main.py`).
2. Add explicit `PLACE item n` loop for harvest goods.
3. Add weed-clear and herd-cap guards.
4. Add cash and inventory guards before any purchase.
5. Local test harness that runs 50 deterministic episodes against a fixed opponent bot.

### 5. Local acceptance gates before Kaggle upload
- 50 episodes completed with 0 uses of `DROP`.
- Final bank ≥ 120 in ≥ 70 % of episodes.
- No episode ends with negative cash.
- Herd size never exceeds 3 cows.
- Weeds cleared within 2 turns of appearing.
- All actions complete inside 1 s (stdlib only, no external libs).

### 6. Non-goals
- No opponent shop denial.
- No RL or learned policy.
- No multi-file structure.
- No land or animal speculation beyond the table above.
