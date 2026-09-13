# Unattended Kaggriculture loop

Runs **5 times per day** in the cloud so the Mac can stay off.

| Local time (`America/Chicago`) | Slot folder | Code folder |
|---|---|---|
| 4:00am | `private/Sep-13-2026-1` | `2026-09-13-s1/` |
| 7:00am | `private/Sep-13-2026-2` | `2026-09-13-s2/` |
| 10:00am | `private/Sep-13-2026-3` | `2026-09-13-s3/` |
| 1:00pm | `private/Sep-13-2026-4` | `2026-09-13-s4/` |
| 3:00pm | `private/Sep-13-2026-5` | `2026-09-13-s5/` |

Each slot waits on the previous upload (~3 hours of live games), then:

1. Pull Kaggle episodes / our agent logs / replays for the last complete submission
2. Compress replays into `replay_summary.json` + `briefing.md`
3. Send the briefing to ChatGPT (`gpt-4o`) via `OPENAI_API_KEY`
4. Write `chatgpt-sX-spec.md` and `kaggriculture-sX-spec.md` under `private/<Mon-DD-YYYY>-X/`
5. Implement `YYYY-MM-DD-sX/main.py` with a **Cursor cloud agent** (`CURSOR_API_KEY`); if that is missing, fall back to ChatGPT writing the file
6. Smoke vs starter on the vendored env when present
7. `kaggle competitions submit kaggriculture`
8. Commit the new `YYYY-MM-DD-sX/main.py` plus `private/<Mon-DD-YYYY>-X/` spec (and `loop_state.json`) and **push to [github.com/ilakkmanoharan/Adaptive-Farm-Agent](https://github.com/ilakkmanoharan/Adaptive-Farm-Agent)**

Replay dumps and `private/api-keys/` stay gitignored. Push runs only after a Kaggle submit (or when `KAGG_LOOP_PUSH=1`). Use `--skip-github` or `KAGG_LOOP_PUSH=0` to disable.

Stops after **2026-09-30**. Kaggle allows 5 submits/day; this uses all of them.

## Code

- Orchestrator: `scripts/kagg_loop/orchestrate.py`
- Scheduler: `.github/workflows/kagg-loop.yml`
- Manual / VPS: `sh scripts/kagg_loop/run.sh --slot 1`

```bash
python3 scripts/kagg_loop/orchestrate.py                  # clock-selected slot
python3 scripts/kagg_loop/orchestrate.py --slot 2 --skip-submit
```

## Cloud setup (one time)

The workflow only runs after this repo is on GitHub with Actions enabled.

1. Repo is [ilakkmanoharan/Adaptive-Farm-Agent](https://github.com/ilakkmanoharan/Adaptive-Farm-Agent). Push `main` (do **not** commit `private/api-keys/`).
2. **Required** or the cron will start and die immediately: [Settings → Secrets and variables → Actions](https://github.com/ilakkmanoharan/Adaptive-Farm-Agent/settings/secrets/actions), add:
   - `OPENAI_API_KEY` — same value as `private/api-keys/api-keys.md`
   - `KAGGLE_USERNAME` / `KAGGLE_KEY` — from `~/.kaggle/kaggle.json`
   - `CURSOR_API_KEY` — [Cursor Dashboard → API Keys](https://cursor.com/dashboard/integrations)
3. Connect this GitHub repo to Cursor (Cloud Agents → GitHub) so step 5 can edit the tree.
4. **Actions → kagg-loop → Run workflow** once to verify. After that the cron fires at the five times above.
5. Optional VPS fallback (if you do not want GitHub):

```cron
TZ=America/Chicago
0 4,7,10,13,15 * * * cd /path/to/Adaptive-Farm-Agent && python3 scripts/kagg_loop/orchestrate.py >> /tmp/kagg-loop.log 2>&1
```

## Secrets policy

Never print, log, or commit API keys. `private/api-keys/` stays gitignored. GitHub Actions injects secrets as env vars only.

## What the coding agent must keep

Crash-safe `PASS` wrapper, no `DROP`, same-turn market delay, one-file `main.py`.
