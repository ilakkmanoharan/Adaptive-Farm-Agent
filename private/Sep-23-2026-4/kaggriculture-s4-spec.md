# Kaggriculture Submission 4 Specification
Date: 2026-09-23 · Slot: s4 · Folder: `2026-09-23-s4/`

Previous Kaggle id: 56498934
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s4 Submission Spec**

**Folder:** `2026-09-23-s4/`  
**Target file:** `main.py` (single stdlib file, <400 LOC)  
**Previous:** 56498934 (s3)  
**Current record:** 0W-0T-0L (rating starts at 600)

### 1. Ladder facts
- No episodes completed. Bank value unknown.
- No opponents observed. No W/L data or bank comparisons available.
- All prior s3 behavior is treated as baseline; s4 must improve survival and scoring under the same rules (unsold inventory = 0 points, animals unsellable).

### 2. Root causes to fix
- **DROP/PICKUP thrash**: s3 used DROP on harvest turns, dumping entire inventory. s4 must never call DROP; only use PLACE n on harvest goods.
- **Herd size**: Over-purchased animals early, locking capital with no sell option.
- **Wheat buys**: Bought wheat seed every turn regardless of land state or existing inventory.
- **Weeds**: No weeding action; plots became unproductive.
- **Land timing**: Actions taken after market close or on already-planted tiles; player actions must resolve before market.

### 3. Exact s4 policy table (vs s3)

| Situation                          | s3 behavior                  | s4 behavior                                      | Priority |
|------------------------------------|------------------------------|--------------------------------------------------|----------|
| Empty plot + seed in inv           | Plant immediately            | Plant only if plot count < 6                     | High     |
| Harvest ready                      | DROP                         | PLACE n (specific harvest stack)                 | High     |
| Weeds present                      | Ignore                       | Weed up to 3 plots before any other action       | High     |
| Wheat seed available + no wheat    | Buy 1 wheat seed             | Buy wheat seed only if inv.wheat < 2             | Med      |
| Animal slot open + money > 120     | Buy animal                   | Never buy animals (capital lock)                 | High     |
| Inventory full + sellable goods    | Hold                         | Sell all sellable goods before end of turn       | High     |
| No action possible                 | Idle                         | Idle (respect 1s timeout)                        | Low      |

Policy is deterministic if-then chain. No state machine beyond current inventory + visible plots.

### 4. Task priority (implement order)
1. Remove all DROP calls; replace with PLACE on harvest.
2. Add weed scan + weed action (max 3 per turn).
3. Add simple inventory guards: wheat ≤ 2, no animal purchases.
4. Add sell logic for all sellable goods at end of turn.
5. Add plot count guard (max 6 active plots).
6. Basic turn skeleton with player actions before market.

### 5. Local acceptance gates (before upload)
- `python main.py` runs in <0.8 s per turn for 50 simulated turns.
- No DROP appears in any output log.
- At least one PLACE call per harvest event.
- Wheat purchases stop once inventory reaches 2.
- Zero animal purchases in any test run.
- Code uses only stdlib (no external imports).

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned parameters.
- No complex pathfinding or multi-turn planning.
- No animal management logic.
- No coin maximization heuristics beyond the policy table.

Implement the policy table as a single `decide()` function called each turn. Keep all logic in `main.py`.
