# longbox-commons

[![CI Status](https://github.com/JoshCLWren/longbox-commons/workflows/CI/badge.svg)](https://github.com/JoshCLWren/longbox-commons/actions)

Comic domain foundation library providing parsing, models, CLZ I/O, and price utilities for Python 3.13+.

## Overview

`longbox-commons` is a foundational package for comic book collection management systems. It provides core domain models, parsing utilities, and data import/export functionality used across the longbox ecosystem.

## Features

- **Issue Number Parsing** — Parse and normalize comic issue numbers with variants, decimals, fractions, and format codes
- **Domain Models** — Pydantic models for series, issues, and identity candidates
- **CLZ CSV I/O** — Read and write Comic Collector CSV exports with validation
- **Price Parsing** — Extract numeric prices from marketplace strings with currency symbols
- **Zero External Dependencies** — Only requires Pydantic

## Installation

```bash
pip install longbox-commons
```

## Quick Start

### Parsing Issue Numbers

```python
from longbox_commons import parse_issue_candidate, ParseResult

# Parse standard issue numbers
result = parse_issue_candidate("#1")
assert result.success
assert result.canonical_issue_number == "1"

# Parse variant issues
result = parse_issue_candidate("12B")
assert result.canonical_issue_number == "12"
assert result.variant_suffix == "B"

# Parse decimal and fraction issues
result = parse_issue_candidate("0.5")
assert result.canonical_issue_number == "0.5"

result = parse_issue_candidate("½")
assert result.canonical_issue_number == "1/2"
```

### Using Domain Models

```python
from longbox_commons import IssueCandidate, SeriesCandidate
from datetime import date

issue = IssueCandidate(
    source="clz",
    source_series_id="batman-1940",
    source_issue_id="12345",
    series_title="Batman",
    series_start_year=1940,
    publisher="DC Comics",
    issue_number="1",
    variant_suffix="A",
    cover_date=date(1940, 4, 1),
    price=0.10,
)

series = SeriesCandidate(
    source="clz",
    source_series_id="batman-1940",
    series_title="Batman",
    series_start_year=1940,
    publisher="DC Comics",
)
```

### CLZ CSV Import

```python
from longbox_commons.clz import read_csv_file, row_to_issue

# Read CLZ export
rows = read_csv_file("my_collection.csv")

# Convert rows to domain models
issues = []
for row in rows:
    try:
        issue = row_to_issue(row)
        issues.append(issue)
    except Exception as e:
        print(f"Skipping row: {e}")
```

### Price Parsing

```python
from longbox_commons import parse_price

# Parse marketplace price strings
price = parse_price("$12.99")
assert price == 12.99

price = parse_price("1,299.00 USD")
assert price == 1299.0
```

## Modules

### `longbox_commons.parsing`

Issue number parsing and normalization. Handles:
- Standard issue numbers: `1`, `#1`, `-1`
- Variants: `12B`, `1A`, `100ABC`
- Decimals: `0.5`, `0.1`
- Fractions: `½`, `¼`, `⅓` (normalized to `1/2`, `1/4`, `1/3`)
- Format codes: `TP`, `HC`, `GN`, `SC`, `TPB`, `OGN`, `OM`
- CLZ format patterns: `HC-2`, `1HC-E`, `TPB`

### `longbox_commons.models`

Pydantic domain models:
- `SeriesInfo` — Core series metadata
- `IssueCandidate` — Intermediate issue representation for ingestion
- `SeriesCandidate` — Intermediate series representation for ingestion
- `ComicIdentity` — Resolved identity with confidence scoring

### `longbox_commons.clz`

CLZ Comic Collector CSV import/export:
- `read_csv_file()` — Load CSV from file path
- `read_csv_string()` — Load CSV from string
- `write_csv_file()` — Write rows to CSV file
- `row_to_issue()` — Convert CSV row to IssueCandidate
- `row_to_series()` — Convert CSV row to SeriesCandidate

### `longbox_commons.prices`

Price parsing utilities:
- `parse_price()` — Extract numeric value from price strings

## Development

```bash
# Clone repository
git clone https://github.com/JoshCLWren/longbox-commons.git
cd longbox-commons

# Install dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest

# Run linting
make lint
```

### Make Commands

- `make lint` — Run ruff and pyright
- `make pytest` — Run test suite with coverage
- `make sync` — Install/update dependencies

## Requirements

- Python 3.13+
- Pydantic 2.0+

## Testing

Minimum 96% test coverage enforced. Run tests with:

```bash
pytest --cov=longbox_commons --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `make lint`
6. Commit with conventional commits
7. Push and create a pull request

## License

MIT License — see LICENSE file for details

## Related Packages

- [scrapekit](https://github.com/JoshCLWren/scrapekit) — HTTP client and caching
- [stealthkit](https://github.com/JoshCLWren/stealthkit) — Playwright stealth automation
- [dbkit](https://github.com/JoshCLWren/dbkit) — Async database factory
- [comic-identity-engine](https://github.com/JoshCLWren/comic-identity-engine) — Entity resolution system

## Credits

Created by Josh Wren
