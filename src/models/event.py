"""Event model for public calendars."""

from dataclasses import dataclass
from typing import Optional
import uuid

from .date_range import DateRange


@dataclass
class Event:
    """Represents a public event in a calendar."""
    
    booking_id: str
    artist_id: str
    venue_id: str
    date: DateRange
    artist_name: str
    venue_name: str
    id: str = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.id is None:
            self.id = str(uuid.uuid4())
