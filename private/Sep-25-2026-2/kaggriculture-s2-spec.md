# Kaggriculture Submission 2 Specification
Date: 2026-09-25 · Slot: s2 · Folder: `2026-09-25-s2/`

Previous Kaggle id: 56544471
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-25-s2**

### 1. Ladder facts
- Record: 0W-0T-0L (no rated games completed yet).
- Bank: None (no meaningful coin data).
- Previous submission (56544471) produced 0 wins; new bot starts at 600 rating.
- No opponent-specific loss data available. All future matches will be against fresh or low-activity bots.

### 2. Root causes to fix (from s1 behavior)
- Repeated `DROP` calls that emptied the entire shed instead of selective `PLACE`.
- Over-purchasing wheat seed without matching land or harvest timing.
- Herd size left unmanaged (animals accumulate but never produce sellable goods).
- Weeds left on tiles for multiple turns, blocking planting cycles.
- Land purchases timed after the market phase, so newly bought land could not be used the same turn.
- No consistent sell policy for harvest goods before end of episode.

### 3. Exact s2 policy table (vs s1)

| State condition                          | s1 action (to replace)      | s2 action                                      | Notes |
|------------------------------------------|-----------------------------|------------------------------------------------|-------|
| Weeds present on any owned tile          | Plant / Buy seed            | `WEED` all weeded tiles first                  | Priority 1 |
| Empty owned land + wheat in inventory    | Buy more wheat              | `PLACE wheat 1` on each empty tile             | Never buy wheat if inventory > 0 |
| Harvest goods in inventory               | `DROP` or hold              | `PLACE item n` (n = count) on empty shed slots | Never use DROP |
| Animals owned ≥ 4 and no wheat planted   | Buy more animals            | Stop animal purchases; focus wheat             | Hard cap at 4 |
| Land available and wheat inventory = 0   | Buy land                    | Buy land only if current wheat seed ≥ 8        | Prevents idle land |
| End of turn, harvest goods still held    | Hold                        | Sell all harvest goods                         | Sell before market resolves |
| No action satisfies above                | Random / idle               | `PASS`                                         | Default safe action |

### 4. Task priority (implement in order)
1. Add weed detection + `WEED` action at start of turn.
2. Replace every `DROP` with conditional `PLACE item n`.
3. Add wheat inventory guard: never buy wheat if current wheat > 0.
4. Add animal purchase cap (max 4 total).
5. Add land purchase guard (only when wheat seed ≥ 8).
6. Add end-of-turn sell of all harvest goods.
7. Default to `PASS` when no other rule fires.

### 5. Local acceptance gates (before any Kaggle upload)
- Run 50 episodes locally with random opponents.
- Zero `DROP` calls observed in logs.
- Herd size never exceeds 4.
- Weeds cleared within 1 turn of appearing.
- At least 60 % of episodes end with positive sell volume.
- No wheat purchases when wheat inventory > 0.
- Total runtime per episode < 0.8 s (actTimeout = 1 s).

### 6. Non-goals
- No opponent shop interference.
- No reinforcement learning or learned parameters.
- No multi-file structure (single `main.py` only).
- No complex state tracking beyond the policy table above.

Implement the policy table as a simple if-elif chain in `main.py`. All logic uses only standard library and the documented environment actions.
