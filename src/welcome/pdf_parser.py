"""Send a parish bulletin PDF to OpenAI and return the extracted-events text."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPT_PATH = REPO_ROOT / "prompt_for_online_chatgpt.txt"
BULLETINS_DIR = REPO_ROOT / "bulletins"

MODEL = "gpt-5"


def latest_bulletin_path() -> Path:
    """Pick the most recent PDF in bulletins/. Files are named YYYYMMDD.pdf, so
    a lexicographic sort is chronological."""
    pdfs = sorted(BULLETINS_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDFs found in {BULLETINS_DIR}")
    return pdfs[-1]


def extract_events_from_pdf(pdf_path: Path) -> str:
    """Upload the PDF to OpenAI and run the bulletin-extraction prompt against it.
    Returns the model's response text verbatim (a numbered chronological event list)."""

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env at the repo root.")

    prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()

    client = OpenAI()

    with pdf_path.open("rb") as f:
        uploaded = client.files.create(file=f, purpose="user_data")

    try:
        response = client.responses.create(
            model=MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": uploaded.id},
                        {"type": "input_text", "text": prompt},
                    ],
                }
            ],
        )
    finally:
        try:
            client.files.delete(uploaded.id)
        except Exception:
            pass

    text = (response.output_text or "").strip()
    if not text:
        raise RuntimeError("OpenAI returned an empty response.")
    return text


if __name__ == "__main__":
    path = latest_bulletin_path()
    print(f"Using bulletin: {path}")
    print(extract_events_from_pdf(path))
