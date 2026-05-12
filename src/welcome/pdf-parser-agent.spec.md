# PDF Bulletin Parser Agent Specification

## Name
PDF Bulletin Parser Agent

## Description
An agent that downloads the Parish Bulletin PDF (manual or automated), extracts text (with OCR for scanned PDFs), and uses OpenAI API to parse upcoming events and details.

## Instructions
1. Acquire PDF link (manual input or scrape website).
2. Download PDF if automated.
3. Extract text using pdfplumber; fallback to Tesseract OCR.
4. Use OpenAI API (ChatGPT) to identify and structure events (who, what, when, where, why).
5. Output structured event data to email generator.
6. Save events to file for reference.

## Capabilities
- PDF text extraction and OCR
- AI-powered content parsing
- Event structuring
- Fallback handling for PDF types
- Event data file saving

## Tools
- pdfplumber, pytesseract
- OpenAI API (ChatGPT)

## Dependencies
- OpenAI API key
- PDF link input

## Validation Gates
- Test parsing on sample PDFs
- AI output accuracy review

## Safety Boundaries
- OpenAI API usage within rate limits
- Fallback to regex parsing if API fails
- No permanent file storage

## Context
- Works in src/welcome-committee-email/
- Provides data to email agent