#!/usr/bin/env python3
"""One slot of the unattended Kaggriculture loop.

  python3 -m scripts.kagg_loop.orchestrate
  python3 scripts/kagg_loop/orchestrate.py --slot 1 --date 2026-09-13
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

# Allow `python3 scripts/kagg_loop/orchestrate.py`
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    __package__ = "scripts.kagg_loop"

from scripts.kagg_loop.chatgpt_spec import write_specs
from scripts.kagg_loop.config import (
    LAST_SUBMIT_DATE,
    ROOT,
    STATE_FILE,
    code_dir,
    spec_dir,
)
from scripts.kagg_loop.implement import implement, latest_code_dir, local_smoke
from scripts.kagg_loop.kaggle_logs import latest_complete_id, list_our_submissions, pull_submission_logs
from scripts.kagg_loop.slots import is_submit_hour, slot_for
from scripts.kagg_loop import state
from scripts.kagg_loop.summarize import briefing_text, summarize_logs
from scripts.kagg_loop.submit import submit


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    return date.fromisoformat(raw)


def resolve_slot(args: argparse.Namespace) -> tuple[date, int]:
    if args.date and args.slot:
        return _parse_date(args.date), int(args.slot)
    day, slot = slot_for()
    if args.date:
        day = _parse_date(args.date)
    if args.slot:
        slot = int(args.slot)
    return day, slot


def git_sync(paths: list[Path], message: str) -> None:
    if os.environ.get("KAGG_LOOP_PUSH") != "1":
        return
    if not (ROOT / ".git").exists():
        return
    to_add = [str(p.relative_to(ROOT)) for p in paths if p.exists()]
    if not to_add:
        return
    subprocess.run(["git", "add", "--"] + to_add, cwd=ROOT, check=False)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False
    )
    if staged.returncode == 0:
        return
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ilakk manoharan",
            "-c",
            "user.email=28582192+ilakkmanoharan@users.noreply.github.com",
            "commit",
            "-m",
            message,
        ],
        cwd=ROOT,
        check=False,
    )
    subprocess.run(["git", "push"], cwd=ROOT, check=False)


def main() -> int:
    p = argparse.ArgumentParser(description="Kaggriculture 5x/day cloud loop")
    p.add_argument("--slot", type=int, choices=(1, 2, 3, 4, 5))
    p.add_argument("--date", help="YYYY-MM-DD in America/Chicago")
    p.add_argument("--require-slot-hour", action="store_true",
                   help="no-op unless local hour is 4/7/10/13/15")
    p.add_argument("--skip-submit", action="store_true")
    p.add_argument("--skip-implement", action="store_true")
    p.add_argument("--force", action="store_true", help="re-run a slot that already submitted")
    args = p.parse_args()

    if args.require_slot_hour and not is_submit_hour() and not (args.slot or args.date):
        print("not a submit hour in America/Chicago; exiting")
        return 0

    day, slot = resolve_slot(args)
    if day > LAST_SUBMIT_DATE:
        print("past final deadline %s; no submit" % LAST_SUBMIT_DATE)
        return 0

    existing = state.slot_record(state.load(), day, slot)
    if existing and existing.get("kaggle_id") and not args.force:
        print("slot %s %s already submitted as %s" % (day, slot, existing.get("kaggle_id")))
        return 0

    sdir = spec_dir(day, slot)
    cdir = code_dir(day, slot)
    logs_dir = sdir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    print("=== kagg-loop %s slot %s ===" % (day.isoformat(), slot))
    print("spec", sdir)
    print("code", cdir)

    subs = []
    try:
        subs = list_our_submissions()
        (logs_dir / "submissions.json").write_text(json.dumps(subs, indent=2), encoding="utf-8")
        print("kaggle submissions", [(s.get("ref"), s.get("publicScore"), s.get("description")) for s in subs[:4]])
    except Exception as exc:
        print("list submissions failed:", exc)

    prev_id = state.latest_kaggle_id() or latest_complete_id(subs)
    prev_code = latest_code_dir(before=cdir)
    print("previous kaggle id", prev_id, "previous code", prev_code)

    if prev_id:
        try:
            pull_submission_logs(prev_id, logs_dir, label="prev")
        except Exception as exc:
            print("pull logs failed:", exc)
            (logs_dir / "pull.err.txt").write_text(str(exc), encoding="utf-8")

    briefing = summarize_logs(logs_dir)
    brief = briefing_text(briefing)
    (sdir / "briefing.md").write_text(brief, encoding="utf-8")
    print("record", briefing.get("record"), "mean bank", briefing.get("mean_us_bank"))

    spec_path = write_specs(
        sdir,
        day=day,
        slot=slot,
        code_folder=cdir.name,
        briefing_text=brief,
        prev_code_dir=prev_code.name if prev_code else None,
        prev_kaggle_id=prev_id,
    )
    print("wrote spec", spec_path)

    message = "%s-%s log-driven spec+impl" % (day.isoformat(), slot)
    smoke = None
    if not args.skip_implement:
        main_py = implement(
            code_dir=cdir,
            spec_path=spec_path,
            prev_dir=prev_code,
            message=message,
        )
        try:
            smoke = local_smoke(main_py)
            print("local smoke", smoke)
            (sdir / "local_smoke.json").write_text(json.dumps(smoke, indent=2), encoding="utf-8")
        except Exception as exc:
            print("smoke failed:", exc)
            (sdir / "local_smoke.err.txt").write_text(str(exc), encoding="utf-8")
    else:
        main_py = cdir / "main.py"

    result = {"skipped": True}
    if not args.skip_submit:
        result = submit(main_py, message)
        print("submitted", result)
    else:
        print("skip submit")

    rec = state.mark(
        day,
        slot,
        kaggle_id=result.get("kaggle_id"),
        prev_kaggle_id=prev_id,
        spec=str(sdir.relative_to(ROOT)),
        code=str(cdir.relative_to(ROOT)),
        message=message,
        smoke=smoke,
        status=result.get("status"),
        finished_at=datetime.utcnow().isoformat() + "Z",
    )
    print("state", rec)

    git_sync(
        [
            sdir / ("kaggriculture-s%s-spec.md" % slot),
            sdir / ("chatgpt-s%s-spec.md" % slot),
            sdir / "briefing.md",
            sdir / "logs" / "replay_summary.json",
            sdir / "logs" / "episodes.json",
            sdir / "logs" / "submissions.json",
            cdir / "main.py",
            STATE_FILE,
        ],
        message,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
