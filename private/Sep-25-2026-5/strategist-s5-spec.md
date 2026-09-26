**Kaggriculture s5 Submission Spec**

**1. Ladder facts from these games**  
- Record: 0W-0T-0L (no completed episodes yet).  
- Starting rating: 600.  
- No opponent data; mean bank unknown.  
- Previous bot (s4, id 56561052) has zero wins logged. All future matches will be against fresh or low-rating bots.

**2. Root causes we must fix**  
- DROP/PICKUP thrash: s4 repeatedly issued DROP (or equivalent) on harvest goods instead of PLACE n, losing inventory value.  
- Herd size: never scaled animals beyond 1–2; animals cannot be sold so idle herd wastes turns.  
- Wheat buys: bought wheat seed every turn regardless of land or storage, causing over-purchase and no harvest timing.  
- Weeds: ignored weed growth; land left fallow too long.  
- Land timing: actions taken after market close; never pre-bought land or seeds one turn ahead.

**3. Exact s5 policy table vs previous bot**

| State (observed)              | s4 behaviour (broken)          | s5 behaviour (fixed)                          | Priority |
|-------------------------------|--------------------------------|-----------------------------------------------|----------|
| Empty land + ≥1 seed in inv   | Buy more seed                  | PLACE seed on land                            | 1        |
| Harvest ready                 | DROP or PICKUP                 | PLACE n (harvest goods only)                  | 1        |
| ≥3 wheat in inv + no animals  | Sell nothing / buy more        | BUY 1 animal if money ≥ price                 | 2        |
| Weeds visible on any plot     | Ignore                         | WEED that plot                                | 2        |
| Money ≥ 80 + empty land       | Do nothing                     | BUY land                                      | 3        |
| Animal count < 3 + money ≥ price | —                           | BUY animal (max 3 total)                      | 3        |
| Any other state               | Random / thrash                | PASS                                          | —        |

All decisions use only stdlib; single forward pass per turn. Never emit DROP.

**4. Task priority**  
1. Implement state reader + policy table above (core loop).  
2. Add simple inventory/land/weed counters.  
3. Enforce PLACE n instead of DROP.  
4. Add animal buy cap at 3.  
5. Local test harness + acceptance gates.  
6. Package as single `main.py`.

**5. Local acceptance gates before Kaggle upload**  
- 100 simulated turns with zero DROP commands.  
- Herd reaches exactly 3 animals and stays ≤3.  
- At least one full wheat→harvest→PLACE cycle completed.  
- No action after market resolution (all buys/place happen on player phase).  
- Runtime ≤ 0.8 s per turn on 1 s timeout machine.  
- Single file `main.py` runs with only Python stdlib.

**6. Non-goals**  
- No opponent modelling or shop denial.  
- No RL or learned policy.  
- No multi-file structure.  
- No complex storage or pricing models.  
- No handling of >3 animals or exotic crops.