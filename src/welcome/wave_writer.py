"""Emit per-ministry copy-paste blocks for the current wave."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .data_parser import MINISTRY_BUCKETS

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WAVE_DIR = REPO_ROOT / "email-materials"


def _wave_path(now: datetime) -> Path:
    WAVE_DIR.mkdir(parents=True, exist_ok=True)
    return WAVE_DIR / f"current_wave_{now.strftime('%Y-%m-%d_%H%M')}.md"


def write_wave_md(
    bucketed: dict[str, list[dict]],
    path: Path | None = None,
) -> tuple[Path, int]:
    """Write a dated current_wave_<timestamp>.md with one section per ministry plus
    a combined 'All members' section listing the unique-deduped emails from every
    ministry in this run. Returns (path_written, num_ministry_sections)."""
    now = datetime.now()
    if path is None:
        path = _wave_path(now)

    ministry_sections: list[str] = []
    all_emails: set[str] = set()
    section_count = 0
    for ministry in MINISTRY_BUCKETS:
        members = bucketed.get(ministry) or []
        emails = sorted({(m.get("email") or "").strip().lower() for m in members if m.get("email")})
        if not emails:
            continue
        ministry_sections.append(f"## {ministry}\n\n{', '.join(emails)}\n")
        all_emails.update(emails)
        section_count += 1

    header = (
        "# Current wave — paste each section's emails into Gmail's BCC field\n\n"
        f"_Generated {now.strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
    )

    if all_emails:
        combined = f"## All members (combined, deduped)\n\n{', '.join(sorted(all_emails))}\n"
        body = combined + "\n" + "\n".join(ministry_sections)
    else:
        body = "_No new members in this wave._\n"

    path.write_text(header + body, encoding="utf-8")
    return path, section_count
