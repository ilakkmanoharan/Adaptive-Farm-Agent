# Sep-17-2026-3 briefing (s1=56298529 research)

## Ladder context
- s1 (56298529): **11-0-15** vs field, mean bank **$37.9k** vs opp mean **$50.0k**.
- Losses are to $63k–$98k farms (Sarthak $98k, JCN2365 $95k, ronger $88k, Abed $80k…).
- s2 (56315005) is a **broken stub** ($3000 every episode) — ignore for lineage. Base = **2026-09-17-s1 / 2026-09-12-s3**.

## Replay action deltas (5 big losses)
| Metric | US (s1) | Winners |
|--------|---------|---------|
| BUY_PRODUCT WHEAT | 49–89 | **86–6400** (often 300–465) |
| BUY_ANIMAL COW | **0** | **8–18** |
| BUY_ANIMAL SHEEP | 7–8 | 0–16 (mixed) |
| SELL MILK | ~0 | **129–267** |
| Land quads | 1 | often **2** |
| Farmer PASS | **512–568** | 1–395 (winners WATER/FEED/CARE) |
| Strawberry plant | low | often 22–35 seed buys |

## Root causes in current main.py
1. **Cows gated behind TARGET_SHEEP=10**: buys sheep until 10 before any cow. With 1 land + PASTURE_RESERVE, herd stalls at ~7–8 sheep → **never buys cows** → no milk.
2. **Wheat top-up too timid**: `feed_want = herd+4`, max 12/turn, only when below want → ~50–90 total vs winners hundreds.
3. **Only 1 land**: `extras < 1` only; winners unlock 2nd for herd+crops.
4. **Farmer idle**: hands do work; farmer PASSes 75%+ of steps — leave for later; fix market/herd first.

## Spec goals for s3
1. Mixed dairy herd: after **2 sheep**, prioritize cows to TARGET_COWS=10; TARGET_SHEEP=6–8.
2. Aggressive market wheat: want `herd*2+8` buffer; buy up to **20–24**/turn; **feed buys before most sells**.
3. Second land when day>=12 and money>=8000 (and first land day>=8 / $4k).
4. More strawberries (target 28, start day 2).
5. Keep crash wrapper, never DROP, one-file main.py.
6. Local smoke must beat starter by large margin (prior good smoke ~$51k).
