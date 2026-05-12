# AGENTS.md - Implementation Phase

## Project Overview
This folder contains the main Python module for the Welcome Committee Email automation. Agents here implement the core functionality: email fetching, parsing, sorting, PDF processing, data file updating, and email sending.

## Agents
- **Gmail Email Fetcher Agent**: Integrates with Gmail API to retrieve emails. See gmail-agent.spec.md for details.
- **Data Parser and Sorter Agent**: Extracts and categorizes family data. See data-parser-agent.spec.md for details.
- **Data File Updater Agent**: Saves scraped email data to file. See data-file-agent.spec.md for details.
- **PDF Bulletin Parser Agent**: Processes Parish Bulletin PDFs with AI. See pdf-parser-agent.spec.md for details.
- **Email Generator and Sender Agent**: Creates and sends welcome emails. See email-agent.spec.md for details.
- **Scheduler Agent**: Manages monthly execution. See scheduler-agent.spec.md for details.

## Setup Commands
- Install dependencies: `pip install -r requirements.txt`
- Set up API credentials as per planning/human-online-account-prep.md

## Build and Test Commands
- Run: `python src/welcome-committee-email/module.py`
- Test: `python -m pytest tests/`

## Code Style Guidelines
- Python 3.8+, PEP 8, type hints, docstrings.
- Modular functions, graceful error handling.
- No PII logging.

## Security Considerations
- Secure API keys in environment variables.
- OAuth for Gmail, minimal data retention.
- Optional temporary data file for review (added to .gitignore).

## Additional Context
- See planning/grok-plan.md for overall plan.
- Agents coordinate via the main module.py.