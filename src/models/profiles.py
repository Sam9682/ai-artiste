"""Profile models for artists and venues."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

from .enums import ArtType
from .address import Address
from .technical import TechnicalRequirements, TechnicalCapabilities
from .date_range import DateRange


@dataclass
class ArtistBasicInfo:
    """Basic information for an artist."""
    
    name: str
    art_type: ArtType
    description: str
    contact_email: str


@dataclass
class ArtistProfile:
    """Complete profile for an artist."""
    
    basic_info: ArtistBasicInfo
    technical_requirements: TechnicalRequirements
    user_id: str
    id: str = None
    availabilities: List[DateRange] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize timestamps and ID if not provided."""
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class VenueBasicInfo:
    """Basic information for a venue."""
    
    name: str
    address: Address
    description: str
    contact_email: str
    accepted_art_types: List[ArtType]


@dataclass
class VenueProfile:
    """Complete profile for a venue."""
    
    basic_info: VenueBasicInfo
    technical_capabilities: TechnicalCapabilities
    user_id: str
    id: str = None
    availabilities: List[DateRange] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize timestamps and ID if not provided."""
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
