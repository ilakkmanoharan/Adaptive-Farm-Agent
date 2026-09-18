**Kaggriculture Submission Spec – 2026-09-18-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no market resolution observed).
- No opponents encountered; rating still at default 600.
- No data on who beat us or how (no losses recorded).

### 2. Root causes we must fix
- Previous bot (s2) performed repeated PICKUP/DROP cycles on harvest goods instead of using PLACE n, causing inventory thrash and zero scoring.
- Herd size never exceeded 1 animal because no consistent BUY animal logic existed.
- Wheat buys occurred only when inventory was already full, wasting the pre-market action window.
- No weed removal action; weeds accumulated and blocked planting.
- Land timing was reactive (plant only after seeing empty plots) instead of proactive (always keep 2–3 plots seeded when possible).
- Animals never fed because FEED was never issued.

### 3. Exact s3 policy table vs previous bot

| Situation                          | s2 behaviour (previous)          | s3 behaviour (new)                                      |
|------------------------------------|----------------------------------|---------------------------------------------------------|
| Empty plot available               | Do nothing or PICKUP             | PLANT wheat if seeds ≥ 1                                |
| Harvest ready on plot              | PICKUP then DROP                 | PLACE 1 (harvest good)                                  |
| Weeds present on any plot          | Ignore                           | REMOVE weed on first weeded plot                        |
| Animal count == 0                  | Never buy                        | BUY animal (any type) if coins ≥ 50                     |
| Animal present and hungry          | Ignore                           | FEED animal                                             |
| Seeds == 0 and coins ≥ 10          | Skip                             | BUY wheat seed (min 3)                                  |
| Inventory has goods and market open| Attempt DROP                     | Never DROP; only PLACE n                                |
| No action possible                 | Idle                             | BUY wheat seed (if affordable) else idle                |

All actions are single-action per turn. Player actions always resolve before market.

### 4. Task priority
1. Implement core loop that never emits DROP.
2. Add PLACE n for every harvest good.
3. Add REMOVE weed when any plot is weeded.
4. Add BUY animal once at start of game.
5. Add FEED when animal exists.
6. Add simple seed-buying rule when seeds == 0.
7. Add wheat planting on empty plots.
8. Local test harness + acceptance gates.

### 5. Local acceptance gates before Kaggle upload
- main.py runs to completion in < 1 s per turn for 100 simulated turns using only stdlib.
- Never emits the token “DROP” in any output.
- Produces at least one PLACE action when harvest goods exist.
- Issues exactly one BUY animal in the first 5 turns if coins allow.
- Plants wheat on ≥ 2 plots by turn 20 in a clean environment.
- No external imports, no files written, single file only.

### 6. Non-goals
- No opponent modelling or shop denial.
- No reinforcement learning or parameter search.
- No multi-animal herd management beyond buying one.
- No crop rotation or advanced timing.
- No handling of multiple animal types or special goods.