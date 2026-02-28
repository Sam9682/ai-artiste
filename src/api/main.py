"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import artists, venues, search, calendar, health
from src.api.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    init_db()
    yield
    # Shutdown
    close_db()


app = FastAPI(
    title="Artist-Venue Matching Platform",
    description="A bidirectional platform for connecting artists with performance and exhibition venues",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(artists.router, prefix="/api/artists", tags=["artists"])
app.include_router(venues.router, prefix="/api/venues", tags=["venues"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])

# Static files (frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
