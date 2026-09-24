**Kaggriculture s5 Submission Spec**

**Folder:** `2026-09-23-s5/`  
**Target file:** `main.py` (single stdlib file, no external deps)  
**Previous:** 56502929 (2026-09-23-s4)

### 1. Ladder facts from these games
- Record: 0W-0T-0L
- Mean bank: None (no episodes completed)
- No opponent data available. No wins/losses recorded. Skill rating still at initial 600.

### 2. Root causes we must fix
- **No prior episodes** → s4 policy never executed; we start from a clean slate with only the known hard rules.
- **DROP risk**: Any use of DROP is fatal (dumps entire inventory). s5 must never emit DROP.
- **PLACE discipline**: Only use `PLACE item n` on harvest goods (wheat, etc.). Animals never sold.
- **Action ordering**: Player actions resolve before market → must buy/plant/harvest in correct sequence within the same turn when possible.
- **Inventory scoring**: Unsold goods score 0 → must convert to sales every cycle.
- **Herd/land timing**: No data yet, but s5 must avoid over-committing early turns to animals or land before first harvest cash.

### 3. Exact s5 policy table vs previous bot

| Situation (observed state)              | s4 behavior (previous)          | s5 behavior (new)                                      | Reason |
|-----------------------------------------|---------------------------------|-------------------------------------------------------|--------|
| Turn 1, bank ≥ 10, no land              | Buy land or wheat               | Buy 1 land if bank ≥ 20 else buy 5 wheat              | Secure planting space first |
| Wheat seeds in inventory, empty plots   | Plant immediately               | Plant all wheat seeds on empty plots                  | Same, but explicit |
| Harvested wheat in inventory            | Sell immediately                | Sell all wheat (no animals yet)                       | Convert to cash before next buy |
| Bank ≥ 30, no animals                   | Buy 1 animal                    | Do nothing (defer animals)                            | Avoid early herd cost with 0 data |
| Weeds present on owned land             | Ignore or buy more land         | Buy 1 weed killer if bank ≥ 5                         | Minimal weed control |
| No action possible this turn            | Idle or DROP                    | Idle (never DROP)                                     | Safety |
| Any inventory of harvest goods          | Mixed sell/PLACE                | Always sell harvest goods; PLACE only if explicitly needed for storage (rare) | Maximize score |
| Bank < 10                               | Buy cheapest seed               | Idle or minimal wheat if possible                     | Prevent negative actions |

### 4. Task priority (implementation order in main.py)
1. Core loop: read state, never emit DROP.
2. Implement s5 policy table above as simple if/elif chain.
3. Add basic wheat buy → plant → harvest → sell cycle.
4. Add minimal weed killer purchase when weeds detected.
5. Defer all animal purchases until after first successful sale cycle.
6. Add safe idle when no profitable action.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs without syntax/runtime errors for 100 simulated turns (mock state).
- Never prints/emits the token `DROP` in any output.
- Always sells harvest goods when present in inventory.
- Bank never goes negative on buys.
- At least one full wheat cycle (buy → plant → harvest → sell) completes without error.
- Code fits in single `main.py` using only stdlib.

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learning.
- No complex herd sizing or multi-crop strategies.
- No land expansion beyond 1 plot until cash flow proven.
- No use of PLACE except when required for harvest goods (avoid unless necessary).