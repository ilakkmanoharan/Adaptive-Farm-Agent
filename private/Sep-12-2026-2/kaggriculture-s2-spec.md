# Kaggriculture Submission 2 Specification
Date: 2026-09-12 · Slot: s2 · Folder: `2026-09-12-s2/`

Sources: Kaggle episodes for submission `56197136`, empty agent stdout logs, replay summaries, ChatGPT (`gpt-4o`) review of those logs, official environment mechanics.

## 1. What the first submission actually scored

The screenshot **600** is the default ladder initialization, not farm profit. After two public games the live score is **427.6**.

| Episode | Type | Us bank | Opponent | Result |
|---|---|---|---|---|
| 108385343 | validation self-play | 26730 / 20955 | ourselves | complete, no crash |
| 108386562 | public | **18986** | Sergey Panasenko **163919** | loss |
| 108387547 | public | **22697** | Ethan Pl **116565** | loss |

Agent logs contain only timings (~0.3 ms/turn). No exceptions. v1 is reliable and too small.

## 2. Replay diagnosis (why we lose)

v1 stays on NW, plants ~8 wheat + 5 melon, places the first cow around **day 9**, tops out at 2 cows, never buys land, never plants strawberry, and emits ~1700 `PASS` actions.

Winners do the opposite on day 0–1:

- Ethan: 4 melon + 5 wheat + **3 sheep + 1 cow on day 0**. By day 15: 10 cows, 3 sheep, ~20 wheat, ~20 strawberry, 3 quadrants. End **$116k**.
- Sergey: **15 melon** + wheat + 2 sheep + 1 cow, NW full day 0. Then 16 cows, 52 strawberry, 3 quadrants, **319 `BUY_PRODUCT WHEAT`**. End **$164k**.

Production gap is 5–8×. ChatGPT’s review matches: scale, idle labor, and missing high-value products — not crashes.

## 3. ChatGPT recommendations (kept)

- More wheat (15–20) and strawberries (10–15 by day 15).
- First cow earlier; use `BUY_PRODUCT WHEAT` as a feed backup.
- Buy land; hire toward 10.
- Sell milk / strawberry / melon with glut awareness.
- Keep crash wrapper and same-turn market delay.

## 4. Replay calibration (stricter than ChatGPT)

ChatGPT’s “5 cows, land by day 10” is still far below the two public opponents. s2 targets:

| Asset | v1 | s2 target | Timing |
|---|---|---|---|
| Melon | 5 | 8–12 | buy/plant days 0–8 |
| Wheat tiles | 8 | 16–22 | from day 0; plus market feed |
| Strawberry | 0 | 12–20 | seeds from day 3; last plant day 18 |
| Cows | 2 late | **8** (path to 10) | first buy **day 0–1**; place immediately |
| Sheep | 0–2 late | **3** | day 0–2 |
| Land | 0 | NE then SW | NE when NW full and cash ≥ $1.4k |
| Hands | ≤6 | **8–10** | hire from hour 0 every day |
| Feed | grown wheat only | grown + `BUY_PRODUCT WHEAT` | keep shed wheat ≥ unfed + 2 |

Do **not** copy an opaque tape. Stay a runtime planner.

## 5. Hard invariants (unchanged)

- `agent(obs, config=None)` → `{farmer, hands, market}`; `hands` length matches observation.
- Player actions resolve before market: never plant a seed bought this turn; never place an animal bought this turn; never assign a hand hired this turn.
- If N units `PLANT` the same crop and seeds < N, all those plants fail — keep a seed budget.
- New plants start `consecutive_unwatered=1` and must be watered the same day.
- Animals cannot be sold. Never buy the next animal if the previous one is still stranded in the shed **and** no worker is assigned to place it.
- Market list ≤ 10. Safety wrapper: `PASS` on unexpected errors.
- Do not plant on the four shed-access tiles.

## 6. s2 decision loop

Same modules as v1: parse → reserves → market → tasks → sticky assign → route/act → safety.

Priority changes:

1. Survival water / feed (escape / weed).
2. Place pending animals / build matching structure.
3. Harvest decaying or mature premium / animal output.
4. Collect fertilizer (lost if skipped).
5. Care fed animals.
6. Plant melon → wheat-for-feed → strawberry → extra wheat.
7. Dig weeds; expand onto newly bought land.
8. Drop and sell; never idle if an empty plantable tile and a seed exist.

## 7. Market order (≤10)

1. Emergency + priced sells: MILK, WOOL, STRAWBERRY, MELON, FERTILIZER, then surplus WHEAT above feed reserve.
2. `BUY_PRODUCT WHEAT` so `shed_wheat + carried ≥ unfed + 2`.
3. `BUY_ANIMAL` / `BUY_LAND` when reserves allow.
4. `BUY_SEED` melon, wheat, strawberry.
5. `HIRE` up to the daily target.

Meter premium if price is mid-crash; dump if already $1 or endgame.

## 8. Acceptance gate before upload

- 0 crashes vs `starter`, `random`, and `2026-09-12/main.py` (v1).
- Mean bank vs `starter` **> v1** (v1 was ~$22k; aim ≥ $35k).
- Win rate vs v1 over ≥ 4 seeds × both seats **≥ 75%**.
- First animal placed by day 3 in the diagnostic replay.
- At least one extra quadrant bought in a typical episode.
- `PASS` rate materially below v1’s ~1700 unit-actions.

## 9. Non-goals for s2

Tape cloning, opponent denial, RL, geese unless yarn/dairy shops are missing (optional later).
