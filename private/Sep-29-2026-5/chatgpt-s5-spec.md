**Kaggriculture Submission Spec – 2026-09-29-s5**

**Folder:** `2026-09-29-s5/`  
**Previous:** 56689358 (2026-09-29-s4)  
**Target:** one stdlib `main.py` only

### 1. Ladder facts
- Record: 0W-0T-0L  
- Starting rating: 600 (new bot)  
- No episodes completed. No bank, inventory, or opponent data available.  
- All prior assumptions about opponent behavior are discarded.

### 2. Root causes to fix (from s4 patterns)
- Repeated DROP/PICKUP cycles that empty the shed without scoring.  
- Over-purchase of wheat seed before any land is cleared.  
- Herd size left at 0 while land is idle.  
- Weeds left on tiles for multiple turns.  
- Harvest goods left in inventory instead of being placed for scoring.  
- No early land acquisition timing.

### 3. Exact s5 policy table (vs s4)

| Situation                          | s4 behavior (to replace)          | s5 rule (implement exactly) |
|------------------------------------|-----------------------------------|-----------------------------|
| Turn 1                             | Buy wheat                         | Buy 2 land tiles            |
| Any tile has weed                  | Ignore or buy more seed           | Hoe the weed first          |
| Empty land + money ≥ 10            | Do nothing                        | Buy 1 cow if herd < 3       |
| Empty land + money < 10            | Buy wheat                         | Buy wheat seed only if ≥1 empty hoed tile |
| Harvest ready                      | Leave in inventory or DROP        | PLACE the harvested item (never DROP) |
| Shed has goods at end of turn      | Keep or DROP                      | PLACE all goods (one action per turn) |
| No action possible                 | Buy wheat                         | Pass (do nothing)           |
| Animals                            | Attempt sell                      | Never touch (cannot sell)   |

Action order per turn (hard-coded):
1. Hoe any visible weed.  
2. If harvest ready → PLACE that item.  
3. If empty hoed land and money ≥10 and herd <3 → buy cow.  
4. Else if empty hoed land and money ≥ seed cost → buy wheat seed.  
5. Else pass.

### 4. Task priority (implement in this order)
1. Basic loop: observe → hoe → PLACE harvest → buy land/cow/seed.  
2. Never emit the DROP action.  
3. Enforce herd cap of 3.  
4. Only buy wheat when a hoed tile exists.  
5. Single-file `main.py` with no external files or imports beyond stdlib.

### 5. Local acceptance gates (run before any upload)
- `python main.py` must produce a valid action string every turn for 50 simulated turns with no exceptions.  
- No `DROP` string appears in any output.  
- At least one PLACE action is generated when inventory > 0.  
- Herd size never exceeds 3.  
- Code runs under 1 s per turn on a fresh Python process.

### 6. Non-goals
- No opponent modeling or shop denial.  
- No RL or learned parameters.  
- No multi-file structure.  
- No complex inventory tracking beyond “has harvest ready” and “herd count”.  
- No late-game optimization.

Implement the policy table above as a simple if-elif chain inside the single `main.py` decision function.