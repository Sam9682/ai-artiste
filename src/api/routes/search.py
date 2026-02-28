"""Search endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.models import ErrorCode
from src.managers import SearchEngine
from src.api.database import get_search_engine

router = APIRouter()


@router.get("/venues-for-artist/{artist_id}")
async def search_venues_for_artist(
    artist_id: str,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    engine: SearchEngine = Depends(get_search_engine)
):
    """Search venues matching an artist's requirements."""
    result = engine.search_venues_for_artist(artist_id, min_compatibility_score=min_score)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return [
        {
            "venue": match.venue.__dict__,
            "compatibility_score": match.compatibility_score,
            "common_availabilities": [
                {"start": dr.start.isoformat(), "end": dr.end.isoformat()}
                for dr in match.common_availabilities
            ],
            "unmatched_requirements": match.unmatched_requirements
        }
        for match in result.value
    ]


@router.get("/artists-for-venue/{venue_id}")
async def search_artists_for_venue(
    venue_id: str,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    engine: SearchEngine = Depends(get_search_engine)
):
    """Search artists matching a venue's capabilities."""
    result = engine.search_artists_for_venue(venue_id, min_compatibility_score=min_score)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return [
        {
            "artist": match.artist.__dict__,
            "compatibility_score": match.compatibility_score,
            "common_availabilities": [
                {"start": dr.start.isoformat(), "end": dr.end.isoformat()}
                for dr in match.common_availabilities
            ],
            "unmatched_requirements": match.unmatched_requirements
        }
        for match in result.value
    ]
