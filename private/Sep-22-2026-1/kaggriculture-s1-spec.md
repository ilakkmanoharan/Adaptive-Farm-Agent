# Kaggriculture Submission 1 Specification
Date: 2026-09-22 · Slot: s1 · Folder: `2026-09-22-s1/`

Previous Kaggle id: 56452874
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-22-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, no episodes yet).
- Starting rating: 600.
- Mean bank: None (no data).
- No opponents observed; no win/loss patterns available.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (dumps entire inventory). Replace with targeted PLACE item n on harvest only.
- **Herd size**: No animal sales allowed; previous bot likely over-purchased animals without sufficient feed/land, leading to idle inventory.
- **Wheat buys**: Over-bought wheat without matching land or timing, leaving unsold inventory that scores 0.
- **Weeds**: No consistent weeding action before planting cycles.
- **Land timing**: Actions resolve before market; previous bot bought land/seeds too late in turn or after market moved.

### 3. Exact s1 policy table vs previous bot

| Situation                  | Previous bot (2026-09-21-s5) | s1 policy (2026-09-22-s1) |
|----------------------------|------------------------------|---------------------------|
| Harvest ready              | DROP                         | PLACE item n (specific harvest goods only) |
| Animal purchase            | Buy any affordable           | Buy max 2 animals only if ≥3 wheat in shed |
| Wheat decision             | Buy whenever coins > 50      | Buy wheat only if land ≥ current herd size + 2 |
| Weeds present              | Ignore or plant anyway       | Weed first, then plant |
| Land available             | Buy land late in turn        | Buy land only on turn start if coins ≥ 120 and wheat surplus ≥ 4 |
| Inventory > 8 items        | Hold or DROP                 | Sell all harvest goods immediately via market action |
| No action possible         | Pass                         | Pass (explicit) |

### 4. Task priority
1. Replace all DROP calls with PLACE item n (harvest only).
2. Add wheat/land guard: buy wheat only when land check passes.
3. Insert weed action before any plant action.
4. Cap animal buys at 2 with wheat feed check.
5. Add simple sell logic for harvest goods at end of turn.
6. Ensure single-file main.py with stdlib only, <1s per action.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 simulated turns without exception or timeout.
- Never emits DROP command in any code path.
- Herd size never exceeds 2 without explicit wheat surplus check.
- All harvest actions use PLACE with index, never DROP.
- Bank never goes negative on land/wheat buys.
- Code is one self-contained main.py (no external files).

### 6. Non-goals
- No RL or learning.
- No opponent shop denial or market manipulation.
- No multi-file structure.
- No complex state tracking beyond current turn inventory/land/herd.
