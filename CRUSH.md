
# CRUSH.md

This file contains essential information for agentic coding agents working in this repository.

## Build/Lint/Test Commands

- No explicit build step required for this Python project.
- Lint: `uv run flake8 .`
- Test: `uv run pytest`
- Run a single test: `uv run pytest <path_to_test_file>::<test_function_name>`

## Code Style Guidelines

- **Imports:** Imports should be grouped and sorted. Standard library imports, then third-party, then local. Each group should be sorted alphabetically.
- **Formatting:** Adhere to [Black](https://github.com/psf/black) formatting style. Use a line length of 88 characters.
- **Types:** Use type hints for function arguments and return values whenever possible.
- **Naming Conventions:** Follow PEP 8 for naming conventions (snake_case for functions and variables, PascalCase for classes).
- **Error Handling:** Use explicit `try-except` blocks for error handling. Avoid bare `except` clauses.
- **Docstrings:** All functions and classes should have clear and concise docstrings.

## `.gitignore`

The `.crush` directory has been added to `.gitignore`.
