"""Repository for artist profile persistence."""

from typing import Optional, List
from sqlalchemy.orm import Session
import json
from dataclasses import asdict

from src.models import ArtistProfile, Result, ErrorDetails, ErrorCode
from src.models.profiles import ArtistBasicInfo
from src.models.technical import TechnicalRequirements
from src.models.date_range import DateRange
from src.models.enums import ArtType
from .models import ArtistProfileDB


class ArtistRepository:
    """Repository for managing artist profile persistence."""
    
    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def create(self, profile: ArtistProfile) -> Result[ArtistProfile]:
        """
        Create a new artist profile in the database.
        
        Args:
            profile: The artist profile to create
            
        Returns:
            Result containing the created profile or error details
        """
        try:
            db_profile = ArtistProfileDB(
                id=profile.id,
                user_id=profile.user_id,
                name=profile.basic_info.name,
                art_type=profile.basic_info.art_type,
                description=profile.basic_info.description,
                contact_email=profile.basic_info.contact_email,
                technical_requirements_json=self._serialize_technical_requirements(profile.technical_requirements),
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
                message=f"Failed to create artist profile: {str(e)}"
            ))
    
    def get_by_id(self, profile_id: str) -> Result[ArtistProfile]:
        """
        Retrieve an artist profile by ID.
        
        Args:
            profile_id: The ID of the profile to retrieve
            
        Returns:
            Result containing the profile or error details
        """
        try:
            db_profile = self.session.query(ArtistProfileDB).filter(
                ArtistProfileDB.id == profile_id
            ).first()
            
            if db_profile is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Artist profile with ID '{profile_id}' not found"
                ))
            
            return Result.ok(self._to_domain_model(db_profile))
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve artist profile: {str(e)}"
            ))
    
    def update(self, profile: ArtistProfile) -> Result[ArtistProfile]:
        """
        Update an existing artist profile.
        
        Args:
            profile: The artist profile with updated data
            
        Returns:
            Result containing the updated profile or error details
        """
        try:
            db_profile = self.session.query(ArtistProfileDB).filter(
                ArtistProfileDB.id == profile.id
            ).first()
            
            if db_profile is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Artist profile with ID '{profile.id}' not found"
                ))
            
            # Update fields
            db_profile.user_id = profile.user_id
            db_profile.name = profile.basic_info.name
            db_profile.art_type = profile.basic_info.art_type
            db_profile.description = profile.basic_info.description
            db_profile.contact_email = profile.basic_info.contact_email
            db_profile.technical_requirements_json = self._serialize_technical_requirements(profile.technical_requirements)
            db_profile.availabilities_json = self._serialize_availabilities(profile.availabilities)
            db_profile.updated_at = profile.updated_at
            
            self.session.commit()
            self.session.refresh(db_profile)
            
            return Result.ok(self._to_domain_model(db_profile))
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to update artist profile: {str(e)}"
            ))
    
    def delete(self, profile_id: str) -> Result[None]:
        """
        Delete an artist profile.
        
        Args:
            profile_id: The ID of the profile to delete
            
        Returns:
            Result indicating success or error details
        """
        try:
            db_profile = self.session.query(ArtistProfileDB).filter(
                ArtistProfileDB.id == profile_id
            ).first()
            
            if db_profile is None:
                return Result.fail(ErrorDetails(
                    code=ErrorCode.NOT_FOUND,
                    message=f"Artist profile with ID '{profile_id}' not found"
                ))
            
            self.session.delete(db_profile)
            self.session.commit()
            
            return Result.ok(None)
        except Exception as e:
            self.session.rollback()
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to delete artist profile: {str(e)}"
            ))
    
    def get_all(self) -> Result[List[ArtistProfile]]:
        """
        Retrieve all artist profiles.
        
        Returns:
            Result containing list of profiles or error details
        """
        try:
            db_profiles = self.session.query(ArtistProfileDB).all()
            profiles = [self._to_domain_model(db_profile) for db_profile in db_profiles]
            return Result.ok(profiles)
        except Exception as e:
            return Result.fail(ErrorDetails(
                code=ErrorCode.DATABASE_ERROR,
                message=f"Failed to retrieve artist profiles: {str(e)}"
            ))
    
    def _serialize_technical_requirements(self, tech_req: TechnicalRequirements) -> str:
        """Serialize technical requirements to JSON."""
        return json.dumps(asdict(tech_req))
    
    def _deserialize_technical_requirements(self, json_str: str) -> TechnicalRequirements:
        """Deserialize technical requirements from JSON."""
        data = json.loads(json_str)
        return TechnicalRequirements(**data)
    
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
    
    def _to_domain_model(self, db_profile: ArtistProfileDB) -> ArtistProfile:
        """Convert database model to domain model."""
        return ArtistProfile(
            id=db_profile.id,
            user_id=db_profile.user_id,
            basic_info=ArtistBasicInfo(
                name=db_profile.name,
                art_type=db_profile.art_type,
                description=db_profile.description,
                contact_email=db_profile.contact_email
            ),
            technical_requirements=self._deserialize_technical_requirements(db_profile.technical_requirements_json),
            availabilities=self._deserialize_availabilities(db_profile.availabilities_json),
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at
        )
