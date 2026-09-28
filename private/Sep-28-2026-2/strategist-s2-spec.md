**Kaggriculture Submission Spec – 2026-09-28-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed).
- Mean bank: None (no data).
- No opponents observed. No W/L/T data, no bank values, no win conditions visible.
- Previous submission (56635004) produced zero rated games.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (dumps entire inventory). s2 must never call DROP; only use PLACE n for harvested goods.
- **Herd size**: No animal management visible; animals cannot be sold so any purchase locks capital permanently.
- **Wheat buys**: No evidence of timed wheat purchases before market resolution.
- **Weeds**: No weed-clearing logic observed.
- **Land timing**: Actions must resolve before market; previous bot likely acted too late or on wrong turns.
- **Inventory scoring**: Unsold goods score 0; must sell every harvest before end of episode.

### 3. Exact s2 policy table vs previous bot

| Situation                  | s1 (previous) behaviour          | s2 behaviour (new)                                      |
|----------------------------|----------------------------------|---------------------------------------------------------|
| Harvest ready              | DROP or nothing                  | PLACE item n (only harvested goods)                     |
| Wheat available & money ≥ price | Buy random amount               | Buy exactly 3 wheat if money ≥ 120 and no wheat owned   |
| Weeds present              | Ignore                           | Clear 1 weed per turn if present                        |
| Empty land & money ≥ 80    | Do nothing                       | Buy 1 land tile if current land < 4                     |
| Animals                    | Never buy                        | Never buy (policy locked)                               |
| Sell window                | Random / late                    | Sell all harvest goods immediately when price ≥ 35      |
| Any other action           | Unspecified                      | Idle (pass)                                             |

All actions chosen in strict priority order above. No DROP ever. No animal purchases.

### 4. Task priority
1. Implement core loop that reads state and emits exactly one action per turn using the policy table.
2. Add PLACE instead of DROP for all harvest handling.
3. Add wheat buy rule (3 units) and land buy rule (max 4 tiles).
4. Add weed clear and sell rules.
5. Ensure single-file `main.py` using only stdlib, <1 s per action.
6. Add minimal state tracking for owned wheat/land/harvest counts.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs without import or runtime errors for 200 turns.
- Never emits the token “DROP” in any output.
- Never buys animals.
- Produces at least one PLACE action when harvest exists.
- Wheat buy only triggers when money ≥ 120 and wheat count == 0.
- Total lines ≤ 250, pure stdlib.
- Runs in <0.8 s per turn on local machine.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned parameters.
- No multi-file structure.
- No complex inventory optimisation beyond the policy table.
- No handling of edge cases outside the listed rules.