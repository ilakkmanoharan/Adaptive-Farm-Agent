**Kaggriculture Submission Spec – 2026-09-24-s4**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (no episodes completed since last upload).
- Mean bank: None (no scored games).
- No opponents observed. Previous bot (56529559) has zero live ladder data.
- Skill rating still at default 600. No wins/losses recorded.

### 2. Root causes we must fix
- Previous bot likely suffered from **DROP/PICKUP thrash** (entire inventory dumped instead of selective PLACE).
- Over-purchasing wheat seeds without matching land or time.
- No weed control (weeds block planting/harvest).
- Herd size never scaled (animals cannot be sold, so only buy what can be fed and harvested before timeout).
- Land timing: actions taken too late in the day, missing market resolution.
- Unsold inventory at end of episode scores zero.

### 3. Exact s4 policy table vs previous bot

| Situation                          | s3 behaviour (previous)          | s4 behaviour (new)                                      | Reason |
|------------------------------------|----------------------------------|---------------------------------------------------------|--------|
| Empty hand, weeds present          | Ignore or buy more seeds         | PICKUP weed (nearest)                                   | Clear space first |
| Empty hand, ripe crop              | —                                | PICKUP crop                                             | Harvest before market |
| Holding crop                       | Possibly DROP                    | PLACE item n (only on empty shed tile)                  | Never use DROP |
| Holding seed, tilled empty land    | Plant immediately                | Plant only if day < 80% of episode length               | Avoid late planting |
| No tilled land, money ≥ 20         | Buy wheat seed                   | Buy wheat seed only if ≥1 empty tilled land exists      | Prevent seed hoarding |
| Money ≥ 80 and no animals          | —                                | Buy 1 chicken (if feed available)                       | Small safe herd start |
| Holding nothing, market open       | —                                | SELL any crop in shed (oldest first)                    | Convert to score |
| No action possible                 | Random buy                       | SKIP                                                    | Avoid thrash |
| End of day                         | —                                | Ensure all ripe crops are PICKed and PLACEed            | Inventory must be in shed |

### 4. Task priority (implement in order)
1. Core loop: observe state → apply policy table above.
2. Replace any DROP with PLACE item n logic.
3. Add simple weed detection and removal.
4. Add minimal herd purchase (max 1 animal) only when feed exists.
5. Add late-planting guard (day check).
6. Add sell logic for shed items at market.

### 5. Local acceptance gates before Kaggle upload
- Runs 100 episodes locally without crashing or using undefined APIs.
- Never calls DROP.
- Average score per episode ≥ 120 (unsold inventory excluded).
- No more than 3 consecutive SKIP actions in a row.
- Code fits in single `main.py` using only stdlib.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned policy.
- No multi-animal herds.
- No complex crop rotation or timing tables beyond the day guard.
- No external files or saved state.

**Implementation note**: All logic must live in one `main.py` inside `2026-09-24-s4/`. Use only the documented environment actions and observations.