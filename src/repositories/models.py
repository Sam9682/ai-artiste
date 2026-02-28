"""SQLAlchemy database models."""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from .database import Base
from src.models.enums import ArtType, BookingStatus


class ArtistProfileDB(Base):
    """Database model for artist profiles."""
    
    __tablename__ = "artist_profiles"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Basic info
    name = Column(String, nullable=False)
    art_type = Column(SQLEnum(ArtType), nullable=False)
    description = Column(Text, nullable=False)
    contact_email = Column(String, nullable=False)
    
    # Technical requirements (stored as JSON)
    technical_requirements_json = Column(Text, nullable=False)
    
    # Availabilities (stored as JSON array)
    availabilities_json = Column(Text, default="[]")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class VenueProfileDB(Base):
    """Database model for venue profiles."""
    
    __tablename__ = "venue_profiles"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Basic info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    contact_email = Column(String, nullable=False)
    
    # Address (stored as JSON)
    address_json = Column(Text, nullable=False)
    
    # Accepted art types (stored as JSON array)
    accepted_art_types_json = Column(Text, nullable=False)
    
    # Technical capabilities (stored as JSON)
    technical_capabilities_json = Column(Text, nullable=False)
    
    # Availabilities (stored as JSON array)
    availabilities_json = Column(Text, default="[]")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class BookingDB(Base):
    """Database model for bookings."""
    
    __tablename__ = "bookings"
    
    id = Column(String, primary_key=True)
    artist_id = Column(String, nullable=False, index=True)
    venue_id = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(BookingStatus), nullable=False)
    
    # Period (stored as JSON)
    period_json = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)
