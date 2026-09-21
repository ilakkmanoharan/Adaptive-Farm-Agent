# Kaggriculture Submission 2 Specification
Date: 2026-09-21 · Slot: s2 · Folder: `2026-09-21-s2/`

Previous Kaggle id: 56418495
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec: 2026-09-21-s2**

**Folder:** `2026-09-21-s2/`  
**Target file:** `main.py` (single stdlib file, <1s actTimeout)  
**Previous:** 56418495 (2026-09-21-s1)

### 1. Ladder Facts
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no scored games).
- No opponents observed; bot starts at default 600 rating.
- No W/L data available; focus on stable first-turn execution and inventory scoring.

### 2. Root Causes to Fix
- **DROP/PICKUP thrash**: s1 used DROP on harvest goods; replace with `PLACE item n` only. Never emit DROP.
- **Herd size**: No animal sales allowed; s1 over-purchased animals without land support. Cap at 2 animals total.
- **Wheat buys**: Bought wheat seeds same turn as planting (invalid). Enforce buy-then-plant separation.
- **Weeds**: No weed removal logic; weeds block land. Add explicit weed check before plant.
- **Land timing**: Bought land after seeds; player actions resolve before market. Buy land first, then seeds/animals.

### 3. Exact s2 Policy Table vs Previous Bot

| Situation                  | s1 Behavior (previous)          | s2 Behavior (new)                          | Rule ID |
|----------------------------|---------------------------------|--------------------------------------------|---------|
| Turn 1, no land            | Buy seeds first                | Buy 1 land plot                            | L1     |
| After land owned, no seeds | Buy wheat seeds                | Buy 2 wheat seeds + 1 animal               | S1     |
| Weeds present on land      | Ignore / plant anyway          | Remove weed first                          | W1     |
| Harvest ready              | DROP inventory                 | PLACE item 0, PLACE item 1 (max 2)         | H1     |
| Inventory > 4 items        | Continue buying                | Sell 2 oldest harvest goods                | I1     |
| Animals >= 3               | Buy more                       | Stop animal purchases                      | A1     |
| Bank < 50                  | Buy anything                   | Only buy land or wheat seeds               | B1     |

All rules checked in fixed order each turn. No market denial.

### 4. Task Priority
1. Implement land-first buy + weed removal (L1 + W1).
2. Replace all DROP with PLACE n (H1).
3. Add animal cap at 2 and wheat buy-after-land (S1 + A1).
4. Add simple inventory sell when >4 (I1).
5. Bank guard (B1).
6. Single-file main.py with deterministic state machine (no external libs).

### 5. Local Acceptance Gates (before upload)
- Run 20 local episodes: ≥80% turns without invalid action (no same-turn buy+use, no DROP).
- Final inventory always scored (no unsold goods left in shed at end).
- Herd size never exceeds 2.
- No actTimeout >800ms on any turn.
- Bank never negative after any action sequence.

### 6. Non-Goals
- No RL or learned policy.
- No opponent shop interaction or denial.
- No multi-file code or external dependencies.
- No complex crop rotation or long-term planning beyond the 6 rules above.
