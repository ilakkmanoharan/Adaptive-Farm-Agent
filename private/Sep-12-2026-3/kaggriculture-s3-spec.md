# Kaggriculture Submission 3 Specification
Date: 2026-09-12 · Slot: s3 · Folder: `2026-09-12-s3/`

Sources: s2 episodes for `56197392`, v1 episodes, official DROP semantics, ChatGPT (`gpt-4o`) review.

## 1. Ladder facts

| Bot | Screenshot / later API | Meaning |
|---|---|---|
| v1 | 488 → ~438 | Started at 600, lost to $50k–$160k farms |
| s2 | 259 → ~354 | Started at 600; banks **$28k–$40k**; 2W–5L |

s2 is stronger than v1 on coins and beats weak bots ($6–8k). It still loses to $32k–$120k farms. Rating dropped because losses vs that field move skill down. 600 was never farm profit.

s2 public banks:

- Win Xiaozhen $38k vs $6k; win Sreesanth $40k vs $8k
- Loss Neo_0x3f **$34k vs $120k** (12 sheep, 42 strawberry, 303 market wheat)
- Loss Shobha $35k vs $78k (6 cows, 418 market wheat)
- Loss kekuru $29k vs $56k (NW-only, 4 sheep + 2 cows, 717 market wheat)
- Loss Jiri $28k vs $32k (no animals; almost zero PASS)

## 2. Root causes in s2 (must fix)

1. **DROP dumps the entire inventory.** Official `DROP` puts wheat and carried animals back in the shed. Combined with a high-priority shed pickup task, this created **1200+ PICKUP** actions vs 40–156 for winners.
2. **Day 0 fills NW** with 17 wheat + 6 melon. One sheep fits; the herd cannot scale.
3. **Almost no `BUY_PRODUCT WHEAT`** (13–24 vs 300–700). Feed is the constraint, not land.
4. **Weeds 13–19** late: too many plants for the water schedule.
5. **Land bought at $150 cash** on day 7.

ChatGPT agrees: selective drop, reserve pastures, sheep-first, market wheat, plant cap, delay land.

## 3. s3 policy

Keep the v1/s2 crash wrapper and same-turn market delay.

| Lever | s2 | s3 |
|---|---|---|
| Drop | `DROP` whole bag | `PLACE item n` for harvest only; never drop wheat/animals |
| Pickup | default shed task | only if unfed+no carried wheat, or unplaced animal in shed; max 2 units |
| Sheep | 3 target, ~1 placed | **8–10**, buy from day 0 |
| Cows | 8 target, 1–3 placed | **4**, after 2 sheep are down |
| Wheat tiles | 17+ | **8–10** until herd ≥ 6 |
| Melon | 10 | **6–8** |
| Strawberry | seeds bought, few planted | plant after pastures exist; cap 20 |
| Market wheat | 13–24 | keep `shed+carried ≥ herd + 4` every turn |
| Land | day 7, cash $150 | day ≥ 10 and bank ≥ $5k |
| Plants | fill all empties | `≤ workers * 3`, water first |
| Pasture reserve | 2 tiles | **8 tiles** until 8 animals placed |

Day-0 spend cap: 2 sheep + 1 cow + 4 melon + 4 wheat + cheap hires. Leave ≥ $800.

## 4. Task priority

1. Survival water / escape-risk feed  
2. Place carried animal / build pasture on reserved tiles  
3. Feed remaining animals (carry wheat; do not drop it)  
4. Harvest / collect fert / care  
5. Plant melon → wheat-to-cap → strawberry  
6. Selective shed deposit of produce  
7. Dig weeds  
8. PASS only if no legal work

## 5. Acceptance before upload

- 0 crashes vs starter, s2, v1  
- Mean bank vs starter **> s2** (~$39k)  
- Win rate vs s2 ≥ 75% over 4 seeds × both seats  
- Diagnostic: ≥ 4 animals placed by day 3; weeds ≤ 5 at day 20; PICKUP unit-actions ≪ 400  
- First extra quadrant only after $5k  

## 6. Non-goals

Tape cloning, opponent shop denial, RL, geese except as a later experiment.

## 7. Shipped as `2026-09-12-s3/`

Implemented and submitted `2026-09-12-s3/main.py` (message: `s3 no-drop pasture-reserve sheep-first market-feed`).

Local gate (official env, 0 crashes):

- vs starter: 4–0, mean bank **~$50k** (s2 was ~$39k)
- vs s2: **8–0**, mean bank ~$43k
- vs v1: 4–0
- ~3 animals by day 3; weeds ~0 at day 20; PICKUP ~430 (s2 was 1200+)

Kaggle: submitting s3 makes the active pair **s2 + s3** (v1 drops off the latest-2 slots).
