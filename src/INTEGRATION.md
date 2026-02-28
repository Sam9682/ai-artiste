# Component Integration Guide

This document explains how all components are wired together in the artist-venue matching platform.

## Architecture Overview

The system follows a three-tier architecture:
1. **Managers** - Business logic layer
2. **Repositories** - Data persistence layer
3. **Models** - Domain models

## Component Wiring

### ProfileManager with Repositories

The `ProfileManager` can work with or without repositories:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.repositories.database import Base
from src.repositories import ArtistRepository, VenueRepository
from src.managers import ProfileManager

# With repositories (persistent storage)
engine = create_engine('sqlite:///artist_venue.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

artist_repo = ArtistRepository(session)
venue_repo = VenueRepository(session)
profile_manager = ProfileManager(
    artist_repository=artist_repo,
    venue_repository=venue_repo
)

# Without repositories (in-memory storage)
profile_manager = ProfileManager()
```

### SearchEngine with ProfileManager, MatchEngine, and AvailabilityManager

The `SearchEngine` orchestrates searches by coordinating multiple managers:

```python
from src.managers import (
    ProfileManager,
    SearchEngine,
    MatchEngine,
    AvailabilityManager
)

# Initialize dependencies
profile_manager = ProfileManager(artist_repo, venue_repo)
match_engine = MatchEngine()
availability_manager = AvailabilityManager()

# Wire SearchEngine
search_engine = SearchEngine(
    profile_manager=profile_manager,
    match_engine=match_engine,
    availability_manager=availability_manager
)
```

### CalendarManager with BookingRepository

The `CalendarManager` can work with or without a booking repository:

```python
from src.repositories import BookingRepository
from src.managers import CalendarManager

# With repository (persistent storage)
booking_repo = BookingRepository(session)
calendar_manager = CalendarManager(booking_repository=booking_repo)

# Without repository (in-memory storage)
calendar_manager = CalendarManager()
```

## Complete Integration Example

Here's a complete example showing all components working together:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.repositories.database import Base
from src.repositories import ArtistRepository, VenueRepository, BookingRepository
from src.managers import (
    ProfileManager,
    SearchEngine,
    MatchEngine,
    AvailabilityManager,
    CalendarManager
)

# Setup database
engine = create_engine('sqlite:///artist_venue.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Initialize repositories
artist_repo = ArtistRepository(session)
venue_repo = VenueRepository(session)
booking_repo = BookingRepository(session)

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

# Now you can use the system
# 1. Create profiles
artist_result = profile_manager.create_artist_profile(artist_profile)

# 2. Search for matches
matches_result = search_engine.search_venues_for_artist(artist_id)

# 3. View calendars
events = calendar_manager.get_artist_calendar(artist_id)
```

## Key Integration Points

### 1. ProfileManager → Repositories
- `create_artist_profile()` → `ArtistRepository.create()`
- `get_artist_profile()` → `ArtistRepository.get_by_id()`
- `update_artist_profile()` → `ArtistRepository.update()`
- Similar for venue profiles

### 2. SearchEngine → ProfileManager
- `search_venues_for_artist()` → `ProfileManager.get_artist_profile()`
- `search_venues_for_artist()` → `ProfileManager.get_all_venue_profiles()`
- Similar for artist searches

### 3. SearchEngine → MatchEngine
- Evaluates technical compatibility for each artist-venue pair
- Calculates compatibility scores
- Identifies unmatched requirements

### 4. SearchEngine → AvailabilityManager
- Finds common availability periods between artists and venues
- Excludes matches with no common availability

### 5. CalendarManager → BookingRepository
- `_is_event_confirmed()` → `BookingRepository.get_by_id()`
- Checks booking status to determine if events should be displayed

## Backward Compatibility

All managers maintain backward compatibility with in-memory storage:
- If no repository is provided, they fall back to in-memory dictionaries
- This allows for easy testing and gradual migration to persistent storage
- Existing tests continue to work without modification

## Benefits of This Architecture

1. **Separation of Concerns**: Each component has a single, well-defined responsibility
2. **Testability**: Components can be tested independently with mock dependencies
3. **Flexibility**: Can switch between in-memory and persistent storage
4. **Maintainability**: Clear interfaces make the system easy to understand and modify
5. **Scalability**: Can easily add new storage backends or business logic
