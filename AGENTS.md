## Build & Run

### Backend
- Install: `cd backend && python3 -m uv pip install -e ".[dev]" --python ../.venv/bin/python`
- Run: `cd backend && ../.venv/bin/python run.py` (port 8000)

### Frontend
- Install: `cd frontend && PATH="/usr/local/Cellar/node/25.2.1/bin:/bin:/usr/bin:$PATH" npm install`
- Dev: `cd frontend && PATH="/usr/local/Cellar/node/25.2.1/bin:/bin:/usr/bin:$PATH" npm run dev` (port 5173, proxies /api)
- Build: `cd frontend && PATH="/usr/local/Cellar/node/25.2.1/bin:/bin:/usr/bin:$PATH" npm run build`

## Validation

- Backend tests: `cd backend && ../.venv/bin/pytest -v`
- Backend lint: `cd backend && ../.venv/bin/ruff check src/ tests/`
- Frontend build check: `cd frontend && PATH="/usr/local/Cellar/node/25.2.1/bin:/bin:/usr/bin:$PATH" npm run build`

## Operational Notes

- `uv` installed as Python package, invoke via `python3 -m uv` (not bare `uv`)
- System Python 3.9.6; venv Python 3.11.5 at `.venv/bin/python`
- System Node.js 18.13.0 (too old for Vite 7); use `/usr/local/Cellar/node/25.2.1/bin/node`
- Monorepo: `backend/` (Python FastAPI), `frontend/` (React+TypeScript+Vite)

### Codebase Patterns

- Dataclasses for models (no ORM), raw SQL
- Repository pattern for DB access
- Amounts always positive; type field determines sign semantics
- Keywords stored as JSON TEXT in categories table
- `:memory:` SQLite for tests
