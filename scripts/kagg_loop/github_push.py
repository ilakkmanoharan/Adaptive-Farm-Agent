"""Commit a slot's code + spec and push to GitHub after a Kaggle submit."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ORIGIN_URL = "https://github.com/ilakkmanoharan/Adaptive-Farm-Agent.git"
ORIGIN_NAME = "origin"
BRANCH = "main"
AUTHOR_NAME = "ilakk manoharan"
AUTHOR_EMAIL = "28582192+ilakkmanoharan@users.noreply.github.com"

from .config import ROOT


class GitPushError(RuntimeError):
    pass


def _run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise GitPushError("%s failed: %s" % (" ".join(args), err[:800]))
    return proc


def _ensure_origin() -> None:
    remotes = _run(["git", "remote"], check=False).stdout.split()
    if ORIGIN_NAME not in remotes:
        _run(["git", "remote", "add", ORIGIN_NAME, ORIGIN_URL])
        return
    current = _run(["git", "remote", "get-url", ORIGIN_NAME]).stdout.strip()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "github.com" in current:
        auth_url = "https://x-access-token:%s@github.com/ilakkmanoharan/Adaptive-Farm-Agent.git" % token
        _run(["git", "remote", "set-url", ORIGIN_NAME, auth_url])
    elif "ilakkmanoharan/Adaptive-Farm-Agent" not in current:
        _run(["git", "remote", "set-url", ORIGIN_NAME, ORIGIN_URL])


def _safe_rel(path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    return str(rel)


def push_slot(*, spec_dir: Path, code_dir: Path, extra: list[Path], message: str) -> dict:
    """Add the spec folder + submission folder, commit if needed, push main."""
    if not (ROOT / ".git").exists():
        raise GitPushError("not a git repo: %s" % ROOT)

    _ensure_origin()
    _run(["git", "fetch", ORIGIN_NAME], check=False)
    _run(["git", "pull", "--rebase", ORIGIN_NAME, BRANCH], check=False)

    rels: list[str] = []
    for path in [spec_dir, code_dir, *extra]:
        rel = _safe_rel(path)
        if rel and path.exists():
            rels.append(rel)
    if not rels:
        raise GitPushError("nothing to add (missing spec/code dirs)")

    _run(["git", "add", "--"] + rels)
    staged = _run(["git", "diff", "--cached", "--quiet"], check=False)
    committed = False
    if staged.returncode != 0:
        _run(
            [
                "git",
                "-c",
                "user.name=%s" % AUTHOR_NAME,
                "-c",
                "user.email=%s" % AUTHOR_EMAIL,
                "commit",
                "-m",
                message,
            ]
        )
        committed = True

    _run(["git", "push", "-u", ORIGIN_NAME, "HEAD:%s" % BRANCH])
    sha = _run(["git", "rev-parse", "HEAD"]).stdout.strip()
    print("pushed %s to %s (%s)" % (sha[:8], ORIGIN_URL, "new commit" if committed else "already committed"))
    return {"sha": sha, "committed": committed, "url": ORIGIN_URL, "paths": rels}
