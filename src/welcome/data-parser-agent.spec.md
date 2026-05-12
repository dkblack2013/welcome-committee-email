# Data Parser and Sorter Agent Specification

## Name
Data Parser and Sorter Agent

## Description
An agent that parses email content to extract family names, emails, and interests, aggregates data from multiple emails, deduplicates, and sorts families into ministry buckets based on criteria.

## Instructions
1. Receive email data from fetcher agent.
2. Parse free-form or structured text for family details.
3. Aggregate and deduplicate across emails.
4. Sort into buckets (e.g., Young Adult Ministry) using interest matching.
5. Handle multi-interest families (add to all relevant buckets).
6. Output bucketed data to email generator.

## Capabilities
- Text parsing and extraction
- Data aggregation and deduplication
- Rule-based sorting
- Edge case handling (missing data, invalid formats)

## Tools
- Regex or NLP libraries for parsing
- Pandas for data manipulation

## Dependencies
- Input from gmail agent
- Ministry bucket definitions from plan

## Validation Gates
- Test parsing accuracy on sample emails
- Verify sorting logic with user

## Safety Boundaries
- No external API calls
- In-memory processing only
- Anonymize data in logs

## Context
- Works in src/welcome-committee-email/
- Orchestrates with gmail and email agents