"""Tests for match result formatting."""

import pytest
from datetime import datetime, timedelta

from src.managers import (
    SearchEngine,
    ProfileManager,
    MatchEngine,
    AvailabilityManager
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


def test_venue_match_format_for_display_contains_required_fields(
    search_engine,
    profile_manager,
    availability_manager
):
    """
    Test that VenueMatch.format_for_display() contains all required fields.
    
    Requirement 4.4: Search results must present key information from venue profile
    (name, address, description, contact_email).
    """
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
    
    # Create a venue with complete information
    venue = VenueProfile(
        user_id="user2",
        basic_info=VenueBasicInfo(
            name="Grand Theater",
            address=Address(
                street="123 Main Street",
                city="Paris",
                region="Île-de-France",
                country="France",
                postal_code="75001",
                coordinates=Coordinates(latitude=48.8566, longitude=2.3522)
            ),
            description="A beautiful historic theater in the heart of Paris",
            contact_email="contact@grandtheater.fr",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Add availability
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue.id, availability)
    
    # Search for venues
    result = search_engine.search_venues_for_artist(artist.id)
    assert result.success
    assert len(result.data) == 1
    
    # Format the match for display
    formatted = result.data[0].format_for_display()
    
    # Verify all required fields are present (Requirement 4.4)
    assert 'name' in formatted
    assert 'address' in formatted
    assert 'description' in formatted
    assert 'contact_email' in formatted
    
    # Verify the values are correct
    assert formatted['name'] == "Grand Theater"
    assert "123 Main Street" in formatted['address']
    assert "Paris" in formatted['address']
    assert "Île-de-France" in formatted['address']
    assert "France" in formatted['address']
    assert "75001" in formatted['address']
    assert formatted['description'] == "A beautiful historic theater in the heart of Paris"
    assert formatted['contact_email'] == "contact@grandtheater.fr"
    
    # Verify additional match information is included
    assert 'compatibility_score' in formatted
    assert 'is_compatible' in formatted
    assert 'common_availabilities' in formatted
    assert formatted['compatibility_score'] == 1.0
    assert formatted['is_compatible'] is True
    assert len(formatted['common_availabilities']) > 0


def test_artist_match_format_for_display_contains_required_fields(
    search_engine,
    profile_manager,
    availability_manager
):
    """
    Test that ArtistMatch.format_for_display() contains all required fields.
    
    Requirement 3.4: Search results must present key information from artist profile
    (name, art_type, description, contact_email).
    """
    # Create a venue
    venue = VenueProfile(
        user_id="user1",
        basic_info=VenueBasicInfo(
            name="Art Gallery",
            address=Address(
                street="456 Oak Avenue",
                city="Lyon",
                region="Auvergne-Rhône-Alpes",
                country="France",
                postal_code="69001"
            ),
            description="Modern art gallery",
            contact_email="info@artgallery.fr",
            accepted_art_types=[ArtType.PAINTING, ArtType.SCULPTURE, ArtType.PHOTOGRAPHY]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=300, height=4, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create an artist with complete information
    artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Marie Dubois",
            art_type=ArtType.PAINTING,
            description="Contemporary painter specializing in abstract expressionism",
            contact_email="marie.dubois@artist.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Add availability
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=14)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(artist.id, availability)
    
    # Search for artists
    result = search_engine.search_artists_for_venue(venue.id)
    assert result.success
    assert len(result.data) == 1
    
    # Format the match for display
    formatted = result.data[0].format_for_display()
    
    # Verify all required fields are present (Requirement 3.4)
    assert 'name' in formatted
    assert 'art_type' in formatted
    assert 'description' in formatted
    assert 'contact_email' in formatted
    
    # Verify the values are correct
    assert formatted['name'] == "Marie Dubois"
    assert formatted['art_type'] == "painting"
    assert formatted['description'] == "Contemporary painter specializing in abstract expressionism"
    assert formatted['contact_email'] == "marie.dubois@artist.com"
    
    # Verify additional match information is included
    assert 'compatibility_score' in formatted
    assert 'is_compatible' in formatted
    assert 'common_availabilities' in formatted
    assert formatted['compatibility_score'] == 1.0
    assert formatted['is_compatible'] is True
    assert len(formatted['common_availabilities']) > 0


def test_venue_match_format_includes_common_availabilities(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that formatted venue match includes common availability periods."""
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
    
    # Add overlapping availability
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    availability_manager.add_availability(venue.id, availability)
    
    # Search and format
    result = search_engine.search_venues_for_artist(artist.id)
    formatted = result.data[0].format_for_display()
    
    # Verify common availabilities are formatted
    assert 'common_availabilities' in formatted
    assert len(formatted['common_availabilities']) > 0
    
    # Verify date format
    for avail in formatted['common_availabilities']:
        assert 'start_date' in avail
        assert 'end_date' in avail
        # Verify ISO format
        assert 'T' in avail['start_date'] or '-' in avail['start_date']
        assert 'T' in avail['end_date'] or '-' in avail['end_date']


def test_artist_match_format_includes_common_availabilities(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that formatted artist match includes common availability periods."""
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
            accepted_art_types=[ArtType.PERFORMANCE]
        ),
        technical_capabilities=TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=6, type="indoor")
        )
    )
    profile_manager.create_venue_profile(venue)
    
    # Create an artist
    artist = ArtistProfile(
        user_id="user2",
        basic_info=ArtistBasicInfo(
            name="Test Performer",
            art_type=ArtType.PERFORMANCE,
            description="A performance artist",
            contact_email="performer@test.com"
        ),
        technical_requirements=TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=80, min_height=4)
        )
    )
    profile_manager.create_artist_profile(artist)
    
    # Add overlapping availability
    now = datetime.now()
    availability = DateRange(
        start_date=now + timedelta(days=5),
        end_date=now + timedelta(days=12)
    )
    availability_manager.add_availability(venue.id, availability)
    availability_manager.add_availability(artist.id, availability)
    
    # Search and format
    result = search_engine.search_artists_for_venue(venue.id)
    formatted = result.data[0].format_for_display()
    
    # Verify common availabilities are formatted
    assert 'common_availabilities' in formatted
    assert len(formatted['common_availabilities']) > 0
    
    # Verify date format
    for avail in formatted['common_availabilities']:
        assert 'start_date' in avail
        assert 'end_date' in avail
        # Verify ISO format
        assert 'T' in avail['start_date'] or '-' in avail['start_date']
        assert 'T' in avail['end_date'] or '-' in avail['end_date']


def test_multiple_venue_matches_all_formatted_correctly(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that multiple venue matches can all be formatted correctly."""
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
    
    # Create multiple venues
    venues = []
    for i in range(3):
        venue = VenueProfile(
            user_id=f"user{i+2}",
            basic_info=VenueBasicInfo(
                name=f"Venue {i+1}",
                address=Address(
                    street=f"{i+1}00 Street {i+1}",
                    city=f"City {i+1}",
                    region=f"Region {i+1}",
                    country="France",
                    postal_code=f"7500{i+1}"
                ),
                description=f"Description for venue {i+1}",
                contact_email=f"venue{i+1}@test.com",
                accepted_art_types=[ArtType.MUSIC]
            ),
            technical_capabilities=TechnicalCapabilities(
                space_capabilities=SpaceCapabilities(area=100 + i*50, height=5, type="indoor")
            )
        )
        profile_manager.create_venue_profile(venue)
        venues.append(venue)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(artist.id, availability)
    for venue in venues:
        availability_manager.add_availability(venue.id, availability)
    
    # Search and format all results
    result = search_engine.search_venues_for_artist(artist.id)
    assert result.success
    assert len(result.data) == 3
    
    # Verify all matches can be formatted
    for i, match in enumerate(result.data):
        formatted = match.format_for_display()
        
        # Verify required fields are present
        assert 'name' in formatted
        assert 'address' in formatted
        assert 'description' in formatted
        assert 'contact_email' in formatted
        
        # Verify each venue has unique information
        assert formatted['name'] in [f"Venue {j+1}" for j in range(3)]
        assert formatted['contact_email'] in [f"venue{j+1}@test.com" for j in range(3)]


def test_multiple_artist_matches_all_formatted_correctly(
    search_engine,
    profile_manager,
    availability_manager
):
    """Test that multiple artist matches can all be formatted correctly."""
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
    
    # Create multiple artists
    art_types = [ArtType.MUSIC, ArtType.PERFORMANCE, ArtType.PAINTING]
    artists = []
    for i, art_type in enumerate(art_types):
        artist = ArtistProfile(
            user_id=f"user{i+2}",
            basic_info=ArtistBasicInfo(
                name=f"Artist {i+1}",
                art_type=art_type,
                description=f"Description for artist {i+1}",
                contact_email=f"artist{i+1}@test.com"
            ),
            technical_requirements=TechnicalRequirements(
                space_requirements=SpaceRequirements(min_area=50 + i*20, min_height=3)
            )
        )
        profile_manager.create_artist_profile(artist)
        artists.append(artist)
    
    # Add availability for all
    now = datetime.now()
    availability = DateRange(
        start_date=now,
        end_date=now + timedelta(days=7)
    )
    availability_manager.add_availability(venue.id, availability)
    for artist in artists:
        availability_manager.add_availability(artist.id, availability)
    
    # Search and format all results
    result = search_engine.search_artists_for_venue(venue.id)
    assert result.success
    assert len(result.data) == 3
    
    # Verify all matches can be formatted
    for i, match in enumerate(result.data):
        formatted = match.format_for_display()
        
        # Verify required fields are present
        assert 'name' in formatted
        assert 'art_type' in formatted
        assert 'description' in formatted
        assert 'contact_email' in formatted
        
        # Verify each artist has unique information
        assert formatted['name'] in [f"Artist {j+1}" for j in range(3)]
        assert formatted['art_type'] in ["music", "performance", "painting"]
        assert formatted['contact_email'] in [f"artist{j+1}@test.com" for j in range(3)]
