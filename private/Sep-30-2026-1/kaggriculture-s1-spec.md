# Kaggriculture Submission 1 Specification
Date: 2026-09-30 · Slot: s1 · Folder: `2026-09-30-s1/`

Previous Kaggle id: 56694054
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-30-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no data).
- No opponents observed. Previous bot (56694054) also has zero recorded ladder games. Skill rating remains at starting 600. No wins/losses to analyze.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (which empties entire inventory). Replace with targeted PLACE n on harvest goods only.
- **Herd size**: No animal management policy; animals cannot be sold so over-purchase locks capital.
- **Wheat buys**: Unconditional or mistimed wheat purchases; must gate on current land + expected harvest timing.
- **Weeds**: No weed-clearing priority; weeds block planting and reduce effective land.
- **Land timing**: Actions resolve before market; bot must buy/place land before attempting to plant on it in same turn.

### 3. Exact s1 policy table vs previous bot

| Situation                          | Previous bot (56694054)          | s1 policy (2026-09-30-s1)                          |
|------------------------------------|----------------------------------|----------------------------------------------------|
| Harvest goods in inventory         | DROP                             | PLACE n (only the harvested item)                  |
| Weeds present on owned land        | Ignore                           | Clear weed first (highest priority action)         |
| No owned land + cash ≥ land price  | Buy land                         | Buy land only if cash ≥ land price + 2×seed cost   |
| Animals in shop + cash available   | Buy animals                      | Never buy animals (non-goal)                       |
| Wheat in shop + land available     | Buy wheat                        | Buy wheat only if ≥1 empty plot and cash ≥ 3×seed  |
| Empty plot + seed in inventory     | Plant                            | Plant only after weed check and land ownership     |
| Inventory full + no market sale    | DROP                             | PLACE n (harvest) or hold (no DROP)                |

### 4. Task priority
1. Replace all DROP with PLACE n for harvest goods.
2. Add weed-clear action before any plant/buy.
3. Add land-ownership guard before wheat purchase.
4. Remove all animal purchase logic.
5. Add simple cash-reserve check for wheat buys.
6. Ensure single-file main.py runs under 1 s actTimeout.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` completes 100 simulated turns with zero exceptions and zero DROP calls.
- Inventory never exceeds 20 items at any turn.
- At least one successful PLACE of a harvest good observed in logs.
- No animal purchases attempted.
- Total runtime per turn < 800 ms on stdlib only.
- Code fits in single `main.py` (no external files).

### 6. Non-goals
- No RL or learning.
- No opponent shop interference.
- No multi-file structure.
- No animal-related code.
- No complex market timing beyond the policy table.
