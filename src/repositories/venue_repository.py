"""Repository for venue profile persistence."""

from typing import Optional, List
from sqlalchemy.orm import Session
import json
from dataclasses import asdict

from src.models import VenueProfile, Result, ErrorDetails, ErrorCode
from src.models.profiles import VenueBasicInfo
from src.models.technical import TechnicalCapabilities
from src.models.date_range import DateRange
from src.models.address import Address
from src.models.enums import ArtType
from .models import VenueProfileDB


class VenueRepository:
    """Repository for managing venue profile persistence."""
    
    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def create(self, profile: VenueProfile) -> Result[VenueProfile]:
        """
        Create a new venue profile in the database.
        
        Args:
            profile: The venue profile to create
            
        Returns:
            Result containing the created profile or error details
        """
        try:
            db_profile = VenueProfileDB(
                id=profile.id,
                user_id=profile.user_id,
                name=profile.basic_info.name,
                description=profile.basic_info.description,
                contact_email=profile.basic_info.contact_email,
                address_json=self._serialize_address(profile.basic_info.address),
                accepted_art_types_json=self._serialize_art_types(profile.basic_info.accepted_art_types),
                technical_capabilities_json=self._serialize_technical_capabilities(profile.technical_capabilities),
                availabilities_json=self._serialize_availabilities(profile.availabilities),
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            
            self.session.add(db_profile)
            self.session.commit()
            self.session.refresh(db_profile)
            
            return Result.ok(self._to_domain_model(db_profile))
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to create venue profile: {str(e)}"
            ))
    
    def get_by_id(self, profile_id: str) -> Result[VenueProfile]:
        """
        Retrieve a venue profile by ID.
        
        Args:
            profile_id: The ID of the profile to retrieve
            
        Returns:
            Result containing the profile or error details
        """
        try:
            db_profile = self.session.query(VenueProfileDB).filter(
                VenueProfileDB.id == profile_id
            ).first()
            
            if db_profile is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Venue profile with ID '{profile_id}' not found"
                ))
            
            return Result.ok(self._to_domain_model(db_profile))
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve venue profile: {str(e)}"
            ))
    
    def update(self, profile: VenueProfile) -> Result[VenueProfile]:
        """
        Update an existing venue profile.
        
        Args:
            profile: The venue profile with updated data
            
        Returns:
            Result containing the updated profile or error details
        """
        try:
            db_profile = self.session.query(VenueProfileDB).filter(
                VenueProfileDB.id == profile.id
            ).first()
            
            if db_profile is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Venue profile with ID '{profile.id}' not found"
                ))
            
            # Update fields
            db_profile.user_id = profile.user_id
            db_profile.name = profile.basic_info.name
            db_profile.description = profile.basic_info.description
            db_profile.contact_email = profile.basic_info.contact_email
            db_profile.address_json = self._serialize_address(profile.basic_info.address)
            db_profile.accepted_art_types_json = self._serialize_art_types(profile.basic_info.accepted_art_types)
            db_profile.technical_capabilities_json = self._serialize_technical_capabilities(profile.technical_capabilities)
            db_profile.availabilities_json = self._serialize_availabilities(profile.availabilities)
            db_profile.updated_at = profile.updated_at
            
            self.session.commit()
            self.session.refresh(db_profile)
            
            return Result.ok(self._to_domain_model(db_profile))
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to update venue profile: {str(e)}"
            ))
    
    def delete(self, profile_id: str) -> Result[None]:
        """
        Delete a venue profile.
        
        Args:
            profile_id: The ID of the profile to delete
            
        Returns:
            Result indicating success or error details
        """
        try:
            db_profile = self.session.query(VenueProfileDB).filter(
                VenueProfileDB.id == profile_id
            ).first()
            
            if db_profile is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Venue profile with ID '{profile_id}' not found"
                ))
            
            self.session.delete(db_profile)
            self.session.commit()
            
            return Result.ok(None)
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to delete venue profile: {str(e)}"
            ))
    
    def get_all(self) -> Result[List[VenueProfile]]:
        """
        Retrieve all venue profiles.
        
        Returns:
            Result containing list of profiles or error details
        """
        try:
            db_profiles = self.session.query(VenueProfileDB).all()
            profiles = [self._to_domain_model(db_profile) for db_profile in db_profiles]
            return Result.ok(profiles)
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve venue profiles: {str(e)}"
            ))
    
    def _serialize_address(self, address: Address) -> str:
        """Serialize address to JSON."""
        return json.dumps(asdict(address))
    
    def _deserialize_address(self, json_str: str) -> Address:
        """Deserialize address from JSON."""
        data = json.loads(json_str)
        return Address(**data)
    
    def _serialize_art_types(self, art_types: List[ArtType]) -> str:
        """Serialize art types to JSON."""
        return json.dumps([art_type.value for art_type in art_types])
    
    def _deserialize_art_types(self, json_str: str) -> List[ArtType]:
        """Deserialize art types from JSON."""
        data = json.loads(json_str)
        return [ArtType(value) for value in data]
    
    def _serialize_technical_capabilities(self, tech_cap: TechnicalCapabilities) -> str:
        """Serialize technical capabilities to JSON."""
        return json.dumps(asdict(tech_cap))
    
    def _deserialize_technical_capabilities(self, json_str: str) -> TechnicalCapabilities:
        """Deserialize technical capabilities from JSON."""
        data = json.loads(json_str)
        return TechnicalCapabilities(**data)
    
    def _serialize_availabilities(self, availabilities: List[DateRange]) -> str:
        """Serialize availabilities to JSON."""
        return json.dumps([
            {
                'id': avail.id,
                'start_date': avail.start_date.isoformat(),
                'end_date': avail.end_date.isoformat()
            }
            for avail in availabilities
        ])
    
    def _deserialize_availabilities(self, json_str: str) -> List[DateRange]:
        """Deserialize availabilities from JSON."""
        from datetime import datetime
        data = json.loads(json_str)
        return [
            DateRange(
                id=item['id'],
                start_date=datetime.fromisoformat(item['start_date']),
                end_date=datetime.fromisoformat(item['end_date'])
            )
            for item in data
        ]
    
    def _to_domain_model(self, db_profile: VenueProfileDB) -> VenueProfile:
        """Convert database model to domain model."""
        return VenueProfile(
            id=db_profile.id,
            user_id=db_profile.user_id,
            basic_info=VenueBasicInfo(
                name=db_profile.name,
                address=self._deserialize_address(db_profile.address_json),
                description=db_profile.description,
                contact_email=db_profile.contact_email,
                accepted_art_types=self._deserialize_art_types(db_profile.accepted_art_types_json)
            ),
            technical_capabilities=self._deserialize_technical_capabilities(db_profile.technical_capabilities_json),
            availabilities=self._deserialize_availabilities(db_profile.availabilities_json),
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at
        )
