# Kaggriculture Submission 5 Specification
Date: 2026-09-21 · Slot: s5 · Folder: `2026-09-21-s5/`

Previous Kaggle id: 56445189
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-21-s5**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new slot, rating starts at 600).
- No completed episodes; no opponent data, no bank values observed.
- Previous submission (56445189 / 2026-09-21-s4) has zero wins logged in this slot.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: s4 used DROP on harvest turns, emptying entire inventory instead of PLACE n. This caused repeated zero-score turns.
- **Herd size**: No cap on animal purchases; inventory filled with unsellable animals, blocking crop sales.
- **Wheat buys**: Bought wheat every turn regardless of land or season, leading to excess unsold inventory.
- **Weeds**: No weeding action; weeds reduced yields on existing plots.
- **Land timing**: Bought land too early or too late relative to cash and seed stock, leaving plots idle.

### 3. Exact s5 policy table vs previous bot

| Situation                          | s4 behaviour (previous)          | s5 behaviour (new)                                      |
|------------------------------------|----------------------------------|---------------------------------------------------------|
| Harvest goods in inventory         | DROP                             | PLACE item n (only the harvested goods)                 |
| Cash ≥ 120 and empty plots ≥ 2     | Buy land                         | Buy land only if wheat seeds ≥ 4                        |
| Cash ≥ 80 and wheat seeds < 6      | Buy wheat                        | Buy wheat only if plots available and no weeds          |
| Weeds present on any plot          | Ignore                           | Weed highest-weed plot first                            |
| Animals owned ≥ 3                  | Buy more animals                 | Never buy animals (cap at 2 from start)                 |
| Inventory full and no PLACE target | Idle                             | Sell any crop that is not wheat if cash < 40            |
| No action possible                 | Idle                             | Weed or buy 1 wheat seed if cash ≥ 20                   |

All decisions are deterministic if-then rules executed in the order above. No loops, no recursion.

### 4. Task priority
1. Replace DROP with PLACE n on every harvest.
2. Add hard animal purchase cap (max 2 total).
3. Add weed action before any buy/plant.
4. Gate wheat and land purchases behind seed/land checks.
5. Add minimal sell logic for non-wheat crops when cash low.
6. Single-file main.py only; no new modules.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns with zero `DROP` calls.
- Never owns >2 animals.
- Performs at least one WEED action when weeds appear.
- Ends with ≥1 crop sold via PLACE (not left in inventory).
- No syntax/runtime errors under stdlib only; finishes in <1s per turn.
- Bank never goes negative.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned parameters.
- No multi-file structure.
- No complex pathfinding or timing beyond the table above.
- No handling of TIE outcomes or rating math.
