"""Implement the next bot: Cursor first, then Grok. OpenAI optional; never required."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from .config import LOCAL_ENV, ROOT, github_repo_url, secret


def latest_code_dir(before: Path | None = None) -> Path | None:
    dirs = sorted(
        [p for p in ROOT.glob("20??-??-??-s*") if p.is_dir() and (p / "main.py").is_file()]
    )
    if before is not None:
        dirs = [p for p in dirs if p.name < before.name]
    return dirs[-1] if dirs else None


def implement(
    *,
    code_dir: Path,
    spec_path: Path,
    prev_dir: Path | None,
    message: str,
) -> Path:
    code_dir.mkdir(parents=True, exist_ok=True)
    dest = code_dir / "main.py"
    if prev_dir and (prev_dir / "main.py").is_file() and not dest.is_file():
        shutil.copy2(prev_dir / "main.py", dest)

    before = dest.read_text(encoding="utf-8") if dest.is_file() else ""
    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    prev_src = (prev_dir / "main.py").read_text(encoding="utf-8") if prev_dir else before
    prompt = _cursor_prompt(
        code_folder=code_dir.name,
        spec=spec,
        prev_folder=prev_dir.name if prev_dir else None,
        prev_src=prev_src,
        message=message,
    )

    runtime = (os.environ.get("KAGG_LOOP_CURSOR_RUNTIME") or "auto").lower()
    used = None
    if secret("CURSOR_API_KEY") and runtime in ("auto", "cloud", "local"):
        try:
            used = _cursor_implement(prompt, runtime=runtime, dest=dest, code_folder=code_dir.name)
            print("cursor implement:", used)
        except Exception as exc:
            (code_dir / "cursor-implement.err.txt").write_text(str(exc), encoding="utf-8")
            print("cursor implement failed:", exc)
            used = None

    if dest.is_file() and dest.stat().st_size > 500:
        after = dest.read_text(encoding="utf-8")
        if used and after != before:
            return dest
        # Cursor cloud may have opened a PR; try to pull main.py from it.
        if used == "cursor" and _try_pull_from_pr(dest, code_dir.name):
            return dest
        if after and len(after) > 500 and used == "cursor-local":
            return dest

    # Grok writes the full file on this runner (reliable for Kaggle upload).
    try:
        grok_src = _llm_implement(
            provider="grok",
            spec=spec,
            prev_src=prev_src,
            code_folder=code_dir.name,
        )
        if grok_src:
            dest.write_text(grok_src, encoding="utf-8")
            print("implement source: grok")
            return dest
    except Exception as exc:
        (code_dir / "grok-implement.err.txt").write_text(str(exc), encoding="utf-8")
        print("grok implement failed:", exc)

    # Optional OpenAI — ignore quota errors.
    try:
        openai_src = _llm_implement(
            provider="openai",
            spec=spec,
            prev_src=prev_src,
            code_folder=code_dir.name,
        )
        if openai_src:
            dest.write_text(openai_src, encoding="utf-8")
            print("implement source: openai")
            return dest
    except Exception as exc:
        print("openai implement skipped:", exc)

    if prev_dir and (prev_dir / "main.py").is_file():
        shutil.copy2(prev_dir / "main.py", dest)
        print("implement source: copy-previous")
        return dest

    if dest.is_file() and dest.stat().st_size > 500:
        print("implement source: existing")
        return dest

    raise SystemExit("implement produced no %s (need CURSOR_API_KEY or XAI_API_KEY)" % dest)


def _cursor_prompt(*, code_folder: str, spec: str, prev_folder: str | None, prev_src: str, message: str) -> str:
    prev_clip = prev_src[-12000:] if prev_src else ""
    return f"""You are implementing Kaggriculture submission `{code_folder}/main.py`.

Rules:
- One stdlib file only: `{code_folder}/main.py` (the Kaggle artifact).
- Keep the crash-safe wrapper: LOCAL_DEBUG / KAGG_DEBUG=1 raises, else safe_pass.
- Never use DROP (it dumps the whole bag). Deposit harvest with PLACE item n.
- Player actions resolve before market.
- Copy the previous bot from `{prev_folder}/main.py` if it exists, then apply the spec.
- Do not touch private/api-keys or print secrets.
- After writing the file, do not open a huge refactor elsewhere.

Commit message hint: {message}

# Spec
{spec}

# Previous main.py (tail if long)
```python
{prev_clip}
```
"""


def _cursor_implement(prompt: str, runtime: str, dest: Path, code_folder: str) -> str:
    from cursor_sdk import Agent, AgentOptions, CloudAgentOptions, CloudRepository, LocalAgentOptions

    key = secret("CURSOR_API_KEY")
    repo = github_repo_url()
    # Prefer local on the Actions runner so main.py lands in this workspace.
    prefer_local = runtime == "local" or (
        runtime == "auto" and os.environ.get("GITHUB_ACTIONS") == "true"
    )
    if prefer_local or runtime == "local":
        options = AgentOptions(
            api_key=key,
            model="composer-2.5",
            local=LocalAgentOptions(cwd=str(ROOT)),
        )
        result = Agent.prompt(prompt, options)
        if getattr(result, "status", None) == "error":
            raise RuntimeError("Cursor local failed: %s" % getattr(result, "id", None))
        if dest.is_file() and dest.stat().st_size > 500:
            return "cursor-local"
        # fall through to cloud if local left no file
        if runtime == "local":
            return "cursor-local"

    if not repo:
        raise RuntimeError("no repo URL for Cursor cloud")
    options = AgentOptions(
        api_key=key,
        model="composer-2.5",
        cloud=CloudAgentOptions(
            repos=[CloudRepository(url=repo, starting_ref=os.environ.get("KAGG_LOOP_REF", "main"))],
            auto_create_pr=True,
            skip_reviewer_request=True,
        ),
    )
    result = Agent.prompt(prompt, options)
    if getattr(result, "status", None) == "error":
        raise RuntimeError("Cursor cloud failed: %s" % getattr(result, "id", None))
    (dest.parent / "cursor-run.json").write_text(
        json.dumps(
            {
                "id": getattr(result, "id", None),
                "status": getattr(result, "status", None),
                "agent_id": getattr(result, "agent_id", None),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return "cursor"


def _try_pull_from_pr(dest: Path, code_folder: str) -> bool:
    """Best-effort: fetch latest open PR and copy code_folder/main.py."""
    try:
        subprocess.run(["git", "fetch", "origin"], cwd=ROOT, check=False, capture_output=True)
        proc = subprocess.run(
            ["git", "ls-remote", "--heads", "origin"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        # Look for cursor / agent branches mentioning the folder name.
        candidates = []
        for line in (proc.stdout or "").splitlines():
            if "refs/heads/" not in line:
                continue
            ref = line.split("refs/heads/", 1)[1].strip()
            low = ref.lower()
            if any(tok in low for tok in ("cursor", "agent", "composer", code_folder.lower())):
                candidates.append(ref)
        for ref in candidates[:5]:
            show = subprocess.run(
                ["git", "show", "origin/%s:%s/main.py" % (ref, code_folder)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            if show.returncode == 0 and show.stdout and len(show.stdout) > 500:
                dest.write_text(show.stdout, encoding="utf-8")
                print("pulled main.py from origin/%s" % ref)
                return True
    except Exception as exc:
        print("pr pull skipped:", exc)
    return False


def _llm_implement(*, provider: str, spec: str, prev_src: str, code_folder: str) -> str | None:
    if provider == "grok":
        key = secret("XAI_API_KEY")
        url = "https://api.x.ai/v1/chat/completions"
        model = (os.environ.get("KAGG_LOOP_GROK_MODEL") or "grok-3").strip()
    else:
        key = secret("OPENAI_API_KEY")
        url = "https://api.openai.com/v1/chat/completions"
        model = (os.environ.get("KAGG_LOOP_OPENAI_MODEL") or "gpt-4o").strip()
    if not key:
        return None

    user = (
        "Rewrite the Kaggriculture agent as a complete Python stdlib main.py.\n"
        "Output ONLY the file contents. No markdown fences.\n"
        "Target folder: %s\n\nSPEC:\n%s\n\nPREVIOUS main.py:\n%s\n"
        % (code_folder, spec[:14000], prev_src[-18000:] if prev_src else "")
    )
    body = {
        "model": model,
        "temperature": 0.15,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You write a single Kaggle competition agent file. "
                    "Keep agent(obs, config=None) as the entry point. "
                    "Never use DROP. Include the crash-safe PASS wrapper."
                ),
            },
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError("%s HTTP %s: %s" % (provider, exc.code, err)) from exc
    text = payload["choices"][0]["message"]["content"]
    return _strip_fences(text)


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1]
        if t.endswith("```"):
            t = t[: t.rfind("```")]
    return t.strip() + "\n"


def local_smoke(code_path: Path, seeds: int = 1) -> dict:
    """One-episode smoke vs starter using the vendored env. Best-effort."""
    if not LOCAL_ENV.is_dir():
        return {"skipped": True}
    import importlib.util
    import sys

    sys.path.insert(0, str(LOCAL_ENV))
    from run_local import _env, _obs_dict, _state, envmod

    spec = importlib.util.spec_from_file_location("kagg_new_agent", str(code_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    env = _env(1000)
    state = [_state(0), _state(1)]
    envmod.interpreter(state, env)
    agents = [mod.agent, envmod.starter_agent]
    for step in range(int(env.configuration.episodeSteps)):
        if any(s.status != "ACTIVE" for s in state):
            break
        for i, s in enumerate(state):
            s.observation.step = step
            s.observation.day = step // 24
            s.observation.hour = step % 24
            s.action = agents[i](_obs_dict(s))
        envmod.interpreter(state, env)
    banks = [float(state[0].observation.farms[i]["money"]) for i in range(2)]
    return {"us": banks[0], "opp": banks[1], "statuses": [s.status for s in state]}
