"""Venue profile endpoints."""
from fastapi import APIRouter, HTTPException, Depends

from src.models import VenueProfile, ErrorCode
from src.managers import ProfileManager
from src.api.database import get_profile_manager

router = APIRouter()


@router.post("/", status_code=201)
async def create_venue(
    profile: dict,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Create a new venue profile."""
    try:
        venue_profile = VenueProfile(**profile)
        result = manager.create_venue_profile(venue_profile)
        
        if result.is_failure:
            raise HTTPException(
                status_code=400,
                detail={"error": result.error.code.value, "message": result.error.message}
            )
        
        return {"id": result.value, "message": "Venue profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{venue_id}")
async def get_venue(
    venue_id: str,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Get venue profile by ID."""
    result = manager.get_venue_profile(venue_id)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return result.value.__dict__


@router.put("/{venue_id}")
async def update_venue(
    venue_id: str,
    profile: dict,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Update venue profile."""
    try:
        venue_profile = VenueProfile(**profile)
        result = manager.update_venue_profile(venue_id, venue_profile)
        
        if result.is_failure:
            raise HTTPException(
                status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
                detail={"error": result.error.code.value, "message": result.error.message}
            )
        
        return {"message": "Venue profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{venue_id}")
async def delete_venue(
    venue_id: str,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Delete venue profile."""
    result = manager.delete_venue_profile(venue_id)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return {"message": "Venue profile deleted successfully"}


@router.get("/")
async def list_venues(
    manager: ProfileManager = Depends(get_profile_manager)
):
    """List all venue profiles."""
    result = manager.get_all_venue_profiles()
    
    if result.is_failure:
        raise HTTPException(status_code=400, detail=result.error.message)
    
    return [venue.__dict__ for venue in result.value]
