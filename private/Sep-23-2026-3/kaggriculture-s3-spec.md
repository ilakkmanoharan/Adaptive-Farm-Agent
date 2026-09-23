# Kaggriculture Submission 3 Specification
Date: 2026-09-23 · Slot: s3 · Folder: `2026-09-23-s3/`

Previous Kaggle id: 56491534
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-23-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, rating starts at 600).
- Mean bank: None (no completed episodes).
- No opponent data available. Previous submission (56491534) also has zero recorded games. All future matches will be against bots that have already played ≥1 episode.

### 2. Root causes we must fix
- **Inventory thrash**: Previous bot used DROP on harvest turns, dumping entire shed instead of selective PLACE. This loses all unsold goods and prevents scoring.
- **Herd size**: No cap on animals; excess animals consume feed without producing sellable output (animals cannot be sold).
- **Wheat buys**: Bought wheat every turn regardless of existing inventory or land state, leading to over-purchase and wasted coins.
- **Weeds**: No weed-clearing action before planting; weeds block land use and reduce effective planting area.
- **Land timing**: Attempted to buy/expand land before clearing existing plots or having enough seeds/animals to use new land.

### 3. Exact s3 policy table vs previous bot

| Situation (checked in order) | s3 action | Previous bot action | Reason |
|------------------------------|-----------|---------------------|--------|
| Weeds present on any plot | CLEAR weeds | (none) | Prevents blocked land |
| Shed has harvest goods | PLACE item n (specific counts only) | DROP | Avoids total inventory loss |
| Animals ≥ 4 | No new animal buys | Bought freely | Prevents feed waste |
| Wheat in shed < 3 and coins ≥ price | BUY wheat (max 3) | Bought every turn | Controlled purchase |
| Empty usable land exists and seeds available | PLANT wheat | (inconsistent) | Use existing land first |
| Coins ≥ land price and all current land in use + cleared | BUY land (1) | Bought early | Only after current land is productive |
| Otherwise | WAIT | Various | Default safe action |

All decisions use only stdlib; no external APIs.

### 4. Task priority
1. Implement state reader (current land, shed contents, animal count, weeds, coins) using only provided observation format.
2. Add CLEAR weeds logic before any plant/buy.
3. Replace all DROP with targeted PLACE.
4. Add animal count cap (max 4) and wheat buy cap (max 3 in shed).
5. Add land expansion guard (only when all plots cleared and in use).
6. Wire the exact policy table above into the main loop.
7. Add 1-second actTimeout safety (simple time check).

### 5. Local acceptance gates before Kaggle upload
- Runs 1000 turns with no exceptions and stays under 1s per action.
- Never emits DROP.
- Animal count never exceeds 4.
- Wheat in shed never exceeds 3 after a buy.
- At least one CLEAR action occurs when weeds are present in test scenarios.
- Final shed value > 0 at end of 1000-turn test (unsold goods score).

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policies.
- No multi-file structure (single main.py only).
- No new environment APIs or assumptions beyond the documented observation/action format.
