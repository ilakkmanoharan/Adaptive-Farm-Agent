**Kaggriculture s4 Submission Spec**  
**Date:** 2026-09-18 slot 4/5  
**Folder:** `2026-09-18-s4/`  
**Target:** one stdlib `main.py` only (no RL, no opponent shop actions)

### 1. Ladder facts
- Current record: 0W-0T-0L (fresh slot entry, rating starts at 600).
- No completed episodes yet; previous s3 bot (id 56335713) produced 0W-0T-0L with bank = None on every replay.
- No opponent names or specific loss patterns available. All scoring is W/L/T only; unsold inventory contributes 0.

### 2. Root causes to fix
- **DROP/PICKUP thrash**: previous bot issued DROP on every harvest cycle, emptying the entire shed instead of selective PLACE.
- **Herd size**: never grew beyond 1 animal; animals cannot be sold so idle capacity was wasted.
- **Wheat buys**: bought wheat every turn regardless of land state or existing inventory.
- **Weeds**: no weeding action; land degraded and stayed unproductive.
- **Land timing**: actions taken after market resolution; seeds/animals bought on turn t could not be used until t+1.

### 3. Exact s4 policy table (vs previous bot)

| Condition (checked in order) | s4 action | previous bot action |
|------------------------------|-----------|---------------------|
| Weeds present on any owned land | WEED that land | (none) |
| Empty land available and no seed in hand | BUY WHEAT (max 1) | BUY WHEAT every turn |
| Own < 3 animals and cash >= animal cost | BUY ANIMAL (max 1 per turn) | (never) |
| Harvest goods in inventory | PLACE item 1 (repeat until inventory empty) | DROP |
| Ripe crop on land | HARVEST | (inconsistent) |
| No weeds, no harvest, no ripe crop, cash >= 2×animal cost | BUY ANIMAL | (never) |
| Otherwise | WAIT | (various) |

All checks use only current observation state. No market actions after turn start. Animals kept permanently.

### 4. Task priority
1. Replace every DROP with PLACE loop (highest impact).
2. Add weed detection + WEED action.
3. Add herd growth rule (target 3 animals).
4. Gate wheat purchase behind empty land check.
5. Enforce one-action-per-turn ordering that respects “player before market”.
6. Add minimal cash guard so bot never goes negative on first buy.

### 5. Local acceptance gates (run before any Kaggle upload)
- `python main.py` must complete 100 deterministic turns with zero exceptions and actTimeout < 1 s.
- Inventory never contains >0 items after a PLACE loop.
- Herd size reaches exactly 3 within 30 turns on empty start.
- No wheat purchase occurs when all land is occupied or weedy.
- Final score (W/L/T) is produced solely from sold goods; unsold inventory = 0.

### 6. Non-goals
- No opponent shop observation or denial.
- No reinforcement learning or parameter search.
- No multi-file structure; everything in single `main.py`.
- No DROP command anywhere in code.