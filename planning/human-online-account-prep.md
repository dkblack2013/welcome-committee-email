# Human Online Account Preparation

This document provides step-by-step instructions for setting up the required online accounts and services for the Welcome Committee Email automation project. These setups are necessary for API access (Gmail API and OpenAI API) and must be done by you, as they require personal authentication and credentials. The process is free for the tiers we'll use.

## Google Cloud Free Tier Setup (for Gmail API)
The Gmail API requires a Google Cloud project. This is free under the free tier (includes $300 credit for new accounts, but we won't exceed it for personal use).

### Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account (use the same one linked to your Gmail).
3. If prompted, agree to terms and create a new project (or select an existing one).
4. In the left menu, go to "APIs & Services" > "Library".
5. Search for "Gmail API" and enable it.
6. Go to "APIs & Services" > "Credentials".
7. Click "Create Credentials" > "OAuth 2.0 Client ID".
8. Configure the OAuth consent screen if prompted (set app name to "Welcome Committee Email", user type to "External").
9. For application type, select "Desktop application" (since this runs locally).
10. Download the credentials JSON file (e.g., `credentials.json`) and save it securely in your project folder (e.g., `src/welcome-committee-email/`).
11. The first run of the app will prompt OAuth authentication—follow the link, grant permissions, and save the token.

**Notes:** Free tier covers ~1 billion API units/month. No billing setup needed initially. If you exceed limits, you'll be notified.

## OpenAI API Setup (Optional, for AI Parsing)
If you choose OpenAI for AI parsing (not free), sign up here. For free alternatives, skip this.

### Steps:
1. Go to [OpenAI Platform](https://platform.openai.com/).
2. Sign up or log in with an account.
3. Go to "API Keys" and create a new secret key.
4. Copy the key and store it securely (e.g., in a `.env` file in your project, not committed to git).
5. Add credits if needed (starts with $5 free, but monitor usage to avoid charges).

**Notes:** Costs start at ~$0.002 per 1K tokens. For free options, use local models instead (see grok-plan.md).

## General Tips
- Store credentials securely (e.g., use environment variables or a config file not in version control).
- Test APIs immediately after setup to ensure access.
- If issues, check Google Cloud/OpenAI docs or contact support.