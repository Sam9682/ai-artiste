"""Health check endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "artist-venue-matching"}


@router.get("/version")
async def version():
    """Version endpoint."""
    return {"version": "1.0.0", "name": "Artist-Venue Matching Platform"}
