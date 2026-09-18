
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
