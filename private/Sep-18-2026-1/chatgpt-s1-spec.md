**Kaggriculture Submission Spec – 2026-09-18-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission after reset)
- Mean bank: None (no episodes completed)
- No opponent data available. Previous bot (56317174) also had 0 recorded games in the provided briefing. No W/L/T or bank values to compare.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (dumps entire inventory). New bot must never call DROP; only use PLACE n on harvest goods when shed space is needed.
- **Herd size**: No animal sales possible. Policy must cap chicken/cow purchases at 2 animals total to avoid feed starvation.
- **Wheat buys**: Over-purchasing wheat when land is not yet planted. Policy buys wheat only after at least one empty plot is owned.
- **Weeds**: No weeding action observed in prior logic. Policy must issue WEED on any plot that returns weed state before planting.
- **Land timing**: Buying land too early or too late relative to cash. Policy buys land only when cash ≥ 120 and current plots ≤ 3.

### 3. Exact s1 policy table vs the previous bot

| Situation                          | Previous bot (2026-09-17-s5) | s1 policy (2026-09-18-s1) |
|------------------------------------|--------------------------------|---------------------------|
| Cash ≥ 120 and plots ≤ 3           | Buy land or do nothing         | BUY_LAND                  |
| Plot is weeds                      | Ignore                         | WEED                      |
| Empty plot + wheat in inventory    | Plant only if wheat > 5        | PLANT_WHEAT               |
| Harvest ready                      | PICKUP then possibly DROP      | PICKUP then PLACE 1 if shed full |
| Animals owned < 2 and cash ≥ 80    | Buy animal                     | BUY_CHICKEN               |
| Animals owned ≥ 2                  | Continue buying                | Never buy more animals    |
| Wheat in inventory = 0 and plots planted | Buy wheat                      | Buy wheat only if empty plots exist |
| Any other state                    | Random or stall                | PASS                      |

All actions are single-action per turn. No multi-action sequences.

### 4. Task priority
1. Implement core state parser (plots, inventory, cash, animals) using only stdlib.
2. Hard-code the policy table above as if-elif chain.
3. Add explicit guard: never emit DROP.
4. Add explicit guard: never buy >2 animals.
5. Add minimal shed management using PLACE only on harvested goods.
6. Add local test harness that runs 50 deterministic turns and checks no forbidden actions.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` must run for 50 turns with zero exceptions and zero DROP calls.
- Inventory never exceeds shed capacity (enforced by PLACE logic).
- Animal count never exceeds 2.
- At least one WEED and one PLACE action must be exercised in the 50-turn test.
- Final binary must be single file `main.py` with only stdlib imports.
- No print statements left in submitted code.

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or parameter search.
- No multi-file structure.
- No handling of sell animals (impossible per rules).
- No complex pathing or timing beyond the policy table.