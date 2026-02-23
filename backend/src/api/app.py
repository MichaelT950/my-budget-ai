"""FastAPI application — lifespan, CORS, router mounts."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.deps import set_connection
from src.api.routers import accounts, categories, dashboard, import_csv, reports, statements, transactions
from src.database.connection import create_connection
from src.database.schema import initialize_database
from src.database.seeds import seed_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.environ.get("DATABASE_PATH", "data/budget.db")
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = create_connection(db_path)
    initialize_database(conn)
    seed_categories(conn)
    set_connection(conn)
    yield
    conn.close()


app = FastAPI(title="My Budget AI", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(statements.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(import_csv.router)

# Serve frontend static files in production
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
