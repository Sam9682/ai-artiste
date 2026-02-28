"""Unit tests for ProfileManager."""

import pytest
from datetime import datetime

from src.managers import ProfileManager
from src.models import (
    ArtistProfile,
    VenueProfile,
    ArtType,
    ErrorCode,
    TechnicalRequirements,
    TechnicalCapabilities
)
from src.models.profiles import ArtistBasicInfo, VenueBasicInfo
from src.models.technical import SpaceRequirements, SpaceCapabilities
from src.models.address import Address


class TestProfileManagerArtist:
    """Tests for artist profile management."""
    
    def test_create_and_retrieve_artist_profile(self):
        """Test creating and retrieving a valid artist profile."""
        manager = ProfileManager()
        
        # Create a valid artist profile
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        space_req = SpaceRequirements(min_area=50, min_height=3, indoor_outdoor="indoor")
        tech_req = TechnicalRequirements(space_requirements=space_req)
        
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=tech_req,
            user_id="user123"
        )
        
        # Create the profile
        result = manager.create_artist_profile(profile)
        assert result.success is True
        assert result.data.id == profile.id
        assert result.data.basic_info.name == "Test Artist"
        
        # Retrieve the profile
        retrieved = manager.get_artist_profile(profile.id)
        assert retrieved.success is True
        assert retrieved.data.id == profile.id
        assert retrieved.data.basic_info.name == "Test Artist"
        assert retrieved.data.basic_info.art_type == ArtType.MUSIC
        assert retrieved.data.user_id == "user123"
    
    def test_get_nonexistent_artist_profile(self):
        """Test retrieving a profile that doesn't exist."""
        manager = ProfileManager()
        
        result = manager.get_artist_profile("nonexistent-id")
        assert result.success is False
        assert result.error.code == ErrorCode.NOT_FOUND
        assert "not found" in result.error.message.lower()
    
    def test_create_artist_profile_missing_name(self):
        """Test creating an artist profile with missing name."""
        manager = ProfileManager()
        
        artist_info = ArtistBasicInfo(
            name="",  # Empty name
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=TechnicalRequirements(),
            user_id="user123"
        )
        
        result = manager.create_artist_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "basic_info.name"
    
    def test_create_artist_profile_missing_description(self):
        """Test creating an artist profile with missing description."""
        manager = ProfileManager()
        
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="",  # Empty description
            contact_email="artist@example.com"
        )
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=TechnicalRequirements(),
            user_id="user123"
        )
        
        result = manager.create_artist_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "basic_info.description"
    
    def test_create_artist_profile_missing_email(self):
        """Test creating an artist profile with missing email."""
        manager = ProfileManager()
        
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email=""  # Empty email
        )
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=TechnicalRequirements(),
            user_id="user123"
        )
        
        result = manager.create_artist_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "basic_info.contact_email"
    
    def test_create_artist_profile_invalid_email(self):
        """Test creating an artist profile with invalid email format."""
        manager = ProfileManager()
        
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="not-an-email"  # Invalid format
        )
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=TechnicalRequirements(),
            user_id="user123"
        )
        
        result = manager.create_artist_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.INVALID_FORMAT
        assert result.error.field == "basic_info.contact_email"
    
    def test_create_artist_profile_missing_user_id(self):
        """Test creating an artist profile with missing user_id."""
        manager = ProfileManager()
        
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=TechnicalRequirements(),
            user_id=""  # Empty user_id
        )
        
        result = manager.create_artist_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "user_id"
    
    def test_update_artist_profile_basic_info(self):
        """Test updating an artist profile's basic info."""
        manager = ProfileManager()
        
        # Create initial profile
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        space_req = SpaceRequirements(min_area=50, min_height=3, indoor_outdoor="indoor")
        tech_req = TechnicalRequirements(space_requirements=space_req)
        
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=tech_req,
            user_id="user123"
        )
        
        create_result = manager.create_artist_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Update the profile
        updated_info = ArtistBasicInfo(
            name="Updated Artist Name",
            art_type=ArtType.PERFORMANCE,
            description="An amazing performer",
            contact_email="updated@example.com"
        )
        
        update_result = manager.update_artist_profile(
            profile_id=profile_id,
            basic_info=updated_info
        )
        
        assert update_result.success is True
        assert update_result.data.basic_info.name == "Updated Artist Name"
        assert update_result.data.basic_info.art_type == ArtType.PERFORMANCE
        assert update_result.data.basic_info.description == "An amazing performer"
        assert update_result.data.basic_info.contact_email == "updated@example.com"
        assert update_result.data.updated_at > create_result.data.created_at
    
    def test_update_artist_profile_technical_requirements(self):
        """Test updating an artist profile's technical requirements."""
        manager = ProfileManager()
        
        # Create initial profile
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        space_req = SpaceRequirements(min_area=50, min_height=3, indoor_outdoor="indoor")
        tech_req = TechnicalRequirements(space_requirements=space_req)
        
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=tech_req,
            user_id="user123"
        )
        
        create_result = manager.create_artist_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Update technical requirements
        new_space_req = SpaceRequirements(min_area=100, min_height=5, indoor_outdoor="outdoor")
        new_tech_req = TechnicalRequirements(space_requirements=new_space_req)
        
        update_result = manager.update_artist_profile(
            profile_id=profile_id,
            technical_requirements=new_tech_req
        )
        
        assert update_result.success is True
        assert update_result.data.technical_requirements.space_requirements.min_area == 100
        assert update_result.data.technical_requirements.space_requirements.min_height == 5
        assert update_result.data.technical_requirements.space_requirements.indoor_outdoor == "outdoor"
    
    def test_update_nonexistent_artist_profile(self):
        """Test updating a profile that doesn't exist."""
        manager = ProfileManager()
        
        updated_info = ArtistBasicInfo(
            name="Updated Artist",
            art_type=ArtType.MUSIC,
            description="Description",
            contact_email="test@example.com"
        )
        
        result = manager.update_artist_profile(
            profile_id="nonexistent-id",
            basic_info=updated_info
        )
        
        assert result.success is False
        assert result.error.code == ErrorCode.NOT_FOUND
    
    def test_update_artist_profile_with_invalid_data(self):
        """Test updating an artist profile with invalid data."""
        manager = ProfileManager()
        
        # Create initial profile
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=TechnicalRequirements(),
            user_id="user123"
        )
        
        create_result = manager.create_artist_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Try to update with invalid data (empty name)
        invalid_info = ArtistBasicInfo(
            name="",  # Invalid empty name
            art_type=ArtType.MUSIC,
            description="Description",
            contact_email="test@example.com"
        )
        
        update_result = manager.update_artist_profile(
            profile_id=profile_id,
            basic_info=invalid_info
        )
        
        assert update_result.success is False
        assert update_result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert update_result.error.field == "basic_info.name"
    
    def test_update_artist_profile_partial_update(self):
        """Test that partial updates preserve unchanged fields."""
        manager = ProfileManager()
        
        # Create initial profile
        artist_info = ArtistBasicInfo(
            name="Test Artist",
            art_type=ArtType.MUSIC,
            description="A talented musician",
            contact_email="artist@example.com"
        )
        space_req = SpaceRequirements(min_area=50, min_height=3, indoor_outdoor="indoor")
        tech_req = TechnicalRequirements(space_requirements=space_req)
        
        profile = ArtistProfile(
            basic_info=artist_info,
            technical_requirements=tech_req,
            user_id="user123"
        )
        
        create_result = manager.create_artist_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        original_tech_req = create_result.data.technical_requirements
        
        # Update only basic info, technical requirements should remain unchanged
        updated_info = ArtistBasicInfo(
            name="Updated Name",
            art_type=ArtType.PERFORMANCE,
            description="Updated description",
            contact_email="updated@example.com"
        )
        
        update_result = manager.update_artist_profile(
            profile_id=profile_id,
            basic_info=updated_info
        )
        
        assert update_result.success is True
        assert update_result.data.basic_info.name == "Updated Name"
        # Technical requirements should be unchanged
        assert update_result.data.technical_requirements.space_requirements.min_area == 50
        assert update_result.data.technical_requirements.space_requirements.min_height == 3


class TestProfileManagerVenue:
    """Tests for venue profile management."""
    
    def test_create_and_retrieve_venue_profile(self):
        """Test creating and retrieving a valid venue profile."""
        manager = ProfileManager()
        
        # Create a valid venue profile
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE]
        )
        space_cap = SpaceCapabilities(area=200, height=8, type="indoor")
        tech_cap = TechnicalCapabilities(space_capabilities=space_cap)
        
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=tech_cap,
            user_id="user456"
        )
        
        # Create the profile
        result = manager.create_venue_profile(profile)
        assert result.success is True
        assert result.data.id == profile.id
        assert result.data.basic_info.name == "Test Venue"
        
        # Retrieve the profile
        retrieved = manager.get_venue_profile(profile.id)
        assert retrieved.success is True
        assert retrieved.data.id == profile.id
        assert retrieved.data.basic_info.name == "Test Venue"
        assert retrieved.data.basic_info.address.city == "Montreal"
        assert retrieved.data.user_id == "user456"
    
    def test_get_nonexistent_venue_profile(self):
        """Test retrieving a venue profile that doesn't exist."""
        manager = ProfileManager()
        
        result = manager.get_venue_profile("nonexistent-id")
        assert result.success is False
        assert result.error.code == ErrorCode.NOT_FOUND
        assert "not found" in result.error.message.lower()
    
    def test_create_venue_profile_missing_name(self):
        """Test creating a venue profile with missing name."""
        manager = ProfileManager()
        
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="",  # Empty name
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=TechnicalCapabilities(
                space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
            ),
            user_id="user456"
        )
        
        result = manager.create_venue_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "basic_info.name"
    
    def test_create_venue_profile_missing_description(self):
        """Test creating a venue profile with missing description."""
        manager = ProfileManager()
        
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="",  # Empty description
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=TechnicalCapabilities(
                space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
            ),
            user_id="user456"
        )
        
        result = manager.create_venue_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "basic_info.description"
    
    def test_create_venue_profile_invalid_email(self):
        """Test creating a venue profile with invalid email format."""
        manager = ProfileManager()
        
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="not-an-email",  # Invalid format
            accepted_art_types=[ArtType.MUSIC]
        )
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=TechnicalCapabilities(
                space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
            ),
            user_id="user456"
        )
        
        result = manager.create_venue_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.INVALID_FORMAT
        assert result.error.field == "basic_info.contact_email"
    
    def test_create_venue_profile_missing_accepted_art_types(self):
        """Test creating a venue profile with missing accepted art types."""
        manager = ProfileManager()
        
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[]  # Empty list
        )
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=TechnicalCapabilities(
                space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
            ),
            user_id="user456"
        )
        
        result = manager.create_venue_profile(profile)
        assert result.success is False
        assert result.error.code == ErrorCode.MISSING_REQUIRED_FIELD
        assert result.error.field == "basic_info.accepted_art_types"
    
    def test_update_venue_profile_basic_info(self):
        """Test updating a venue profile's basic info."""
        manager = ProfileManager()
        
        # Create initial profile
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        space_cap = SpaceCapabilities(area=200, height=8, type="indoor")
        tech_cap = TechnicalCapabilities(space_capabilities=space_cap)
        
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=tech_cap,
            user_id="user456"
        )
        
        create_result = manager.create_venue_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Update the profile
        new_address = Address(
            street="456 New St",
            city="Toronto",
            region="Ontario",
            country="Canada",
            postal_code="M1M 1M1"
        )
        updated_info = VenueBasicInfo(
            name="Updated Venue Name",
            address=new_address,
            description="An updated performance space",
            contact_email="updated@venue.com",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE]
        )
        
        update_result = manager.update_venue_profile(
            profile_id=profile_id,
            basic_info=updated_info
        )
        
        assert update_result.success is True
        assert update_result.data.basic_info.name == "Updated Venue Name"
        assert update_result.data.basic_info.address.city == "Toronto"
        assert update_result.data.basic_info.description == "An updated performance space"
        assert update_result.data.basic_info.contact_email == "updated@venue.com"
        assert ArtType.PERFORMANCE in update_result.data.basic_info.accepted_art_types
        assert update_result.data.updated_at > create_result.data.created_at
    
    def test_update_venue_profile_technical_capabilities(self):
        """Test updating a venue profile's technical capabilities."""
        manager = ProfileManager()
        
        # Create initial profile
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        space_cap = SpaceCapabilities(area=200, height=8, type="indoor")
        tech_cap = TechnicalCapabilities(space_capabilities=space_cap)
        
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=tech_cap,
            user_id="user456"
        )
        
        create_result = manager.create_venue_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Update technical capabilities
        new_space_cap = SpaceCapabilities(area=500, height=12, type="both")
        new_tech_cap = TechnicalCapabilities(space_capabilities=new_space_cap)
        
        update_result = manager.update_venue_profile(
            profile_id=profile_id,
            technical_capabilities=new_tech_cap
        )
        
        assert update_result.success is True
        assert update_result.data.technical_capabilities.space_capabilities.area == 500
        assert update_result.data.technical_capabilities.space_capabilities.height == 12
        assert update_result.data.technical_capabilities.space_capabilities.type == "both"
    
    def test_update_nonexistent_venue_profile(self):
        """Test updating a venue profile that doesn't exist."""
        manager = ProfileManager()
        
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        updated_info = VenueBasicInfo(
            name="Updated Venue",
            address=address,
            description="Description",
            contact_email="test@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        
        result = manager.update_venue_profile(
            profile_id="nonexistent-id",
            basic_info=updated_info
        )
        
        assert result.success is False
        assert result.error.code == ErrorCode.NOT_FOUND
    
    def test_update_venue_profile_with_invalid_data(self):
        """Test updating a venue profile with invalid data."""
        manager = ProfileManager()
        
        # Create initial profile
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=TechnicalCapabilities(
                space_capabilities=SpaceCapabilities(area=200, height=8, type="indoor")
            ),
            user_id="user456"
        )
        
        create_result = manager.create_venue_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Try to update with invalid data (invalid email)
        invalid_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="Description",
            contact_email="not-an-email",  # Invalid email
            accepted_art_types=[ArtType.MUSIC]
        )
        
        update_result = manager.update_venue_profile(
            profile_id=profile_id,
            basic_info=invalid_info
        )
        
        assert update_result.success is False
        assert update_result.error.code == ErrorCode.INVALID_FORMAT
        assert update_result.error.field == "basic_info.contact_email"
    
    def test_update_venue_profile_partial_update(self):
        """Test that partial updates preserve unchanged fields."""
        manager = ProfileManager()
        
        # Create initial profile
        address = Address(
            street="123 Main St",
            city="Montreal",
            region="Quebec",
            country="Canada",
            postal_code="H1A 1A1"
        )
        venue_info = VenueBasicInfo(
            name="Test Venue",
            address=address,
            description="A great performance space",
            contact_email="venue@example.com",
            accepted_art_types=[ArtType.MUSIC]
        )
        space_cap = SpaceCapabilities(area=200, height=8, type="indoor")
        tech_cap = TechnicalCapabilities(space_capabilities=space_cap)
        
        profile = VenueProfile(
            basic_info=venue_info,
            technical_capabilities=tech_cap,
            user_id="user456"
        )
        
        create_result = manager.create_venue_profile(profile)
        assert create_result.success is True
        profile_id = create_result.data.id
        
        # Update only basic info, technical capabilities should remain unchanged
        new_address = Address(
            street="456 New St",
            city="Toronto",
            region="Ontario",
            country="Canada",
            postal_code="M1M 1M1"
        )
        updated_info = VenueBasicInfo(
            name="Updated Venue",
            address=new_address,
            description="Updated description",
            contact_email="updated@venue.com",
            accepted_art_types=[ArtType.MUSIC, ArtType.PERFORMANCE]
        )
        
        update_result = manager.update_venue_profile(
            profile_id=profile_id,
            basic_info=updated_info
        )
        
        assert update_result.success is True
        assert update_result.data.basic_info.name == "Updated Venue"
        assert update_result.data.basic_info.address.city == "Toronto"
        # Technical capabilities should be unchanged
        assert update_result.data.technical_capabilities.space_capabilities.area == 200
        assert update_result.data.technical_capabilities.space_capabilities.height == 8
        assert update_result.data.technical_capabilities.space_capabilities.type == "indoor"
