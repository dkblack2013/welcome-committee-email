"""CLI entry point: `python -m welcome emails` and `python -m welcome bulletin`."""

from __future__ import annotations

import argparse
from pathlib import Path

from .data_parser import parse_emails
from .excel_writer import XLSX_PATH, upsert_members
from .gmail_fetcher import authenticate_gmail, fetch_registration_emails
from .pdf_parser import extract_events_from_pdf, latest_bulletin_path
from .state import load_last_run_epoch, save_last_run_epoch
from .wave_writer import WAVE_PATH, write_wave_md

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DRAFT_PATH = REPO_ROOT / "bulletin_email_draft.txt"


def cmd_emails(args: argparse.Namespace) -> int:
    since = load_last_run_epoch()
    if since is None:
        print(f"No prior state — fetching the most recent {args.first_run_max} emails as a baseline.")
    else:
        print(f"Fetching emails since epoch {since}.")

    service = authenticate_gmail()
    emails = fetch_registration_emails(
        service,
        since_epoch=since,
        fallback_max_results=args.first_run_max,
    )

    if not emails:
        print("No new emails since last run.")
        write_wave_md({})
        print(f"Wrote empty wave file: {WAVE_PATH}")
        return 0

    bucketed = parse_emails(emails)

    # Build a (member, ministries) pair list for the Excel upsert.
    member_to_ministries: dict[str, tuple[dict, set[str]]] = {}
    for ministry, members in bucketed.items():
        for member in members:
            email = (member.get("email") or "").strip().lower()
            if not email:
                continue
            if email not in member_to_ministries:
                member_to_ministries[email] = (member, set())
            member_to_ministries[email][1].add(ministry)

    added, updated = upsert_members(member_to_ministries.values())
    written = write_wave_md(bucketed)

    newest_epoch = max(e["internal_date_epoch"] for e in emails)
    save_last_run_epoch(newest_epoch)

    print(
        f"Processed {len(emails)} email(s) → {added} new member(s), "
        f"{updated} updated. {written} ministry section(s) in current_wave.md."
    )
    print(f"  Excel: {XLSX_PATH}")
    print(f"  Wave : {WAVE_PATH}")
    return 0


def cmd_bulletin(args: argparse.Namespace) -> int:
    pdf_path = Path(args.file).resolve() if args.file else latest_bulletin_path()
    if not pdf_path.exists():
        print(f"Bulletin not found: {pdf_path}")
        return 1
    print(f"Using bulletin: {pdf_path}")

    events_text = extract_events_from_pdf(pdf_path)

    draft = (
        "Subject: This week at the parish\n\n"
        "[paste the body below into Gmail; edit greeting/closing as needed]\n\n"
        "Hello everyone,\n\n"
        "Here are the parish events coming up over the next 30 days:\n\n"
        f"{events_text}\n\n"
        "Warm regards,\n"
        "The Welcome Committee\n"
    )
    DRAFT_PATH.write_text(draft, encoding="utf-8")
    print(f"Wrote draft: {DRAFT_PATH}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="welcome",
        description="Welcome Committee CLI: scrape Gmail registrations and draft bulletin event emails.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_emails = sub.add_parser("emails", help="Fetch new registrations and update Excel + current_wave.md")
    p_emails.add_argument(
        "--first-run-max",
        type=int,
        default=50,
        help="On first run only, how many recent emails to pull (default: 50).",
    )
    p_emails.set_defaults(func=cmd_emails)

    p_bulletin = sub.add_parser("bulletin", help="Run OpenAI on a bulletin PDF and write a draft email")
    p_bulletin.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a specific PDF (default: newest in bulletins/).",
    )
    p_bulletin.set_defaults(func=cmd_bulletin)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
