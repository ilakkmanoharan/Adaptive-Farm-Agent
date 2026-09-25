**Kaggriculture Submission Spec – 2026-09-24-s5**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating starts at 600).
- No completed episodes; no opponent data, no bank values observed.
- No wins/losses to analyze. All future rating changes will come from first real matches after upload.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (dumps entire inventory). s5 must never emit DROP; only use PLACE n for harvested goods.
- **Herd size**: No animal sales possible. s5 must limit animal purchases to 0–2 per game and only when feed is already secured.
- **Wheat buys**: Over-purchasing wheat without immediate planting slots. s5 caps wheat buys at current empty tilled land + 2.
- **Weeds**: No weeding action observed in prior logic. s5 must insert WEED when any tile has weed stage ≥2.
- **Land timing**: Actions resolved before market. s5 must buy/place seeds only on already-tilled land and never rely on same-turn till+plant.

### 3. Exact s5 policy table vs previous bot

| Situation                          | s4 (previous) behaviour          | s5 behaviour                                      | Priority |
|------------------------------------|----------------------------------|---------------------------------------------------|----------|
| Empty tilled land + wheat ≥1       | Buy wheat then plant             | Plant existing wheat first; buy only if land > wheat | High     |
| Any tile weed stage ≥2             | Ignore                           | WEED highest-weed tile                            | High     |
| Harvest ready (any crop)           | PICKUP then later DROP           | PICKUP then PLACE 1–3 on same turn                | High     |
| Animal feed < 3 and animals >0     | Buy animals                      | Skip animal buy                                   | Med      |
| Empty land + no seeds              | Buy seeds                        | TILL first if land < 8                            | Med      |
| Inventory full                     | DROP                             | PLACE all harvest goods; never DROP               | High     |
| Bank < 50                          | Buy animals/seeds                | Only buy wheat if land ready                      | Med      |

### 4. Task priority
1. Remove all DROP calls; replace with PLACE logic.
2. Add WEED action when weed stage ≥2.
3. Add simple wheat buy cap = empty tilled + 2.
4. Add animal buy guard (max 2 total, only if feed ≥3).
5. Basic land timing: TILL before seed purchase when land < 8.
6. Single-file main.py only; no external modules.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs in <1s per turn for 200 simulated turns with no exceptions.
- Never emits the token “DROP” in any output line.
- At least one WEED action emitted in a 50-turn weed-heavy test.
- Wheat purchases never exceed empty tilled land + 2.
- Herd size never exceeds 2 animals.
- All harvest goods are placed via PLACE n (no inventory left at end of test games).

### 6. Non-goals
- No RL or learning.
- No opponent shop denial or price manipulation.
- No multi-file structure.
- No complex crop rotation or long-term planning beyond the policy table.