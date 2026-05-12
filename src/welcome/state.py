"""Persistent state for the `emails` workflow — tracks the latest message we've processed."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_PATH = REPO_ROOT / "state.json"


def load_last_run_epoch(path: Path = STATE_PATH) -> int | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    value = data.get("last_email_run_epoch")
    return int(value) if value is not None else None


def save_last_run_epoch(epoch: int, path: Path = STATE_PATH) -> None:
    path.write_text(json.dumps({"last_email_run_epoch": int(epoch)}, indent=2), encoding="utf-8")
