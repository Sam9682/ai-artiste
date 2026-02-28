"""Calendar and booking endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from src.models import Booking, ErrorCode
from src.managers import CalendarManager
from src.api.database import get_calendar_manager

router = APIRouter()


@router.post("/bookings", status_code=201)
async def create_booking(
    booking: dict,
    manager: CalendarManager = Depends(get_calendar_manager)
):
    """Create a new booking."""
    try:
        booking_obj = Booking(**booking)
        result = manager.create_booking(booking_obj)
        
        if result.is_failure:
            raise HTTPException(
                status_code=400,
                detail={"error": result.error.code.value, "message": result.error.message}
            )
        
        return {"id": result.value, "message": "Booking created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: str,
    manager: CalendarManager = Depends(get_calendar_manager)
):
    """Get booking by ID."""
    result = manager.get_booking(booking_id)
    
    if result.is_failure:
        raise HTTPException(
            status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
            detail={"error": result.error.code.value, "message": result.error.message}
        )
    
    return result.value.__dict__


@router.put("/bookings/{booking_id}")
async def update_booking(
    booking_id: str,
    booking: dict,
    manager: CalendarManager = Depends(get_calendar_manager)
):
    """Update booking."""
    try:
        booking_obj = Booking(**booking)
        result = manager.update_booking(booking_id, booking_obj)
        
        if result.is_failure:
            raise HTTPException(
                status_code=404 if result.error.code == ErrorCode.NOT_FOUND else 400,
                detail={"error": result.error.code.value, "message": result.error.message}
            )
        
        return {"message": "Booking updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/artist/{artist_id}")
async def get_artist_calendar(
    artist_id: str,
    manager: CalendarManager = Depends(get_calendar_manager)
):
    """Get calendar events for an artist."""
    events = manager.get_artist_calendar(artist_id)
    return [event.__dict__ for event in events]


@router.get("/venue/{venue_id}")
async def get_venue_calendar(
    venue_id: str,
    manager: CalendarManager = Depends(get_calendar_manager)
):
    """Get calendar events for a venue."""
    events = manager.get_venue_calendar(venue_id)
    return [event.__dict__ for event in events]
