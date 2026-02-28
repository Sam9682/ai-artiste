"""Artist profile endpoints."""
from fastapi import APIRouter, HTTPException, Depends

from src.models import ArtistProfile, ErrorCode
from src.managers import ProfileManager
from src.api.database import get_profile_manager

router = APIRouter()


@router.post("/", status_code=201)
async def create_artist(
    profile: dict,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Create a new artist profile."""
    try:
        # Convert dict to ArtistProfile
        artist_profile = ArtistProfile(**profile)
        result = manager.create_artist_profile(artist_profile)
        
        if result.is_failure:
            raise HTTPException(
                status_code=400,
                detail={"error": result.error.code.value, "message": result.error.message}
            )
        
        return {"id": result.value, "message": "Artist profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{artist_id}")
async def get_artist(
    artist_id: str,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Get artist profile by ID."""
    result = manager.get_artist_profile(artist_id)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return result.value.__dict__


@router.put("/{artist_id}")
async def update_artist(
    artist_id: str,
    profile: dict,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Update artist profile."""
    try:
        artist_profile = ArtistProfile(**profile)
        result = manager.update_artist_profile(artist_id, artist_profile)
        
        if result.is_failure:
            raise HTTPException(
                status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
                detail={"error": result.error.code.value, "message": result.error.message}
            )
        
        return {"message": "Artist profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{artist_id}")
async def delete_artist(
    artist_id: str,
    manager: ProfileManager = Depends(get_profile_manager)
):
    """Delete artist profile."""
    result = manager.delete_artist_profile(artist_id)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return {"message": "Artist profile deleted successfully"}


@router.get("/")
async def list_artists(
    manager: ProfileManager = Depends(get_profile_manager)
):
    """List all artist profiles."""
    result = manager.get_all_artist_profiles()
    
    if result.is_failure:
        raise HTTPException(status_code=400, detail=result.error.message)
    
    return [artist.__dict__ for artist in result.value]
