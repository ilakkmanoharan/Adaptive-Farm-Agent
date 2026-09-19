# Kaggriculture Submission 2 Specification
Date: 2026-09-19 · Slot: s2 · Folder: `2026-09-19-s2/`

Previous Kaggle id: 56354677
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-19-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new bot, started at 600 rating).
- No completed episodes; no opponent data, no bank values observed.
- No wins/losses recorded yet. All future rating changes will come from s2 matches.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: Previous bot used DROP (which empties entire inventory). s2 must never call DROP; only use `PLACE item n` on harvest goods when shed space is needed.
- **Herd size**: No animal management policy; risk of over-purchasing animals that cannot be sold. s2 caps animals at 2 and only buys when wheat surplus exists.
- **Wheat buys**: No timing logic; bought wheat without checking land or season. s2 buys wheat only on turns 1–3 and only if ≥2 empty plots.
- **Weeds**: No weeding action in loop. s2 inserts `WEED` on any plot that shows weed status before harvest.
- **Land timing**: Actions taken after market resolution. s2 performs all land/plant actions first, then market-dependent buys.

### 3. Exact s2 policy table vs previous bot

| Situation                        | s1 (previous) behaviour          | s2 behaviour                                      |
|----------------------------------|----------------------------------|---------------------------------------------------|
| Turn 1–3, ≥2 empty plots         | Buy wheat randomly               | Buy wheat (max 2)                                 |
| Any plot shows weeds             | Ignore                           | WEED that plot                                    |
| Harvest ready + shed < 4 free    | DROP                             | PLACE harvest goods (n=1..3)                      |
| Animals < 2 and wheat ≥ 8        | Buy animal                       | Buy 1 animal (max 2 total)                        |
| No action possible               | Pass                             | Pass                                              |
| After any harvest                | Sell immediately                 | Sell only if market price ≥ base (no change)      |

All actions use only documented stdlib calls. Player actions always before market.

### 4. Task priority
1. Implement core loop with action ordering (land/weed/place before buys).
2. Add weed detection + WEED action.
3. Replace DROP with PLACE logic.
4. Add simple herd cap (≤2) and wheat buy guard.
5. Add minimal state tracking (plots, animals, shed free).
6. Local test harness + acceptance gates.

### 5. Local acceptance gates before Kaggle upload
- Runs 50 turns with zero `DROP` calls.
- Never exceeds 2 animals.
- Wheat purchases only occur on turns 1–3 when empty plots ≥2.
- At least one WEED action executed when weeds present.
- No runtime errors under 1s actTimeout.
- Single file `main.py` using only stdlib.

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policy.
- No multi-file structure.
- No complex inventory optimization beyond the table above.
