# AGENTS.md - Testing Phase

## Project Overview
This folder contains unit and integration tests for the Welcome Committee Email project. Agents here ensure code reliability through automated testing.

## Agents
- **Testing Agent**: Runs and validates tests. See testing-agent.spec.md for details.

## Setup Commands
- Install test dependencies: `pip install pytest`

## Testing Instructions
- Run all tests: `python -m pytest`
- Mock external APIs for unit tests.
- Test edge cases: no emails, invalid data.

## Code Style Guidelines
- Write tests for all public functions.
- Use descriptive test names.

## Additional Context
- Tests validate parsing, sorting, and sending logic.
- See main AGENTS.md for project overview.