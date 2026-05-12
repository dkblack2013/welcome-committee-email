"""Emit per-ministry copy-paste blocks for the current wave."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .data_parser import MINISTRY_BUCKETS

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WAVE_PATH = REPO_ROOT / "current_wave.md"


def write_wave_md(
    bucketed: dict[str, list[dict]],
    path: Path = WAVE_PATH,
) -> int:
    """Write current_wave.md with one section per ministry that has members in
    this run. Returns the number of ministries written."""
    sections = []
    written = 0
    for ministry in MINISTRY_BUCKETS:
        members = bucketed.get(ministry) or []
        emails = sorted({(m.get("email") or "").strip().lower() for m in members if m.get("email")})
        if not emails:
            continue
        sections.append(f"## {ministry}\n\n{', '.join(emails)}\n")
        written += 1

    header = (
        "# Current wave — paste each section's emails into Gmail's BCC field\n\n"
        f"_Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
    )
    body = "\n".join(sections) if sections else "_No new members in this wave._\n"
    path.write_text(header + body, encoding="utf-8")
    return written
