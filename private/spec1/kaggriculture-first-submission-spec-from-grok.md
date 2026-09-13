# Kaggriculture — First Submission Specs (v1)

Competition: https://www.kaggle.com/competitions/kaggriculture  
Deadline: **Sep 30, 2026** · Entry deadline **Sep 23** · Top 10 × $5k

## 1. What you're entering

- 2-player farming sim, **720 turns** (30 days × 24), start **$3000**, NW 5×5 unlocked.
- Win = **more coins in bank** at end (unsold inventory doesn't count).
- Ladder = **skill rating** from W/L/T vs similar bots; only **latest 2** submissions are active; **5/day**; ≤ **100 MiB**.
- Validation = agent vs itself; if it crashes → `Error`.
- Final = Bradley-Terry over continued episodes after lock.

## 2. What the field has learned (don't reinvent day 1)

Public notebooks / discussions converge on:

| Lesson | Implication for v1 |
|---|---|
| Official wheat starter is weak | Beat `"starter"` + `"random"` locally before submit |
| **Animals dominate tiles** (esp. with CARE + daily fertilizer) | v1 should *path toward* livestock, not stay wheat forever |
| Fertilizer from animals ≈ huge free cash (no town sink) | Collect fertilizer daily; sell or use |
| Walking thrash kills banks | Finish all acts on a tile before moving |
| Market order **order matters** | Sell premium first: MELON/MILK/WOOL/STRAWBERRY → staples |
| Premium glut crashes to $1 fast | Meter sales; don't dump everything every turn |
| Land ($1k/$2k/$4k) scales cheaply once productive | Buy land after cashflow exists, not on turn 0 |
| Hire fib resets daily (~$143 for 10 hands) | Hire early each day once you have work |
| Many LB bots are forks of same public notebook | Identical mirror matches are normal |

Useful refs:

- [How to play](https://www.kaggle.com/competitions/kaggriculture/overview/how-to-play)
- [Crop economics discussion](https://www.kaggle.com/competitions/kaggriculture/discussion/734412)
- [Reference agents dataset](https://www.kaggle.com/datasets/raykkretzschmar/kaggriculture-reference-agents)
- [Premium-first market agent](https://www.kaggle.com/code/ameythakur20/kaggriculture-premium-first-market-agent)
- [Visualized mechanics](https://www.kaggle.com/code/georgymamarin/kaggriculture-visualized-what-every-crop-pays)

## 3. Goal for *today's* first submit

Ship a **deterministic, crash-proof, stdlib-only** agent that:

1. Never errors in validation.
2. Beats built-in `"starter"` and `"random"` over ≥10 seeds (both seats).
3. Implements a clear **phased plan**: bootstrap cash → hire → expand → livestock → smart sells.
4. Gets you onto the ladder so later submissions can climb.

**Out of scope for v1:** ML, search trees, opponent modeling, shop-adaptive sparse routers, multi-file ML weights.

## 4. Delivery format

```text
main.py                 # required root; defines agent(obs) [and optionally agent(obs, config)]
# optional later: helpers.py — but keep v1 single-file if possible
```

Return shape every turn:

```python
{
  "farmer": [...],         # one action list for main farmer
  "hands":  [[...], ...],  # one per hired hand, same length as me["hands"]
  "market": [["BUY_SEED","WHEAT",1], ["SELL","MILK",2], ...]  # ≤10 orders
}
```

Files land under `/kaggle_simulations/agent/` — use relative imports if you split files.

## 5. Agent architecture (v1)

### Modules inside one file

1. `parse(obs)` — money, day, hour, tiles, farmer/hands positions, shed, seeds, prices, shops, unlocked quadrants.
2. `plan_market(state)` — buys + sells (no movement).
3. `assign_targets(state)` — map each unit → a tile task.
4. `unit_action(unit, target)` — if on tile → act; else `step_toward`.
5. `agent(obs)` — glue; always return valid structure; catch-all → PASS.

### Hard invariants (must never break)

- Water every plant that isn't watered today (plants die after 2 missed days; new plant starts at unwatered=1).
- Feed every animal every day with wheat (escape after 2 missed; place starts unfed=0).
- `hands` list length == number of hired hands.
- Never plant more seeds than you own in one turn across units.
- Don't sell feed wheat you still need today.
- Cap market list at 10; **reorder sells: premium first**.

## 6. Strategy phases (spec)

### Phase A — Bootstrap (days 0–3)

- Loop wheat on NW empty tiles: buy seeds → plant → water → harvest at age ≥2 (better at peak ~4 with water; fertilize later).
- Sell wheat only surplus above a **feed reserve** (start reserve=0 until animals exist).
- Hire **2–4 hands** each morning once ≥2–3 plants need care.
- Clear weeds with `DIG` before planting.
- Target bank: enough for first land or first animals (~$1k–$1.5k).

### Phase B — Scale land + labor (days 3–8)

- `BUY_LAND` when money ≥ 1000 + safety buffer ($200) and NW is mostly utilized.
- Ramp hires toward ~6–10/day as tile count grows (fib cost is cheap).
- Keep monoculture wheat (or wheat+carrot) until feed pipeline is stable.
- Persist **per-unit task**: finish FEED/CARE/HARVEST/COLLECT_FERTILIZER on current tile before pathing elsewhere.

### Phase C — Livestock core (days 5–20)

Target herd (community consensus starting point — tune later):

- **6–8 cows** + **3–4 sheep** (or geese if yarn/dairy shops missing — optional v1.1).

Build path per animal tile: empty → `BUILD_PASTURE`/`BUILD_COOP` → `BUY_ANIMAL` → `PICKUP`/`PLACE` → daily `FEED` + `CARE` + `HARVEST` + `COLLECT_FERTILIZER`.

- Dedicate enough wheat tiles (or `BUY_PRODUCT WHEAT`) so feed never fails.
- Use fertilizer on wheat/melon during bonus windows when inventory allows.

### Phase D — Market discipline (all season)

Sell priority order:

1. `MELON`, `MILK`, `WOOL`, `STRAWBERRY`
2. `EGG`, `TOMATO`, `CARROT`
3. Excess `FERTILIZER` (often very valuable early)
4. Excess `WHEAT` only above feed reserve

Rules:

- Meter premium sales (don't dump full shed every turn).
- Prefer selling near town consumption ticks if easy (`townShopSellInterval=4`, town center every 24).
- Endgame (last ~24–48 turns): liquidate non-feed inventory; stop new long-horizon plantings.

### Phase E — Endgame (days 25–29)

- No new melons/strawberries/animals.
- Harvest + sell everything sellable.
- Keep animals alive only if remaining product > feed cost; otherwise optional stop expanding.

## 7. Action priority per unit (on its assigned tile)

1. If animal tile: `FEED` (if not fed) → `CARE` (if not cared) → `HARVEST` (if yield>0) → `COLLECT_FERTILIZER` (if available)
2. If plant: `WATER` (if not watered) → `HARVEST` (if ready / decaying) → `FERTILIZE` (if bonus window + have fert)
3. If weed: `DIG`
4. If empty + should plant: `PLANT <crop>`
5. If empty + should build: `BUILD_*`
6. Else move toward next assigned target (BFS / Manhattan step: N/S/E/W)

**Market (same turn, before/with actions):** restock seeds/animals, hire, buy land, ordered sells.

## 8. Local acceptance tests (gate before submit)

Install:

```bash
pip install -U kaggle-environments
```

Run:

```bash
# smoke
python -c "from kaggle_environments import make; e=make('kaggriculture', debug=True); e.run(['main.py','starter']); print([(i,s.reward) for i,s in enumerate(e.steps[-1])])"

# battery: ≥10 seeds × both seats vs starter and random
# PASS criteria for v1:
# - 0 crashes
# - win rate ≥ 80% vs starter
# - win rate ≥ 90% vs random
# - mean bank vs starter margin > 0 with room (aim > +5k)
```

Also verify: shed never silently discards critical feed; no animal escapes in logs; plants don't weed from missed water.

## 9. Submit checklist (today)

1. Join competition / accept rules on the site.
2. `kaggle competitions submit kaggriculture -f main.py -m "v1 phased wheat→livestock premium-first sells"`
3. Watch validation: `kaggle competitions submissions kaggriculture`
4. If `Error` → download logs, fix, resubmit (you have 5 today).
5. After a few episodes: `kaggle competitions episodes <ID>` + replay/logs.
6. Keep **this** as one of your latest 2 until v2 is proven stronger locally.

## 10. Explicit non-goals for v1 (do tomorrow+)

- Shop-conditional sparse router (yarn missing → fewer sheep)
- Opponent farm reading / denial
- Full search / MCTS
- Copying an opaque top notebook without understanding (ladder is full of clones; you'll mirror-tie them)

## 11. Suggested build order for the next few hours

1. Implement spatial wheat loop that **moves** (starter sample barely moves — extend it).
2. Add hire + nearest-target scheduler.
3. Add land buy.
4. Add pasture/cow pipeline + feed reserve.
5. Add market reorder.
6. Run acceptance battery → submit.
