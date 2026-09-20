**Kaggriculture s2 Submission Spec**  
**Date:** 2026-09-20 slot 2/5  
**Folder:** `2026-09-20-s2/`  
**Target file:** `main.py` (single stdlib file, no external deps)

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no completed episodes yet).
- Mean bank: None (no scoring data).
- Previous submission (56382230) produced no wins; new bots start at 600 rating.
- No opponent-specific data available. All future matches will be against unknown bots.

### 2. Root causes we must fix
- Previous bot performed repeated PICKUP/DROP cycles on the same tiles (inventory thrash).
- Herd size never stabilized; animals bought but never fed consistently.
- Wheat purchased every turn regardless of existing stock or growth stage.
- Weeds left uncleared on high-value plots.
- Land actions (buy/expand) executed too early or too late relative to cash and crop cycles.
- Unsold inventory at end of episode contributed 0 to score.

### 3. Exact s2 policy table vs previous bot

| Situation                          | s1 behaviour (previous)          | s2 behaviour (new)                                      | Reason |
|------------------------------------|----------------------------------|---------------------------------------------------------|--------|
| Cash ≥ 120 and no wheat seed       | Buy 3 wheat seeds                | Buy 2 wheat seeds only if current wheat < 4             | Reduce overbuy |
| Wheat ready on tile                | PICKUP then immediate DROP       | PICKUP then PLACE 1 into shed (never DROP)              | Eliminate thrash |
| Weeds present on any owned tile    | Ignore                           | Clear weed on highest-value tile first                  | Protect yield |
| Animal count < 3 and cash ≥ 80     | Buy animal every turn            | Buy 1 animal only if feed stock ≥ 6                     | Stable herd |
| Feed stock < 3                     | Buy wheat                        | Buy 2 feed only if cash ≥ 60 and no pending harvest     | Prioritise existing crops |
| Cash ≥ 200 and owned land < 6      | Buy land immediately             | Buy land only after current plots have ≥ 2 mature crops | Timing |
| Inventory full                     | DROP                             | PLACE all harvest goods into shed (no DROP)             | Score inventory |
| No action possible                 | Idle                             | Clear one weed or feed one animal                       | Always productive |

### 4. Task priority (implement in this order)
1. Core loop: observe state → apply policy table above.
2. Replace all DROP with PLACE n for harvest goods.
3. Add simple counters for wheat, feed, animals, weeds.
4. Add one-turn look-ahead for cash after planned buys.
5. Hard limit: never buy more than 2 of any item per turn.
6. End-of-episode: ensure all harvest goods are PLACEd.

### 5. Local acceptance gates before Kaggle upload
- Run 20 local episodes with `actTimeout=1`.
- Must finish every episode without PICKUP/DROP on same tile in one turn.
- Must have ≥ 3 animals fed at least once per episode.
- Final inventory score > 0 in ≥ 70% of episodes.
- No runtime exceptions and total actions per turn ≤ 8.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned parameters.
- No multi-file structure.
- No complex pathfinding beyond adjacent tiles.
- No selling animals (impossible anyway).

Implement the policy table as a single `if-elif` chain inside the main action function. Keep all state in simple integers/dicts.