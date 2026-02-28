"""Database initialization and dependency injection."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.repositories.database import Base
from src.repositories import ArtistRepository, VenueRepository, BookingRepository
from src.managers import (
    ProfileManager,
    SearchEngine,
    MatchEngine,
    AvailabilityManager,
    CalendarManager
)

# Global instances
_engine = None
_SessionLocal = None
_session = None
_managers = {}


def init_db(database_url: str = "sqlite:///./artist_venue.db"):
    """Initialize database and managers."""
    global _engine, _SessionLocal, _session, _managers
    
    _engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    _session = _SessionLocal()
    
    # Initialize repositories
    artist_repo = ArtistRepository(_session)
    venue_repo = VenueRepository(_session)
    booking_repo = BookingRepository(_session)
    
    # Initialize managers
    profile_manager = ProfileManager(
        artist_repository=artist_repo,
        venue_repository=venue_repo
    )
    
    match_engine = MatchEngine()
    availability_manager = AvailabilityManager()
    
    search_engine = SearchEngine(
        profile_manager=profile_manager,
        match_engine=match_engine,
        availability_manager=availability_manager
    )
    
    calendar_manager = CalendarManager(
        booking_repository=booking_repo
    )
    
    _managers = {
        "profile": profile_manager,
        "search": search_engine,
        "calendar": calendar_manager,
        "match": match_engine,
        "availability": availability_manager
    }


def close_db():
    """Close database connection."""
    global _session
    if _session:
        _session.close()


def get_session() -> Session:
    """Get database session."""
    return _session


def get_profile_manager() -> ProfileManager:
    """Get profile manager instance."""
    return _managers["profile"]


def get_search_engine() -> SearchEngine:
    """Get search engine instance."""
    return _managers["search"]


def get_calendar_manager() -> CalendarManager:
    """Get calendar manager instance."""
    return _managers["calendar"]
