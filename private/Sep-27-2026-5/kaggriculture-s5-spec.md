# Kaggriculture Submission 5 Specification
Date: 2026-09-27 · Slot: s5 · Folder: `2026-09-27-s5/`

Previous Kaggle id: 56621221
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture s5 Submission Spec**

**1. Ladder facts from these games**  
- Record: 0W-0T-0L (no rated games completed in slot 5).  
- Starting rating: 600 (new bot reset).  
- No bank or opponent data available. Previous s4 bot (56621221) also recorded 0W-0T-0L before reset. No wins logged; rating remains at entry level.

**2. Root causes we must fix**  
- Repeated PLACE/DROP thrash on harvest goods instead of direct PLACE n.  
- Herd size too small (≤2 animals) → insufficient production volume.  
- Over-purchasing wheat early, leaving no cash for land or animals.  
- No weed removal logic → fields blocked after first cycle.  
- Land purchases timed after market close instead of before action phase.  
- Inventory left unsold at end of episode (zero scoring contribution).

**3. Exact s5 policy table vs previous bot**

| Situation                        | s4 behaviour (previous)          | s5 behaviour                                      |
|----------------------------------|----------------------------------|---------------------------------------------------|
| Harvest goods in inventory       | DROP then later PLACE            | PLACE n immediately (never DROP)                  |
| Cash ≥ 120 and animals < 4       | Buy wheat or do nothing          | Buy 1 animal if animals < 4                       |
| Cash ≥ 80 and empty field        | Buy wheat                        | Buy land if any field empty                       |
| Weeds present on any field       | Ignore                           | Remove weed on first available action             |
| Cash < 50 and animals ≥ 3        | Buy wheat                        | Sell any harvest goods (PLACE n)                  |
| End of turn with goods           | Leave in inventory               | PLACE n to shed before timeout                    |
| No action possible               | Idle                             | Idle (respect 1 s actTimeout)                     |

**4. Task priority**  
1. Replace all DROP with PLACE n for harvest goods.  
2. Add simple animal count check: buy animal when cash ≥ 120 and count < 4.  
3. Add weed removal action before any purchase.  
4. Add land purchase when cash ≥ 80 and empty field exists.  
5. Add end-of-turn sell logic (PLACE n) when cash < 50.  
6. Remove all wheat purchase logic.

**5. Local acceptance gates before Kaggle upload**  
- main.py runs to completion in < 1 s per turn on stdlib only.  
- No DROP calls remain in source.  
- At least one animal purchased by turn 10 in a 20-turn local loop.  
- At least one land tile purchased when starting with empty fields.  
- All harvest goods placed via PLACE n (zero unsold at end of simulated episode).  
- File placed in `2026-09-27-s5/main.py` and runs with `python main.py`.

**6. Non-goals**  
- No RL or learning.  
- No opponent shop interaction or denial.  
- No multi-file structure.  
- No complex state tracking beyond cash, animal count, field status, and inventory items.  
- No wheat purchases.
