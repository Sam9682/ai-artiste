"""Booking model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

from .enums import BookingStatus
from .date_range import DateRange


@dataclass
class Booking:
    """Represents a booking between an artist and a venue."""
    
    artist_id: str
    venue_id: str
    period: DateRange
    status: BookingStatus
    id: str = None
    created_at: datetime = None
    confirmed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps and ID if not provided."""
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
