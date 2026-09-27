# Kaggriculture Submission 4 Specification
Date: 2026-09-27 · Slot: s4 · Folder: `2026-09-27-s4/`

Previous Kaggle id: 56617893
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s4 Submission Spec**  
`2026-09-27-s4/` (one `main.py`, stdlib only)

### 1. Ladder facts
- Record: 0W-0T-0L (new slot, rating starts at 600).  
- No prior episodes; bank = None.  
- Previous bot (s3) therefore has zero ladder data. All improvements are pre-emptive.

### 2. Root causes to fix (from s3 code review)
- **DROP/PICKUP thrash**: s3 used `DROP` on harvest turns, dumping entire shed. s4 must never emit `DROP`; only `PLACE item n` for goods that must be sold.  
- **Herd size**: s3 over-bought animals early; animals cannot be sold and block shed space. s4 caps animals at 0 until land ≥ 6 and wheat surplus ≥ 8.  
- **Wheat buys**: s3 bought wheat every turn regardless of price or inventory. s4 buys wheat only when current wheat < 3 and price ≤ 4.  
- **Weeds**: s3 ignored weed growth; land became unusable. s4 inserts `WEED` action when any plot has weed ≥ 2.  
- **Land timing**: s3 bought land too late. s4 buys land on turn 3 if cash ≥ 12 and current land < 4.

### 3. Exact s4 policy table (vs s3)

| Situation                          | s3 behaviour                  | s4 behaviour                                      |
|------------------------------------|-------------------------------|---------------------------------------------------|
| Turn 1–2                           | Random buy                    | `BUY LAND` if cash ≥ 12                           |
| Wheat < 3 and price ≤ 4            | Always buy                    | `BUY WHEAT 2`                                     |
| Any plot weed ≥ 2                  | Ignore                        | `WEED` that plot                                  |
| Harvest ready                      | `DROP` then sell              | `PLACE item n` (n = count) then sell              |
| Cash ≥ 20 and land < 6             | Skip                          | `BUY LAND`                                        |
| Animals > 0 or cash < 15           | Bought animals                | Never buy animals                                 |
| No action possible                 | Idle                          | `PASS`                                            |

All other actions unchanged from s3 skeleton.

### 4. Task priority (single main.py)
1. Implement state parser (land, inventory, cash, weeds).  
2. Add the six rules above as an if-elif chain (highest priority first).  
3. Replace every `DROP` with `PLACE` logic.  
4. Add simple 1-second timeout guard (already in env).  
5. Remove all animal purchase paths.

### 5. Local acceptance gates (before Kaggle upload)
- Runs 50 deterministic episodes with no `DROP` emitted.  
- Average land ≥ 5 by turn 20.  
- Wheat inventory never exceeds 12.  
- Zero animal purchases.  
- No runtime exceptions under 1 s actTimeout.

### 6. Non-goals
- No opponent modelling or shop denial.  
- No RL or learned parameters.  
- No multi-file structure.  
- No weed prediction beyond current turn.
