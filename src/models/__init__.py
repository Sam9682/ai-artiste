"""Data models for the artist-venue matching platform."""

from .enums import ArtType, BookingStatus, ErrorCode
from .result import Result, ErrorDetails
from .date_range import DateRange
from .address import Address
from .technical import TechnicalRequirements, TechnicalCapabilities
from .profiles import ArtistProfile, VenueProfile
from .booking import Booking
from .event import Event
from .compatibility import CompatibilityResult

__all__ = [
    "ArtType",
    "BookingStatus",
    "ErrorCode",
    "Result",
    "ErrorDetails",
    "DateRange",
    "Address",
    "TechnicalRequirements",
    "TechnicalCapabilities",
    "ArtistProfile",
    "VenueProfile",
    "Booking",
    "Event",
    "CompatibilityResult",
]
