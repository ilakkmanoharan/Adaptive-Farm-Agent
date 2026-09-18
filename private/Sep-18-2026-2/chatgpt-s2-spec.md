**Kaggriculture Submission Spec – 2026-09-18-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission, no episodes completed).
- Mean bank: None (no scoring data).
- Starting rating: 600.
- No opponents observed; no win/loss patterns available.
- Previous submission (56324010 / 2026-09-18-s1) has zero ladder history.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: s1 used DROP (dumps entire inventory). s2 must never call DROP; only use PLACE n on harvest goods.
- **Herd size**: No animal sales allowed. s1 likely over-purchased animals without space/plan. s2 caps total animals at 3 and only buys after securing feed/land.
- **Wheat buys**: s1 bought wheat without checking existing inventory or land timing. s2 buys wheat only when inventory < 2 and a free plot exists.
- **Weeds**: No weed handling in s1. s2 adds explicit WEED action on any plot with weeds before planting.
- **Land timing**: s1 planted without checking plot availability or season. s2 only plants on empty plots and only after current turn actions resolve before market.

### 3. Exact s2 policy table vs previous bot

| Situation                        | s1 (previous) behaviour          | s2 policy (new)                                      |
|----------------------------------|----------------------------------|------------------------------------------------------|
| Inventory full + harvest ready   | DROP                             | PLACE n (only harvest goods)                         |
| Empty plot + weeds present       | Plant anyway                     | WEED first                                           |
| Empty plot + no weeds + seeds    | Plant immediately                | Plant only if inventory ≥ 2 seeds                    |
| Animal count < 3 + money ≥ 50    | Buy animal                       | Buy only if feed inventory ≥ 4                       |
| Wheat inventory < 2 + money ≥ 10 | Buy wheat                        | Buy wheat only if free plot exists                   |
| No free plots                    | Idle / buy more                  | Sell lowest-value harvest good via PLACE             |
| Turn start                       | Any order                        | Fixed order: WEED → PLACE → PLANT → BUY (if safe)    |

### 4. Task priority
1. Remove all DROP calls; replace with PLACE n logic.
2. Add weed detection and WEED action before any plant.
3. Implement simple plot-state tracking (empty/weeded/occupied).
4. Add hard cap of 3 animals + feed check before purchase.
5. Add wheat buy guard (inventory < 2 AND free plot).
6. Enforce action order that respects “player before market”.
7. Single-file main.py only (stdlib).

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without exception or timeout (>1s).
- Never emits DROP.
- Animal count never exceeds 3.
- At least one successful PLACE of harvest goods.
- No wheat purchase when inventory ≥ 2 or no free plots.
- Produces non-zero score on at least one local episode.

### 6. Non-goals
- No RL or learning.
- No opponent shop interference.
- No multi-file structure.
- No complex inventory optimization beyond the policy table.
- No handling of future seasons or weather.