# Repository Guidelines

## Project Structure & Module Organization
The main package code lives in the `longbox_commons` directory containing the core modules:
- `parsing.py` — Issue number parsing and normalization
- `models.py` — Pydantic domain models (SeriesInfo, IssueCandidate, SeriesCandidate, ComicIdentity)
- `clz.py` — CLZ CSV import/export utilities
- `prices.py` — Price parsing utilities

Tooling metadata (`pyproject.toml`, `uv.lock`) defines project dependencies. Tests live in the `tests/` directory.

## Build, Test, and Development Commands
- `source .venv/bin/activate`: activate the virtual environment (do this once per session).
- `uv sync --all-extras`: install dependencies via uv.
- `pytest`: run tests.
- `make pytest`: run the test suite with coverage.
- `make lint`: run ruff and pyright.
- `make sync`: install/update dependencies.

## Getting Started
When working on this package:
1. Run `uv sync --all-extras` to install all dependencies
2. Run `source .venv/bin/activate` to activate the virtual environment
3. Run `pytest` to verify tests pass
4. Make your changes with proper test coverage
5. Run `make lint` before committing

## Architecture

### Core Responsibilities
This package provides foundational comic domain utilities with zero dependencies beyond Pydantic:
- **Parsing**: Issue number normalization, variant detection, format code handling
- **Models**: Pydantic models for series/issue candidates and identity resolution
- **CLZ I/O**: CSV import/export for Comic Collector compatibility
- **Prices**: Robust price parsing from marketplace strings

### Design Principles
- **Zero external dependencies** — Only Pydantic is required
- **Type-safe** — Full type hints with pyright validation
- **Battle-tested** — Edge cases from thousands of real comics handled
- **Frozen models** — Immutable data classes where appropriate

### Module Dependencies
- `models.py` — Standalone, only depends on pydantic
- `parsing.py` — Standalone, only depends on stdlib
- `prices.py` — Standalone, only depends on stdlib
- `clz.py` — Depends on models and parsing modules

## Git Worktrees (Parallel Work)
Use git worktrees to work on multiple cards in parallel without branch conflicts:
- Create a branch per card: `git switch -c card/short-slug`
- Add a worktree: `git worktree add ../longbox-commons-<slug> card/short-slug`
- Work only in that worktree for the card; run tests there.
- Keep the branch updated: `git fetch` then `git rebase origin/main` (or merge).
- When merged, remove it: `git worktree remove ../longbox-commons-<slug>`
- Clean stale refs: `git worktree prune`
- WIP limit: 3 cards total in progress across all worktrees.

## Test Coverage Requirements
- Current target: 96% coverage threshold (configured in `pyproject.toml`)
- Always run `pytest --cov=longbox_commons --cov-report=term-missing` to check missing coverage
- When touching logic or input handling, ensure tests are added to maintain coverage
- Parsing edge cases are critical — add tests for new patterns found in wild comic data
- Strategies for increasing coverage:
  - Add tests for remaining uncovered edge cases
  - Add tests for complex error handling paths
  - Add tests for platform-specific code paths (e.g., CLZ quirks)

## Coding Style & Naming Conventions
Follow standard PEP 8 spacing (4 spaces, 100-character soft wrap) and favor descriptive snake_case for functions and variables. Use dataclasses for typed data containers and keep public functions annotated with precise types.

Ruff configuration (from `pyproject.toml`):
- Line length: 100 characters
- Python version: 3.13
- Enabled rules: E, F, I, N, UP, B, C4, D, ANN401
- Ignored: D203, D213, E501
- Code comments are discouraged — prefer clear code and commit messages

## Pre-commit Hook
A pre-commit hook is installed in `.git/hooks/pre-commit` that automatically runs:
- Check for type/linter ignores in staged files
- Run the shared lint script (`scripts/lint.sh`)

The lint script runs:
- Python compilation check
- Ruff linting
- Any type usage check (ruff ANN401 rule)
- Pyright type checking

The hook will block commits containing `# type: ignore`, `# noqa`, `# ruff: ignore`, or `# pylint: ignore`.

To test the hook manually: `make githook` or `bash scripts/lint.sh`

## Code Quality Standards
- Run linting after each change: `make lint` or `bash scripts/lint.sh`
- Use specific types instead of `Any` in type annotations (ruff ANN401 rule)
- Run tests when you touch logic or input handling: `pytest`
- Always write a regression test when fixing a bug.
- If you break something while fixing it, fix both in the same PR.
- Do not use in-line comments to disable linting or type checks.
- Do not narrate your code with comments; prefer clear code and commit messages.

## Parsing Module Guidelines
The parsing module is the most critical component — it handles thousands of real-world comic issue number formats:
- **Test wild examples** — When adding support for new formats, test against real data from multiple platforms
- **Preserve original input** — Always store the raw input string in ParseResult
- **Clear error codes** — Use descriptive error codes for failure modes (EMPTY_INPUT, MULTI_ISSUE_RANGE, etc.)
- **Document edge cases** — Add docstring examples for tricky patterns
- **Normalize aggressively** — Convert unicode symbols (½ → 1/2), handle CLZ quirks, strip punctuation

## Model Module Guidelines
Domain models use Pydantic for validation and serialization:
- **Frozen models** — Use `ConfigDict(frozen=True)` for immutable data (SeriesInfo, ComicIdentity)
- **Optional fields** — Make fields optional when data may be missing from sources
- **Helper methods** — Add display methods (e.g., `display_issue_number()`) for common formatting needs
- **Preserve raw data** — Store original payloads in `raw_payload` field for debugging

## CLZ Module Guidelines
CLZ CSV import must handle messy real-world exports:
- **Validate strictly** — Raise CLZValidationError for missing required fields
- **Parse leniently** — Handle multiple date formats, price formats, whitespace variations
- **Use parsing utilities** — Leverage `parse_issue_candidate` and `parse_format_issue` for consistency
- **Clean data** — Strip whitespace, normalize empty strings to None
- **Preserve errors** — Include context in validation errors for debugging

## Style Guidelines
- Keep helpers explicit and descriptive (snake_case), and annotate public functions with precise types.
- Avoid shell-specific shortcuts; prefer Python APIs and `pathlib.Path` helpers.
- Use frozen dataclasses where immutability is desired.
- Prefer `str | None` over `Optional[str]` (Python 3.10+ style).

## Branch Workflow
- Always create a feature branch from `main` before making changes:
  - `git checkout -b feature-name`
  - Use descriptive names like `fix-issue-parsing` or `add-clz-support`
- Push the feature branch to create a pull request
- After your PR is merged, update your local `main`:
  - `git checkout main`
  - `git pull`
  - Delete the merged branch: `git branch -d feature-name`

## Testing Guidelines
- Automated tests live in `tests/` and run with `python -m pytest` (or `make pytest`).
- When adding tests, keep `pytest` naming like `test_parse_issue_candidate`.
- Test both success and failure paths for parsing functions.
- Include edge cases from real comic data in test fixtures.
- Always use appropriate fixtures from `conftest.py` for testing dependencies.

## Commit & Pull Request Guidelines
- Use imperative, component-scoped commit messages (e.g., "fix: handle CLZ fraction variants", "feat: add unicode symbol normalization")
- Bundle related changes per commit
- PR summary should describe user impact and testing performed
- For parsing changes, include example inputs/outputs in the PR description
