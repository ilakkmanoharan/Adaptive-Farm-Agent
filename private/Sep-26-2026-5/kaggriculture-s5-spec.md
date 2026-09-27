# Kaggriculture Submission 5 Specification
Date: 2026-09-26 · Slot: s5 · Folder: `2026-09-26-s5/`

Previous Kaggle id: 56588691
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-26-s5**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (new slot, no episodes yet).
- Previous submission (56588691 / 2026-09-26-s4) has zero live ladder data.
- No opponent replays available. All analysis is based on known failure modes from s4 code and the listed root causes.

### 2. Root causes we must fix
- **DROP/PICKUP thrash**: s4 used DROP on harvest turns, dumping entire inventory (including unsold goods and tools). This loses all scoring potential.
- **Herd size**: No cap or sell logic for animals; inventory bloats with unsellable animals.
- **Wheat buys**: Over-purchased wheat seed without checking land availability or existing inventory.
- **Weeds**: No weeding action or priority; weeds block planting and reduce yield.
- **Land timing**: Planting and harvesting not sequenced with market resolution (player actions resolve first). Late land expansion or idle turns.

### 3. Exact s5 policy table vs previous bot

| Situation                          | s4 behavior (previous)          | s5 policy (new)                                      | Notes |
|------------------------------------|---------------------------------|------------------------------------------------------|-------|
| Harvest goods in inventory         | DROP                            | PLACE item n (only harvest goods)                    | Never DROP |
| Animal in inventory                | Keep or DROP                    | Never sell/place animals; ignore for scoring         | Animals unsellable |
| Wheat seed > 0 and empty plots     | Buy more wheat                  | Skip buy if seed ≥ 3 or no empty plots               | Hard cap |
| Weeds present on any plot          | Ignore                          | Prioritize WEED on lowest-index weeded plot          | Before plant |
| Ready-to-harvest crop              | Harvest then DROP               | HARVEST then PLACE n                                 | Same turn ok |
| No action possible this turn       | Idle                            | BUY only if wheat seed == 0 and money ≥ 10 and empty plots exist | Conservative |
| Land expansion opportunity         | Buy land late                   | Buy land only if money ≥ 50 and current plots < 6    | One land max per turn |
| Multiple harvest goods             | PLACE 1                         | PLACE all harvest goods in one pass (loop)           | Max score |

Policy is deterministic, single-pass, no state beyond current observation.

### 4. Task priority (implement order in main.py)
1. Replace all DROP with PLACE logic for harvest items only.
2. Add weed scan + WEED action before any plant/buy.
3. Add wheat seed cap (≥3) and empty-plot check before BUY.
4. Add land buy guard (money ≥ 50 and plots < 6).
5. Add simple inventory loop that only PLACEs harvest goods (skip animals).
6. Add no-op guard when no legal action matches policy.

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs to completion with actTimeout ≤ 1s on 100 random seeds.
- No DROP calls appear in any output trace.
- At least one PLACE action executed on every harvest turn in test traces.
- Wheat seed never exceeds 3 in any simulated episode.
- Weeds are cleared within 1 turn of appearing in test maps.
- Code is pure stdlib (no external imports, no files written).

### 6. Non-goals
- No opponent modeling or shop denial.
- No RL or learned policy.
- No multi-turn planning or search.
- No animal selling or herd management beyond ignoring them.
- No new data structures or classes beyond simple dict/list.

**Implementation constraint**: Entire agent must fit in one `main.py` using only Python standard library. Observation and action format must match the existing Kaggriculture environment interface exactly.
