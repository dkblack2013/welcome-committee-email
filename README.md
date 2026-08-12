# welcome-committee-email

A small CLI for the parish welcome committee. Two workflows, both end in copy-paste into Gmail — nothing is sent automatically.

1. **`emails`** — pulls every registration email from the parish office since the last run, parses families into ministry buckets, appends to a local Excel workbook, and writes a per-ministry "current wave" file ready to paste into Gmail BCC fields.
2. **`bulletin`** — picks the newest bulletin PDF in `bulletins/`, sends it to OpenAI with the prompt in `prompt_for_online_chatgpt.txt`, and writes a draft "upcoming events" email you can paste into Gmail and edit.

The app never sends email. Gmail OAuth is scoped `gmail.readonly`. All outputs are local files.

## Requirements

- Windows with Python 3.10+
- A Google Cloud OAuth client (`credentials.json`) with the Gmail API enabled, for the account that receives the registration emails
- An OpenAI API key (only needed for the `bulletin` command)
- The parish bulletin PDFs dropped into `bulletins/`, named `YYYYMMDD.pdf`

## First-time setup

From the repo root (`C:\Users\dkbla\repos\welcome-committee-email-v2`):

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

The `-e .` flag installs this repo in editable mode using `pyproject.toml`. After that, the `welcome` console script is on your PATH (inside the venv) and you can run `welcome ...` directly.

Drop the following files into the repo root (all gitignored):

- `credentials.json` — OAuth client downloaded from Google Cloud Console
- `.env` — single line: `OPENAI_API_KEY=sk-...`

On the first `welcome emails` run, a browser window will open for Gmail OAuth consent. A `token.json` will be written to the repo root and reused on subsequent runs.

## Commands

All commands can be invoked two equivalent ways. Pick whichever you prefer:

```cmd
welcome <subcommand> [flags]
python -m welcome <subcommand> [flags]
```

### `welcome --help`

Shows top-level help and lists the two subcommands.

### `welcome emails`

Pull new registration emails since the last run, update the Excel record, write the current wave file, and advance the state pointer.

```cmd
welcome emails
welcome emails --first-run-max 38
```

**Flags**

| Flag | Default | What it does |
|---|---|---|
| `--first-run-max N` | `38` | On the first run only (when `state.json` doesn't yet exist), pull the most recent N emails as a baseline. Ignored on subsequent runs, which use the `after:<epoch>` filter instead. |

**What it does**

1. Reads `state.json` for the timestamp of the newest email processed last time. If missing, treats this as a first run.
2. Authenticates against Gmail (browser flow on first use, cached `token.json` after).
3. Queries `from:office@eastsideregion.org` plus an `after:<epoch>` filter, paginating until exhausted.
4. Extracts each family's adults, emails, and ministry interests from the message body.
5. Buckets each member into one or more of the 27 canonical ministries (exact case-insensitive match against the registration form's options).
6. Appends/upserts each member into `welcome_committee.xlsx` — deduped by lowercased email; on a re-match, ministries are merged and the earliest "Date Received" is kept.
7. Writes `current_wave_<YYYY-MM-DD_HHMM>.md` with one section per ministry that had new members in this batch, each section a comma-separated email list ready to paste into Gmail's BCC field.
8. Updates `state.json` with the newest message timestamp.

### `welcome bulletin`

Send a bulletin PDF to OpenAI and write a draft email summarizing the next 30 days of events.

```cmd
welcome bulletin
welcome bulletin --file bulletins\20260208.pdf
```

**Flags**

| Flag | Default | What it does |
|---|---|---|
| `--file PATH` | newest PDF in `bulletins/` | Use a specific bulletin instead of the auto-picked latest. |

**What it does**

1. Picks the newest PDF in `bulletins/` (lexicographic sort of `YYYYMMDD.pdf` filenames), or the file you passed via `--file`.
2. Reads the prompt verbatim from `prompt_for_online_chatgpt.txt`.
3. Uploads the PDF to OpenAI via the Files API and runs the prompt against it through the Responses API (`gpt-5`).
4. Writes the model's numbered event list — plus a small subject/intro/closing template — to a timestamped file under `email-materials/`.

Open the newest file in `email-materials/`, paste the body into a new Gmail compose window, edit greeting/closing as desired, send.

## Outputs

Output files live in the repo root or under `email-materials/`. All are gitignored.

| File | Written by | Purpose |
|---|---|---|
| `welcome_committee.xlsx` | `welcome emails` | Cumulative record of every parsed member, deduped by email. Columns: Date Received, Family Last Name, First Name, Last Name, Email, Ministries. |
| `email-materials/current_wave_<YYYY-MM-DD_HHMM>.md` | `welcome emails` | This run's ministry-grouped email lists, plus a combined "All members" list at the top. Filename is timestamped so prior runs aren't overwritten. |
| `welcome_committee_template.xlsx` | `welcome emails` | Two-sheet workbook matching `welcome-committee-example.xlsx`: a `Members` sheet (copy of the main xlsx) and a `Sheet2` with one column per ministry. Row 2 of Sheet2 is reserved for ministry-lead emails you fill in manually — preserved across runs. |
| `email-materials/bulletin_email_draft_<YYYY-MM-DD_HHMM>.txt` | `welcome bulletin` | Draft email containing the model's chronological event list. Filename is timestamped so prior drafts aren't overwritten. |
| `state.json` | `welcome emails` | Tracks the latest message timestamp processed, so the next run only fetches what's newer. |
| `bulletin_email_draft.txt` | `welcome bulletin` | A draft email body containing the model's chronological event list. Overwritten every run. |
| `token.json` | first OAuth flow | Cached Gmail credentials. |

## Repo layout

```
welcome-committee-email-v2/
  pyproject.toml                 # package metadata; declares the `welcome` console script
  prompt_for_online_chatgpt.txt  # prompt sent to OpenAI by `welcome bulletin`
  bulletins/                     # input bulletin PDFs (YYYYMMDD.pdf)
  email-materials/               # generated wave files and bulletin drafts, both timestamped
  CLAUDE.md                      # guidance for AI assistants editing this repo
  README.md                      # this file
  src/welcome/
    cli.py                       # argparse entry; dispatches subcommands
    __main__.py                  # `python -m welcome` shim
    gmail_fetcher.py             # OAuth + paginated fetch with `after:` filter
    data_parser.py               # registration-form parsing + ministry buckets
    pdf_parser.py                # OpenAI Files API + Responses API
    state.py                     # state.json reader/writer
    excel_writer.py              # openpyxl upsert into welcome_committee.xlsx
    wave_writer.py               # writes email-materials/current_wave_*.md
```

## Troubleshooting

**`OPENAI_API_KEY is not set`** — Create `.env` at the repo root with one line: `OPENAI_API_KEY=sk-...`. Confirm the file is at the repo root, not inside `src/`.

**`OAuth client file not found`** — Place `credentials.json` (downloaded from Google Cloud Console) at the repo root. Make sure the OAuth client is configured for "Desktop app" and that the Gmail API is enabled in the same project.

**Gmail prompts for consent every run** — Your `token.json` may be invalid or for the wrong scope. Delete `token.json` and re-run; you'll go through the OAuth flow once more.

**Excel rows duplicated after a re-run** — Shouldn't happen; upsert is keyed on lowercased email. If you see duplicates, check whether the same person registered twice with different cases or extra whitespace in the email field. Open `welcome_committee.xlsx` and normalize manually.

**Want to re-process a batch you already ran** — Edit `state.json` to an earlier `last_email_run_epoch` (Unix seconds) or delete the file entirely. The next `welcome emails` run will refetch.

**Bulletin output is poor quality** — Confirm the right PDF was picked (the command prints the path). Try `welcome bulletin --file bulletins\<specific>.pdf`. Compare against pasting the same PDF into ChatGPT in the browser — output should match.

## Notes

- The CLI is the only entry point. Importing modules directly works for ad-hoc use but isn't a supported interface.
- This app does not send email and does not request a Gmail send scope. See `CLAUDE.md` for the standing rule.
- The 27 ministry names are defined in `src/welcome/data_parser.py:MINISTRY_BUCKETS`. They must match the canonical names on the parish registration form for the bucket matcher to work.
