# Kaggriculture Submission 3 Specification
Date: 2026-09-25 · Slot: s3 · Folder: `2026-09-25-s3/`

Previous Kaggle id: 56551831
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s3 Submission Spec**

**Folder:** `2026-09-25-s3/`  
**Target file:** `main.py` (single stdlib file, <1s per turn)  
**Previous:** 56551831 (2026-09-25-s2)

### 1. Ladder facts
- Record: 0W-0T-0L  
- Mean bank: None (no completed episodes)  
- No opponent data available. All rating changes will be determined by first 5–10 live matches after upload.

### 2. Root causes to fix (from s2 behavior patterns)
- **DROP/PICKUP thrash**: s2 used DROP on harvest turns, dumping entire inventory instead of selective PLACE.  
- **Herd size**: Over-purchased animals early; animals cannot be sold and block shed space.  
- **Wheat buys**: Bought wheat seed every turn regardless of existing inventory or land state.  
- **Weeds**: Never cleared weeds before planting, leading to zero-yield plots.  
- **Land timing**: Bought extra land before existing plots were planted or harvested, wasting coins on idle tiles.

### 3. Exact s3 policy table (vs s2)

| Situation                          | s2 action                  | s3 action                                      | Reason |
|------------------------------------|----------------------------|------------------------------------------------|--------|
| Weeds present on any plot          | Ignore / plant             | PLOW all weeded plots first                    | Zero-yield otherwise |
| Shed has harvest goods             | DROP or nothing            | PLACE n for each harvest item (n = count)      | Avoid full dump |
| No wheat seed and plots ready      | Buy 1 wheat seed           | Buy wheat seed only if <2 in inventory         | Prevent overbuy |
| Animal count ≥ 3                   | Buy more animals           | Never buy animals                              | Unsold animals hurt rating |
| Empty plots + wheat seed ≥ 1       | Buy land                   | PLANT wheat on existing empty plots first      | Land only after all plots used |
| Bank < 50 and no harvest ready     | Buy seed/land              | Do nothing (wait)                              | Preserve coins |
| Harvest ready on any plot          | —                          | HARVEST then PLACE n                           | Score inventory |

All other actions default to the highest-priority matching row above. No market selling logic (unsold inventory does not score).

### 4. Task priority (implement in this order)
1. Weed detection + PLOW before any plant action.
2. Replace all DROP with PLACE n.
3. Add animal purchase guard (never buy if count ≥ 3).
4. Wheat seed purchase guard (only if inventory < 2).
5. Land purchase guard (only if no empty plots remain).
6. Simple turn-order: weeds → harvest/place → plant → guarded buys.

### 5. Local acceptance gates (before upload)
- Run 20 deterministic local episodes with fixed seed.
- Zero uses of DROP in any episode.
- Animal count never exceeds 3.
- Wheat seed purchases only occur when inventory < 2.
- At least one full harvest cycle completes with inventory placed (not dropped).
- No turn exceeds 200 ms wall time.

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned parameters.
- No multi-file structure.
- No market selling or coin-focused logic.
- No land expansion beyond 4 plots.
