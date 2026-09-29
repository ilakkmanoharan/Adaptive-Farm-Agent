# Kaggriculture Submission 2 Specification
Date: 2026-09-29 · Slot: s2 · Folder: `2026-09-29-s2/`

Previous Kaggle id: 56663751
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-29-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission, no episodes completed).
- Mean bank: None (no market resolution observed).
- Starting rating: 600.
- No opponent data available. Previous submission (56663751) also has zero games.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (forbidden). Must replace all harvest handling with `PLACE item n`.
- **Herd size**: No animal purchase logic; animals cannot be sold so we must avoid over-purchase.
- **Wheat buys**: No seed purchase timing; must buy wheat seed only when land is ready and inventory space exists.
- **Weeds**: No weed removal action; weeds block land and must be cleared before planting.
- **Land timing**: No `BUY_LAND` or `PLACE` sequencing; land must be acquired and cleared before any crop cycle.

### 3. Exact s2 policy table vs previous bot

| Situation                        | s1 (previous) behaviour          | s2 behaviour                                      | Reason |
|----------------------------------|----------------------------------|---------------------------------------------------|--------|
| Harvest goods in inventory       | DROP                             | `PLACE item n` (n = count)                        | Avoid full dump |
| Empty land + weeds present       | None                             | `REMOVE_WEED` until clear                         | Unblock planting |
| Empty land + no weeds + cash ≥ 5 | None                             | `BUY item wheat_seed 1` then `PLANT`              | One seed per turn |
| Land full + crop ready           | None                             | `HARVEST` then `PLACE item n`                     | Sell next turn |
| Cash ≥ 20 + herd < 2             | None                             | `BUY item chicken 1` (max 2 total)                | Small safe herd |
| No action possible               | None                             | `BUY_LAND` if cash ≥ 50 else `PASS`               | Expand only when safe |
| Inventory > 80% full             | None                             | Sell oldest crop first via market (no DROP)       | Prevent overflow |

All actions use only documented stdlib calls. No `DROP`.

### 4. Task priority
1. Implement core loop with `PLACE` instead of `DROP`.
2. Add weed removal before any plant action.
3. Add single wheat seed buy + plant when land ready.
4. Add `BUY_LAND` only when cash ≥ 50 and no pending crops.
5. Cap chicken purchases at 2 total.
6. Add simple inventory check to sell before buying more seed.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs without import or syntax errors using only stdlib.
- No `DROP` string appears in source.
- At least one `PLACE`, `REMOVE_WEED`, `BUY item wheat_seed`, and `BUY_LAND` path exists.
- Herd size never exceeds 2 in any simulated branch.
- Code finishes within 1 s per turn on a 100-turn dummy loop.

### 6. Non-goals
- No RL or learning.
- No opponent shop interference.
- No multi-file structure.
- No complex inventory sorting or price prediction.
