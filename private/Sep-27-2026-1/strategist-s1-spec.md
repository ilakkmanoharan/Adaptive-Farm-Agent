**Kaggriculture Submission Spec – 2026-09-27-s1**

**1. Ladder facts from these games**  
- Record: 0W-0T-0L (no episodes completed).  
- Mean bank: None (no data).  
- No opponents observed; no W/L/T deltas recorded.  
- Previous submission (56598104) also has zero ladder footprint.

**2. Root causes we must fix**  
- PICKUP/PLACE thrash on harvest goods instead of direct PLACE n.  
- Herd size left unmanaged (animals accumulate without sale path).  
- Wheat bought every turn regardless of land or storage state.  
- Weeds ignored until they block planting.  
- Land timing: actions taken before checking available plots, causing idle turns.  
- No early-game focus on scoring sellable goods before market phase.

**3. Exact s1 policy table vs previous bot**

| State check (in order)                  | s1 action                          | Previous bot behaviour          |
|-----------------------------------------|------------------------------------|---------------------------------|
| Weeds present on any plot               | PLOW that plot                     | Continue previous action        |
| No wheat seed and plots empty           | BUY wheat 1                        | BUY wheat every turn            |
| Harvest goods in inventory              | PLACE item n (first harvest good)  | PICKUP then later PLACE         |
| Empty plots and wheat seed in inv       | PLANT wheat                        | PLANT only after extra checks   |
| Animals >= 3 and no sale path           | HIRE worker (if affordable)        | Ignore herd size                |
| Money >= 8 and empty plots >= 2         | BUY wheat 2                        | BUY wheat 1 unconditionally     |
| Nothing above triggered                 | PASS                               | Random or repeat last action    |

All actions use only documented env calls. Never emit DROP.

**4. Task priority**  
1. Implement state checks + policy table above in one main.py.  
2. Add minimal inventory tracking (count harvest goods, wheat seeds, animals).  
3. Ensure every turn ends with at most one action that can score (PLACE or PLANT).  
4. Local test harness that runs 50 deterministic turns and prints final sellable inventory.

**5. Local acceptance gates before Kaggle upload**  
- 50-turn run produces ≥ 4 placed harvest goods and 0 DROP calls.  
- No PICKUP action ever emitted.  
- Herd size never exceeds 4 without a worker hire attempt when money ≥ 5.  
- Weeds cleared within 2 turns of appearing.  
- Total runtime per turn < 200 ms (stdlib only).

**6. Non-goals**  
- Opponent shop interference.  
- Any form of RL or learned policy.  
- Multi-file structure or external libs.  
- Long-term land expansion or animal breeding logic.