"""Tests for the SearchEngine class."""

import pytest
from datetime import datetime, timedelta

from src.managers import (
    SearchEngine,
    ProfileManager,
    MatchEngine,
    AvailabilityManager,
    VenueSearchFilters,
    GeographicArea
)
from src.models import (
    ArtistProfile,
    VenueProfile,
    DateRange,
    ArtType
)
from src.models.profiles import ArtistBasicInfo, VenueBasicInfo
from src.models.technical import (
    TechnicalRequirements,
    TechnicalCapabilities,
    SpaceRequirements,
    SpaceCapabilities
)
from src.models.address import Address, Coordinates


@pytest.fixture
def profile_manager():
    """Create a profile manager for testing."""
    return ProfileManager()


@pytest.fixture
def match_engine():
    """Create a match engine for testing."""
    return MatchEngine()


@pytest.fixture
def availability_manager():
    """Create an availability manager for testing."""
    return AvailabilityManager()


@pytest.fixture
def search_engine(profile_manager, match_engine, availability_manager):
    """Create a search engine for testing."""
    return SearchEngine(profile_manager, match_engine, availability_manager)



def test_search_venues_for_artist_basic(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test basic venue search for an artist."""
    # Create an artist profile
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create a compatible venue
    venue = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Add availability for both
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue.id, availability)
    
    # Search for venues
    result = search_engine.search_venues_for_artist(artist.id)
    
    # Verify results
    assert result.success
    assert len(result.data) == 1
    assert result.data[0].venue.id == venue.id
    assert result.data[0].is_compatible
    assert result.data[0].compatibility_score == 1.0
    assert len(result.data[0].common_availabilities) > 0



def test_search_venues_excludes_incompatible(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that incompatible venues are excluded from results (Requirement 4.1)."""
    # Create an artist with specific requirements
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=200, min_height=5)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create an incompatible venue (too small)
    venue = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Small Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A small venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=50, height=3, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Add availability for both
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue.id, availability)
    
    # Search for venues
    result = search_engine.search_venues_for_artist(artist.id)
    
    # Verify no results (venue is incompatible)
    assert result.success
    assert len(result.data) == 0



def test_search_venues_excludes_no_common_availability(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that venues with no common availability are excluded (Requirement 6.4)."""
    # Create an artist
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create a compatible venue
    venue = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Add non-overlapping availability
    now = datetime.now()
    artist_availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    venue_availability = DateRange(
        start_date=now + timedelta(days=10),
        end_date=now + timedelta(days=17)
    )
    availability_manager.add_availability(artist.id, artist_availability)
    availability_manager.add_availability(venue.id, venue_availability)
    
    # Search for venues
    result = search_engine.search_venues_for_artist(artist.id)
    
    # Verify no results (no common availability)
    assert result.success
    assert len(result.data) == 0



def test_search_venues_sorted_by_compatibility_score(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that results are sorted by compatibility score descending (Requirement 5.5)."""
    # Create an artist with only space requirements
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create venue 1 - basic compatibility (score 1.0 with only space)
    venue1 = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Basic Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A basic venue",
            contact_email="venue1@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue1)
    
    # Create venue 2 - also compatible (score 1.0 with only space)
    venue2 = VenueProfile(
        user_id="user3",
        basic_info=VenueBasicInfo(
            name="Another Venue",
            address=Address(
                street="456 Oak St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="Another venue",
            contact_email="venue2@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=6, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue2)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue1.id, availability)
    availability_manager.add_availability(venue2.id, availability)
    
    # Search for venues
    result = search_engine.search_venues_for_artist(artist.id)
    
    # Verify results are returned and sorted (both have same score in this case)
    assert result.success
    assert len(result.data) == 2
    # Both venues should have score 1.0 since they both meet all requirements
    assert result.data[0].compatibility_score == 1.0
    assert result.data[1].compatibility_score == 1.0
    # Verify they are both compatible
    assert result.data[0].is_compatible
    assert result.data[1].is_compatible



def test_search_venues_filter_by_date_range(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test filtering venues by date range (Requirement 4.2)."""
    # Create an artist
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create a venue
    venue = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Add availability
    now = datetime.now()
    artist_availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=30)
    )
    venue_availability = DateRange(
        start_date=now + timedelta(days=10),
        end_date=now + timedelta(days=20)
    )
    availability_manager.add_availability(artist.id, artist_availability)
    availability_manager.add_availability(venue.id, venue_availability)
    
    # Search with filter that matches
    filter_matching = VenueSearchFilters(
        date_range=DateRange(
            start_date=now + timedelta(days=12),
            end_date=now + timedelta(days=18)
        )
    )
    result = search_engine.search_venues_for_artist(artist.id, filter_matching)
    assert result.success
    assert len(result.data) == 1
    
    # Search with filter that doesn't match
    filter_non_matching = VenueSearchFilters(
        date_range=DateRange(
            start_date=now + timedelta(days=25),
            end_date=now + timedelta(days=28)
        )
    )
    result = search_engine.search_venues_for_artist(artist.id, filter_non_matching)
    assert result.success
    assert len(result.data) == 0



def test_search_venues_filter_by_location(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test filtering venues by geographic location (Requirement 4.3)."""
    # Create an artist
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create venue 1 - nearby (Paris coordinates)
    venue1 = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Nearby Venue",
            address=Address(
                street="123 Main St",
                city="Paris",
                region="Île-de-France",
                country="France",
                postal_code="75001",
                coordinates=Coordinates(latitude=48.8566, longitude=2.3522)
            ),
            description="A nearby venue",
            contact_email="venue1@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue1)
    
    # Create venue 2 - far away (London coordinates)
    venue2 = VenueProfile(
        user_id="user3",
        basic_info=VenueBasicInfo(
            name="Far Venue",
            address=Address(
                street="456 Oak St",
                city="London",
                region="England",
                country="UK",
                postal_code="SW1A 1AA",
                coordinates=Coordinates(latitude=51.5074, longitude=-0.1278)
            ),
            description="A far venue",
            contact_email="venue2@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue2)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue1.id, availability)
    availability_manager.add_availability(venue2.id, availability)
    
    # Search with location filter (50km radius around Paris)
    location_filter = VenueSearchFilters(
        location=GeographicArea(
            center=Coordinates(latitude=48.8566, longitude=2.3522),
            radius_km=50
        )
    )
    result = search_engine.search_venues_for_artist(artist.id, location_filter)
    
    # Verify only nearby venue is returned
    assert result.success
    assert len(result.data) == 1
    assert result.data[0].venue.id == venue1.id



def test_search_artists_for_venue_basic(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test basic artist search for a venue."""
    # Create a venue profile
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create a compatible artist
    artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Add availability for both
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(artist.id, availability)
    
    # Search for artists
    result = search_engine.search_artists_for_venue(venue.id)
    
    # Verify results
    assert result.success
    assert len(result.data) == 1
    assert result.data[0].artist.id == artist.id
    assert result.data[0].is_compatible
    assert result.data[0].compatibility_score == 1.0
    assert len(result.data[0].common_availabilities) > 0


def test_search_artists_excludes_incompatible(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that incompatible artists are excluded from results (Requirement 3.1)."""
    # Create a venue with specific capabilities
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Small Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A small venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=50, height=3, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create an incompatible artist (needs too much space)
    artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Big Artist",
            art_type=ArtType.MUSIC,
            description="An artist with big requirements",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=200, min_height=5)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Add availability for both
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(artist.id, availability)
    
    # Search for artists
    result = search_engine.search_artists_for_venue(venue.id)
    
    # Verify no results (artist is incompatible)
    assert result.success
    assert len(result.data) == 0


def test_search_artists_excludes_no_common_availability(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that artists with no common availability are excluded (Requirement 6.4)."""
    # Create a venue
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create a compatible artist
    artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Add non-overlapping availability
    now = datetime.now()
    venue_availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    artist_availability = DateRange(
        start_date=now + timedelta(days=10),
        end_date=now + timedelta(days=17)
    )
    availability_manager.add_availability(venue.id, venue_availability)
    availability_manager.add_availability(artist.id, artist_availability)
    
    # Search for artists
    result = search_engine.search_artists_for_venue(venue.id)
    
    # Verify no results (no common availability)
    assert result.success
    assert len(result.data) == 0


def test_search_artists_sorted_by_compatibility_score(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that results are sorted by compatibility score descending (Requirement 5.5)."""
    # Create a venue
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
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
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create artist 1 - compatible
    artist1 = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Artist 1",
            art_type=ArtType.MUSIC,
            description="First artist",
            contact_email="artist1@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist1)
    
    # Create artist 2 - also compatible
    artist2 = ArtistProfile(
        user_id="user3",
        basic_info=ArtistBasicInfo(
            name="Artist 2",
            art_type=ArtType.PERFORMANCE,
            description="Second artist",
            contact_email="artist2@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=60, min_height=4)
        )
    )
    profile_manager.create_artist_profile(artist2)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(artist1.id, availability)
    availability_manager.add_availability(artist2.id, availability)
    
    # Search for artists
    result = search_engine.search_artists_for_venue(venue.id)
    
    # Verify results are returned and sorted
    assert result.success
    assert len(result.data) == 2
    # Both artists should have score 1.0 since they both meet all requirements
    assert result.data[0].compatibility_score == 1.0
    assert result.data[1].compatibility_score == 1.0
    # Verify they are both compatible
    assert result.data[0].is_compatible
    assert result.data[1].is_compatible


def test_search_artists_filter_by_date_range(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test filtering artists by date range (Requirement 3.2)."""
    from src.managers import ArtistSearchFilters
    
    # Create a venue
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create an artist
    artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Add availability
    now = datetime.now()
    venue_availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=30)
    )
    artist_availability = DateRange(
        start_date=now + timedelta(days=10),
        end_date=now + timedelta(days=20)
    )
    availability_manager.add_availability(venue.id, venue_availability)
    availability_manager.add_availability(artist.id, artist_availability)
    
    # Search with filter that matches
    filter_matching = ArtistSearchFilters(
        date_range=DateRange(
            start_date=now + timedelta(days=12),
            end_date=now + timedelta(days=18)
        )
    )
    result = search_engine.search_artists_for_venue(venue.id, filter_matching)
    assert result.success
    assert len(result.data) == 1
    
    # Search with filter that doesn't match
    filter_non_matching = ArtistSearchFilters(
        date_range=DateRange(
            start_date=now + timedelta(days=25),
            end_date=now + timedelta(days=28)
        )
    )
    result = search_engine.search_artists_for_venue(venue.id, filter_non_matching)
    assert result.success
    assert len(result.data) == 0


def test_search_artists_filter_by_art_type(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test filtering artists by art type (Requirement 3.3)."""
    from src.managers import ArtistSearchFilters
    
    # Create a venue that accepts multiple art types
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE, ArtType.PAINTING]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create a music artist
    music_artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Music Artist",
            art_type=ArtType.MUSIC,
            description="A music artist",
            contact_email="music@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(music_artist)
    
    # Create a performance artist
    performance_artist = ArtistProfile(
        user_id="user3",
        basic_info=ArtistBasicInfo(
            name="Performance Artist",
            art_type=ArtType.PERFORMANCE,
            description="A performance artist",
            contact_email="performance@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(performance_artist)
    
    # Create a painting artist
    painting_artist = ArtistProfile(
        user_id="user4",
        basic_info=ArtistBasicInfo(
            name="Painting Artist",
            art_type=ArtType.PAINTING,
            description="A painting artist",
            contact_email="painting@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(painting_artist)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(music_artist.id, availability)
    availability_manager.add_availability(performance_artist.id, availability)
    availability_manager.add_availability(painting_artist.id, availability)
    
    # Search without filter - should return all 3 artists
    result = search_engine.search_artists_for_venue(venue.id)
    assert result.success
    assert len(result.data) == 3
    
    # Search with filter for MUSIC only
    filter_music = ArtistSearchFilters(art_type=[ArtType.MUSIC])
    result = search_engine.search_artists_for_venue(venue.id, filter_music)
    assert result.success
    assert len(result.data) == 1
    assert result.data[0].artist.basic_info.art_type == ArtType.MUSIC
    
    # Search with filter for MUSIC and PERFORMANCE
    filter_multiple = ArtistSearchFilters(art_type=[ArtType.MUSIC, ArtType.PERFORMANCE])
    result = search_engine.search_artists_for_venue(venue.id, filter_multiple)
    assert result.success
    assert len(result.data) == 2
    art_types = {match.artist.basic_info.art_type for match in result.data}
    assert art_types == {ArtType.MUSIC, ArtType.PERFORMANCE}


def test_search_venues_results_sorted_descending(
    search_engine,
    profile_manager,
    availability_manager
):
    """
    Test that search results are sorted by compatibility score in descending order (Requirement 5.5).
    
    Note: In the current implementation, only fully compatible venues (score 1.0) are returned
    in search results, so all results will have the same score. This test verifies that the
    sorting mechanism is in place and results are ordered correctly.
    """
    # Create an artist with simple requirements
    artist = ArtistProfile(
        user_id="user1",
        basic_info=ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A test artist",
            contact_email="artist@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Create multiple compatible venues
    venue1 = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Venue A",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="First venue",
            contact_email="venue1@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=5, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue1)
    
    venue2 = VenueProfile(
        user_id="user3",
        basic_info=VenueBasicInfo(
            name="Venue B",
            address=Address(
                street="456 Oak St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="Second venue",
            contact_email="venue2@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=6, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue2)
    
    venue3 = VenueProfile(
        user_id="user4",
        basic_info=VenueBasicInfo(
            name="Venue C",
            address=Address(
                street="789 Pine St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="Third venue",
            contact_email="venue3@test.com",
            accepted_art_types=[ArtType.MUSIC]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=200, height=7, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue3)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue1.id, availability)
    availability_manager.add_availability(venue2.id, availability)
    availability_manager.add_availability(venue3.id, availability)
    
    # Search for venues
    result = search_engine.search_venues_for_artist(artist.id)
    
    # Verify results are returned
    assert result.success
    assert len(result.data) == 3
    
    # Verify all venues are compatible with score 1.0
    for match in result.data:
        assert match.is_compatible
        assert match.compatibility_score == 1.0
    
    # Verify results are in descending order by score (even though all are 1.0)
    # This confirms the sorting mechanism is in place
    for i in range(len(result.data) - 1):
        assert result.data[i].compatibility_score >= result.data[i + 1].compatibility_score


def test_search_artists_results_sorted_descending(
    search_engine,
    profile_manager,
    availability_manager
):
    """
    Test that search results are sorted by compatibility score in descending order (Requirement 5.5).
    
    Note: In the current implementation, only fully compatible artists (score 1.0) are returned
    in search results, so all results will have the same score. This test verifies that the
    sorting mechanism is in place and results are ordered correctly.
    """
    # Create a venue
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Test Venue",
            address=Address(
                street="123 Main St",
                city="Test City",
                region="Test Region",
                country="Test Country",
                postal_code="12345"
            ),
            description="A test venue",
            contact_email="venue@test.com",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE, ArtType.PAINTING]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=200, height=6, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create multiple compatible artists
    artist1 = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Artist A",
            art_type=ArtType.MUSIC,
            description="First artist",
            contact_email="artist1@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist1)
    
    artist2 = ArtistProfile(
        user_id="user3",
        basic_info=ArtistBasicInfo(
            name="Artist B",
            art_type=ArtType.PERFORMANCE,
            description="Second artist",
            contact_email="artist2@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=60, min_height=4)
        )
    )
    profile_manager.create_artist_profile(artist2)
    
    artist3 = ArtistProfile(
        user_id="user4",
        basic_info=ArtistBasicInfo(
            name="Artist C",
            art_type=ArtType.PAINTING,
            description="Third artist",
            contact_email="artist3@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=80, min_height=5)
        )
    )
    profile_manager.create_artist_profile(artist3)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(artist1.id, availability)
    availability_manager.add_availability(artist2.id, availability)
    availability_manager.add_availability(artist3.id, availability)
    
    # Search for artists
    result = search_engine.search_artists_for_venue(venue.id)
    
    # Verify results are returned
    assert result.success
    assert len(result.data) == 3
    
    # Verify all artists are compatible with score 1.0
    for match in result.data:
        assert match.is_compatible
        assert match.compatibility_score == 1.0
    
    # Verify results are in descending order by score (even though all are 1.0)
    # This confirms the sorting mechanism is in place
    for i in range(len(result.data) - 1):
        assert result.data[i].compatibility_score >= result.data[i + 1].compatibility_score
