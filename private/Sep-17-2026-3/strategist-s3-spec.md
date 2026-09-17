**Kaggriculture s3 Submission Spec**  
**Date:** 2026-09-17 slot 3/5  
**Folder:** `2026-09-17-s3/`  
**Base:** `2026-09-17-s1` (id 56298529)  
**Goal:** One-file `main.py` that fixes herd, wheat, and land bottlenecks while preserving crash wrapper and never using DROP.

### 1. Ladder facts from these games
- Record: 11-0-15, mean bank $37.9k vs opponent mean $50.0k.
- Losses exclusively to farms with $63k–$98k final bank (Sarthak $98k, JCN2365 $95k, ronger $88k, Abed $80k).
- Winners consistently bought 86–6400 wheat (typical 300–465), 8–18 cows, sold 129–267 milk, and used 2 land quads.
- s1 never bought a cow and bought only 49–89 wheat total.

### 2. Root causes we must fix
- Herd size: `TARGET_SHEEP=10` gate blocks all cows; stalls at 7–8 sheep with 1 land + PASTURE_RESERVE.
- Wheat buys: `feed_want = herd+4`, max 12/turn, only when below want → total 49–89 wheat.
- Land timing: first land only at day≥10 / $5k; no second land path.
- Farmer idle: 512–568 PASS actions; no early strawberry or wheat market priority.
- Weeds / inventory: no explicit early weed control or strawberry ramp (target was only 20).
- No DROP/PICKUP thrash observed, but spec forbids any DROP and limits PLACE to harvest goods only.

### 3. Exact s3 policy table vs previous bot

| Policy | s1 (previous) | s3 (new) |
|--------|---------------|----------|
| TARGET_SHEEP | 10 | 6 |
| TARGET_COWS | 4 (gated) | 10 (after 2 sheep) |
| TARGET_STRAWBERRY | 20 | 28 |
| Wheat buffer | herd+4, max 12/turn | herd*2+8, buy up to 24/turn |
| Wheat buy order | after sells | before most sells |
| First land | day≥10 & ≥$5000 | day≥8 & ≥$4000 |
| Second land | never | day≥12 & ≥$8000 |
| Strawberry start | day 3+ | day 2 |
| Farmer action | heavy PASS | WATER/FEED/CARE priority after market |

Market order each turn (after player actions resolve):
1. Buy wheat up to (herd*2+8) buffer if money allows (max 24).
2. Buy 2 sheep if sheep < 2.
3. Buy cows if sheep ≥ 2 and cows < 10.
4. Buy strawberry seeds toward 28 (start day 2).
5. Sell milk/eggs/strawberries only after feed buys.
6. Place harvest goods only; never DROP.

### 4. Task priority (implement in this order)
1. Change animal buy logic: sheep until 2, then cows to 10; sheep cap at 6–8.
2. Replace wheat top-up with aggressive `herd*2+8` buffer, 20–24/turn max, feed buys first.
3. Add second-land unlock at day≥12 & money≥8000 (first land at day≥8 / $4000).
4. Raise strawberry target to 28 and start day 2.
5. Keep crash wrapper, one-file `main.py`, never emit DROP.

### 5. Local acceptance gates before Kaggle upload
- Run 20 local episodes against starter bot.
- Must achieve mean bank ≥ $51k (prior good smoke target) with ≥70 % win rate.
- No crashes, no DROP commands, wheat buys visible in logs ≥150 per episode by day 20.
- Herd must contain ≥6 cows by day 25 in at least 80 % of runs.

### 6. Non-goals
- No opponent shop denial.
- No RL or learned policy.
- No multi-file structure.
- No changes to crash wrapper.
- No weed-specific logic beyond existing farmer actions.