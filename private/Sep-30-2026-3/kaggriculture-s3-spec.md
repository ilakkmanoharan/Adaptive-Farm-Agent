# Kaggriculture Submission 3 Specification
Date: 2026-09-30 · Slot: s3 · Folder: `2026-09-30-s3/`

Previous Kaggle id: 56712166
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-30-s3**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission, rating starts at 600)
- Mean bank: None (no episodes played)
- No opponent data yet. Previous submission 56712166 (folder 2026-09-30-s2) has zero recorded matches.

### 2. Root causes we must fix
- No prior policy exists; s2 was placeholder. New bot must avoid:
  - Any use of DROP (dumps entire inventory, zero scoring).
  - Over-purchasing wheat seed when land is not yet cleared.
  - Buying animals before basic crop cycle is stable.
  - Ignoring weeds on owned land.
  - Late land purchases that leave no time for planting/harvest before market.
- Core constraints to respect: player actions resolve before market, unsold inventory scores 0, animals unsellable, PLACE item n only for harvested goods.

### 3. Exact s3 policy table vs previous bot

| Situation                          | s2 (previous)          | s3 policy (new)                                      | Reason |
|------------------------------------|------------------------|------------------------------------------------------|--------|
| Turn 1–3                           | Random / idle          | Buy 2 land if bank ≥ 400, else buy 1 land           | Secure planting area early |
| Land owned but empty               | —                      | Buy wheat seed only (max 3 per empty plot)          | Fastest crop cycle |
| Weeds present on owned land        | —                      | Weed before any buy or plant                        | Prevents blocked growth |
| After first harvest                | —                      | PLACE harvested wheat (never DROP)                  | Score points immediately |
| Bank ≥ 1200 and ≥ 4 land           | —                      | Buy 1 chicken (only once)                           | Start minimal herd after crop base |
| Bank < 300 or no empty land        | —                      | Skip all purchases, wait for harvest                | Avoid negative cash flow |
| Any other state                    | —                      | Weed → PLACE → buy seed/land only if safe           | Strict priority order |

Policy is deterministic, single-pass, no state machine beyond the above checks.

### 4. Task priority
1. Implement core loop in `main.py` that reads observation and emits exactly one action per turn using the s3 policy table.
2. Hard-code the decision order: weed check → PLACE harvested goods → land/seed buys → chicken buy (once).
3. Add bank and land count guards to prevent over-spend.
4. Ensure no DROP is ever emitted.
5. Add minimal logging of bank, land, inventory counts for local debugging.

### 5. Local acceptance gates before Kaggle upload
- Script runs 100 turns without crashing or emitting DROP.
- Never buys chicken before owning ≥ 4 land.
- Never buys seed when no empty land exists.
- Always uses PLACE for any harvested item.
- Single file `2026-09-30-s3/main.py` uses only stdlib.
- Executes in < 0.8 s per turn on local test harness.

### 6. Non-goals
- No opponent modeling or shop denial.
- No reinforcement learning or parameter search.
- No multi-file structure or external data.
- No animal selling logic (impossible).
- No complex inventory management beyond PLACE harvested goods.
