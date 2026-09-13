#!/usr/bin/env python3
"""One slot of the unattended Kaggriculture loop.

  python3 -m scripts.kagg_loop.orchestrate
  python3 scripts/kagg_loop/orchestrate.py --slot 1 --date 2026-09-13
"""

from __future__ import annotations

import argparse
import json
import os
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
from scripts.kagg_loop.github_push import GitPushError, push_slot
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


def should_push_github(submitted: bool, skip_github: bool) -> bool:
    if skip_github:
        return False
    if os.environ.get("KAGG_LOOP_PUSH") == "0":
        return False
    if submitted:
        return True
    return os.environ.get("KAGG_LOOP_PUSH") == "1"


def main() -> int:
    p = argparse.ArgumentParser(description="Kaggriculture 5x/day cloud loop")
    p.add_argument("--slot", type=int, choices=(1, 2, 3, 4, 5))
    p.add_argument("--date", help="YYYY-MM-DD in America/Chicago")
    p.add_argument("--require-slot-hour", action="store_true",
                   help="no-op unless local hour is 4/7/10/13/15")
    p.add_argument("--skip-submit", action="store_true")
    p.add_argument("--skip-implement", action="store_true")
    p.add_argument("--force", action="store_true", help="re-run a slot that already submitted")
    p.add_argument("--skip-github", action="store_true", help="do not commit/push to GitHub")
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

    kid = result.get("kaggle_id")
    rec = state.mark(
        day,
        slot,
        kaggle_id=kid,
        prev_kaggle_id=prev_id,
        spec=str(sdir.relative_to(ROOT)),
        code=str(cdir.relative_to(ROOT)),
        message=message,
        smoke=smoke,
        status=result.get("status"),
        finished_at=datetime.utcnow().isoformat() + "Z",
    )
    print("state", rec)

    submitted = bool(kid) or (not args.skip_submit and result.get("status") not in (None, "skipped", "unknown"))
    # A completed Kaggle upload always ships code+spec to GitHub, even if the id lookup lagged.
    if not args.skip_submit and result.get("skipped") is not True:
        submitted = True
    if should_push_github(submitted, args.skip_github):
        commit_msg = "Submit %s to Kaggle%s: spec + main.py" % (
            cdir.name,
            " %s" % kid if kid else "",
        )
        try:
            pushed = push_slot(
                spec_dir=sdir,
                code_dir=cdir,
                extra=[STATE_FILE],
                message=commit_msg,
            )
            print("github", pushed)
            state.mark(day, slot, github_sha=pushed.get("sha"), github_url=pushed.get("url"))
        except GitPushError as exc:
            print("github push failed:", exc)
            (sdir / "github-push.err.txt").write_text(str(exc), encoding="utf-8")
            return 2
    else:
        print("skip github push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
