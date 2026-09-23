**Kaggriculture Submission Spec – 2026-09-23-s1**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new daily slot, no episodes played yet).
- Starting rating: 600 (standard new-bot baseline).
- Mean bank: None (no data).
- No opponents observed. Previous submission (56477247) also has zero recorded games in this slot.

### 2. Root causes we must fix
- **DROP abuse**: Previous bot used DROP, which empties the entire inventory. Must replace every DROP with targeted `PLACE item n`.
- **Herd size drift**: No cap on animals; unsold animals give zero score and block inventory slots.
- **Wheat buy timing**: Bought wheat without checking current land availability or weed status, leading to idle turns.
- **Weed handling**: No explicit weed removal step before planting.
- **Land timing**: Actions taken before market resolution; land purchases must be sequenced after checking current free plots.
- **Inventory scoring**: Unsold goods at end of episode score nothing; policy must prioritize selling over hoarding.

### 3. Exact s1 policy table vs previous bot

| State check (in order)          | s1 action                          | Previous bot action | Reason |
|--------------------------------|------------------------------------|---------------------|--------|
| Weeds present on any plot      | Remove weed (highest priority)    | None                | Prevents blocked planting |
| Free plots == 0                | Buy land (max 1 per turn)         | Buy land            | Same, but after weed check |
| Wheat in inventory ≥ 1 and free plots > 0 | Plant wheat                      | Plant wheat         | Same |
| Animals > 4                    | Sell animal (oldest first)        | None                | Prevents herd bloat |
| Harvest goods in inventory     | `PLACE item n` (one at a time)    | DROP                | Avoids total inventory loss |
| Cash ≥ 50 and wheat price low  | Buy wheat (min(3, free plots))    | Buy wheat           | Added cash & plot guard |
| No other action possible       | Sell any harvest goods            | Sell                | Ensures scoring |

All actions respect “player before market” ordering. Never emit DROP.

### 4. Task priority
1. Implement state checks and policy table above in single `main.py`.
2. Replace every DROP with `PLACE item n`.
3. Add hard herd cap (≤4 animals) and auto-sell logic.
4. Add weed removal and land-buy sequencing.
5. Add simple wheat buy guard (cash + free plots).
6. Ensure all selling uses market sell action, not inventory drop.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs with no syntax/runtime errors under stdlib only.
- No `DROP` string appears in source.
- Herd size never exceeds 4 in any simulated 50-turn loop.
- At least one `PLACE` call is present for harvest goods.
- Code contains the exact ordered policy table as comments or dict.
- Total file ≤ 300 lines, single file, no external imports.

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or learned parameters.
- No multi-file structure or custom classes beyond simple functions.
- No complex pathfinding or timing beyond the policy table.
- No handling of future rule changes.