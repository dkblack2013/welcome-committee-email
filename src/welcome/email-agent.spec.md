# Email Generator and Sender Agent Specification

## Name
Email Generator and Sender Agent

## Description
An agent that generates personalized HTML welcome emails for families and notification emails for ministry leads, incorporating parsed data and bulletin events, then sends via Gmail API.

## Instructions
1. Receive bucketed family data and bulletin events.
2. Generate HTML templates: one per family (personalized), one per bucket for leads.
3. Include greetings, event lists, contact info.
4. Send emails via Gmail API.
5. Log successes/failures without PII.

## Capabilities
- Template rendering
- HTML email composition
- Batch sending
- Error handling and retries

## Tools
- Jinja2 for templates
- Gmail API for sending

## Dependencies
- Data from parser agents
- Gmail API setup

## Validation Gates
- Template review by user
- Test email sends (to self)

## Safety Boundaries
- No spam; targeted sends only
- Secure authentication
- Rate limit compliance

## Context
- Works in src/welcome-committee-email/
- Final agent in workflow