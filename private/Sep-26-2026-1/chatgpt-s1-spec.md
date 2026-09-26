**Kaggriculture Submission Spec – 2026-09-26-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating starts at 600).
- No completed episodes; mean bank = None.
- No opponent data available. All future rating changes will be driven by first 5–10 matches.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (which empties entire shed). We will never emit DROP; only PLACE n for harvested goods.
- **Herd size**: No animals purchased or managed; inventory scoring requires active crop cycles instead.
- **Wheat buys**: No wheat seed purchases observed; bot must buy wheat seeds on day 1–2 when price is lowest.
- **Weeds**: No weeding action taken; weeds reduce yield on every plot.
- **Land timing**: No land expansion or timed planting; bot must plant immediately after buying seeds and harvest before market close.

### 3. Exact s1 policy table vs previous bot

| Situation                          | Previous bot (2026-09-25-s5) | s1 policy (2026-09-26-s1) |
|------------------------------------|--------------------------------|---------------------------|
| Turn 1                             | Random / idle                  | BUY wheat 10              |
| After buying seeds                 | No action                      | PLANT wheat on all empty plots |
| Any plot has weeds                 | Ignore                         | WEED every weeded plot    |
| Harvest ready                      | PLACE 1 then DROP              | PLACE n (exact count)     |
| Inventory > 0 at market            | Sell partial / DROP            | SELL all wheat            |
| No wheat left & money >= 50        | Idle                           | BUY wheat 10              |
| Animals in shop                    | Never buy                      | Never buy (animals unsellable) |
| actTimeout approaching             | —                              | Emit cheapest valid action (WEED > PLACE > SELL) |

### 4. Task priority
1. Implement deterministic rule loop in `main.py` (stdlib only).
2. Hard-code wheat buy/plant/weed/place/sell sequence.
3. Remove all DROP usage.
4. Add simple inventory counter to decide exact PLACE n.
5. Add 1-second action timeout guard (submit action every turn).

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs without import errors or external packages.
- No `DROP` string appears in source.
- Every turn produces exactly one valid action string.
- 100 simulated turns complete in < 5 s on local machine.
- Inventory never exceeds 200 (to avoid obvious overflow).

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or parameter search.
- No animal handling.
- No multi-crop or advanced land timing.
- No file I/O or persistent state beyond one run.