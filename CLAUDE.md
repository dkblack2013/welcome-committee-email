# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Hard rules

- **Stay inside this repo folder.** Do not read, write, list, or `cd` into anything outside `C:\Users\dkbla\repos\welcome-committee-email-v2` without explicit per-session permission from the user. This includes sibling repos, parent directories, and global config locations. If a task seems to require an external path, stop and ask.
- **Never auto-send email.** This app is copy-paste only. Do not call `service.users().messages().send(...)`, do not add SMTP, and do not request the `gmail.send` OAuth scope. Gmail scope stays at `gmail.readonly`.
- **Never generate per-family personalized email HTML.** That was scope creep and was removed. The output is per-ministry copy-paste blocks plus a single bulletin-events draft.
- **Do not commit secrets.** `.env`, `credentials.json`, `token.json`, and `state.json` are gitignored. If you find one staged, unstage it and tell the user. If `OPENAI_API_KEY` was ever committed, tell the user to rotate.

## What this app does

A small Python CLI for the parish welcome committee. Two workflows, both end in copy-paste-into-Gmail:

1. **`emails`** — pulls every email from `office@eastsideregion.org` since the last run, parses the family registration form fields, sorts members into ministry buckets, appends to `welcome_committee.xlsx`, and writes a `current_wave.md` with per-ministry email lists ready to BCC.
2. **`bulletin`** — picks the newest PDF in `bulletins/`, uploads it to OpenAI via the Files API, runs the prompt in `prompt_for_online_chatgpt.txt`, and writes the model's numbered event list to `bulletin_email_draft.txt`.

## Run

```
python -m welcome emails
python -m welcome bulletin
python -m welcome bulletin --file bulletins\20260208.pdf
```

Auth on first run: a browser window opens for Gmail OAuth. `OPENAI_API_KEY` must be set in `.env`.

## Architecture

```
src/welcome-committee-email/
  cli.py             # argparse entry, dispatches subcommands
  gmail_fetcher.py   # OAuth + paginated fetch with `after:` filter
  data_parser.py     # registration-form parsing + 27 ministry buckets
  pdf_parser.py      # OpenAI Files API + Responses API call
  state.py           # state.json read/write (last_email_run_epoch)
  excel_writer.py    # openpyxl append/upsert into welcome_committee.xlsx
  wave_writer.py     # current_wave.md emitter
bulletins/           # input PDFs, named YYYYMMDD.pdf
prompt_for_online_chatgpt.txt   # single source of truth for the bulletin prompt
```

Outputs (all gitignored, all in repo root): `welcome_committee.xlsx`, `current_wave.md`, `bulletin_email_draft.txt`, `state.json`.

## Conventions

- Bulletin filenames are `YYYYMMDD.pdf` — lexicographic sort = chronological.
- The bulletin prompt lives in `prompt_for_online_chatgpt.txt` and is read at runtime. **Do not duplicate the prompt into Python source.** Edit the `.txt`.
- Excel deduping is by email (lowercased). Re-runs upsert; they don't append duplicates.
- Last-run state is stored as Unix epoch seconds of the newest processed message's `internalDate`. The Gmail query uses `after:{epoch}`.
- The OpenAI call uses `client.responses.create(model="gpt-5", input=[input_file, input_text])`. Do not fall back to `chat.completions` with truncated text — that path produced worse output than the browser ChatGPT and was removed.
- Ministry-bucket matching is exact case-insensitive equality, not substring. The registration form uses canonical names from `MINISTRY_BUCKETS`.

## Out of scope (do not add back)

- Gmail send / SMTP / per-family HTML / Jinja templates
- `pdfplumber`, `pytesseract`, `transformers`, `pandas`, `jinja2`, `schedule` — none are needed; do not reintroduce
- Web scraping the parish website — explicitly chosen against; we use the local `bulletins/` folder
- Google Sheets integration — explicitly chosen against in favor of local `.xlsx`

## Before claiming a change works

- For Gmail/Excel changes: run `python -m welcome emails` end-to-end and open the xlsx + `current_wave.md` to verify contents.
- For bulletin changes: run `python -m welcome bulletin` and read `bulletin_email_draft.txt`. Compare against pasting the same PDF into ChatGPT browser — output should be comparable.
- Type checks and unit tests verify code, not feature correctness. If the workflow can't be run end-to-end (e.g., no OpenAI key in your sandbox), say so explicitly.
