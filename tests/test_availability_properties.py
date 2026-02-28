"""Property-based tests for availability management.

This module contains property tests that validate the correctness properties
for availability management using Hypothesis with minimum 100 iterations per test.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, assume
from src.managers import AvailabilityManager, ProfileManager
from src.models import (
    DateRange, ArtistProfile, VenueProfile,
    TechnicalRequirements, TechnicalCapabilities, Address, ArtType, ErrorCode
)
from src.models.profiles import ArtistBasicInfo, VenueBasicInfo


# ============================================================================
# Hypothesis Strategies (Generators)
# ============================================================================

@st.composite
def valid_date_range_strategy(draw):
    """Generate a valid DateRange with end_date > start_date."""
    # Generate a start date between 2024 and 2025
    start_date = draw(st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2025, 12, 31)
    ))
    
    # Generate a duration between 1 and 30 days
    duration_days = draw(st.integers(min_value=1, max_value=30))
    end_date = start_date + timedelta(days=duration_days)
    
    return DateRange(start_date=start_date, end_date=end_date)


@st.composite
def invalid_date_range_strategy(draw):
    """Generate an invalid DateRange with end_date <= start_date."""
    # Generate an end date
    end_date = draw(st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2025, 12, 31)
    ))
    
    # Generate a start date that is >= end_date
    # Either equal or 1-30 days after
    days_offset = draw(st.integers(min_value=0, max_value=30))
    start_date = end_date + timedelta(days=days_offset)
    
    return DateRange(start_date=start_date, end_date=end_date)


@st.composite
def user_id_strategy(draw):
    """Generate a user ID."""
    return draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
        min_size=5,
        max_size=20
    ))


@st.composite
def artist_profile_strategy(draw):
    """Generate a valid ArtistProfile."""
    basic_info = ArtistBasicInfo(
        name=draw(st.text(min_size=1, max_size=100)),
        art_type=draw(st.sampled_from(list(ArtType))),
        description=draw(st.text(min_size=10, max_size=500)),
        contact_email=draw(st.emails())
    )
    
    tech_req = TechnicalRequirements(
        space_requirements={
            'min_area': draw(st.integers(min_value=10, max_value=1000)),
            'min_height': draw(st.integers(min_value=2, max_value=20)),
            'indoor_outdoor': draw(st.sampled_from(['indoor', 'outdoor', 'both']))
        }
    )
    
    user_id = draw(user_id_strategy())
    
    return ArtistProfile(
        basic_info=basic_info,
        technical_requirements=tech_req,
        user_id=user_id,
        availabilities=[]
    )


@st.composite
def venue_profile_strategy(draw):
    """Generate a valid VenueProfile."""
    address = Address(
        street=draw(st.text(min_size=5, max_size=100)),
        city=draw(st.text(min_size=2, max_size=50)),
        region=draw(st.text(min_size=2, max_size=50)),
        country=draw(st.text(min_size=2, max_size=50)),
        postal_code=draw(st.text(min_size=3, max_size=10))
    )
    
    basic_info = VenueBasicInfo(
        name=draw(st.text(min_size=1, max_size=100)),
        address=address,
        description=draw(st.text(min_size=10, max_size=500)),
        contact_email=draw(st.emails()),
        accepted_art_types=draw(st.lists(st.sampled_from(list(ArtType)), min_size=1, max_size=5))
    )
    
    tech_cap = TechnicalCapabilities(
        space_capabilities={
            'area': draw(st.integers(min_value=10, max_value=1000)),
            'height': draw(st.integers(min_value=2, max_value=20)),
            'type': draw(st.sampled_from(['indoor', 'outdoor', 'both']))
        }
    )
    
    user_id = draw(user_id_strategy())
    
    return VenueProfile(
        basic_info=basic_info,
        technical_capabilities=tech_cap,
        user_id=user_id,
        availabilities=[]
    )


# ============================================================================
# Property Tests
# ============================================================================

class TestAvailabilityProperties:
    """Property-based tests for availability management."""
    
    # Feature: artist-venue-matching, Property 3: Mise à jour de disponibilité artiste
    @given(
        artist_profile=artist_profile_strategy(),
        availability=valid_date_range_strategy()
    )
    def test_property_3_artist_availability_update(
        self, artist_profile, availability
    ):
        """
        Property 3: Mise à jour de disponibilité artiste
        
        For any existing artist profile and any valid availability period,
        adding the availability and then retrieving the profile should show
        the new availability in the list.
        
        Validates: Requirements 1.3
        """
        # Create fresh managers for this test
        profile_manager = ProfileManager()
        availability_manager = AvailabilityManager()
        
        # Create the artist profile
        create_result = profile_manager.create_artist_profile(artist_profile)
        assume(create_result.success)
        created_profile = create_result.data
        
        # Add availability
        add_result = availability_manager.add_availability(
            created_profile.user_id,
            availability
        )
        assert add_result.success, f"Failed to add availability: {add_result.error}"
        
        # Retrieve availabilities
        availabilities = availability_manager.get_availabilities(created_profile.user_id)
        
        # The new availability should be in the list
        assert len(availabilities) >= 1, "Availability list should not be empty"
        
        # Find the added availability by ID
        found = any(avail.id == availability.id for avail in availabilities)
        assert found, f"Added availability {availability.id} not found in list"
        
        # Verify the dates match
        matching_avail = next(avail for avail in availabilities if avail.id == availability.id)
        assert matching_avail.start_date == availability.start_date
        assert matching_avail.end_date == availability.end_date
    
    # Feature: artist-venue-matching, Property 4: Mise à jour de disponibilité lieu
    @given(
        venue_profile=venue_profile_strategy(),
        availability=valid_date_range_strategy()
    )
    def test_property_4_venue_availability_update(
        self, venue_profile, availability
    ):
        """
        Property 4: Mise à jour de disponibilité lieu
        
        For any existing venue profile and any valid availability period,
        adding the availability and then retrieving the profile should show
        the new availability in the list.
        
        Validates: Requirements 2.3
        """
        # Create fresh managers for this test
        profile_manager = ProfileManager()
        availability_manager = AvailabilityManager()
        
        # Create the venue profile
        create_result = profile_manager.create_venue_profile(venue_profile)
        assume(create_result.success)
        created_profile = create_result.data
        
        # Add availability
        add_result = availability_manager.add_availability(
            created_profile.user_id,
            availability
        )
        assert add_result.success, f"Failed to add availability: {add_result.error}"
        
        # Retrieve availabilities
        availabilities = availability_manager.get_availabilities(created_profile.user_id)
        
        # The new availability should be in the list
        assert len(availabilities) >= 1, "Availability list should not be empty"
        
        # Find the added availability by ID
        found = any(avail.id == availability.id for avail in availabilities)
        assert found, f"Added availability {availability.id} not found in list"
        
        # Verify the dates match
        matching_avail = next(avail for avail in availabilities if avail.id == availability.id)
        assert matching_avail.start_date == availability.start_date
        assert matching_avail.end_date == availability.end_date
    
    # Feature: artist-venue-matching, Property 5: Round-trip des disponibilités
    @given(
        user_id=user_id_strategy(),
        availability=valid_date_range_strategy()
    )
    def test_property_5_availability_roundtrip(
        self, user_id, availability
    ):
        """
        Property 5: Round-trip des disponibilités
        
        For any user and any availability period, adding the period and then
        retrieving it should return the same start and end dates.
        
        Validates: Requirements 6.1
        """
        # Create fresh manager for this test
        availability_manager = AvailabilityManager()
        
        # Add the availability
        add_result = availability_manager.add_availability(user_id, availability)
        assert add_result.success, f"Failed to add availability: {add_result.error}"
        
        # Retrieve availabilities
        availabilities = availability_manager.get_availabilities(user_id)
        
        # Should have at least one availability
        assert len(availabilities) >= 1
        
        # Find the added availability
        matching_avail = next(
            (avail for avail in availabilities if avail.id == availability.id),
            None
        )
        assert matching_avail is not None, "Added availability not found"
        
        # Verify dates are preserved (round-trip)
        assert matching_avail.start_date == availability.start_date, \
            "Start date not preserved in round-trip"
        assert matching_avail.end_date == availability.end_date, \
            "End date not preserved in round-trip"
    
    # Feature: artist-venue-matching, Property 6: Suppression de disponibilité
    @given(
        user_id=user_id_strategy(),
        availability=valid_date_range_strategy()
    )
    def test_property_6_availability_removal(
        self, user_id, availability
    ):
        """
        Property 6: Suppression de disponibilité
        
        For any user and any existing availability period, removing the period
        should result in its absence from the profile on the next retrieval.
        
        Validates: Requirements 6.2
        """
        # Create fresh manager for this test
        availability_manager = AvailabilityManager()
        
        # Add the availability
        add_result = availability_manager.add_availability(user_id, availability)
        assume(add_result.success)
        
        # Verify it was added
        availabilities_before = availability_manager.get_availabilities(user_id)
        assert any(avail.id == availability.id for avail in availabilities_before)
        
        # Remove the availability
        remove_result = availability_manager.remove_availability(user_id, availability.id)
        assert remove_result.success, f"Failed to remove availability: {remove_result.error}"
        
        # Retrieve availabilities again
        availabilities_after = availability_manager.get_availabilities(user_id)
        
        # The removed availability should not be in the list
        found = any(avail.id == availability.id for avail in availabilities_after)
        assert not found, f"Removed availability {availability.id} still found in list"
    
    # Feature: artist-venue-matching, Property 9: Validation des périodes de disponibilité
    @given(
        user_id=user_id_strategy(),
        invalid_availability=invalid_date_range_strategy()
    )
    def test_property_9_availability_validation(
        self, user_id, invalid_availability
    ):
        """
        Property 9: Validation des périodes de disponibilité
        
        For any availability period where the end date precedes or equals the
        start date, the attempt to add should fail with an error message.
        
        Validates: Requirements 10.2
        """
        # Create fresh manager for this test
        availability_manager = AvailabilityManager()
        
        # Try to add the invalid availability
        result = availability_manager.add_availability(user_id, invalid_availability)
        
        # Should fail
        assert not result.success, \
            "Adding invalid date range should fail"
        
        # Should have an error
        assert result.error is not None, \
            "Failed result should have error details"
        
        # Should have the correct error code
        assert result.error.code == ErrorCode.INVALID_DATE_RANGE, \
            f"Expected INVALID_DATE_RANGE error, got {result.error.code}"
        
        # Should have an error message
        assert result.error.message is not None and len(result.error.message) > 0, \
            "Error should have a descriptive message"
        
        # Verify nothing was added
        availabilities = availability_manager.get_availabilities(user_id)
        assert len(availabilities) == 0, \
            "Invalid availability should not be added to the list"
