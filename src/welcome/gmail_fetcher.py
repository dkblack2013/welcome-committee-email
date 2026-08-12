"""Gmail OAuth + paginated fetch of parish-office registration emails."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
PARISH_SENDER = "office@eastsideregion.org"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOKEN_PATH = REPO_ROOT / "token.json"
CREDENTIALS_PATH = REPO_ROOT / "credentials.json"


def authenticate_gmail(
    token_path: Path = TOKEN_PATH,
    credentials_path: Path = CREDENTIALS_PATH,
) -> Any:
    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                token_path.unlink(missing_ok=True)
                creds = None
        if not creds:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"OAuth client file not found at {credentials_path}. "
                    "Download it from Google Cloud Console and place it at the repo root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_registration_emails(
    service: Any,
    since_epoch: int | None = None,
    fallback_max_results: int = 50,
) -> list[dict[str, Any]]:
    """Fetch parish-office emails. If `since_epoch` is set, returns everything newer
    than that timestamp; otherwise returns the most recent `fallback_max_results`
    (used on first run when no state exists)."""

    query = f"from:{PARISH_SENDER}"
    if since_epoch is not None:
        query += f" after:{since_epoch}"

    print(f"Gmail query: {query}")

    message_ids: list[str] = []
    page_token: str | None = None
    while True:
        kwargs: dict[str, Any] = {"userId": "me", "q": query}
        if since_epoch is None:
            kwargs["maxResults"] = fallback_max_results
        if page_token:
            kwargs["pageToken"] = page_token

        result = service.users().messages().list(**kwargs).execute()
        for msg in result.get("messages", []):
            message_ids.append(msg["id"])

        if since_epoch is None:
            break
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    print(f"Found {len(message_ids)} matching messages")

    emails: list[dict[str, Any]] = []
    for msg_id in message_ids:
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        payload = msg["payload"]
        internal_epoch = int(msg["internalDate"]) // 1000
        # Gmail's `after:` operator doesn't compare at second-level precision, so
        # apply a strict filter client-side to exclude the boundary message.
        if since_epoch is not None and internal_epoch <= since_epoch:
            continue
        emails.append(
            {
                "id": msg_id,
                "internal_date_epoch": internal_epoch,
                "subject": _get_header(payload, "Subject"),
                "from": _get_header(payload, "From"),
                "date": _get_header(payload, "Date"),
                "body": _get_email_body(payload),
            }
        )

    return emails


def _get_header(payload: dict, header_name: str) -> str:
    target = header_name.lower()
    for header in payload.get("headers", []):
        if header["name"].lower() == target:
            return header["value"]
    return ""


def _get_email_body(payload: dict) -> str:
    """Walk a possibly-nested multipart payload and return the first text/plain body found."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    for part in payload.get("parts", []) or []:
        body = _get_email_body(part)
        if body:
            return body

    data = payload.get("body", {}).get("data", "")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


if __name__ == "__main__":
    service = authenticate_gmail()
    emails = fetch_registration_emails(service, fallback_max_results=5)
    print(f"Fetched {len(emails)} emails")
    for email in emails:
        print(f"  {email['date']} — {email['subject']}")
