"""Profile manager for creating and managing artist and venue profiles."""

from typing import Optional
from datetime import datetime
from dataclasses import replace
from src.models import (
    ArtistProfile,
    VenueProfile,
    Result,
    ErrorDetails,
    ErrorCode
)
from src.models.profiles import ArtistBasicInfo, VenueBasicInfo


class ProfileManager:
    """Manages artist and venue profiles with validation."""
    
    def __init__(self, artist_repository=None, venue_repository=None):
        """
        Initialize the profile manager with repositories.
        
        Args:
            artist_repository: Repository for artist profile persistence (optional)
            venue_repository: Repository for venue profile persistence (optional)
        """
        self.artist_repository = artist_repository
        self.venue_repository = venue_repository
    
    def create_artist_profile(self, profile: ArtistProfile) -> Result[ArtistProfile]:
        """
        Create a new artist profile.
        
        Args:
            profile: The artist profile to create
            
        Returns:
            Result containing the created profile or error details
        """
        # Validate required fields
        validation_result = self._validate_artist_profile(profile)
        if not validation_result.success:
            return validation_result
        
        # Store the profile using repository if available
        if self.artist_repository:
            return self.artist_repository.create(profile)
        
        # Fallback to in-memory storage for backward compatibility
        if not hasattr(self, '_artist_profiles'):
            self._artist_profiles = {}
        self._artist_profiles[profile.id] = profile
        return Result.ok(profile)
    
    def get_artist_profile(self, profile_id: str) -> Result[ArtistProfile]:
        """
        Retrieve an artist profile by ID.
        
        Args:
            profile_id: The ID of the profile to retrieve
            
        Returns:
            Result containing the profile or error details
        """
        # Use repository if available
        if self.artist_repository:
            return self.artist_repository.get_by_id(profile_id)
        
        # Fallback to in-memory storage
        if not hasattr(self, '_artist_profiles'):
            self._artist_profiles = {}
        
        if profile_id not in self._artist_profiles:
            return Result.fail(ErrorDetails(
                code=ErrorCode.NOT_FOUND,
                message=f"Artist profile with ID '{profile_id}' not found"
            ))
        
        return Result.ok(self._artist_profiles[profile_id])
    
    def create_venue_profile(self, profile: VenueProfile) -> Result[VenueProfile]:
        """
        Create a new venue profile.
        
        Args:
            profile: The venue profile to create
            
        Returns:
            Result containing the created profile or error details
        """
        # Validate required fields
        validation_result = self._validate_venue_profile(profile)
        if not validation_result.success:
            return validation_result
        
        # Store the profile using repository if available
        if self.venue_repository:
            return self.venue_repository.create(profile)
        
        # Fallback to in-memory storage for backward compatibility
        if not hasattr(self, '_venue_profiles'):
            self._venue_profiles = {}
        self._venue_profiles[profile.id] = profile
        return Result.ok(profile)
    
    def get_venue_profile(self, profile_id: str) -> Result[VenueProfile]:
        """
        Retrieve a venue profile by ID.
        
        Args:
            profile_id: The ID of the profile to retrieve
            
        Returns:
            Result containing the profile or error details
        """
        # Use repository if available
        if self.venue_repository:
            return self.venue_repository.get_by_id(profile_id)
        
        # Fallback to in-memory storage
        if not hasattr(self, '_venue_profiles'):
            self._venue_profiles = {}
        
        if profile_id not in self._venue_profiles:
            return Result.fail(ErrorDetails(
                code=ErrorCode.NOT_FOUND,
                message=f"Venue profile with ID '{profile_id}' not found"
            ))
        
        return Result.ok(self._venue_profiles[profile_id])
    
    def update_artist_profile(
        self,
        profile_id: str,
        basic_info: Optional[ArtistBasicInfo] = None,
        technical_requirements: Optional[object] = None,
        availabilities: Optional[list] = None
    ) -> Result[ArtistProfile]:
        """
        Update an existing artist profile.
        
        Args:
            profile_id: The ID of the profile to update
            basic_info: Optional updated basic information
            technical_requirements: Optional updated technical requirements
            availabilities: Optional updated availabilities
            
        Returns:
            Result containing the updated profile or error details
        """
        # Get the existing profile
        existing_result = self.get_artist_profile(profile_id)
        if not existing_result.success:
            return existing_result
        
        existing_profile = existing_result.data
        
        # Create updated profile with new values
        updated_basic_info = basic_info if basic_info is not None else existing_profile.basic_info
        updated_tech_req = technical_requirements if technical_requirements is not None else existing_profile.technical_requirements
        updated_availabilities = availabilities if availabilities is not None else existing_profile.availabilities
        
        # Create a new profile with updated values
        updated_profile = replace(
            existing_profile,
            basic_info=updated_basic_info,
            technical_requirements=updated_tech_req,
            availabilities=updated_availabilities,
            updated_at=datetime.now()
        )
        
        # Validate the updated profile
        validation_result = self._validate_artist_profile(updated_profile)
        if not validation_result.success:
            return validation_result
        
        # Store the updated profile using repository if available
        if self.artist_repository:
            return self.artist_repository.update(updated_profile)
        
        # Fallback to in-memory storage
        if not hasattr(self, '_artist_profiles'):
            self._artist_profiles = {}
        self._artist_profiles[profile_id] = updated_profile
        return Result.ok(updated_profile)
    
    def update_venue_profile(
        self,
        profile_id: str,
        basic_info: Optional[VenueBasicInfo] = None,
        technical_capabilities: Optional[object] = None,
        availabilities: Optional[list] = None
    ) -> Result[VenueProfile]:
        """
        Update an existing venue profile.
        
        Args:
            profile_id: The ID of the profile to update
            basic_info: Optional updated basic information
            technical_capabilities: Optional updated technical capabilities
            availabilities: Optional updated availabilities
            
        Returns:
            Result containing the updated profile or error details
        """
        # Get the existing profile
        existing_result = self.get_venue_profile(profile_id)
        if not existing_result.success:
            return existing_result
        
        existing_profile = existing_result.data
        
        # Create updated profile with new values
        updated_basic_info = basic_info if basic_info is not None else existing_profile.basic_info
        updated_tech_cap = technical_capabilities if technical_capabilities is not None else existing_profile.technical_capabilities
        updated_availabilities = availabilities if availabilities is not None else existing_profile.availabilities
        
        # Create a new profile with updated values
        updated_profile = replace(
            existing_profile,
            basic_info=updated_basic_info,
            technical_capabilities=updated_tech_cap,
            availabilities=updated_availabilities,
            updated_at=datetime.now()
        )
        
        # Validate the updated profile
        validation_result = self._validate_venue_profile(updated_profile)
        if not validation_result.success:
            return validation_result
        
        # Store the updated profile using repository if available
        if self.venue_repository:
            return self.venue_repository.update(updated_profile)
        
        # Fallback to in-memory storage
        if not hasattr(self, '_venue_profiles'):
            self._venue_profiles = {}
        self._venue_profiles[profile_id] = updated_profile
        return Result.ok(updated_profile)
    
    def _validate_artist_profile(self, profile: ArtistProfile) -> Result[ArtistProfile]:
        """
        Validate an artist profile.
        
        Args:
            profile: The profile to validate
            
        Returns:
            Result indicating success or validation error
        """
        # Validate basic info
        if not profile.basic_info:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Basic info is required",
                field="basic_info"
            ))
        
        # Validate name
        if not profile.basic_info.name or not profile.basic_info.name.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Artist name is required",
                field="basic_info.name"
            ))
        
        # Validate art type
        if not profile.basic_info.art_type:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Art type is required",
                field="basic_info.art_type"
            ))
        
        # Validate description
        if not profile.basic_info.description or not profile.basic_info.description.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Description is required",
                field="basic_info.description"
            ))
        
        # Validate contact email
        if not profile.basic_info.contact_email or not profile.basic_info.contact_email.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Contact email is required",
                field="basic_info.contact_email"
            ))
        
        # Basic email format validation
        if '@' not in profile.basic_info.contact_email:
            return Result.fail(ErrorDetails(
                code=ErrorCode.INVALID_FORMAT,
                message="Invalid email format",
                field="basic_info.contact_email"
            ))
        
        # Validate user_id
        if not profile.user_id or not profile.user_id.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="User ID is required",
                field="user_id"
            ))
        
        # Validate technical requirements
        if not profile.technical_requirements:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Technical requirements are required",
                field="technical_requirements"
            ))
        
        return Result.ok(profile)
    
    def _validate_venue_profile(self, profile: VenueProfile) -> Result[VenueProfile]:
        """
        Validate a venue profile.
        
        Args:
            profile: The profile to validate
            
        Returns:
            Result indicating success or validation error
        """
        # Validate basic info
        if not profile.basic_info:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Basic info is required",
                field="basic_info"
            ))
        
        # Validate name
        if not profile.basic_info.name or not profile.basic_info.name.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Venue name is required",
                field="basic_info.name"
            ))
        
        # Validate address
        if not profile.basic_info.address:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Address is required",
                field="basic_info.address"
            ))
        
        # Validate description
        if not profile.basic_info.description or not profile.basic_info.description.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Description is required",
                field="basic_info.description"
            ))
        
        # Validate contact email
        if not profile.basic_info.contact_email or not profile.basic_info.contact_email.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Contact email is required",
                field="basic_info.contact_email"
            ))
        
        # Basic email format validation
        if '@' not in profile.basic_info.contact_email:
            return Result.fail(ErrorDetails(
                code=ErrorCode.INVALID_FORMAT,
                message="Invalid email format",
                field="basic_info.contact_email"
            ))
        
        # Validate user_id
        if not profile.user_id or not profile.user_id.strip():
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="User ID is required",
                field="user_id"
            ))
        
        # Validate accepted art types
        if not profile.basic_info.accepted_art_types:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Accepted art types are required",
                field="basic_info.accepted_art_types"
            ))
        
        # Validate technical capabilities
        if not profile.technical_capabilities:
            return Result.fail(ErrorDetails(
                code=ErrorCode.MISSING_REQUIRED_FIELD,
                message="Technical capabilities are required",
                field="technical_capabilities"
            ))
        
        return Result.ok(profile)

    def get_all_artist_profiles(self) -> Result[list]:
        """
        Get all artist profiles.
        
        Returns:
            Result containing list of all artist profiles or error details
        """
        if self.artist_repository:
            return self.artist_repository.get_all()
        
        # Fallback to in-memory storage
        if not hasattr(self, '_artist_profiles'):
            self._artist_profiles = {}
        return Result.ok(list(self._artist_profiles.values()))
    
    def get_all_venue_profiles(self) -> Result[list]:
        """
        Get all venue profiles.
        
        Returns:
            Result containing list of all venue profiles or error details
        """
        if self.venue_repository:
            return self.venue_repository.get_all()
        
        # Fallback to in-memory storage
        if not hasattr(self, '_venue_profiles'):
            self._venue_profiles = {}
        return Result.ok(list(self._venue_profiles.values()))
