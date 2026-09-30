# Kaggriculture Submission 2 Specification
Date: 2026-09-30 · Slot: s2 · Folder: `2026-09-30-s2/`

Previous Kaggle id: 56701942
Sources: pulled live episodes + strategist (`grok`).

**Kaggriculture Submission Spec – 2026-09-30-s2**

### 1. Ladder facts from these games
- Record: 0W-0T-0L (first submission, no rated games completed).
- Starting rating: 600.
- Mean bank: None (no completed episodes).
- No opponent data available. All future matches will be against bots that have already played ≥1 game.

### 2. Root causes we must fix
- Previous bot (s1) used `DROP` on harvest turns, dumping entire inventory instead of `PLACE item n`.
- Over-purchased wheat seed (no weed control or land timing).
- Herd size never exceeded 2 animals; no consistent feeding loop.
- No `PICKUP` after `PLACE` on the same tile, causing repeated thrash on harvest goods.
- Land actions taken too early (before any crop ready) and too late (after weeds appeared).
- No sell policy; unsold inventory scored 0.

### 3. Exact s2 policy table vs previous bot

| Situation                          | s1 behaviour (previous)          | s2 behaviour (new)                                      | Priority |
|------------------------------------|----------------------------------|---------------------------------------------------------|----------|
| Harvest goods in inventory         | `DROP`                           | `PLACE item n` on empty shed tile                       | 1        |
| After `PLACE` on harvest tile      | Nothing                          | `PICKUP` on same tile next turn                         | 1        |
| Wheat seed available + empty plot  | Buy more wheat                   | Plant only if no weeds visible and land is tilled       | 2        |
| Animal count < 3                   | Ignore                           | Buy 1 animal only when bank ≥ 120 and feed available    | 2        |
| Weeds on any plot                  | Ignore                           | `WEED` highest-priority action before any plant         | 1        |
| Ready crop on land                 | Plant new crop                   | Harvest first, then decide                              | 1        |
| Bank ≥ 80 and nothing to do        | Buy random seed                  | Buy 1 wheat seed only if ≤2 wheat in inventory          | 3        |
| No action possible                 | Pass                             | Pass                                                    | —        |

### 4. Task priority
1. Replace every `DROP` with `PLACE item n` + follow-up `PICKUP`.
2. Add weed check before any planting action.
3. Add minimal herd-growth rule (max 3 animals).
4. Add simple sell logic for any harvest good that reaches inventory.
5. Add land-timing guard (only till/plant when no weeds and no ready crop).

### 5. Local acceptance gates before Kaggle upload
- `python main.py` runs to completion with actTimeout ≤ 1s on 3 consecutive random seeds.
- No `DROP` call appears in source.
- At least one `PLACE` + `PICKUP` pair executed in every simulated harvest.
- Herd size reaches exactly 3 animals by turn 40 in a 60-turn local run.
- No runtime exceptions on empty inventory or zero-bank states.

### 6. Non-goals
- No opponent modelling or shop denial.
- No RL or learned policy.
- No multi-file structure (single `main.py` only).
- No complex crop rotation or pricing models.
