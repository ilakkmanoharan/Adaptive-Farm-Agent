**Kaggriculture Submission Spec – 2026-09-19-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating still 600).
- No completed episodes; bank value reported as None.
- No opponent data available. All future matches will be against bots that have already played ≥1 game.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (which empties entire inventory) instead of targeted PLACE. This caused repeated full-inventory loss and wasted turns.
- **Herd size**: No cap on animal purchases; inventory filled with unsellable animals, blocking crop slots and scoring.
- **Wheat buys**: Bought wheat seed every turn regardless of land or season, leading to over-purchase and spoilage.
- **Weeds**: No weed-clearing action; weeds accumulated and reduced effective land.
- **Land timing**: Actions taken before checking available land; planted on insufficient plots.

### 3. Exact s3 policy table vs previous bot

| Situation                          | s2 behaviour (previous)          | s3 behaviour (new)                          | Reason |
|------------------------------------|----------------------------------|---------------------------------------------|--------|
| Inventory has harvest goods        | DROP                             | PLACE item n (only the harvested goods)     | Avoid full dump |
| Animals in inventory > 2           | Keep buying                      | Stop buying animals                         | Animals unsellable |
| Wheat seed available & land ≥ 1    | Buy wheat every turn             | Buy wheat only if current wheat < 3         | Reduce overbuy |
| Weeds present on any plot          | Ignore                           | Clear weed on lowest-numbered weeded plot   | Restore land |
| No harvest goods & land free       | Random buy                       | Buy wheat seed if wheat < 3 else do nothing | Simple stable loop |
| Any other state                    | —                                | Do nothing (pass)                           | Prevent thrash |

### 4. Task priority
1. Replace all DROP with PLACE n.
2. Add hard cap: never buy animals if current animal count ≥ 2.
3. Add wheat buy guard: only buy if wheat count < 3.
4. Insert weed-clear action before any buy/plant.
5. Add land check before any plant action.
6. Single-file main.py only; no extra modules.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns with zero exceptions and actTimeout < 1 s.
- Never emits the token “DROP”.
- Animal count never exceeds 2.
- Wheat count never exceeds 5 at end of any turn.
- At least one PLACE action executed when harvest goods exist.
- No syntax or import errors under plain `python main.py`.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No coin maximisation heuristics beyond the policy table above.