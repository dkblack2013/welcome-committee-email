"""Append/upsert parsed members into welcome_committee.xlsx."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook, load_workbook

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
XLSX_PATH = REPO_ROOT / "welcome_committee.xlsx"

HEADERS = ["Date Received", "Family Last Name", "First Name", "Last Name", "Email", "Ministries"]
SHEET_NAME = "Members"


def _format_date(epoch: int | None) -> str:
    if epoch is None:
        return ""
    return datetime.fromtimestamp(epoch, tz=timezone.utc).astimezone().strftime("%Y-%m-%d")


def _ensure_workbook(path: Path):
    if path.exists():
        wb = load_workbook(path)
        if SHEET_NAME not in wb.sheetnames:
            ws = wb.create_sheet(SHEET_NAME)
            ws.append(HEADERS)
        return wb
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME
    ws.append(HEADERS)
    return wb


def upsert_members(
    members_with_ministries: Iterable[tuple[dict, set[str]]],
    path: Path = XLSX_PATH,
) -> tuple[int, int]:
    """Append new rows or update existing ones. Returns (added, updated).

    `members_with_ministries` is an iterable of (member_dict, ministries_set) pairs.
    Members are deduped on lowercased email. On match: the Ministries column is
    replaced with the union of old and new ministries; Date Received keeps whichever
    is earlier.
    """
    wb = _ensure_workbook(path)
    ws = wb[SHEET_NAME]

    email_col = HEADERS.index("Email") + 1
    date_col = HEADERS.index("Date Received") + 1
    ministries_col = HEADERS.index("Ministries") + 1

    existing: dict[str, int] = {}
    for row_idx in range(2, ws.max_row + 1):
        cell_email = ws.cell(row=row_idx, column=email_col).value
        if cell_email:
            existing[str(cell_email).strip().lower()] = row_idx

    added = 0
    updated = 0
    for member, ministries in members_with_ministries:
        email = (member.get("email") or "").strip().lower()
        if not email:
            continue
        new_date = _format_date(member.get("date_received_epoch"))
        new_ministries_set = set(ministries)
        new_ministries_str = ", ".join(sorted(new_ministries_set))

        if email in existing:
            row_idx = existing[email]
            old_ministries_cell = ws.cell(row=row_idx, column=ministries_col).value or ""
            old_set = {m.strip() for m in str(old_ministries_cell).split(",") if m.strip()}
            merged = old_set | new_ministries_set
            ws.cell(row=row_idx, column=ministries_col).value = ", ".join(sorted(merged))

            old_date_cell = ws.cell(row=row_idx, column=date_col).value or ""
            if new_date and (not old_date_cell or new_date < str(old_date_cell)):
                ws.cell(row=row_idx, column=date_col).value = new_date
            updated += 1
        else:
            ws.append(
                [
                    new_date,
                    member.get("family_name", "") or "",
                    member.get("first_name", "") or "",
                    member.get("last_name", "") or "",
                    email,
                    new_ministries_str,
                ]
            )
            existing[email] = ws.max_row
            added += 1

    wb.save(path)
    return added, updated
