# Project Instructions

## Git Workflow
- Always use the `/commit-push-pr` skill for all commits. Never commit directly with raw git commands.

## Environment
- Python: use `python3 -m uv` (not bare `uv`); venv at `.venv/bin/python` (3.11.5)
- Backend install: `cd backend && python3 -m uv pip install -e ".[dev]" --python ../.venv/bin/python`
- Backend tests: `cd backend && ../.venv/bin/pytest -v`
- Backend run: `cd backend && ../.venv/bin/python run.py` (port 8000)
- Node.js: system version is too old for Vite 7; always prefix frontend commands with `PATH="/usr/local/Cellar/node/25.2.1/bin:/bin:/usr/bin:$PATH"`

## Architecture
- Monorepo: `backend/` (Python FastAPI) + `frontend/` (React + TypeScript + Vite)
- 4 tables: accounts, categories, transactions, statement_snapshots
- Dataclasses + raw SQL (no ORM), repository pattern, DI via sqlite3.Connection
- FastAPI REST API with Pydantic schemas
- React frontend: TanStack Query, React Router, Recharts, Tailwind CSS

## Code Conventions
- TypeScript: `erasableSyntaxOnly` is enabled — no parameter properties in constructors
- Recharts formatter callbacks: don't type-annotate params, use `Number(v ?? 0)`
