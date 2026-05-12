# AGENTS.md

## Project Overview
This project automates the Welcome Committee email process for a Catholic Parish. It pulls new family details from Gmail emails, sorts them into ministry buckets, parses the Parish Bulletin PDF using AI, generates/sends monthly welcome emails, and updates a data file with scraped information. Built with Python for simplicity and privacy.

Key components:
- Gmail API integration for email reading/sending
- PDF parsing with text extraction and OCR fallback
- AI parsing using OpenAI API (ChatGPT) with regex fallback
- Data sorting and email templating
- Data file updating with scraped email data
- Bulletin events file saving for reference
- Monthly scheduling via cron

## Setup Commands
- Install dependencies: `pip install -r requirements.txt`
- Set up Python environment: Use Python 3.8+; configure virtual environment if needed
- API setup: Follow human-online-account-prep.md for Google Cloud and optional OpenAI
- Local AI: Install Ollama or Hugging Face Transformers for free AI parsing

## Build and Test Commands
- Run the app: `python src/welcome-committee-email/module.py`
- Test parsing: Run unit tests with `python -m pytest` (add tests in a tests/ folder)
- Lint: `flake8 src/` or `black src/` for code formatting
- Validate: Check for syntax errors with `python -m py_compile src/welcome-committee-email/module.py`

## Code Style Guidelines
- Use Python 3.8+ syntax
- Follow PEP 8 for formatting (use Black for auto-formatting)
- Use type hints where possible
- Keep functions modular and documented with docstrings
- Handle exceptions gracefully; log errors without exposing PII
- No permanent data storage; process in-memory for privacy (optional temporary data file for review)

## Testing Instructions
- Write unit tests for key functions (e.g., email parsing, sorting, PDF extraction)
- Test with sample data: Mock Gmail API responses and PDF files
- Edge cases: No emails, invalid data, API failures
- Run tests before commits: `python -m pytest`
- Integration test: Full run with real credentials (in dev mode)

## Security Considerations
- Store API keys securely (environment variables, not in code)
- No logging of personal info (PII); use anonymized logs
- Validate inputs to prevent injection attacks
- Use OAuth for Gmail access; revoke tokens if compromised
- Comply with data privacy laws (e.g., GDPR); minimal data retention

## PR Instructions
- Title format: [Feature/Bug] Brief description
- Run tests and linting before submitting
- Include unit tests for new code
- Update grok-plan.md if changing requirements
- Squash commits for clean history

## Agents
This project uses multiple specialized agents defined with PROSE specifications for reliable AI-native development. Agents are organized hierarchically:

- **Planning Agents**: In planning/AGENTS.md - Handle requirements and specs.
- **Implementation Agents**: In src/welcome-committee-email/AGENTS.md - Core functionality.
- **Testing Agents**: In tests/AGENTS.md - Validation and testing.

Each agent has a .spec.md file with PROSE constraints (Orchestrated Composition, Safety Boundaries, etc.) for structured operation.

## Additional Context
- See planning/grok-plan.md for detailed plan
- See planning/human-online-account-prep.md for account setup
- For AI parsing, prefer free local models to avoid costs
- Monthly run: Schedule via cron (e.g., `0 0 1 * * python /path/to/module.py`)

## New prompt for Claude
 I already tried building an app here, and it partially works. So far, I've been having partial success. If I
  manually look at my email, count the number of emails received since the prior batch, and then update the number of
  emails to scrape, I can pull the correct emails from my Gmail. If I set it to test mode, it will generate the list
  of emails for me to paste in my Gmail GUI (I don't trust the auto send, and I was never planning on sending
  individualized emails to people, that was a bit of scope creep). The listing of emails broken out by ministry
  category works for me to document everything, so I would want to keep that, but I would like it to automatically
  update an excel spreadsheet (or better yet, update my existing Google Sheets spreadsheet). I'm manually downloading
  the past week's bulletin using my browser and then manually updating the file path, then using the OpenAI API to
  pull out all relevant details. However, it has yet to be as effective as pasting the PDF in my ChatGPT browser
  conversation, and I'm not sure how to improve the output. Please put together a plan to take the existing code in
  this repo (or to start over completely) and build the app I was trying to build at the start. What I'm looking for
  is a CLI app that can look at the most recent run, see what time that was, and pull every email in my Gmail from the
  parish office email address down. Then it should parse those emails, put together a database, and make it easy for
  me to copy-paste the current wave emails into Gmail manually. In a separate workflow, it should either scrape the
  parish website for the most recent bulletin or find the most recent bulletin file saved to the repo bulletins
  folder, then figure out a way to apply the prompt_for_online_chatgpt.txt prompt on that bulletin to gather the list
  of upcoming events and craft a new email for me. I would like to then be able to copy-paste the email draft into my
  Gmail GUI, review it, and send it.