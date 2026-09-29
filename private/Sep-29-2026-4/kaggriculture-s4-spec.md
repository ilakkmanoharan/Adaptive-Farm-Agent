# Kaggriculture Submission 4 Specification
Date: 2026-09-29 · Slot: s4 · Folder: `2026-09-29-s4/`

Previous Kaggle id: 56684742
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s4 Submission Spec**

**Folder:** `2026-09-29-s4/`  
**Target file:** `main.py` (single stdlib file, <1s per turn)  
**Base:** 2026-09-29-s3 (id 56684742)

### 1. Ladder facts from these games
- Record: 0W-0T-0L
- No completed episodes. No opponent data, no bank values observed.
- Skill rating still at initial 600. No wins/losses recorded.

### 2. Root causes we must fix
- Previous bot performed unnecessary full-inventory operations (DROP/PICKUP thrash) on harvest turns.
- Herd size never scaled because animals were never purchased.
- Wheat buys were absent or mistimed; no seed purchasing logic existed.
- Weeds were ignored, allowing land to degrade.
- Land timing was passive; no explicit buy/expand actions on early turns.
- Unsold inventory at end of episode contributed 0 to score.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behaviour (previous)          | s4 behaviour (new)                                      |
|------------------------------------|----------------------------------|---------------------------------------------------------|
| Turn 1–3                           | Idle / random                    | Buy 2 animals if money ≥ 200, else buy 8 wheat seeds    |
| Wheat seeds available in inventory | Do nothing                       | PLACE wheat on empty land                               |
| Harvest goods in inventory         | DROP or PICKUP thrash            | PLACE item n on empty land (never DROP)                 |
| Weeds present on any tile          | Ignore                           | Clear weed on first weeded tile                         |
| Money ≥ 300 and < 3 animals        | —                                | Buy 1 animal                                            |
| Money ≥ 150 and wheat seeds = 0    | —                                | Buy 6 wheat seeds                                       |
| No action possible                 | Pass                             | Pass                                                    |
| End of turn (always)               | —                                | Sell all harvest goods if market open                   |

### 4. Task priority
1. Implement the exact policy table above as a single if/elif chain in `main.py`.
2. Add minimal state tracking (current animals, wheat seeds, weeded tiles) using only episode observations.
3. Ensure PLACE is used for every harvest good; remove all DROP calls.
4. Add early-game animal and wheat seed purchase logic.
5. Add weed-clear and land expansion only when money thresholds met.
6. Local test run + Kaggle upload.

### 5. Local acceptance gates before Kaggle upload
- Runs 50 turns without exception or timeout (>1s).
- Never emits DROP action.
- Performs at least one animal buy and one wheat seed buy in first 10 turns when starting capital allows.
- Sells harvest goods on every turn they exist in inventory.
- Produces non-zero score on a 50-turn local episode with default market.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No complex pathfinding or long-term planning beyond the table.
