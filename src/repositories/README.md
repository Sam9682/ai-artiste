# Repository Layer

This directory contains the persistence layer for the artist-venue matching platform. The repositories provide CRUD operations for artist profiles, venue profiles, and bookings.

## Architecture

The repository layer uses SQLAlchemy ORM for database abstraction, supporting both SQLite (development) and PostgreSQL (production).

### Components

- **Database**: Manages database connections and sessions
- **ArtistRepository**: Handles persistence of artist profiles
- **VenueRepository**: Handles persistence of venue profiles
- **BookingRepository**: Handles persistence of bookings

## Usage

### Setting up the Database

```python
from src.repositories import Database

# For development (SQLite in-memory)
db = Database()

# For development (SQLite file)
db = Database("sqlite:///./artist_venue.db")

# For production (PostgreSQL)
db = Database("postgresql://user:password@localhost/dbname")

# Create tables
db.create_tables()
```

### Using Repositories

```python
from src.repositories import ArtistRepository, VenueRepository, BookingRepository

# Get a database session
session = db.get_session()

# Create repositories
artist_repo = ArtistRepository(session)
venue_repo = VenueRepository(session)
booking_repo = BookingRepository(session)

# Create an artist profile
result = artist_repo.create(artist_profile)
if result.success:
    print(f"Created profile: {result.data.id}")
else:
    print(f"Error: {result.error.message}")

# Retrieve a profile
result = artist_repo.get_by_id(profile_id)
if result.success:
    profile = result.data
    print(f"Found profile: {profile.basic_info.name}")

# Update a profile
profile.basic_info.name = "New Name"
result = artist_repo.update(profile)

# Delete a profile
result = artist_repo.delete(profile_id)

# Close session when done
session.close()
```

### Repository Methods

All repositories follow the same pattern and return `Result[T]` objects:

#### ArtistRepository
- `create(profile: ArtistProfile) -> Result[ArtistProfile]`
- `get_by_id(profile_id: str) -> Result[ArtistProfile]`
- `update(profile: ArtistProfile) -> Result[ArtistProfile]`
- `delete(profile_id: str) -> Result[None]`
- `get_all() -> Result[List[ArtistProfile]]`

#### VenueRepository
- `create(profile: VenueProfile) -> Result[VenueProfile]`
- `get_by_id(profile_id: str) -> Result[VenueProfile]`
- `update(profile: VenueProfile) -> Result[VenueProfile]`
- `delete(profile_id: str) -> Result[None]`
- `get_all() -> Result[List[VenueProfile]]`

#### BookingRepository
- `create(booking: Booking) -> Result[Booking]`
- `get_by_id(booking_id: str) -> Result[Booking]`
- `get_by_artist_id(artist_id: str) -> Result[List[Booking]]`
- `get_by_venue_id(venue_id: str) -> Result[List[Booking]]`
- `get_confirmed_bookings() -> Result[List[Booking]]`
- `update(booking: Booking) -> Result[Booking]`
- `delete(booking_id: str) -> Result[None]`
- `get_all() -> Result[List[Booking]]`

## Database Schema

### artist_profiles
- `id` (String, PK)
- `user_id` (String, indexed)
- `name` (String)
- `art_type` (Enum)
- `description` (Text)
- `contact_email` (String)
- `technical_requirements_json` (Text)
- `availabilities_json` (Text)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### venue_profiles
- `id` (String, PK)
- `user_id` (String, indexed)
- `name` (String)
- `description` (Text)
- `contact_email` (String)
- `address_json` (Text)
- `accepted_art_types_json` (Text)
- `technical_capabilities_json` (Text)
- `availabilities_json` (Text)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### bookings
- `id` (String, PK)
- `artist_id` (String, indexed)
- `venue_id` (String, indexed)
- `status` (Enum)
- `period_json` (Text)
- `created_at` (DateTime)
- `confirmed_at` (DateTime, nullable)

## Error Handling

All repository methods return `Result[T]` objects that encapsulate success or failure:

```python
result = artist_repo.create(profile)

if result.success:
    # Success case
    profile = result.data
    print(f"Created: {profile.id}")
else:
    # Error case
    error = result.error
    print(f"Error {error.code}: {error.message}")
```

Common error codes:
- `NOT_FOUND`: Resource not found
- `DATABASE_ERROR`: Database operation failed
- `VALIDATION_ERROR`: Data validation failed

## Testing

Run repository tests:

```bash
pytest tests/test_repositories.py -v
```

## Production Deployment

For production with PostgreSQL:

1. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Set up database connection:
   ```python
   db = Database("postgresql://user:password@host:5432/dbname")
   db.create_tables()
   ```

3. Consider using environment variables for connection strings:
   ```python
   import os
   db_url = os.getenv("DATABASE_URL", "sqlite:///./artist_venue.db")
   db = Database(db_url)
   ```
