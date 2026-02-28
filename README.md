# Artist-Venue Matching Platform

A bidirectional platform for connecting artists with performance and exhibition venues.

## Project Structure

```
.
├── src/
│   ├── models/          # Data models
│   │   ├── enums.py     # Enumerations (ArtType, BookingStatus, ErrorCode)
│   │   ├── result.py    # Result type for error handling
│   │   ├── date_range.py
│   │   ├── address.py
│   │   ├── technical.py # Technical requirements and capabilities
│   │   ├── profiles.py  # Artist and Venue profiles
│   │   ├── booking.py
│   │   └── event.py
│   └── __init__.py
├── tests/               # Test suite
│   └── __init__.py
├── pyproject.toml       # Project configuration
└── requirements-dev.txt # Development dependencies

```

## Installation

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Data Models

### Core Models

- **ArtistProfile**: Complete profile for an artist including basic info, technical requirements, and availabilities
- **VenueProfile**: Complete profile for a venue including basic info, technical capabilities, and availabilities
- **DateRange**: Time period with start and end dates
- **Booking**: Reservation between an artist and a venue
- **Event**: Public calendar event

### Enumerations

- **ArtType**: Types of art (music, performance, sculpture, painting, photography, mixed_media, other)
- **BookingStatus**: Status of bookings (pending, confirmed, cancelled)
- **ErrorCode**: Error codes for the Result type

### Error Handling

The system uses a `Result<T>` type for explicit error handling:

```python
from src.models import Result, ErrorDetails, ErrorCode

# Success case
result = Result.ok(data)

# Failure case
result = Result.fail(ErrorDetails(
    code=ErrorCode.VALIDATION_ERROR,
    message="Invalid data",
    field="email"
))
```

## Development

This project follows the design document in `.kiro/specs/artist-venue-matching/design.md`.

Testing strategy:
- Unit tests for specific examples and edge cases
- Property-based tests (using Hypothesis) for universal properties
- Minimum 100 iterations for property-based tests
