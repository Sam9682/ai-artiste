"""Calendar manager for managing public calendars and events."""

from typing import Dict, List
from src.models import (
    Event,
    Booking,
    BookingStatus,
    Result,
    ErrorDetails,
    ErrorCode
)


class CalendarManager:
    """Manages public calendars and events for artists and venues."""
    
    def __init__(self, booking_repository=None):
        """
        Initialize the calendar manager with booking repository.
        
        Args:
            booking_repository: Repository for booking persistence (optional)
        """
        self.booking_repository = booking_repository
        self._events: Dict[str, Event] = {}
    
    def get_artist_calendar(self, artist_id: str) -> List[Event]:
        """
        Get all confirmed events for an artist, sorted chronologically.
        
        Args:
            artist_id: The ID of the artist
            
        Returns:
            List of confirmed events sorted by start date
        """
        # Filter events for this artist with confirmed status
        artist_events = [
            event for event in self._events.values()
            if event.artist_id == artist_id and self._is_event_confirmed(event)
        ]
        
        # Sort events chronologically by start date
        artist_events.sort(key=lambda e: e.date.start_date)
        
        return artist_events
    
    def get_venue_calendar(self, venue_id: str) -> List[Event]:
        """
        Get all confirmed events for a venue, sorted chronologically.
        
        Args:
            venue_id: The ID of the venue
            
        Returns:
            List of confirmed events sorted by start date
        """
        # Filter events for this venue with confirmed status
        venue_events = [
            event for event in self._events.values()
            if event.venue_id == venue_id and self._is_event_confirmed(event)
        ]
        
        # Sort events chronologically by start date
        venue_events.sort(key=lambda e: e.date.start_date)
        
        return venue_events
    
    def _is_event_confirmed(self, event: Event) -> bool:
        """
        Check if an event is confirmed by looking up its booking status.
        
        Args:
            event: The event to check
            
        Returns:
            True if the event's booking is confirmed, False otherwise
        """
        if self.booking_repository:
            booking_result = self.booking_repository.get_by_id(event.booking_id)
            if booking_result.success:
                return booking_result.data.status == BookingStatus.CONFIRMED
            return False
        
        # Fallback to in-memory storage
        if not hasattr(self, '_bookings'):
            self._bookings = {}
        booking = self._bookings.get(event.booking_id)
        return booking is not None and booking.status == BookingStatus.CONFIRMED
    
    def add_event(self, event: Event) -> Result[Event]:
        """
        Add an event to the calendar.
        
        Args:
            event: The event to add
            
        Returns:
            Result containing the added event or error details
        """
        if event.id in self._events:
            return Result(
                success=False,
                error=ErrorDetails(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"Event with ID {event.id} already exists"
                )
            )
        
        self._events[event.id] = event
        return Result(success=True, data=event)
    
    def remove_event(self, event_id: str) -> Result[bool]:
        """
        Remove an event from the calendar.
        
        Args:
            event_id: The ID of the event to remove
            
        Returns:
            Result containing True if removed, or error details
        """
        if event_id not in self._events:
            return Result(
                success=False,
                error=ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Event with ID {event_id} not found"
                )
            )
        
        del self._events[event_id]
        return Result(success=True, data=True)
    
    def format_event_for_public(self, event: Event) -> dict:
        """
        Format an event for public display.
        
        Args:
            event: The event to format
            
        Returns:
            Dictionary with formatted event information
        """
        return {
            "id": event.id,
            "artist_name": event.artist_name,
            "venue_name": event.venue_name,
            "start_date": event.date.start_date.isoformat(),
            "end_date": event.date.end_date.isoformat(),
            "description": event.description
        }
    
    def register_booking(self, booking: Booking) -> None:
        """
        Register a booking for tracking (used when not using repository).
        
        Args:
            booking: The booking to register
        """
        if not hasattr(self, '_bookings'):
            self._bookings = {}
        self._bookings[booking.id] = booking
