**Kaggriculture s4 Submission Spec**  
**Folder:** `2026-09-19-s4/`  
**Target:** single `main.py` (stdlib only)  
**Previous:** 56366541 (2026-09-19-s3)

### 1. Ladder facts
- Record: 0W-0T-0L (new or reset bot, 600 starting rating)
- No completed episodes → no bank values, no opponent names, no observed loss patterns
- All prior knowledge is from s3 code inspection only

### 2. Root causes to fix (from s3 code review)
- **DROP/PICKUP thrash**: s3 used `DROP` on harvest turns; entire inventory lost to shed instead of `PLACE item n`.
- **Herd size**: No cap; bought animals every turn money allowed, leading to feed starvation and zero sales (animals unsellable).
- **Wheat buys**: Bought wheat seed every turn regardless of existing inventory or land availability.
- **Weeds**: No `WEED` action; plots left blocked.
- **Land timing**: Bought land before any seed/plant action; wasted turns with empty plots.
- **Action order**: Market actions after player actions not respected in sequencing; sell attempts on animals.

### 3. Exact s4 policy table (vs s3)

| Situation                          | s3 behaviour                  | s4 behaviour                                      | Priority |
|------------------------------------|-------------------------------|---------------------------------------------------|----------|
| Harvest goods in inventory         | DROP                          | `PLACE item n` (n = count)                        | 1        |
| Weeds present on any plot          | None                          | `WEED` all visible weeds                          | 1        |
| Empty plots + wheat seed ≥ 1       | Buy wheat seed                | Plant wheat if seed ≥ 1 else buy max 2            | 2        |
| Money ≥ 50 and no animals          | Buy animal every turn         | Buy at most 1 animal only if feed ≥ 3             | 2        |
| Animals ≥ 3                        | Continue buying               | Stop buying animals                               | 2        |
| Harvest goods ready to sell        | Sell after market             | Sell immediately (player action before market)    | 1        |
| Land purchase                      | Early land buy                | Land buy only after 2+ planted plots              | 3        |
| No action possible                 | Random                        | `PASS`                                            | 4        |

### 4. Task priority (implement order)
1. Replace all `DROP` with `PLACE item n`; add weed scan + `WEED`.
2. Add simple inventory counters (wheat seed, harvest goods, feed, animals).
3. Enforce animal cap (max 3) and feed check before buy.
4. Wheat buy/plant logic: buy only when seed == 0 and plots available.
5. Land buy guard (≥2 planted plots).
6. Sell logic for harvest goods only.
7. Final `PASS` fallback + 1-second timeout safety.

### 5. Local acceptance gates (before upload)
- Run 20 episodes locally with random opponents.
- Zero `DROP` calls in logs.
- Animal count never exceeds 3.
- At least one successful `PLACE` + sell cycle per episode.
- No wheat seed purchases when inventory > 0.
- Final rating ≥ 580 after 20 games (no rating regression).

### 6. Non-goals
- No opponent shop interaction or denial
- No RL / learning
- No multi-file structure
- No complex pathing or timing beyond the table above
- No animal selling attempts

Implement the above policy table directly in one `main.py` using only the documented actions and stdlib.