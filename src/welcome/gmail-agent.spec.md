# Gmail Email Fetcher Agent Specification

## Name
Gmail Email Fetcher Agent

## Description
An agent that integrates with the Gmail API to securely fetch incoming emails containing new family details. Filters emails by sender/subject, retrieves content, and passes to data parser agent.

## Instructions
0. Create a Python module: src/welcome-committee-email/gmail_fetcher.py with functions for auth and fetching.
1. Authenticate with Gmail API using OAuth. API key in .env file.
2. Search for emails matching criteria (e.g., from parish office, subject keywords).
2b. The parish office email address is: Parish Offices <office@eastsideregion.org>
2c. Email subject is usually "St Cecilia New Parishioner Registration".
3. Retrieve email bodies and attachments.
4. Handle pagination for large volumes.
5. Output structured email data to data parser.

## Capabilities
- OAuth authentication
- Email searching and retrieval
- Secure credential management
- Error handling for API limits

## Tools
- Gmail API client libraries
- Secure storage for tokens

## Dependencies
- Google Cloud project setup (see human-online-account-prep.md)
- Python google-api-python-client

## Validation Gates
- Successful authentication and test email fetch
- No PII exposure in logs

## Safety Boundaries
- Read-only access to emails
- No sending capabilities
- Respect API quotas

## Context
- Works in src/welcome-committee-email/
- Coordinates with data parser agent