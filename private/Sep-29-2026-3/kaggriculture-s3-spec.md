# Kaggriculture Submission 3 Specification
Date: 2026-09-29 · Slot: s3 · Folder: `2026-09-29-s3/`

Previous Kaggle id: 56675407
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-29-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no data).
- No opponents observed; no losses or wins recorded.
- Previous submission (56675407 / 2026-09-29-s2) has zero ladder impact so far.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (dumps entire inventory). Must never emit DROP. Use only PLACE item n for harvested goods.
- **Herd size**: No animal sales possible. Must cap purchases to avoid permanent inventory bloat that never scores.
- **Wheat buys**: Over-purchasing wheat when land or time is insufficient leads to unsold inventory.
- **Weeds**: No explicit weed-clearing logic; weeds block land use.
- **Land timing**: Actions must respect that player resolves before market. Buying seed/animal/hire this turn cannot be used this turn.

### 3. Exact s3 policy table vs previous bot

| State condition                          | s2 behaviour (previous)      | s3 behaviour (new)                          | Action emitted                  |
|------------------------------------------|------------------------------|---------------------------------------------|---------------------------------|
| Weeds present on any owned land          | Ignore                       | Clear one weed per turn if possible         | CLEAR_WEED x                    |
| Empty land + wheat in inventory ≥ 1      | Buy more wheat               | Plant existing wheat                        | PLANT_WHEAT x                   |
| Empty land + no wheat                    | Buy wheat                    | Buy max 2 wheat only if land ≥ 2            | BUY_WHEAT 2 (or less)           |
| Animals in inventory > 0                 | Buy more animals             | Never buy animals                           | —                               |
| Harvest goods in inventory               | DROP                         | PLACE item n (one type at a time)           | PLACE item n                    |
| No action possible this turn             | Random buy                   | Idle (no-op)                                | (no action)                     |
| Bank < 50                                | Buy wheat/animals            | Only buy wheat if land available            | BUY_WHEAT (conditional)         |

### 4. Task priority
1. Implement core loop that reads state and emits exactly one legal action per turn.
2. Add weed-clearing check before any planting.
3. Enforce wheat purchase cap (max 2) and only when empty land exists.
4. Replace all DROP with PLACE item n logic.
5. Add animal purchase block (never buy).
6. Add simple land-count and inventory checks.
7. Ensure single-file stdlib main.py with no external imports.

### 5. Local acceptance gates before Kaggle upload
- Runs for 100 turns without crashing or emitting DROP.
- Never buys animals.
- Never buys >2 wheat in one turn.
- Uses PLACE instead of DROP on every harvest.
- Clears at least one weed when weeds are present.
- Produces only valid actions within 1s actTimeout.
- Single file `main.py` using only Python stdlib.

### 6. Non-goals
- No RL or learning.
- No opponent shop denial or market manipulation.
- No multi-file structure.
- No complex pathfinding or long-term planning beyond the policy table.
- No handling of opponent actions.
