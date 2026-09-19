**Kaggriculture Submission Spec – 2026-09-19-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Starting rating: 600.
- No bank or inventory data available (mean bank = None).
- No opponents observed; no W/L/T data or specific loss patterns recorded.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (dumps entire shed). New bot must never call DROP; only use PLACE item n on harvest goods after they are produced.
- **Herd size**: No animal management policy; animals cannot be sold so over-purchase wastes turns and space.
- **Wheat buys**: No timing or quantity rule; bought wheat without matching land or storage.
- **Weeds**: No weeding action scheduled; weeds reduce yield on planted tiles.
- **Land timing**: Actions taken after market resolution or without checking available plots first.

### 3. Exact s1 policy table vs previous bot

| Situation                          | Previous bot (2026-09-18-s5) | s1 policy (2026-09-19-s1) |
|------------------------------------|--------------------------------|---------------------------|
| Empty plots available              | Buy random seeds               | If plots ≥ 3 and money ≥ 30: buy 3 wheat seeds |
| Harvest goods in inventory         | DROP or sell                   | PLACE item n (only harvest goods) |
| Weeds present on owned land        | Ignore                         | Weed one tile per turn if any |
| Animals in shop and money ≥ 80     | Buy 1 animal                   | Never buy animals (herd size = 0) |
| Wheat seeds bought this turn       | Plant immediately              | Hold until next turn (player actions before market) |
| No action possible                 | Random buy                     | PASS |
| Inventory full                     | DROP                           | PLACE highest-value harvest good first |

### 4. Task priority
1. Implement core loop that reads state and applies the s1 policy table above.
2. Add explicit check: never emit DROP.
3. Add weed scan + single-tile weeding.
4. Add simple wheat buy/plant rule (max 3 seeds when plots free).
5. Add PLACE logic only for harvest goods.
6. Add PASS fallback when no rule matches.
7. Ensure single-file main.py with only stdlib.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 random episodes locally without raising exceptions.
- Never emits the token “DROP” in any action.
- Wheat purchases ≤ 3 per turn and only when free plots ≥ 3.
- At least one PLACE action emitted on harvest goods in episodes that reach harvest.
- No animal purchases in any run.
- Total lines ≤ 300, single file, pure stdlib.

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or value tables.
- No multi-file structure or external data.
- No complex inventory scoring or long-term planning beyond the policy table.