**Kaggriculture Submission Spec – 2026-09-21-s1**

### 1. Ladder facts from these games (W/L, banks, who beat us and how)
- Record: 0W-0T-0L. New bot starts at 600 rating.
- No completed episodes. Mean bank = None.
- No opponent data available. All future matches will be against existing ladder bots (previous submission 56408457 from 2026-09-20-s5 folder).

### 2. Root causes we must fix
- Previous bot used DROP on unsold goods, losing all inventory value.
- Over-purchased wheat seeds without matching land or timing, leading to idle turns.
- No weed control (PICKUP on weeds never prioritized).
- Herd size started too high or at wrong time; animals cannot be sold and consume actions.
- Land timing was reactive instead of pre-planned (buy land before seeds arrive).
- PICKUP/DROP thrash on harvest goods instead of direct PLACE.

### 3. Exact s1 policy table vs the previous bot

| Situation                        | Previous bot (2026-09-20-s5)          | s1 policy (2026-09-21-s1)                          | Reason |
|----------------------------------|---------------------------------------|----------------------------------------------------|--------|
| Inventory has harvest goods      | DROP or PICKUP                        | PLACE item n (only)                                | Avoid total loss |
| Weeds present on owned land      | Ignore or buy more seeds              | PICKUP weed first                                  | Prevent land degradation |
| No owned land + cash >= 200      | Buy seeds                             | BUY land (1 plot)                                  | Secure planting space first |
| Owned land empty + seeds >= 1    | Plant immediately                     | PLANT wheat on empty plot                          | Maximize turns |
| Cash >= 80 and land available    | Buy wheat seeds                       | BUY wheat seed (max 2 per turn)                    | Controlled buying |
| Animals in inventory             | Place or keep                         | Never buy animals (policy = 0)                     | Cannot sell, wastes actions |
| Turn count mod 4 == 0            | Random action                         | Check weeds → PLACE → PLANT → BUY seed             | Deterministic order |
| No action possible               | SKIP                                  | SKIP                                               | Same |

### 4. Task priority
1. Implement core loop with strict action ordering (weed → place → plant → buy land/seed).
2. Hard-code zero animal purchases.
3. Replace all DROP with PLACE n.
4. Add simple cash/land/seed counters to avoid overbuy.
5. Single-file main.py only (stdlib).

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without exception or timeout (>1s).
- Never emits DROP action.
- Never buys any animal.
- Produces at least one successful PLACE of harvest goods.
- Bank never goes negative on seed/land buys.
- Code fits in one main.py with no external files.

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No complex herd management.