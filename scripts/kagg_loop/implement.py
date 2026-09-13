"""Implement the next bot: Cursor cloud/local first, OpenAI full-file fallback."""

from __future__ import annotations

import json
import os
import shutil
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

    spec = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    prev_src = (prev_dir / "main.py").read_text(encoding="utf-8") if prev_dir else ""
    prompt = _cursor_prompt(
        code_folder=code_dir.name,
        spec=spec,
        prev_folder=prev_dir.name if prev_dir else None,
        prev_src=prev_src,
        message=message,
    )

    runtime = (os.environ.get("KAGG_LOOP_CURSOR_RUNTIME") or "auto").lower()
    key = secret("CURSOR_API_KEY")
    used = None
    if key and runtime in ("auto", "cloud", "local"):
        try:
            used = _cursor_implement(prompt, runtime=runtime)
        except Exception as exc:
            (code_dir / "cursor-implement.err.txt").write_text(str(exc), encoding="utf-8")
            used = None

    if dest.is_file() and dest.stat().st_size > 500 and used == "cursor":
        return dest

    # If Cursor ran locally it should have written dest. Cloud writes on a VM —
    # we still need a file here for Kaggle submit, so fall back to OpenAI.
    if dest.is_file() and dest.stat().st_size > 500 and not key:
        return dest

    openai_src = _openai_implement(spec=spec, prev_src=prev_src, code_folder=code_dir.name)
    if openai_src:
        dest.write_text(openai_src, encoding="utf-8")
    if not dest.is_file():
        raise SystemExit("implement produced no %s" % dest)
    return dest


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


def _cursor_implement(prompt: str, runtime: str) -> str:
    from cursor_sdk import Agent, AgentOptions, CloudAgentOptions, CloudRepository, LocalAgentOptions

    key = secret("CURSOR_API_KEY")
    repo = github_repo_url()
    use_cloud = runtime == "cloud" or (runtime == "auto" and repo)
    if use_cloud and not repo:
        use_cloud = False

    if use_cloud:
        options = AgentOptions(
            api_key=key,
            model="composer-2.5",
            cloud=CloudAgentOptions(
                repos=[CloudRepository(url=repo, starting_ref=os.environ.get("KAGG_LOOP_REF", "main"))],
                auto_create_pr=True,
                skip_reviewer_request=True,
            ),
        )
    else:
        options = AgentOptions(
            api_key=key,
            model="composer-2.5",
            local=LocalAgentOptions(cwd=str(ROOT)),
        )
    result = Agent.prompt(prompt, options)
    status = getattr(result, "status", None)
    if status == "error":
        raise RuntimeError("Cursor run failed: %s" % getattr(result, "id", status))
    return "cursor"


def _openai_implement(*, spec: str, prev_src: str, code_folder: str) -> str | None:
    key = secret("OPENAI_API_KEY")
    if not key:
        return None
    user = (
        "Rewrite the Kaggriculture agent as a complete Python stdlib main.py.\n"
        "Output ONLY the file contents. No markdown fences.\n"
        "Target folder: %s\n\nSPEC:\n%s\n\nPREVIOUS main.py:\n%s\n"
        % (code_folder, spec[:14000], prev_src[-18000:] if prev_src else "")
    )
    body = {
        "model": "gpt-4o",
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
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
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
    from run_local import _env, _obs_dict, _state

    import kaggriculture_env as envmod

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
