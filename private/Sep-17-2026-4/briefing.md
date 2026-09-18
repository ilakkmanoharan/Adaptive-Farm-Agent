# Winner mechanisms (s1 56298529 losses)

Source: 5 big-loss replays under `private/Sep-17-2026-3/logs/`  
US = Ilakk / submission **56298529**. Full numeric tables: `replay_tables.json`.

| Episode | Opp | US bank | Opp bank | Gap |
|---------|-----|---------|----------|-----|
| 109980298 | Sarthak Vedant Mohanty | $33,868 | $98,405 | **+$64,537** |
| 110001163 | JCN2365 | $41,927 | $94,809 | **+$52,882** |
| 109987972 | ronger zhu | $31,128 | $88,110 | **+$56,982** |
| 110015745 | AchyutKishore123 | $48,239 | $75,857 | **+$27,618** |
| 109981400 | Mint120 | $48,979 | $71,588 | **+$22,609** |

Mean: US **$40.8k** vs opp **$85.8k** (gap **~$45.0k**).

---

## Aggregate US vs OPP (summed market qty)

| Metric | US mean (range) | Opp mean (range) | Δ (opp−us) |
|--------|-----------------|------------------|------------|
| BUY_PRODUCT WHEAT | 61 (49–89) | 1451 (0–6402)* | +1390 |
| BUY_ANIMAL COW | **0** | **12.0** (8–18) | **+12** |
| BUY_ANIMAL SHEEP | 7.6 (7–8) | 4.4 (0–16) | −3.2 |
| BUY_LAND | 1.0 | 1.8 (1–2) | +0.8 |
| SELL MILK | **0** | **198** (129–267) | **+198** |
| SELL WOOL | 87.6 | 38.4 | −49 |
| SELL MELON | 79.6 | 49.8 | −30 |
| SELL STRAWBERRY | 28.2 | 76.8 | +49 |
| SELL WHEAT | 116.8 | 1564* | — |
| HIRE | 282 | 284 | ~0 |
| hand non-PASS | 3740 | 5003 | +1263 |

\*JCN2365 churns ~6400 buy / ~7000 sell wheat; typical winners buy **86–465** market wheat. Sarthak bought **0** market wheat but grew feed for 14 cows.

### Money trajectory (mean)

| Day | US $ | Opp $ | Note |
|-----|------|-------|------|
| 0 | 912 | 903 | even |
| 5 | 253 | 815 | winners already buying cows |
| 10 | **7113** | 1141 | US *leads* (crops cash; opp investing) |
| 15 | **13431** | 9304 | US still ahead or close |
| 20 | 22764 | **26171** | milk compounds; crossover |
| 25 | 32771 | **55935** | gap blows open |
| 29 | 40828 | **85754** | final |

### Herd on tiles (mean cows/sheep)

| Day | US | Opp |
|-----|----|-----|
| 5 | 0c / 3s | **3.0c** / 0.4s |
| 15 | 0c / 4s | **8.6c** / 1.8s |
| 25 | 0c / 3.8s | **9.2c** / 2.0s |

US bought 7–8 sheep but only ~3–5 sit on tiles (pasture/place bottleneck on 2 quads). Opp places nearly full dairy herd.

---

## Causal mechanisms (ranked)

### 1. Cows → milk → sell dominates wool (largest)
- US: **0 cows, 0 milk sells** in all 5 games.
- Opp: **8–18 cows**, **129–267 milk sells**.
- US wool 67–108 cannot match milk revenue. Money crossover lands **~day 10–20**, right after first milk (day 8–14).

### 2. Early cow timing (day 0–5), not late sheep-first
- Opp first cow on day **0** (4/5) or day **5** (Sarthak).
- US sheep-gates cows → never starts dairy. Mid-game US cash lead is a **false comfort**.

### 3. Second land unlocks herd + crops
- US: always **1** BUY_LAND → **2** quads.
- Opp: **1–2** BUY_LAND → usually **3** quads (4/5).
- Extra quadrant frees pasture for 8–14 cows while still running melon/strawberry/wheat.

### 4. Market wheat buffer (or grown wheat) prevents unfed herd collapse
- Large dairy needs reliable feed. Typical winners buy **hundreds** of wheat; JCN overbuys; Sarthak substitutes grown wheat.
- US **49–89** total is enough only for a tiny sheep herd — not for 10+ cows.

### 5. Milk compounding after day 15 (bank rocket)
- Day 15→25: opp mean bank **$9.3k → $55.9k** (+$47k); US **$13.4k → $32.8k** (+$19k).
- Gap is mostly **late-game milk volume**, not early crop sales.

### 6. CARE / FEED intensity scales with herd value
- Opp hand FEED+CARE much higher when cows present (e.g. Sarthak FEED 207 / CARE 208 vs US FEED 79 / CARE 0).
- Healthy cows → more milk units sold. US often skips CARE entirely.

### 7. Farmer not idle — winners work the board
- US farmer PASS **512–568**/episode; winners often **1–100** (Achyut 395 still far more active than US).
- Hand non-PASS: US ~3.7k vs opp ~5.0k mean → more WATER/HARVEST/FEED throughput.

### 8. Strawberry secondary cash (mixed but real)
- Opp strawberry sells mean **77** vs US **28**; ronger sold **179**.
- Helps but does not explain $60k gaps alone — dairy does.

### 9. Sheep-only + pasture stall caps herd below buy intent
- US buys 7–8 sheep but tiles show ~3–5 animals through day 25.
- Combined with no cows + 2 quads + PASTURE_RESERVE, herd never becomes a milk engine.

### 10. Hire count is not the differentiator
- HIRE ~282 both sides. Labor *headcount* is similar; **what they work on** (dairy CARE/FEED vs crop WATER) differs.

---

## Per-episode snapshots

### 109980298 — Sarthak ($98k)
- Opp: 14 cows, 0 sheep, 2 land buys (3 quads), **0** market wheat, **267 milk**.
- US: 0 cows, 8 sheep buys, 67 wool, 1 land.
- Money: US ahead day 10 ($7.6k vs $1.0k); opp passes ~day 18; day 25 $64k vs $29k.

### 110001163 — JCN2365 ($95k)
- Opp: 18 cows, 6402 wheat buy / 7003 wheat sell (churn), 226 milk, 2 land.
- Extreme feed market use; dairy still core.

### 109987972 — ronger ($88k)
- Opp: 9 cows, only 1 land (2 quads), 86 wheat, **179 strawberry** + 129 milk.
- Shows dairy+berry can win without 3rd quad; US still 0 milk.

### 110015745 — Achyut ($76k)
- Opp mixed herd 8c/6s, 210 milk + 124 wool, 302 wheat, 2 land.
- Closest bank; still +$28k from dairy volume.

### 109981400 — Mint120 ($72k)
- Opp 11c/16s buys, tiles ~7c/4s, 159 milk, 465 wheat, 2 land.
- US best bank ($49k) still loses on milk.

---

## Implications for next bot (validate s3 / plan s4)

1. **Must buy cows early** (by day 0–5); never gate behind TARGET_SHEEP=10.
2. **Milk sell loop** is the primary score function; wool is backup.
3. **2nd BUY_LAND** (3 quads) when cash allows — 4/5 winners did.
4. **Wheat buffer** scales with herd (market and/or plots); 50–90 total is loser-tier for dairy.
5. **CARE+FEED** hands/farmer on animal tiles; reduce farmer PASS.
6. Mid-game cash lead without cows **predicts a loss** after day 15.

s3 (56315459) targeted items 1–4; confirm with episodes once PENDING clears.



# S4 research synthesis (neuro-symbolic)

## Offline intervention hypotheses (ranked by evidence)
1. **do(BUY_COW on day 0–3)** → milk compounding → +$20–45k bank vs sheep-first (replay + Grok).
2. **do(BUY_LAND ×2)** → 3 quads → herd capacity for 8–14 cows.
3. **do(BUY_PRODUCT WHEAT ≥ herd×2+12)** → prevents unfed collapse under dairy.
4. **do(CARE+FEED priority)** → higher milk units / animal.
5. **do(PLACE animals same day)** → closes buy→tile gap (s1 bought 7–8, placed ~4).

## Explicit mechanisms (priors for reasoner)
| name | cause | effect | prior weight |
|------|-------|--------|--------------|
| dairy_compounding | BUY_COW_EARLY | MILK_BANK | 1.5 |
| wheat_buffer | BUY_PRODUCT_WHEAT | HERD_YIELD | 1.2 |
| third_land | BUY_LAND_3 | HERD_CAPACITY | 1.1 |
| placement_throughput | PLACE_FAST | HERD_ON_TILES | 1.3 |
| care_feed | CARE_FEED | MILK_UNITS | 1.0 |

## Online adaptation
Each morning (hour==0): observe Δmoney, update mode EMA + mechanism Welford stats.
Plan mode via UCB over {cow_first_dairy, land_rush, wheat_heavy_dairy, balanced_mix}.

## s4 vs s3 policy
- Cow-first (0–1 sheep max before cows), TARGET_COWS=12
- Wheat want herd*2+12, max 32/turn
- Land: first day≥6/$3500; second day≥9/$6500; allow third day≥16/$14000
- PASTURE_RESERVE slightly lower when expanding dairy
- Farmer: bias toward FEED/CARE/WATER targets before PASS


## Intervention results
{
  "mean_s3": 57321.0,
  "mean_s4": 58768.724137931036,
  "delta": 1447.7241379310362,
  "n": 29,
  "s4_wins": 21,
  "rows": [
    {
      "seed": 1000,
      "s3": 57803.0,
      "s4": 49790.0
    },
    {
      "seed": 1001,
      "s3": 56132.0,
      "s4": 57723.0
    },
    {
      "seed": 1002,
      "s3": 55018.0,
      "s4": 59625.0
    },
    {
      "seed": 1003,
      "s3": 60573.0,
      "s4": 63979.0
    },
    {
      "seed": 1004,
      "s3": 56952.0,
      "s4": 50222.0
    },
    {
      "seed": 1005,
      "s3": 61264.0,
      "s4": 60452.0
    },
    {
      "seed": 1006,
      "s3": 53575.0,
      "s4": 56469.0
    },
    {
      "seed": 1007,
      "s3": 62629.0,
      "s4": 57052.0
    },
    {
      "seed": 1008,
      "s3": 58881.0,
      "s4": 58085.0
    },
    {
      "seed": 1009,
      "s3": 60263.0,
      "s4": 61179.0
    },
    {
      "seed": 1010,
      "s3": 51153.0,
      "s4": 61480.0
    },
    {
      "seed": 1011,
      "s3": 58252.0,
      "s4": 61325.0
    },
    {
      "seed": 1012,
      "s3": 55761.0,
      "s4": 60150.0
    },
    {
      "seed": 1013,
      "s3": 52707.0,
      "s4": 53674.0
    },
    {
      "seed": 1014,
      "s3": 58527.0,
      "s4": 62560.0
    },
    {
      "seed": 1015,
      "s3": 54300.0,
      "s4": 54922.0
    },
    {
      "seed": 1016,
      "s3": 59866.0,
      "s4": 63271.0
    },
    {
      "seed": 1017,
      "s3": 57788.0,
      "s4": 53733.0
    },
    {
      "seed": 1018,
      "s3": 57

## Neuro-symbolic design shipped in s4
- Mechanism objects with Welford online updates from daily money deltas
- Mode curriculum: cow_first_dairy → land_rush → wheat_heavy_dairy
- Continuous knobs _adapt: wheat_extra/cap, land2_day/cash updated from mechanism weights
- Offline lab: private/Sep-17-2026-4/research/neuro_symbolic.py
- Aggressive cow-first / 3rd land ablations HURT local score; kept s3 animal gate + stronger wheat/land priors
