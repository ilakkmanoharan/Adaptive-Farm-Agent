**Kaggriculture Submission Spec – 2026-09-22-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no data).
- No opponents observed. No W/L/T rating movement. Previous submission (56460842) also has zero recorded games.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (entire inventory) and repeated PICKUP. s2 forbids DROP entirely; only PLACE n for harvested goods.
- **Herd size**: No animal purchase or management logic; animals cannot be sold so over-purchase is permanent dead weight.
- **Wheat buys**: No price or timing check; bought wheat regardless of market.
- **Weeds**: No weeding action scheduled; weeds reduce yield.
- **Land timing**: Actions taken after market resolution or on already-planted tiles; player actions must resolve before market.

### 3. Exact s2 policy table vs previous bot

| Situation                          | s1 (previous) behaviour                  | s2 behaviour                                      | Reason |
|------------------------------------|------------------------------------------|---------------------------------------------------|--------|
| Empty tile, day < 20               | Buy wheat if coins > 10                  | Buy wheat only if coins ≥ 25 and no weeds        | Avoid early over-spend |
| Tile has weeds                     | Ignore                                   | WEED then plant                                  | Prevent yield loss |
| Harvest ready                      | DROP                                     | PLACE 1 (repeat for stack)                       | Never dump entire inventory |
| Animal slot empty, coins ≥ 80      | Buy 1 animal                             | Buy 0 animals (permanent)                        | Animals unsellable |
| Inventory > 0 at end of turn       | PICKUP / DROP cycle                      | Only PLACE harvested goods; no PICKUP            | Eliminate thrash |
| Market open                        | Act after market                         | All actions before market tick                   | Correct resolution order |
| No valid action                    | Idle                                     | Idle (1 action max per turn)                     | actTimeout = 1s |

### 4. Task priority
1. Remove all DROP calls; replace with PLACE n for harvested items only.
2. Add weed check before any plant action.
3. Add coin threshold (≥25) and day < 20 guard on wheat purchases.
4. Disable all animal purchase logic.
5. Enforce single action per turn with explicit pre-market ordering.
6. Add minimal end-of-turn PLACE for any harvested goods still in inventory.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs with no syntax/runtime errors using only stdlib.
- No DROP appears in source.
- All plant actions are preceded by weed check.
- Wheat purchase guarded by `coins >= 25 and day < 20`.
- No animal purchase code present.
- Single action emitted per turn.
- Code fits in one `main.py` file.

### 6. Non-goals
- No opponent modelling or shop denial.
- No reinforcement learning or learned parameters.
- No multi-file structure.
- No new environment APIs or external data.