"""Pull the previous submission's episodes, agent logs, and replays."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import COMPETITION, US_NAME


def _api():
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    return api


def list_our_submissions(limit: int = 8) -> list[dict[str, Any]]:
    api = _api()
    rows = []
    for s in api.competition_submissions(COMPETITION) or []:
        rows.append(
            {
                "ref": getattr(s, "ref", None),
                "date": str(getattr(s, "date", "")),
                "description": getattr(s, "description", "") or "",
                "status": str(getattr(s, "status", "")),
                "publicScore": getattr(s, "publicScore", None),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def latest_complete_id(rows: list[dict[str, Any]] | None = None) -> int | None:
    rows = rows if rows is not None else list_our_submissions()
    for row in rows:
        status = str(row.get("status") or "").lower()
        if row.get("ref") and "complete" in status:
            return int(row["ref"])
    if rows and rows[0].get("ref"):
        return int(rows[0]["ref"])
    return None


def _episode_request_types():
    import kagglesdk.competitions.types.competition_api_service as svc

    def pick(*names):
        for name in names:
            cls = getattr(svc, name, None)
            if cls is not None:
                return cls
        available = [n for n in dir(svc) if "Episode" in n or "Replay" in n]
        raise ImportError("kagglesdk missing episode types; have %s" % available)

    return (
        pick("ApiListSubmissionEpisodesRequest"),
        pick("ApiGetEpisodeAgentLogsRequest", "ApiGetEpisodeLogsRequest"),
        pick("ApiGetEpisodeReplayRequest", "ApiGetReplayRequest"),
    )


def pull_submission_logs(submission_id: int, out_dir: Path, label: str = "prev") -> dict[str, Any]:
    """Download episodes + our agent logs + full replays. Opponent logs often 403."""
    ApiListSubmissionEpisodesRequest, ApiGetEpisodeAgentLogsRequest, ApiGetEpisodeReplayRequest = (
        _episode_request_types()
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    api = _api()
    episodes_out: list[dict[str, Any]] = []
    with api.build_kaggle_client() as kaggle:
        req = ApiListSubmissionEpisodesRequest()
        req.submission_id = int(submission_id)
        resp = kaggle.competitions.competition_api_client.list_submission_episodes(req)
        episodes = resp.episodes or []
        for e in episodes:
            agents = []
            for a in e.agents or []:
                agents.append(
                    {
                        "index": getattr(a, "index", None),
                        "submission_id": getattr(a, "submission_id", None),
                        "team_name": getattr(a, "team_name", None)
                        or getattr(a, "agent_name", None),
                        "reward": getattr(a, "reward", None),
                    }
                )
            row = {
                "id": getattr(e, "id", None),
                "agents": agents,
            }
            episodes_out.append(row)
            eid = row["id"]
            if not eid:
                continue
            for agent in agents:
                idx = agent.get("index")
                if idx is None:
                    continue
                name = str(agent.get("team_name") or "")
                if US_NAME.lower() not in name.lower() and str(agent.get("submission_id")) != str(
                    submission_id
                ):
                    # Still try our seat if names are missing.
                    if name and US_NAME.lower() not in name.lower():
                        continue
                try:
                    lreq = ApiGetEpisodeAgentLogsRequest()
                    lreq.episode_id = int(eid)
                    lreq.agent_index = int(idx)
                    logs = kaggle.competitions.competition_api_client.get_episode_agent_logs(lreq)
                    (out_dir / ("%s-episode-%s-agent-%s-logs.json" % (label, eid, idx))).write_text(
                        json.dumps(_jsonable(logs), indent=2),
                        encoding="utf-8",
                    )
                except Exception as exc:
                    (out_dir / ("%s-episode-%s-agent-%s-logs.err.txt" % (label, eid, idx))).write_text(
                        str(exc), encoding="utf-8"
                    )
            try:
                rreq = ApiGetEpisodeReplayRequest()
                rreq.episode_id = int(eid)
                replay = kaggle.competitions.competition_api_client.get_episode_replay(rreq)
                replay_obj = _unwrap_replay(replay)
                (out_dir / ("%s-episode-%s-replay.json" % (label, eid))).write_text(
                    json.dumps(replay_obj),
                    encoding="utf-8",
                )
            except Exception as exc:
                (out_dir / ("%s-episode-%s-replay.err.txt" % (label, eid))).write_text(
                    str(exc), encoding="utf-8"
                )

    meta = {"submission_id": submission_id, "label": label, "episodes": episodes_out}
    (out_dir / "episodes.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def _unwrap_replay(replay: Any) -> Any:
    for attr in ("replay", "episode", "data"):
        inner = getattr(replay, attr, None)
        if inner is None:
            continue
        if isinstance(inner, str):
            try:
                return json.loads(inner)
            except json.JSONDecodeError:
                return {"raw": inner[:2000]}
        return _jsonable(inner)
    return _jsonable(replay)


def _jsonable(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    if hasattr(obj, "to_dict"):
        try:
            return _jsonable(obj.to_dict())
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return {
            k: _jsonable(v)
            for k, v in vars(obj).items()
            if not k.startswith("_")
        }
    return str(obj)
