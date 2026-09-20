# Kaggriculture Submission 1 Specification
Date: 2026-09-20 · Slot: s1 · Folder: `2026-09-20-s1/`

Previous Kaggle id: 56375217
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-20-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no scoring data).
- Starting rating: 600.
- No opponents observed; no losses or bank values recorded.
- Previous submission (56375217) produced no usable ladder data.

### 2. Root causes we must fix
- Never emit DROP (dumps entire inventory).
- Use PLACE item n only on harvest goods; never on animals.
- Prevent herd-size bloat (animals cannot be sold, so cap purchases).
- Avoid buying wheat when inventory already holds unsold stock.
- Clear weeds before they block planting windows.
- Time land purchases only after current plots are fully utilized and inventory is moving.
- Eliminate PICKUP/PLACE thrash on the same tile in one turn.

### 3. Exact s1 policy table vs previous bot

| Situation                          | s1 action (new)                          | Previous bot (2026-09-19-s5) |
|------------------------------------|------------------------------------------|------------------------------|
| Empty plot + no weeds + seeds in inv | PLANT seed                               | Same                         |
| Weeds present                      | CLEAR                                    | Same                         |
| Harvest ready                      | PICKUP then PLACE item n (one good)      | PICKUP + possible DROP       |
| Animal slot open + bank ≥ 120      | BUY animal (max 2 total)                 | Unlimited buys               |
| Wheat in market + inv wheat < 8    | BUY wheat (min(8, affordable))           | Overbuy                      |
| Unsold harvest goods ≥ 6           | SELL highest-value good                  | Hold or DROP                 |
| Free land available + plots full   | BUY land (1 at a time)                   | Buy multiple early           |
| Nothing else productive            | WAIT                                     | Same                         |

All actions respect “player before market” and 1 s timeout. Single action per turn.

### 4. Task priority
1. Core loop: read state, apply policy table, output single legal action.
2. Inventory tracking (count only sellable goods; ignore animals).
3. Weed & plot state machine (CLEAR before PLANT).
4. Herd cap at 2 animals.
5. Wheat buy limit (≤8) and sell logic.
6. Land buy only when all existing plots occupied.
7. Replace any DROP with PLACE item n.
8. Local test harness using stdlib only.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns with zero DROP commands.
- Herd size never exceeds 2.
- Wheat purchases stop at 8 when inventory already holds wheat.
- At least one successful SELL of harvest goods per 20 turns.
- No PICKUP immediately followed by PLACE on same tile in same turn.
- Code is single `main.py` using only Python stdlib; runs in <1 s per turn on empty input.

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policies.
- No multi-file structure.
- No complex pathfinding or multi-turn planning beyond the policy table.
