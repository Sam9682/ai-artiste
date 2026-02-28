"""Date range model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class DateRange:
    """Represents a time period with start and end dates."""
    
    start_date: datetime
    end_date: datetime
    id: str = None
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.id is None:
            self.id = str(uuid.uuid4())
