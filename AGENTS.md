## Build & Run

- Install: `python3 -m uv pip install -e ".[dev]" --python .venv/bin/python`
- Run: `.venv/bin/python -m src.main`

## Validation

- Tests: `.venv/bin/pytest -v`
- Lint: `.venv/bin/ruff check src/ tests/`
- Single test: `.venv/bin/pytest tests/test_foo.py -v`

## Operational Notes

- `uv` installed as Python package, invoke via `python3 -m uv` (not bare `uv`)
- venv created with `python3 -m uv venv --python 3.11`
- System Python is 3.9.6; venv Python is 3.11.5

### Codebase Patterns

- Dataclasses for models (no ORM), raw SQL
- Repository pattern for DB access
- Amounts always positive; type field determines sign semantics
- Keywords stored as JSON TEXT in categories table
- `:memory:` SQLite for tests
