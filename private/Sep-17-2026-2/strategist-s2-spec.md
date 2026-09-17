**Kaggriculture Submission Spec – 2026-09-17-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no market data).
- No opponents observed; no win/loss patterns or bank values available.
- Previous submission (56298529) produced zero rated games.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (entire inventory) instead of targeted PLACE n for harvest goods only. This empties the shed and prevents scoring.
- **Herd size**: No animal purchase logic; animals cannot be sold so over-purchase locks capital with zero scoring value.
- **Wheat buys**: No timing or quantity control; buys occur without checking land availability or existing inventory.
- **Weeds**: No weed-clearing action before planting or harvesting.
- **Land timing**: Actions taken on land that is not yet cleared or ready, violating player-before-market resolution.

### 3. Exact s2 policy table vs previous bot

| Situation                          | s1 (previous) behaviour          | s2 behaviour (new)                          | Reason |
|------------------------------------|----------------------------------|---------------------------------------------|--------|
| Empty land, no weeds, cash ≥ 10    | Buy wheat or do nothing          | Buy 1 wheat only if land count < 3          | Prevent over-purchase |
| Harvest goods in inventory         | DROP                             | PLACE item n (specific count)               | Avoid full shed dump |
| Weeds present on target land       | Plant anyway                     | Clear weeds first                           | Land must be clean |
| Cash < 10 or land full             | Buy animals                      | Skip animal purchase                        | Animals unsellable |
| Any turn with actTimeout risk      | Complex multi-action             | Single highest-priority action only         | 1 s limit |
| Inventory > 0 at end of turn       | Leave in inventory               | PLACE all harvest goods before market       | Unsold inventory scores 0 |

### 4. Task priority
1. Replace all DROP with PLACE n (highest).
2. Add weed-clear before any plant action.
3. Add simple land-count guard on wheat buys (max 3 plots).
4. Remove all animal purchase code.
5. Enforce single-action-per-turn with explicit priority order.
6. Add basic end-of-turn PLACE for any remaining harvest goods.

### 5. Local acceptance gates before Kaggle upload
- main.py runs to completion in < 1 s per turn on 100 simulated turns with no exceptions.
- No DROP calls appear in source.
- Wheat purchase only occurs when land count < 3 and cash ≥ 10.
- At least one PLACE n call exists for every harvest good type.
- No animal purchase lines remain.
- Code uses only stdlib (no external imports).

### 6. Non-goals
- No opponent modelling or shop denial.
- No reinforcement learning or learned parameters.
- No multi-turn planning or state search.
- No custom data structures beyond simple counters and lists.