# Kaggriculture Submission 4 Specification
Date: 2026-09-25 · Slot: s4 · Folder: `2026-09-25-s4/`

Previous Kaggle id: 56557667
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-25-s4**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission on ladder).
- Mean bank: None (no completed episodes).
- No opponent data yet. All future matches will be evaluated on W/L/T only; unsold inventory scores 0.

### 2. Root causes we must fix
- Previous bot (s3) performed excessive PICKUP/DROP cycles on harvest goods instead of direct PLACE.
- Herd size never exceeded 2 animals because no consistent wheat purchase + feed loop.
- Wheat buys were sporadic and occurred after land was already planted, causing starvation.
- Weeds accumulated on empty plots because no early weeding priority.
- Land timing was reactive (bought land only when inventory was full) instead of proactive expansion on turns 3–6.
- No early-game wheat stockpile, leading to zero animal growth in first 20 turns.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behaviour (previous)          | s4 behaviour (new)                                      | Reason |
|------------------------------------|----------------------------------|---------------------------------------------------------|--------|
| Turn 1–2                           | Buy random seed                  | Buy 3 wheat + 1 cow if money ≥ 120                      | Fast herd start |
| Empty plot + weeds present         | Plant seed                       | Weed first, then plant only if no weeds                 | Prevent weed lock |
| Harvest goods in inventory         | PICKUP then later DROP           | PLACE item n directly on empty plot                     | Eliminate thrash |
| Wheat in inventory + animal hungry | Do nothing                       | Feed wheat to animal (highest priority)                 | Herd growth |
| Money ≥ 80 and < 3 animals         | Buy land                         | Buy wheat + 1 animal instead                            | Prioritise herd over land |
| Money ≥ 200 and ≥ 3 animals        | Buy land                         | Buy land (max 1 per turn)                               | Controlled expansion |
| No action possible                 | Idle                             | Weed any visible weed, else buy 1 wheat                 | Never idle |
| End of turn with goods             | Keep in inventory                | PLACE all harvest goods before market phase             | Score goods |

### 4. Task priority (implementation order)
1. Replace all DROP usage with direct PLACE item n.
2. Add early wheat purchase + feed logic (turns 1–8).
3. Add weed-first rule on any plot that has weeds.
4. Add simple herd-size check (stop buying animals at 4).
5. Add land purchase rule only when herd ≥ 3 and money ≥ 200.
6. Ensure single main.py runs under 1 s per action.

### 5. Local acceptance gates before Kaggle upload
- main.py must run 50 simulated episodes with zero DROP calls.
- Herd size must reach ≥ 3 animals in ≥ 70 % of episodes by turn 30.
- Average weeds per plot at end of episode ≤ 0.5.
- No action timeout (> 900 ms) in any turn.
- Code must be pure stdlib (no external imports).

### 6. Non-goals
- No opponent modelling or shop denial.
- No reinforcement learning or parameter search.
- No complex state tracking beyond current turn, money, inventory, and visible plots/animals.
- No multi-file structure — everything in one main.py.
