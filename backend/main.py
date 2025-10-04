from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging, logging.config, os

from .config.settings import get_settings
from .routes import runs as runs_routes
from .routes import webhook as webhook_routes

settings = get_settings()

app = FastAPI(
    title="AutoInfra CoPilot API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for local dev / Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health
@app.get("/health")
def health():
    return {"ok": True, "env": settings.environment, "sync": settings.run_sync}

# logging config
cfg_path = os.path.join(os.path.dirname(__file__), "config", "logging.conf")
if os.path.exists(cfg_path):
    logging.config.fileConfig(cfg_path, disable_existing_loggers=False)

# Mount run-related routes
app.include_router(runs_routes.router)
app.include_router(webhook_routes.router)
