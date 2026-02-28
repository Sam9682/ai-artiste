"""Tests for CalendarManager."""

import pytest
from datetime import datetime, timedelta
from src.managers import CalendarManager
from src.models import Event, Booking, BookingStatus, DateRange


class TestCalendarManager:
    """Test suite for CalendarManager."""
    
    def test_get_artist_calendar_returns_only_confirmed_events(self):
        """Test that get_artist_calendar returns only confirmed events."""
        manager = CalendarManager()
        artist_id = "artist-1"
        venue_id = "venue-1"
        
        # Create bookings with different statuses
        confirmed_booking = Booking(
            id="booking-1",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-1",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 2)
            ),
            status=BookingStatus.CONFIRMED
        )
        
        pending_booking = Booking(
            id="booking-2",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-2",
                start_date=datetime(2024, 7, 1),
                end_date=datetime(2024, 7, 2)
            ),
            status=BookingStatus.PENDING
        )
        
        cancelled_booking = Booking(
            id="booking-3",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-3",
                start_date=datetime(2024, 8, 1),
                end_date=datetime(2024, 8, 2)
            ),
            status=BookingStatus.CANCELLED
        )
        
        # Add bookings to manager
        manager.register_booking(confirmed_booking)
        manager.register_booking(pending_booking)
        manager.register_booking(cancelled_booking)
        
        # Create events for each booking
        confirmed_event = Event(
            id="event-1",
            booking_id=confirmed_booking.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=confirmed_booking.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        pending_event = Event(
            id="event-2",
            booking_id=pending_booking.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=pending_booking.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        cancelled_event = Event(
            id="event-3",
            booking_id=cancelled_booking.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=cancelled_booking.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        # Add events to manager
        manager._events[confirmed_event.id] = confirmed_event
        manager._events[pending_event.id] = pending_event
        manager._events[cancelled_event.id] = cancelled_event
        
        # Get artist calendar
        calendar = manager.get_artist_calendar(artist_id)
        
        # Should only return confirmed event
        assert len(calendar) == 1
        assert calendar[0].id == confirmed_event.id
    
    def test_get_artist_calendar_sorts_chronologically(self):
        """Test that get_artist_calendar sorts events by start date."""
        manager = CalendarManager()
        artist_id = "artist-1"
        venue_id = "venue-1"
        
        # Create bookings in non-chronological order
        booking1 = Booking(
            id="booking-1",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-1",
                start_date=datetime(2024, 8, 1),
                end_date=datetime(2024, 8, 2)
            ),
            status=BookingStatus.CONFIRMED
        )
        
        booking2 = Booking(
            id="booking-2",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-2",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 2)
            ),
            status=BookingStatus.CONFIRMED
        )
        
        booking3 = Booking(
            id="booking-3",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-3",
                start_date=datetime(2024, 7, 1),
                end_date=datetime(2024, 7, 2)
            ),
            status=BookingStatus.CONFIRMED
        )
        
        # Add bookings
        manager.register_booking(booking1)
        manager.register_booking(booking2)
        manager.register_booking(booking3)
        
        # Create events
        event1 = Event(
            id="event-1",
            booking_id=booking1.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=booking1.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        event2 = Event(
            id="event-2",
            booking_id=booking2.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=booking2.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        event3 = Event(
            id="event-3",
            booking_id=booking3.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=booking3.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        # Add events
        manager._events[event1.id] = event1
        manager._events[event2.id] = event2
        manager._events[event3.id] = event3
        
        # Get calendar
        calendar = manager.get_artist_calendar(artist_id)
        
        # Should be sorted chronologically
        assert len(calendar) == 3
        assert calendar[0].date.start_date == datetime(2024, 6, 1)
        assert calendar[1].date.start_date == datetime(2024, 7, 1)
        assert calendar[2].date.start_date == datetime(2024, 8, 1)
    
    def test_get_venue_calendar_returns_only_confirmed_events(self):
        """Test that get_venue_calendar returns only confirmed events."""
        manager = CalendarManager()
        artist_id = "artist-1"
        venue_id = "venue-1"
        
        # Create confirmed and pending bookings
        confirmed_booking = Booking(
            id="booking-1",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-1",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 2)
            ),
            status=BookingStatus.CONFIRMED
        )
        
        pending_booking = Booking(
            id="booking-2",
            artist_id=artist_id,
            venue_id=venue_id,
            period=DateRange(
                id="range-2",
                start_date=datetime(2024, 7, 1),
                end_date=datetime(2024, 7, 2)
            ),
            status=BookingStatus.PENDING
        )
        
        # Add bookings
        manager.register_booking(confirmed_booking)
        manager.register_booking(pending_booking)
        
        # Create events
        confirmed_event = Event(
            id="event-1",
            booking_id=confirmed_booking.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=confirmed_booking.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        pending_event = Event(
            id="event-2",
            booking_id=pending_booking.id,
            artist_id=artist_id,
            venue_id=venue_id,
            date=pending_booking.period,
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        # Add events
        manager._events[confirmed_event.id] = confirmed_event
        manager._events[pending_event.id] = pending_event
        
        # Get venue calendar
        calendar = manager.get_venue_calendar(venue_id)
        
        # Should only return confirmed event
        assert len(calendar) == 1
        assert calendar[0].id == confirmed_event.id

    
    def test_add_event_success(self):
        """Test adding an event successfully."""
        manager = CalendarManager()
        
        event = Event(
            id="event-1",
            booking_id="booking-1",
            artist_id="artist-1",
            venue_id="venue-1",
            date=DateRange(
                id="range-1",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 2)
            ),
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        result = manager.add_event(event)
        
        assert result.success is True
        assert result.data.id == event.id
        assert event.id in manager._events
    
    def test_add_event_duplicate_fails(self):
        """Test that adding a duplicate event fails."""
        manager = CalendarManager()
        
        event = Event(
            id="event-1",
            booking_id="booking-1",
            artist_id="artist-1",
            venue_id="venue-1",
            date=DateRange(
                id="range-1",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 2)
            ),
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        # Add event first time
        manager.add_event(event)
        
        # Try to add again
        result = manager.add_event(event)
        
        assert result.success is False
        assert "already exists" in result.error.message
    
    def test_remove_event_success(self):
        """Test removing an event successfully."""
        manager = CalendarManager()
        
        event = Event(
            id="event-1",
            booking_id="booking-1",
            artist_id="artist-1",
            venue_id="venue-1",
            date=DateRange(
                id="range-1",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 2)
            ),
            artist_name="Artist One",
            venue_name="Venue One"
        )
        
        manager._events[event.id] = event
        
        result = manager.remove_event(event.id)
        
        assert result.success is True
        assert result.data is True
        assert event.id not in manager._events
    
    def test_remove_event_not_found(self):
        """Test that removing a non-existent event fails."""
        manager = CalendarManager()
        
        result = manager.remove_event("non-existent")
        
        assert result.success is False
        assert "not found" in result.error.message
    
    def test_format_event_for_public(self):
        """Test formatting an event for public display."""
        manager = CalendarManager()
        
        event = Event(
            id="event-1",
            booking_id="booking-1",
            artist_id="artist-1",
            venue_id="venue-1",
            date=DateRange(
                id="range-1",
                start_date=datetime(2024, 6, 1, 20, 0),
                end_date=datetime(2024, 6, 1, 23, 0)
            ),
            artist_name="Artist One",
            venue_name="Venue One",
            description="A great performance"
        )
        
        formatted = manager.format_event_for_public(event)
        
        assert formatted["id"] == "event-1"
        assert formatted["artist_name"] == "Artist One"
        assert formatted["venue_name"] == "Venue One"
        assert formatted["start_date"] == "2024-06-01T20:00:00"
        assert formatted["end_date"] == "2024-06-01T23:00:00"
        assert formatted["description"] == "A great performance"
