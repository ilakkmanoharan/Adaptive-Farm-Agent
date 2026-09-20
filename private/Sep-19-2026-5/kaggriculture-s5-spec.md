# Kaggriculture Submission 5 Specification
Date: 2026-09-19 · Slot: s5 · Folder: `2026-09-19-s5/`

Previous Kaggle id: 56370908
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s5 Submission Spec**  
Date: 2026-09-19 | Slot: 5/5 | Folder: `2026-09-19-s5/`  
Previous: 56370908 (s4)

### 1. Ladder facts from these games
- Record: 0W-0T-0L  
- Mean bank: None (no episodes completed)  
- No opponents observed. No W/L data, no bank values, no loss patterns available.

### 2. Root causes we must fix (from s4 code review)
- **DROP/PICKUP thrash**: s4 used `DROP` on harvest goods. Rule violation — entire inventory lost. Must switch to `PLACE item n`.
- **Herd size**: No cap. Animals kept growing past profitable land use.
- **Wheat buys**: Bought wheat every turn regardless of land or season timing.
- **Weeds**: No weed removal action; weeds reduced effective land.
- **Land timing**: Actions taken after buying land in same turn (violates “player actions resolve before market”).
- **Inventory scoring**: Unsold goods at end of episode contributed 0.

### 3. Exact s5 policy table vs previous bot

| Situation                          | s4 behaviour (remove)              | s5 behaviour (implement)                          | Priority |
|------------------------------------|------------------------------------|---------------------------------------------------|----------|
| Harvest goods ready                | DROP                               | `PLACE item n` (one at a time)                    | 1        |
| Animal count ≥ 4                   | Continue buying                    | Stop buying animals                               | 2        |
| Wheat in shop & land available     | Buy every turn                     | Buy wheat only if ≥1 empty land tile              | 2        |
| Weeds present on owned land        | Ignore                             | Remove weed first action if any                   | 3        |
| New land just purchased            | Act on it same turn                | Wait one turn before using new land               | 3        |
| Inventory > 0 at end of turn       | —                                  | Sell highest-value item first                     | 1        |
| No profitable action               | Buy random                         | Do nothing (pass)                                 | 4        |

### 4. Task priority (implement in order)
1. Replace all `DROP` with `PLACE item n`.
2. Add animal cap (max 4) and wheat buy guard (only if empty land).
3. Add weed removal check at start of turn.
4. Enforce one-turn delay after land purchase.
5. Add simple sell logic for highest-value item when inventory > 0.
6. Add pass when no valid action.

### 5. Local acceptance gates before Kaggle upload
- `main.py` runs in < 0.8 s per turn for 200 turns (actTimeout = 1 s).
- No `DROP` calls anywhere in code.
- Herd size never exceeds 4 in any simulated episode.
- At least one `PLACE` call executed when harvest goods exist.
- No action taken on land bought in the same turn.
- Code uses only stdlib + provided env calls (no new APIs).

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No coin-based scoring logic (ladder uses W/L/T only).
- No complex crop rotation or seasonal calendars.
