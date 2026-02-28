"""Enumerations for the artist-venue matching platform."""

from enum import Enum


class ArtType(str, Enum):
    """Types of art supported by the platform."""
    
    MUSIC = "music"
    PERFORMANCE = "performance"
    SCULPTURE = "sculpture"
    PAINTING = "painting"
    PHOTOGRAPHY = "photography"
    MIXED_MEDIA = "mixed_media"
    OTHER = "other"


class BookingStatus(str, Enum):
    """Status of a booking."""
    
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ErrorCode(str, Enum):
    """Error codes for the Result type."""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Conflict errors
    BOOKING_CONFLICT = "BOOKING_CONFLICT"
    AVAILABILITY_CONFLICT = "AVAILABILITY_CONFLICT"
    
    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    
    # System errors
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
