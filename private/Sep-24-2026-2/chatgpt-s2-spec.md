**Kaggriculture Submission Spec – 2026-09-24-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no market resolution observed).
- No opponents encountered; rating remains at starting 600.
- No data on who beat us or specific failure modes yet.

### 2. Root causes we must fix (from s1 code review)
- **DROP/PICKUP thrash**: s1 used `DROP` on every harvest cycle, dumping entire inventory instead of selective `PLACE item n`.
- **Herd size**: No cap on animal purchases; inventory filled with unsellable animals.
- **Wheat buys**: Bought wheat every turn without checking existing seed count or land availability.
- **Weeds**: No weed-clearing action; weeds accumulated and blocked planting.
- **Land timing**: Bought land before having seeds/animals ready, leaving plots idle.

### 3. Exact s2 policy table vs previous bot

| Situation                        | s1 behaviour (previous)          | s2 behaviour (new)                                      | Reason |
|----------------------------------|----------------------------------|---------------------------------------------------------|--------|
| Harvest goods ready              | `DROP`                           | `PLACE item n` (only harvested goods)                   | Avoid full dump |
| Animal count ≥ 3                 | Keep buying                      | Stop buying animals                                     | Animals unsellable |
| Wheat seeds in inventory < 2     | Buy wheat every turn             | Buy wheat only if seeds < 2 and land free               | Reduce waste |
| Weeds present on any plot        | Ignore                           | Clear one weed per turn before any buy/plant            | Prevent blockage |
| Empty plots ≥ 1 and seeds ≥ 1    | Buy land first                   | Plant on existing empty plots first                     | Better timing |
| No action possible               | Random buy                       | `PASS`                                                  | Avoid thrash |
| Bank < 50                        | Buy anything                     | Only buy wheat if seeds < 2                             | Conserve cash |

### 4. Task priority
1. Replace all `DROP` calls with `PLACE item n` for harvest goods only.
2. Add hard cap: never buy animals if current animal count ≥ 3.
3. Add wheat buy guard: buy only when seeds < 2 and ≥1 empty plot.
4. Insert weed-clear step at start of every turn if weeds detected.
5. Reorder land/plant logic: plant before buying land.
6. Add `PASS` fallback when no productive action available.
7. Single-file implementation only (`main.py`).

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without raising on any action.
- Never emits `DROP`.
- Animal count never exceeds 3.
- Wheat seed count stays ≤ 5 at all times.
- At least one weed-clear action executed when weeds present.
- No land purchase until at least one successful plant action.
- Total lines ≤ 250, pure stdlib, single file.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned parameters.
- No multi-file structure.
- No coin maximisation heuristics beyond the policy table.
- No handling of market price fluctuations.