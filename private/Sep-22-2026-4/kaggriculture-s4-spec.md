# Kaggriculture Submission 4 Specification
Date: 2026-09-22 · Slot: s4 · Folder: `2026-09-22-s4/`

Previous Kaggle id: 56471865
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s4 Submission Spec**  
**Folder:** `2026-09-22-s4/`  
**Target file:** `main.py` (single stdlib file)  
**Previous:** 56471865 (s3)

### 1. Ladder facts from these games
- Record: 0W-0T-0L  
- Mean bank: None (no completed episodes)  
- No opponent data available. All rating movement will come from first real matches after upload.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: s3 used DROP on harvest turns, dumping entire shed and losing scoring items.  
- **Herd size**: No cap on animals bought; inventory bloat prevented selling harvested goods.  
- **Wheat buys**: Bought wheat every turn regardless of land or existing stock.  
- **Weeds**: Never cleared weeds before planting, causing zero-yield turns.  
- **Land timing**: Bought extra land before existing plots were productive; actions resolved before market so unsold goods scored 0.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behaviour (previous)          | s4 behaviour (new)                                      |
|------------------------------------|----------------------------------|---------------------------------------------------------|
| Weeds present on any plot          | Ignore                           | Clear one weed per turn (highest priority)              |
| Empty fertile plot + wheat ≥ 1     | Buy wheat                        | Plant wheat if no weeds                                 |
| Harvest ready                      | DROP                             | PLACE item n (only harvested goods)                     |
| Animals owned ≥ 3                  | Keep buying                      | Stop buying animals                                     |
| Wheat in inventory ≥ 4             | Keep buying                      | Stop buying wheat                                       |
| No fertile land free + wheat ≥ 2   | Buy land                         | Do not buy land                                         |
| Nothing else to do                 | Buy wheat / animals              | Sell one harvested good if any in inventory             |
| Bank < 10                          | Any buy                          | Only clear weeds or sell                                |

### 4. Task priority (implementation order in main.py)
1. Weed clearing check (first action each turn)  
2. Harvest → PLACE (never DROP)  
3. Plant wheat only on clean plots when stock allows  
4. Animal purchase gate (max 3 total)  
5. Wheat purchase gate (max 4 in inventory)  
6. Land purchase gate (only if ≥1 clean empty plot and wheat stock < 2)  
7. Sell one item if inventory has harvest goods and no other action taken  
8. Idle if nothing matches

### 5. Local acceptance gates before Kaggle upload
- Runs 50 turns without exception or DROP call  
- Never owns >3 animals  
- Never has >4 wheat in inventory at end of turn  
- Performs at least one PLACE action on harvest  
- Clears at least one weed when present  
- No land purchase until turn 8+ and only when conditions met  
- Single file `main.py` runs under 1 s per action (stdlib only)

### 6. Non-goals
- No opponent modelling or shop denial  
- No RL or learned parameters  
- No multi-file structure  
- No complex crop rotation or animal selling logic  
- No attempt to maximise coins (focus is W/L/T via consistent scoring)
