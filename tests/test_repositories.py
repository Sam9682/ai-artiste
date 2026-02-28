"""Tests for repository implementations."""

import pytest
from datetime import datetime

from src.repositories import Database, ArtistRepository, VenueRepository, BookingRepository
from src.models import (
    ArtistProfile,
    VenueProfile,
    Booking,
    ArtType,
    BookingStatus,
    DateRange,
    Address
)
from src.models.profiles import ArtistBasicInfo, VenueBasicInfo
from src.models.technical import (
    TechnicalRequirements,
    TechnicalCapabilities,
    SpaceRequirements,
    SpaceCapabilities
)


@pytest.fixture
def database():
    """Create an in-memory database for testing."""
    db = Database("sqlite:///:memory:")
    db.create_tables()
    yield db
    db.drop_tables()


@pytest.fixture
def artist_repository(database):
    """Create an artist repository with a test session."""
    session = database.get_session()
    yield ArtistRepository(session)
    session.close()


@pytest.fixture
def venue_repository(database):
    """Create a venue repository with a test session."""
    session = database.get_session()
    yield VenueRepository(session)
    session.close()


@pytest.fixture
def booking_repository(database):
    """Create a booking repository with a test session."""
    session = database.get_session()
    yield BookingRepository(session)
    session.close()


@pytest.fixture
def sample_artist_profile():
    """Create a sample artist profile for testing."""
    return ArtistProfile(
        user_id="user-123",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(
                min_area=100,
                min_height=5,
                indoor_outdoor="indoor"
            )
        ),
        availabilities=[]
    )


@pytest.fixture
def sample_venue_profile():
    """Create a sample venue profile for testing."""
    return VenueProfile(
        user_id="user-456",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Test St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(
                area=200,
                height=10,
                type="indoor"
            )
        ),
        availabilities=[]
    )


@pytest.fixture
def sample_booking():
    """Create a sample booking for testing."""
    return Booking(
        artist_id="artist-123",
        venue_id="venue-456",
        period=DateRange(
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 5)
        ),
        status=BookingStatus.PENDING
    )


class TestArtistRepository:
    """Tests for ArtistRepository."""
    
    def test_create_and_retrieve_artist_profile(self, artist_repository, sample_artist_profile):
        """Test creating and retrieving an artist profile."""
        # Create profile
        create_result = artist_repository.create(sample_artist_profile)
        assert create_result.success
        assert create_result.data.id == sample_artist_profile.id
        
        # Retrieve profile
        get_result = artist_repository.get_by_id(sample_artist_profile.id)
        assert get_result.success
        assert get_result.data.id == sample_artist_profile.id
        assert get_result.data.basic_info.name == "Test Artist"
        assert get_result.data.basic_info.art_type == ArtType.MUSIC
    
    def test_update_artist_profile(self, artist_repository, sample_artist_profile):
        """Test updating an artist profile."""
        # Create profile
        artist_repository.create(sample_artist_profile)
        
        # Update profile
        sample_artist_profile.basic_info.name = "Updated Artist"
        update_result = artist_repository.update(sample_artist_profile)
        assert update_result.success
        
        # Verify update
        get_result = artist_repository.get_by_id(sample_artist_profile.id)
        assert get_result.success
        assert get_result.data.basic_info.name == "Updated Artist"
    
    def test_delete_artist_profile(self, artist_repository, sample_artist_profile):
        """Test deleting an artist profile."""
        # Create profile
        artist_repository.create(sample_artist_profile)
        
        # Delete profile
        delete_result = artist_repository.delete(sample_artist_profile.id)
        assert delete_result.success
        
        # Verify deletion
        get_result = artist_repository.get_by_id(sample_artist_profile.id)
        assert not get_result.success
    
    def test_get_all_artist_profiles(self, artist_repository, sample_artist_profile):
        """Test retrieving all artist profiles."""
        # Create multiple profiles
        artist_repository.create(sample_artist_profile)
        
        profile2 = ArtistProfile(
            user_id="user-789",
            basic_info=ArtistBasicInfo(
                name="Another Artist",
                art_type=ArtType.PAINTING,
                description="Another test artist",
                contact_email="artist2@test.com"
            ),
            technical_requirements=TechnicalRequirements(
                space_requirements=SpaceRequirements(
                    min_area=50,
                    min_height=3,
                    indoor_outdoor="indoor"
                )
            ),
            availabilities=[]
        )
        artist_repository.create(profile2)
        
        # Get all profiles
        all_result = artist_repository.get_all()
        assert all_result.success
        assert len(all_result.data) == 2


class TestVenueRepository:
    """Tests for VenueRepository."""
    
    def test_create_and_retrieve_venue_profile(self, venue_repository, sample_venue_profile):
        """Test creating and retrieving a venue profile."""
        # Create profile
        create_result = venue_repository.create(sample_venue_profile)
        assert create_result.success
        assert create_result.data.id == sample_venue_profile.id
        
        # Retrieve profile
        get_result = venue_repository.get_by_id(sample_venue_profile.id)
        assert get_result.success
        assert get_result.data.id == sample_venue_profile.id
        assert get_result.data.basic_info.name == "Test Venue"
        assert get_result.data.basic_info.address.city == "Test City"
    
    def test_update_venue_profile(self, venue_repository, sample_venue_profile):
        """Test updating a venue profile."""
        # Create profile
        venue_repository.create(sample_venue_profile)
        
        # Update profile
        sample_venue_profile.basic_info.name = "Updated Venue"
        update_result = venue_repository.update(sample_venue_profile)
        assert update_result.success
        
        # Verify update
        get_result = venue_repository.get_by_id(sample_venue_profile.id)
        assert get_result.success
        assert get_result.data.basic_info.name == "Updated Venue"
    
    def test_delete_venue_profile(self, venue_repository, sample_venue_profile):
        """Test deleting a venue profile."""
        # Create profile
        venue_repository.create(sample_venue_profile)
        
        # Delete profile
        delete_result = venue_repository.delete(sample_venue_profile.id)
        assert delete_result.success
        
        # Verify deletion
        get_result = venue_repository.get_by_id(sample_venue_profile.id)
        assert not get_result.success


class TestBookingRepository:
    """Tests for BookingRepository."""
    
    def test_create_and_retrieve_booking(self, booking_repository, sample_booking):
        """Test creating and retrieving a booking."""
        # Create booking
        create_result = booking_repository.create(sample_booking)
        assert create_result.success
        assert create_result.data.id == sample_booking.id
        
        # Retrieve booking
        get_result = booking_repository.get_by_id(sample_booking.id)
        assert get_result.success
        assert get_result.data.id == sample_booking.id
        assert get_result.data.artist_id == "artist-123"
        assert get_result.data.venue_id == "venue-456"
    
    def test_get_bookings_by_artist(self, booking_repository, sample_booking):
        """Test retrieving bookings by artist ID."""
        # Create booking
        booking_repository.create(sample_booking)
        
        # Get bookings by artist
        result = booking_repository.get_by_artist_id("artist-123")
        assert result.success
        assert len(result.data) == 1
        assert result.data[0].artist_id == "artist-123"
    
    def test_get_bookings_by_venue(self, booking_repository, sample_booking):
        """Test retrieving bookings by venue ID."""
        # Create booking
        booking_repository.create(sample_booking)
        
        # Get bookings by venue
        result = booking_repository.get_by_venue_id("venue-456")
        assert result.success
        assert len(result.data) == 1
        assert result.data[0].venue_id == "venue-456"
    
    def test_get_confirmed_bookings(self, booking_repository, sample_booking):
        """Test retrieving confirmed bookings."""
        # Create pending booking
        booking_repository.create(sample_booking)
        
        # Create confirmed booking
        confirmed_booking = Booking(
            artist_id="artist-789",
            venue_id="venue-789",
            period=DateRange(
                start_date=datetime(2024, 7, 1),
                end_date=datetime(2024, 7, 5)
            ),
            status=BookingStatus.CONFIRMED
        )
        booking_repository.create(confirmed_booking)
        
        # Get confirmed bookings
        result = booking_repository.get_confirmed_bookings()
        assert result.success
        assert len(result.data) == 1
        assert result.data[0].status == BookingStatus.CONFIRMED
    
    def test_update_booking(self, booking_repository, sample_booking):
        """Test updating a booking."""
        # Create booking
        booking_repository.create(sample_booking)
        
        # Update booking status
        sample_booking.status = BookingStatus.CONFIRMED
        sample_booking.confirmed_at = datetime.now()
        update_result = booking_repository.update(sample_booking)
        assert update_result.success
        
        # Verify update
        get_result = booking_repository.get_by_id(sample_booking.id)
        assert get_result.success
        assert get_result.data.status == BookingStatus.CONFIRMED
        assert get_result.data.confirmed_at is not None
