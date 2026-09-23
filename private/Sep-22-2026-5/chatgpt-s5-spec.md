**Kaggriculture Submission Spec – 2026-09-22-s5**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no data).
- No opponents observed. No W/L/T changes recorded. Previous submission (56474734 / s4) has not yet produced usable ladder signal.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: s4 used DROP (entire inventory) and repeated PICKUP. This is banned; only PLACE n for harvested goods.
- **Herd size**: No animal management policy; animals cannot be sold so over-purchase risks permanent inventory lock.
- **Wheat buys**: No timing or quantity rule; buys occurred without checking existing seed/land state.
- **Weeds**: No explicit weed-clearing action sequence.
- **Land timing**: Actions taken before land was ready or after market resolution, violating “player actions before market” ordering.
- All fixes must be deterministic rules inside one stdlib main.py; no external state files.

### 3. Exact s5 policy table vs previous bot

| Situation (checked in order) | s4 behaviour (previous) | s5 behaviour (new) |
|------------------------------|--------------------------|--------------------|
| Inventory contains harvested goods | DROP or PICKUP | PLACE n (only harvested items, n = count) |
| Weeds present on any owned land | Ignore | Clear weeds first (one action per turn) |
| No wheat seed and land ready | Buy 1 wheat seed | Buy exactly 1 wheat seed only if land is empty and ready |
| Animals available and money > 200 | Buy 1 animal | Never buy animals (herd size = 0 policy) |
| Land not yet purchased | Buy cheapest land | Buy land only when current land is fully utilised and bank ≥ 150 |
| Nothing else matches | Random / idle | Idle (do nothing) |

Policy is evaluated once per turn using only visible board state. No loops, no recursion.

### 4. Task priority
1. Implement PLACE-only harvest handling (remove all DROP).
2. Add weed-clearing rule.
3. Add wheat-seed buy guard (land-ready check).
4. Hard-disable animal purchases.
5. Add minimal land-timing guard.
6. Ensure entire logic fits in one main.py using only stdlib.

### 5. Local acceptance gates before Kaggle upload
- Script runs to completion in < 0.8 s per turn for 100 simulated turns (actTimeout = 1 s).
- No DROP calls appear in any code path.
- No animal purchase calls.
- PLACE is only called on harvested goods with correct count.
- Wheat buy only occurs when land is empty and ready.
- No syntax/runtime errors under Python 3.11 stdlib only.
- Single file: `2026-09-22-s5/main.py`.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned parameters.
- No multi-file structure.
- No coin maximisation heuristics beyond the policy table.
- No handling of future rule changes.