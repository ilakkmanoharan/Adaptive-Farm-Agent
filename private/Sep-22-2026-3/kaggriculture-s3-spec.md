# Kaggriculture Submission 3 Specification
Date: 2026-09-22 · Slot: s3 · Folder: `2026-09-22-s3/`

Previous Kaggle id: 56467225
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s3 Submission Spec**

**Date:** 2026-09-22 slot 3/5  
**Folder:** `2026-09-22-s3/`  
**Base:** `2026-09-22-s2` (id 56467225)  
**Constraint:** single stdlib `main.py`, 1 s timeout, no RL, no shop denial.

### 1. Ladder facts from these games
- Record: 0W-0T-0L  
- Mean bank at end of episode: None (no completed games)  
- No opponent data yet. New bot starts at 600 rating. All future wins/losses will be measured strictly by final W/L/T after market resolution.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: previous bot used DROP on harvest turns, dumping entire inventory instead of selective PLACE.  
- **Herd size**: no cap on animals; feed cost and space starvation after turn 8–10.  
- **Wheat buys**: bought wheat seed every turn regardless of existing stock or season.  
- **Weeds**: never cleared; reduced plantable tiles by 15–25 % by mid-game.  
- **Land timing**: expanded land before any harvest revenue, leaving negative effective cash for 4+ turns.

### 3. Exact s3 policy table vs previous bot

| Situation (checked in order) | s3 action | s2 behaviour (to replace) |
|------------------------------|-----------|---------------------------|
| Weeds present on any owned tile | CLEAR nearest weed | ignored |
| Inventory has harvest goods (wheat, eggs, milk) | PLACE item 1 (repeat until empty) | used DROP |
| Cash ≥ 12 and wheat stock < 8 and no pending plant | BUY wheat_seed 4 | bought every turn |
| Cash ≥ 25 and cows < 3 and feed stock ≥ 4 | BUY cow 1 | bought cows unbounded |
| Cash ≥ 15 and chickens < 5 and feed stock ≥ 3 | BUY chicken 1 | same |
| Any crop ready | HARVEST nearest | same |
| Empty tile and wheat seed in inventory | PLANT wheat | same |
| Cash ≥ 40 and total land < 12 and last expansion ≥ 6 turns ago | EXPAND 1 | expanded too early |
| Feed stock < 3 and cash ≥ 6 | BUY feed 6 | ignored feed |
| Nothing above | WAIT | same |

All checks use only current observation; no history beyond “turns since last expand”.

### 4. Task priority (implementation order)
1. Replace every DROP with PLACE loop.  
2. Add weed scan + CLEAR before any buy/plant.  
3. Add hard caps: cows ≤ 3, chickens ≤ 5.  
4. Add wheat stock guard (buy only if < 8).  
5. Add land expansion cooldown (≥ 6 turns).  
6. Add minimal feed buy rule.  
7. Wire the ordered policy table into the main loop.

### 5. Local acceptance gates before Kaggle upload
- Runs 50 random episodes with no exception and act < 800 ms.  
- Zero uses of DROP in any log.  
- Final inventory value ≥ 30 in ≥ 70 % of episodes (unsold goods do not score).  
- Herd never exceeds 3 cows + 5 chickens.  
- At least one CLEAR action executed in episodes where weeds appear.

### 6. Non-goals
- No opponent modelling or shop blocking.  
- No multi-turn planning or search.  
- No new crop/animal types.  
- No config files or external data.  
- No changes to folder layout beyond single `main.py`.
