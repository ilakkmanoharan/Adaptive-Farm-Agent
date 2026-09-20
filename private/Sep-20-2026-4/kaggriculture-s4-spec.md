# Kaggriculture Submission 4 Specification
Date: 2026-09-20 · Slot: s4 · Folder: `2026-09-20-s4/`

Previous Kaggle id: 56400377
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s4 Submission Spec**  
**Folder:** `2026-09-20-s4/`  
**Target:** one stdlib `main.py` (no external deps)  
**Previous:** 56400377 (2026-09-20-s3)

### 1. Ladder facts
- Record: 0W-0T-0L (no episodes completed yet).
- Starting rating: 600.
- Mean bank: None (no data).
- No opponent replays available; s3 bot never reached a scored game.

### 2. Root causes to fix (from s3 code review)
- **DROP/PICKUP thrash**: s3 used `DROP` on harvest turns, dumping entire inventory and losing all goods.
- **Herd size**: Never bought animals; zero milk/wool production.
- **Wheat buys**: Bought wheat every turn regardless of land or season.
- **Weeds**: No weeding action; plots became unproductive.
- **Land timing**: Bought extra land before any crops were planted or harvested.
- Result: zero sellable inventory at episode end.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behaviour (old)              | s4 behaviour (new)                          | Action sequence |
|------------------------------------|---------------------------------|---------------------------------------------|-----------------|
| Turn 1                             | Buy wheat                       | Buy 1 cow                                   | `BUY cow 1` |
| Any turn, weeds present            | Ignore                          | Weed all plots                              | `WEED` (repeat until clear) |
| Harvest ready                      | `DROP`                          | `PLACE item n` for each harvest good        | `PLACE` only |
| Bank ≥ 80 and no wheat planted     | Buy wheat                       | Buy wheat only if ≥1 empty tilled plot      | `BUY wheat 1` max |
| Bank ≥ 120 and herd < 3            | Never buy animals               | Buy 1 more cow                              | `BUY cow 1` |
| Bank ≥ 200 and empty plots ≥ 2     | Buy land                        | Never buy land in s4                        | — |
| Inventory has goods                | —                               | Sell everything possible                    | `SELL item n` |
| No action possible                 | —                               | `PASS`                                      | `PASS` |

### 4. Task priority (implement in this order)
1. Replace every `DROP` with `PLACE item n` (or `PASS`).
2. Add single cow purchase on turn 1.
3. Add weed loop before any plant/buy.
4. Gate wheat purchase on empty tilled plots.
5. Add minimal herd growth (max 3 cows).
6. Remove all land purchases.
7. Add sell loop for any goods in inventory.
8. Final `PASS` safety.

### 5. Local acceptance gates (run before upload)
- `python main.py` must finish 100 random episodes with zero `DROP` calls.
- At least one cow purchased in every episode.
- Final inventory value > 0 in ≥70% of episodes.
- No land purchases in any run.
- Runtime per episode < 0.8 s (actTimeout = 1 s).

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned parameters.
- No multi-animal types or advanced crop rotation.
- No land expansion.

Implement the policy table above directly in `main.py` as a simple if/elif ladder. Keep total code under 200 lines.
