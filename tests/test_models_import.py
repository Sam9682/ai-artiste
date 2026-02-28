"""Test that all models can be imported correctly."""

import pytest


def test_import_enums():
    """Test importing enumerations."""
    from src.models import ArtType, BookingStatus, ErrorCode
    
    assert ArtType.MUSIC == "music"
    assert BookingStatus.CONFIRMED == "confirmed"
    assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"


def test_import_result():
    """Test importing Result type."""
    from src.models import Result, ErrorDetails, ErrorCode
    
    # Test success case
    result = Result.ok("test data")
    assert result.success is True
    assert result.data == "test data"
    assert result.error is None
    
    # Test failure case
    error = ErrorDetails(
        code=ErrorCode.VALIDATION_ERROR,
        message="Test error"
    )
    result = Result.fail(error)
    assert result.success is False
    assert result.data is None
    assert result.error.code == ErrorCode.VALIDATION_ERROR


def test_import_date_range():
    """Test importing DateRange."""
    from datetime import datetime
    from src.models import DateRange
    
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)
    date_range = DateRange(start_date=start, end_date=end)
    
    assert date_range.start_date == start
    assert date_range.end_date == end
    assert date_range.id is not None


def test_import_address():
    """Test importing Address."""
    from src.models.address import Address, Coordinates
    
    coords = Coordinates(latitude=45.5, longitude=-73.5)
    address = Address(
        street="123 Main St",
        city="Montreal",
        region="Quebec",
        country="Canada",
        postal_code="H1A 1A1",
        coordinates=coords
    )
    
    assert address.city == "Montreal"
    assert address.coordinates.latitude == 45.5


def test_import_technical():
    """Test importing technical models."""
    from src.models import TechnicalRequirements, TechnicalCapabilities
    from src.models.technical import SpaceRequirements, SpaceCapabilities
    
    space_req = SpaceRequirements(min_area=100, min_height=5, indoor_outdoor="indoor")
    tech_req = TechnicalRequirements(space_requirements=space_req)
    
    assert tech_req.space_requirements.min_area == 100
    
    space_cap = SpaceCapabilities(area=150, height=6, type="indoor")
    tech_cap = TechnicalCapabilities(space_capabilities=space_cap)
    
    assert tech_cap.space_capabilities.area == 150


def test_import_profiles():
    """Test importing profile models."""
    from src.models import ArtistProfile, VenueProfile, ArtType
    from src.models.profiles import ArtistBasicInfo, VenueBasicInfo
    from src.models.technical import TechnicalRequirements, TechnicalCapabilities, SpaceCapabilities
    from src.models.address import Address
    
    # Artist profile
    artist_info = ArtistBasicInfo(
        name="Test Artist",
        art_type=ArtType.MUSIC,
        description="A test artist",
        contact_email="artist@test.com"
    )
    artist_profile = ArtistProfile(
        basic_info=artist_info,
        technical_requirements=TechnicalRequirements(),
        user_id="user123"
    )
    
    assert artist_profile.basic_info.name == "Test Artist"
    assert artist_profile.id is not None
    assert artist_profile.created_at is not None
    
    # Venue profile
    venue_info = VenueBasicInfo(
        name="Test Venue",
        address=Address(
            street="456 Venue St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H2B 2B2"
        ),
        description="A test venue",
        contact_email="venue@test.com",
        accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE]
    )
    venue_profile = VenueProfile(
        basic_info=venue_info,
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
        ),
        user_id="user456"
    )
    
    assert venue_profile.basic_info.name == "Test Venue"
    assert venue_profile.id is not None


def test_import_booking():
    """Test importing Booking."""
    from datetime import datetime
    from src.models import Booking, BookingStatus, DateRange
    
    period = DateRange(
        start_date=datetime(2024, 6, 1),
        end_date=datetime(2024, 6, 7)
    )
    booking = Booking(
        artist_id="artist123",
        venue_id="venue456",
        period=period,
        status=BookingStatus.PENDING
    )
    
    assert booking.artist_id == "artist123"
    assert booking.status == BookingStatus.PENDING
    assert booking.id is not None


def test_import_event():
    """Test importing Event."""
    from datetime import datetime
    from src.models import Event, DateRange
    
    date = DateRange(
        start_date=datetime(2024, 6, 1),
        end_date=datetime(2024, 6, 7)
    )
    event = Event(
        booking_id="booking123",
        artist_id="artist123",
        venue_id="venue456",
        date=date,
        artist_name="Test Artist",
        venue_name="Test Venue"
    )
    
    assert event.artist_name == "Test Artist"
    assert event.id is not None
