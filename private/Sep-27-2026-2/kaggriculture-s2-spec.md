# Kaggriculture Submission 2 Specification
Date: 2026-09-27 · Slot: s2 · Folder: `2026-09-27-s2/`

Previous Kaggle id: 56605959
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s2 Submission Spec**  
`2026-09-27-s2/` (one `main.py`, stdlib only)

### 1. Ladder facts from these games
- Record: 0W-0T-0L  
- Mean bank: None (no episodes completed)  
- No opponents observed. New bot starts at 600 rating. No data on who beat us or how.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Never emit `DROP`. Use `PLACE item n` only on harvest goods.  
- **Herd size**: No animals purchased until land and wheat pipeline are stable (animals cannot be sold).  
- **Wheat buys**: Over-buying seeds without matching plantable land.  
- **Weeds**: No weeding action in previous bot; weeds block tiles.  
- **Land timing**: Actions resolve before market; must buy/place land before attempting to plant on it.

### 3. Exact s2 policy table vs previous bot

| Situation                        | s1 (previous) behaviour          | s2 behaviour                                      |
|----------------------------------|----------------------------------|---------------------------------------------------|
| Bank < 50                        | Idle / random buy                | `BUY wheat 1` only if land available              |
| Empty fertile tile + wheat ≥ 1   | Plant if possible                | `PLANT wheat` on lowest-index empty tile          |
| Harvest ready                    | —                                | `HARVEST` then `PLACE wheat n` (n = count)        |
| Weeds present                    | None                             | `WEED` lowest-index weeded tile first             |
| No land + bank ≥ 200             | —                                | `BUY land 1`                                      |
| Animals affordable               | —                                | Never buy (until s3)                              |
| Any other action                 | —                                | `PASS`                                            |

Action order per turn (first that applies):
1. `WEED` if any weeds  
2. `HARVEST` if any ready  
3. `PLACE wheat n` if harvested wheat > 0  
4. `PLANT wheat` if wheat ≥ 1 and empty tile  
5. `BUY land 1` if bank ≥ 200 and < 3 land tiles  
6. `BUY wheat 1` if bank ≥ 10 and wheat < 5 and land available  
7. `PASS`

### 4. Task priority
1. Implement deterministic 7-step action loop above in `main.py`  
2. Track inventory, land count, and weed/ready state from observations only (no env APIs invented)  
3. Ensure `PLACE` is used instead of `DROP`  
4. Add minimal state machine so actions are emitted within 1 s

### 5. Local acceptance gates before Kaggle upload
- Runs 100 turns without exception or `DROP`  
- Never buys animals  
- Emits only the 7 allowed actions in the defined order  
- Produces non-zero score on at least one simulated episode (unsold inventory = 0)

### 6. Non-goals
- No opponent modelling or shop denial  
- No RL / learning  
- No multi-file structure  
- No animal logic  
- No market timing beyond the simple policy table
