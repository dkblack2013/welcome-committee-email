# Grok Plan: Automate Welcome Committee Email Process

## Overview
This plan outlines building a Python-based application to automate the Welcome Committee tasks for a Catholic Parish. The app will pull new family details from Gmail emails, sort them into ministry buckets, parse the Parish Bulletin PDF using AI, and generate/send a monthly welcome email. This replaces manual processes, ensuring timely communications while prioritizing data privacy.

Based on project specs: Automate pulling info from Gmail emails about new families (names, emails, details), sorting into buckets for informing ministry leads, and preparing monthly emails by parsing the latest Parish Bulletin PDF.

## Key Requirements and Clarifications
- **Incoming Emails**: Emails contain new family details (names, emails, interests from sign-up forms). Structure: Free-form or table in body; filter by sender/subject (e.g., from parish office). Extract programmatically.
- **Ministry Buckets**: Categories include General Welcoming Email List, Young Adult Ministry, Bible Studies, Family of Faith Formation, Women's Fellowship, Men's Guild, RCIA, Women's Group, Respect Life, Choir/Music Ministry, Garden Crew, SVDP, Thanksgiving Dinner, Worship Commission, Adornment, Building & Grounds, Parish Council, Lectors, Eucharistic Minister, Knights of Columbus, Home Distributors of Holy Communion, Bereavement, Ushers, Altar Servers, EPIC, Stewardship Commission, Greeters, Church Cleaning. Sorting based on interests selected in sign-up forms (e.g., "Church Cleaning|Garden Crew|Thanksgiving Dinner"). Families with multiple interests go into all relevant buckets.
- **Bulletin Parsing**: Use AI to extract upcoming events and details (who, what, when, where, why, plus other relevant info) from the PDF. Handle scanned PDFs with OCR.
- **PDF Acquisition**: Manual download; user inputs PDF link into the script. Optional: Automate via web scraping.
- **Email Output**: Monthly welcome email to families (personalized) and notifications to ministry leads with bucketed lists. Format: HTML for readability.
- **Scheduling**: Run monthly (e.g., 1st of the month); trigger via local cron or `schedule` library.
- **Privacy**: Handle personal data securely; no permanent storage, in-memory processing only. Optionally save parsed data to a temporary file for review and record-keeping.

## Technologies
- **Language**: Python.
- **Gmail Integration**: Gmail API for reading/sending emails (free tier).
- **PDF Parsing**: `pdfplumber` for text extraction; Tesseract for OCR on scanned PDFs.
- **AI**: Free local models (e.g., Hugging Face Transformers or Ollama with Llama 3.1) for event extraction. Optional: OpenAI API.
- **Scheduling**: `schedule` library or local cron.
- **Other**: `pandas` for data sorting, `requests`/`beautifulsoup` for optional PDF scraping, secure credential management.

## Steps
1. Set up Google Cloud project and enable Gmail API for OAuth 2.0 authentication (see human-online-account-prep.md).
2. Implement email filtering and parsing logic in [src/welcome-committee-email/module.py](src/welcome-committee-email/module.py) to extract family data from Gmail (e.g., search by sender/subject).
3. Add data aggregation: Combine multiple emails, deduplicate families, handle multi-interest bucketing.
4. Add sorting functionality to categorize families into buckets.
5. Save parsed and bucketed data to a data file for review and record-keeping.
6. Integrate PDF parsing: Extract text (with OCR fallback), then use AI to structure events (define prompts for JSON output).
7. Create email template generation: HTML templates for personalized family emails and lead notifications.
8. Implement email sending via Gmail API.
9. Add scheduling for monthly execution (e.g., cron job).
10. Add error handling: Retries for API failures, logging, notifications for failures (e.g., no families = send bulletin-only email).
11. Ensure privacy: No PII in logs, secure key storage.

## Verification
- Test with sample Gmail credentials, emails, and bulletin PDF.
- Verify filtering, parsing accuracy, sorting, AI extraction, and email sending.
- Use unit tests for key functions (e.g., parsing, sorting).
- Manually review generated emails; test edge cases (no families, invalid data).

## Cost Analysis
Most components are free; focus on free AI to keep total at $0.

- **Gmail API**: Free (Google Cloud free tier: ~1B units/month).
- **PDF Parsing (pdfplumber/Tesseract)**: Free (open-source).
- **AI Parsing**: OpenAI API at ~$0.01-0.10/month (with regex fallback). Optional: Free local models (Hugging Face/Ollama).
- **Other Libraries**: Free.
- **Hosting**: Free (local machine).

**Total Monthly Cost**: $0.01-0.10 (OpenAI API). Free option available with local models.

## Decisions
- Python for ecosystem fit.
- Manual PDF input initially; free AI for parsing.
- No data persistence for privacy.
- Account setups by user (see human-online-account-prep.md).