# How everyday Kaggle submissions run with the Mac off

Date written: 2026-09-15

Yes — we are really doing this. Your laptop does not need to be on. GitHub’s cloud runners do the work.

## Short answer

1. The repo lives at [github.com/ilakkmanoharan/Adaptive-Farm-Agent](https://github.com/ilakkmanoharan/Adaptive-Farm-Agent).
2. A GitHub Actions workflow (`.github/workflows/kagg-loop.yml`) is scheduled with `cron: "0 * * * *"` — every hour UTC.
3. Each hour, GitHub starts a fresh Ubuntu VM, checks out the repo, injects secrets, and runs `scripts/kagg_loop/orchestrate.py`.
4. That script pulls the last submission’s episode data, asks ChatGPT for a next-spec, implements `main.py`, uploads to Kaggle, then commits the bot + spec back to GitHub.
5. After **5 successful uploads for the Chicago calendar day**, later hourly runs exit without submitting (Kaggle’s daily cap).

Your Mac is only needed to push code changes, edit secrets, or run a manual **Actions → kagg-loop → Run workflow**. It is not in the submit path.

## Where the loop lives

| Piece | Path / place |
|---|---|
| Scheduler | `.github/workflows/kagg-loop.yml` |
| Orchestrator | `scripts/kagg_loop/orchestrate.py` |
| Slot bookkeeping | `private/loop_state.json` |
| Specs | `private/Sep-DD-YYYY-N/` |
| Bots | `YYYY-MM-DD-sN/main.py` |
| Secrets | GitHub repo → Settings → Secrets and variables → Actions |

Required secrets (already set on the repo):

- `OPENAI_API_KEY`
- `KAGGLE_USERNAME`
- `KAGGLE_KEY` (also used as `KAGGLE_API_TOKEN` / `~/.kaggle/access_token` on the runner)
- `CURSOR_API_KEY` (optional; without it, ChatGPT writes the agent)

`private/api-keys/` stays gitignored. Actions never needs your Mac’s key files after the secrets are stored.

## What one hourly run does

```
GitHub cron (top of hour UTC)
        │
        ▼
   Ubuntu runner checks out main
        │
        ▼
   Write ~/.kaggle/{kaggle.json,access_token}
        │
        ▼
   python3 scripts/kagg_loop/orchestrate.py
        │
        ├─ pick next unused Chicago-day slot (1–5)
        ├─ if 5 already done → exit 0 (no submit)
        ├─ list Kaggle submissions; find previous id
        ├─ pull episodes / replays for previous id
        ├─ summarize → briefing.md
        ├─ ChatGPT → chatgpt-sN-spec.md + kaggriculture-sN-spec.md
        ├─ implement YYYY-MM-DD-sN/main.py
        ├─ local smoke vs starter (when env is present)
        ├─ kaggle competitions submit kaggriculture
        └─ git commit + push spec folder + main.py + loop_state.json
```

Timezone for “which day / which slot” is `America/Chicago`. Cron is UTC; GitHub often fires a few minutes late. That is normal.

## Proof it is really running (as of 2026-09-15 evening)

### GitHub Actions (scheduled, not your laptop)

Recent **schedule** runs on [Actions → kagg-loop](https://github.com/ilakkmanoharan/Adaptive-Farm-Agent/actions/workflows/kagg-loop.yml):

| When (UTC) | Run | Result |
|---|---|---|
| 2026-09-15 22:02 | #16 | success → s4 |
| 2026-09-15 18:04 | #15 | success → s3 |
| 2026-09-15 13:22 | #14 | success → s2 |
| 2026-09-15 07:32 | #13 | success → s1 |
| 2026-09-15 01:18 | #12 | success → Sep-14 s5 |
| … | #8–#11 | success through Sep-14 s1–s4 |

All of those event types are `schedule`. They were not started from this Mac.

### Kaggle uploads

Recent competition submissions (complete):

| Kaggle id | Description |
|---|---|
| 56263176 | `2026-09-15-4 log-driven spec+impl` |
| 56260468 | `2026-09-15-3 log-driven spec+impl` |
| 56255331 | `2026-09-15-2 log-driven spec+impl` |
| 56248884 | `2026-09-15-1 log-driven spec+impl` |
| 56242301 | `2026-09-14-5 log-driven spec+impl` |
| … | Sep-14 s1–s4, Sep-13 s5 |

### GitHub tree

Folders on `origin/main` that the loop created unattended:

- Bots: `2026-09-13-s5`, `2026-09-14-s1` … `s5`, `2026-09-15-s1` … `s4`
- Specs: `private/Sep-13-2026-5`, `private/Sep-14-2026-1` … `5`, `private/Sep-15-2026-1` … `4`

Example commit message pattern:

`Submit 2026-09-15-s4 to Kaggle 56263176: spec + main.py`

### Early failures (for context)

Sep 13 runs #1–#5 failed before secrets / Kaggle auth were fixed. Manual run #7 was the first successful cloud submit (`56216661`). From #8 onward, scheduled runs have been succeeding.

## Why your computer being off does not matter

- GitHub Actions VMs are hosted by GitHub, not on your LAN.
- Secrets are stored in GitHub; the runner gets them as env vars each job.
- Kaggle and OpenAI are called from that VM.
- Results are pushed back to the same GitHub repo with the job’s `GITHUB_TOKEN`.

Closing the Mac only stops **local** Cursor chats. It does not stop the cron.

## Limits and caveats

- **5 submits / Chicago day** — after that, hourly jobs succeed but do nothing.
- **GitHub cron drift** — often 5–40 minutes late; spacing is “about hourly,” not exact.
- **Entry / final deadlines** — orchestrator stops after `2026-09-30`.
- **Quality of each bot** — if episode-log pull fails, ChatGPT may get a thin briefing and the new `main.py` can look a lot like the previous one. Auth and scheduling can still be healthy while strategy improvement is weak.
- **Only 2 active bots** on the Kaggle ladder — each new upload displaces an older one from the active pair.

## How to check anytime

1. [Actions → kagg-loop](https://github.com/ilakkmanoharan/Adaptive-Farm-Agent/actions/workflows/kagg-loop.yml) — green `schedule` runs?
2. [Kaggle Submissions](https://www.kaggle.com/competitions/kaggriculture/submissions) — new `YYYY-MM-DD-N log-driven…` rows?
3. GitHub `main` — new `2026-09-*-s*` folders and matching `private/Sep-*-*` specs?
4. `private/loop_state.json` on `main` — `kaggle_id` per day/slot?

## Related notes

- Setup / secrets: `private/auto-gent-spec.md`
- Do **not** put API keys in this file or commit `private/api-keys/`.
