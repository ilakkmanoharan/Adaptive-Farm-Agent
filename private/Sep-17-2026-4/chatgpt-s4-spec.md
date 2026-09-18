**Kaggriculture s4 Submission Spec**  
**Folder:** `2026-09-17-s4/`  
**Target file:** `main.py` (single stdlib file, no external deps)  
**Previous:** s3 (56315459)  
**Goal:** Ship cow-first dairy engine that survives the 5 replay opponents while remaining a single-file bot.

### 1. Ladder facts (from the 5 decisive losses)
- Record vs top agents: **0-5** (all episodes lost).
- Mean final bank: **US $40.8k** vs **Opp $85.8k** (gap **+$45k**).
- Opponents that beat us: Sarthak (98k), JCN2365 (95k), ronger (88k), AchyutKishore123 (76k), Mint120 (72k).
- Common pattern: opponents reached 8–18 cows + 129–267 milk sells; US reached 0 cows, 7–8 sheep, 67–108 wool.
- Money crossover: opponents overtake between day 15–20 once milk compounds.
- Land: US always stopped at 1 BUY_LAND (2 quads); winners used 2 BUY_LAND (3 quads) in 4/5 games.
- Wheat: US total 49–89; winners used 86–465 (or grew their own).

### 2. Root causes we must fix
- **Herd size & timing**: 0 cows bought before day 5; sheep-first policy never transitions.
- **Wheat buffer**: 49–89 total purchases insufficient for any dairy herd; no market wheat scaling.
- **Land timing**: second BUY_LAND never triggered; pasture capacity caps at ~4–5 animals.
- **Placement & action thrash**: animals bought but not placed same day; frequent DROP/PICKUP cycles on limited quads.
- **Weeds & idle time**: farmer PASS count 512–568; insufficient WATER/FEED/CARE throughput.
- **CARE/FEED starvation**: zero CARE actions in all 5 replays; cows never appear so loop never starts.

### 3. Exact s4 policy table vs previous bot

| Decision                  | s3 (previous)                  | s4 (target)                                      | Trigger condition                  |
|---------------------------|--------------------------------|--------------------------------------------------|------------------------------------|
| First animal              | Sheep until 10                 | Cow on day 0–3 (max 1 sheep before first cow)    | Cash ≥ 1200                        |
| Target cows               | 0                              | 12                                               | —                                  |
| Wheat buys per turn       | 0–10                           | min(32, max(0, (current_cows*2 + 12) – stock))   | Every morning                      |
| Land 1                    | day ≥ 8 / $4000                | day ≥ 6 / $3500                                  | Same                               |
| Land 2                    | never                          | day ≥ 9 / $6500                                  | After first land                   |
| Land 3 (optional)         | never                          | day ≥ 16 / $14000                                | Cash & 2nd land already bought     |
| PASTURE_RESERVE           | 2                              | 1 when cows ≥ 6                                  | Dynamic                            |
| Farmer priority order     | WATER → HARVEST → PASS         | FEED → CARE → WATER → HARVEST → PLACE → PASS     | Daily                              |
| Max wheat market buys/turn| 10                             | 32                                               | —                                  |
| Sell priority             | Wool → Melon → Strawberry      | Milk → Wool → Melon → Strawberry                 | —                                  |

### 4. Task priority (daily loop order)
1. Morning (hour==0): update mechanism stats (money delta, cow count, wheat stock).
2. If cash allows and cows < 12 → BUY_ANIMAL COW (day 0–5 priority).
3. Compute wheat_need = cows*2 + 12 – current_wheat; BUY_PRODUCT WHEAT up to 32.
4. If conditions met → BUY_LAND (second land on day ≥9).
5. Farmer actions: FEED/CARE any animal tile that needs it, then WATER crops, then PLACE newly bought animals, then HARVEST, then PASS.
6. Evening: sell Milk first, then Wool/Melon/Strawberry as needed.
7. Never DROP entire inventory; only PLACE harvest goods.

### 5. Local acceptance gates before Kaggle upload
- Run the 29-seed offline suite (`private/Sep-17-2026-4/research/neuro_symbolic.py` or equivalent 29 seeds).
- Required: mean bank ≥ 58 000 and ≥ 21 wins vs s3 baseline.
- No regression on any single seed > 8 % below s3.
- Zero syntax/runtime errors on 1-second actTimeout.
- Farmer PASS count < 300 per episode on average.
- At least one run must show ≥ 8 cows placed and ≥ 100 milk sold.

### 6. Non-goals
- No RL or learned policy.
- No opponent shop denial or market manipulation.
- No multi-file structure or external libraries.
- No third land unless cash > $14k after day 16.
- No sheep > 1 before first cow.

Implement the above policy directly in `2026-09-17-s4/main.py`. Keep all logic inside the single `main.py` file using only standard library.