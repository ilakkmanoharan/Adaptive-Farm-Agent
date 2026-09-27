**Kaggriculture Submission Spec – 2026-09-27-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Starting rating: 600 (new bot).
- Mean bank: None (no market resolution observed).
- No opponent data available. No wins/losses recorded against any bot.

### 2. Root causes we must fix
- Previous bot (s2) performed no actions or only invalid ones, resulting in zero scoring inventory.
- Risk of DROP/PICKUP thrash on harvest turns (explicitly forbidden; only PLACE item n allowed for goods).
- No herd-size management (animals cannot be sold; must avoid over-purchase).
- No wheat-buy timing logic (player actions resolve before market).
- No weed-clear or land-timing logic.
- Unsold inventory at end of episode scores zero.

### 3. Exact s3 policy table vs previous bot

| Situation                          | s2 behaviour (previous) | s3 behaviour (target)                          | Reason |
|------------------------------------|-------------------------|------------------------------------------------|--------|
| Turn 1–3, money ≥ 20               | Idle / invalid          | BUY WHEAT 1                                    | Fastest scoring crop |
| Wheat ready (age ≥ 3)              | —                       | PLACE WHEAT 1 (never DROP)                     | Score inventory |
| Money ≥ 50 and no animals          | —                       | BUY COW 1                                      | Long-term points |
| Weeds present on owned land        | —                       | CLEAR WEED 1                                   | Prevent land loss |
| Land slot empty and money ≥ 30     | —                       | BUY LAND 1                                     | Expand capacity |
| Any other state                    | —                       | BUY WHEAT 1 (if money ≥ 20) else WAIT          | Default safe action |
| Harvest goods in hand              | —                       | PLACE item n (n = count of that good)          | Mandatory rule |

### 4. Task priority
1. Implement deterministic rule table above in single `main.py`.
2. Add minimal state tracking (money, inventory counts, land status, animal count) using only stdlib.
3. Enforce PLACE instead of DROP on every harvest.
4. Add simple wheat-age and weed checks.
5. Ensure actTimeout compliance (≤ 1 s) with O(1) decisions.

### 5. Local acceptance gates before Kaggle upload
- Script runs 1000 turns with no exceptions and finishes in < 0.8 s per turn.
- Never emits the token “DROP”.
- Always uses “PLACE” when moving harvest goods.
- Produces at least one non-zero inventory item by turn 10 in a fresh episode.
- No external libraries or files required.

### 6. Non-goals
- No reinforcement learning or learning.
- No opponent shop interference.
- No multi-file structure.
- No complex pathfinding or long-term planning beyond the rule table.