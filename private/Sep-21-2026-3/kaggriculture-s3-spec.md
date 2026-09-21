# Kaggriculture Submission 3 Specification
Date: 2026-09-21 · Slot: s3 · Folder: `2026-09-21-s3/`

Previous Kaggle id: 56432006
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s3 Submission Spec**  
Folder: `2026-09-21-s3/`  
Target: replace `2026-09-21-s2` (id 56432006) with one `main.py`

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed yet).  
- Mean bank: None (no market data).  
- Starting rating: 600.  
- No opponents observed; no loss patterns available.

### 2. Root causes we must fix
- Previous bot used `DROP` on harvest goods (forbidden; loses all inventory).  
- No `PLACE item n` logic for harvested wheat/carrots.  
- No herd-size cap (animals cannot be sold, so over-purchase locks capital).  
- No wheat-buy limit when land is already planted.  
- No weed-clear timing (weeds block planting).  
- No land-timing rule (buy land only when current plots are fully used).  
- No `PICKUP` vs `PLACE` separation, causing thrash on same turn.

### 3. Exact s3 policy table vs previous bot

| Situation                          | s2 behaviour (previous)          | s3 behaviour (new)                                      |
|------------------------------------|----------------------------------|---------------------------------------------------------|
| Harvest goods in inventory         | `DROP`                           | `PLACE item n` on empty shed slot                       |
| Wheat seed available + empty plot  | Buy unlimited                    | Buy max 3 if plots < 4                                  |
| Animal available                   | Buy any                          | Buy at most 1 chicken or 1 cow only if bank > 120       |
| Weeds on any plot                  | Ignore                           | Clear one weed per turn before any buy/plant            |
| No empty plots + bank > 200        | Do nothing                       | Buy 1 land plot                                         |
| Harvest ready                      | `PICKUP` then `DROP`             | `PICKUP` then `PLACE item n` on next turn               |
| Nothing to do                      | Idle                             | `PICKUP` any ready harvest or clear one weed            |

All actions respect “player before market”. Never emit `DROP`.

### 4. Task priority
1. Implement `PLACE item n` harvest path (highest).  
2. Add simple weed-clear + land-buy rules.  
3. Add wheat and animal purchase caps.  
4. Remove all `DROP` calls.  
5. Add 1-second timeout guard (sleep 0.05 between actions if needed).

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs to completion with no `DROP` in output.  
- At least one `PLACE item n` emitted on harvest.  
- Herd size never exceeds 2 animals in any 50-turn simulation.  
- Wheat purchases stop at 3 when plots < 4.  
- No syntax/runtime errors under stdlib only.

### 6. Non-goals
- No opponent modelling or shop denial.  
- No RL or learned parameters.  
- No multi-file structure.  
- No coin maximisation heuristics beyond the policy table.
