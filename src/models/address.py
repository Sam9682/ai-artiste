"""Address model for venue locations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Coordinates:
    """Geographic coordinates."""
    
    latitude: float
    longitude: float


@dataclass
class Address:
    """Physical address for a venue."""
    
    street: str
    city: str
    region: str
    country: str
    postal_code: str
    coordinates: Optional[Coordinates] = None
