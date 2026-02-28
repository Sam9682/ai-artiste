"""Unit tests for AvailabilityManager."""

import pytest
from datetime import datetime, timedelta
from src.managers import AvailabilityManager
from src.models import DateRange, ErrorCode


class TestAvailabilityManager:
    """Test suite for AvailabilityManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh AvailabilityManager for each test."""
        return AvailabilityManager()
    
    @pytest.fixture
    def valid_period(self):
        """Create a valid date range."""
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        return DateRange(start_date=start, end_date=end)
    
    def test_add_availability_success(self, manager, valid_period):
        """Test adding a valid availability period."""
        result = manager.add_availability("user-1", valid_period)
        
        assert result.success is True
        assert result.error is None
        
        # Verify it was added
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 1
        assert availabilities[0].id == valid_period.id
        assert availabilities[0].start_date == valid_period.start_date
        assert availabilities[0].end_date == valid_period.end_date
    
    def test_add_multiple_availabilities(self, manager):
        """Test adding multiple availability periods for the same user."""
        period1 = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 20)
        )
        period2 = DateRange(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 10)
        )
        
        result1 = manager.add_availability("user-1", period1)
        result2 = manager.add_availability("user-1", period2)
        
        assert result1.success is True
        assert result2.success is True
        
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 2
    
    def test_add_availability_invalid_date_range(self, manager):
        """Test adding an availability with end date before start date."""
        invalid_period = DateRange(
            start_date=datetime(2024, 1, 20),
            end_date=datetime(2024, 1, 15)
        )
        
        result = manager.add_availability("user-1", invalid_period)
        
        assert result.success is False
        assert result.error is not None
        assert result.error.code == ErrorCode.INVALID_DATE_RANGE
        assert "postérieure" in result.error.message
        assert result.error.field == "dateRange"
        
        # Verify nothing was added
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 0
    
    def test_add_availability_equal_dates(self, manager):
        """Test adding an availability with equal start and end dates."""
        same_date = datetime(2024, 1, 15)
        invalid_period = DateRange(start_date=same_date, end_date=same_date)
        
        result = manager.add_availability("user-1", invalid_period)
        
        assert result.success is False
        assert result.error.code == ErrorCode.INVALID_DATE_RANGE
    
    def test_remove_availability_success(self, manager, valid_period):
        """Test removing an existing availability period."""
        # Add a period first
        manager.add_availability("user-1", valid_period)
        
        # Remove it
        result = manager.remove_availability("user-1", valid_period.id)
        
        assert result.success is True
        assert result.error is None
        
        # Verify it was removed
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 0
    
    def test_remove_availability_not_found(self, manager):
        """Test removing a non-existent availability period."""
        result = manager.remove_availability("user-1", "non-existent-id")
        
        assert result.success is False
        assert result.error is not None
        assert result.error.code == ErrorCode.NOT_FOUND
        assert "No availabilities found" in result.error.message
    
    def test_remove_availability_wrong_period_id(self, manager, valid_period):
        """Test removing with wrong period ID."""
        # Add a period
        manager.add_availability("user-1", valid_period)
        
        # Try to remove with wrong ID
        result = manager.remove_availability("user-1", "wrong-id")
        
        assert result.success is False
        assert result.error.code == ErrorCode.NOT_FOUND
        assert "not found for user" in result.error.message
    
    def test_get_availabilities_empty(self, manager):
        """Test getting availabilities for a user with none."""
        availabilities = manager.get_availabilities("user-1")
        
        assert availabilities == []
        assert len(availabilities) == 0
    
    def test_get_availabilities_multiple_users(self, manager):
        """Test that availabilities are isolated per user."""
        period1 = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 20)
        )
        period2 = DateRange(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 10)
        )
        
        manager.add_availability("user-1", period1)
        manager.add_availability("user-2", period2)
        
        user1_avail = manager.get_availabilities("user-1")
        user2_avail = manager.get_availabilities("user-2")
        
        assert len(user1_avail) == 1
        assert len(user2_avail) == 1
        assert user1_avail[0].id == period1.id
        assert user2_avail[0].id == period2.id
    
    def test_remove_one_of_multiple_availabilities(self, manager):
        """Test removing one availability when user has multiple."""
        period1 = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 20)
        )
        period2 = DateRange(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 10)
        )
        
        manager.add_availability("user-1", period1)
        manager.add_availability("user-1", period2)
        
        # Remove the first one
        result = manager.remove_availability("user-1", period1.id)
        
        assert result.success is True
        
        # Verify only the second one remains
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 1
        assert availabilities[0].id == period2.id


class TestFindCommonAvailability:
    """Test suite for find_common_availability method."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh AvailabilityManager for each test."""
        return AvailabilityManager()
    
    def test_find_common_availability_no_overlap(self, manager):
        """Test finding common availability when periods don't overlap."""
        # Artist available Jan 1-10
        artist_period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        # Venue available Jan 15-25
        venue_period = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        
        manager.add_availability("artist-1", artist_period)
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 0
    
    def test_find_common_availability_complete_overlap(self, manager):
        """Test finding common availability when one period is completely within another."""
        # Artist available Jan 1-31
        artist_period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        # Venue available Jan 10-20 (completely within artist's period)
        venue_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        manager.add_availability("artist-1", artist_period)
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 1
        assert common[0].start_date == datetime(2024, 1, 10)
        assert common[0].end_date == datetime(2024, 1, 20)
    
    def test_find_common_availability_partial_overlap(self, manager):
        """Test finding common availability when periods partially overlap."""
        # Artist available Jan 1-15
        artist_period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 15)
        )
        # Venue available Jan 10-25
        venue_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 25)
        )
        
        manager.add_availability("artist-1", artist_period)
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 1
        assert common[0].start_date == datetime(2024, 1, 10)
        assert common[0].end_date == datetime(2024, 1, 15)
    
    def test_find_common_availability_exact_match(self, manager):
        """Test finding common availability when periods are exactly the same."""
        # Both available Jan 10-20
        artist_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        venue_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        manager.add_availability("artist-1", artist_period)
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 1
        assert common[0].start_date == datetime(2024, 1, 10)
        assert common[0].end_date == datetime(2024, 1, 20)
    
    def test_find_common_availability_multiple_periods(self, manager):
        """Test finding common availability with multiple periods for each user."""
        # Artist available Jan 1-15 and Feb 1-15
        artist_period1 = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 15)
        )
        artist_period2 = DateRange(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 15)
        )
        
        # Venue available Jan 10-20 and Feb 10-20
        venue_period1 = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        venue_period2 = DateRange(
            start_date=datetime(2024, 2, 10),
            end_date=datetime(2024, 2, 20)
        )
        
        manager.add_availability("artist-1", artist_period1)
        manager.add_availability("artist-1", artist_period2)
        manager.add_availability("venue-1", venue_period1)
        manager.add_availability("venue-1", venue_period2)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        # Should find two overlapping periods
        assert len(common) == 2
        
        # First overlap: Jan 10-15
        assert common[0].start_date == datetime(2024, 1, 10)
        assert common[0].end_date == datetime(2024, 1, 15)
        
        # Second overlap: Feb 10-15
        assert common[1].start_date == datetime(2024, 2, 10)
        assert common[1].end_date == datetime(2024, 2, 15)
    
    def test_find_common_availability_empty_artist(self, manager):
        """Test finding common availability when artist has no availabilities."""
        venue_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 0
    
    def test_find_common_availability_empty_venue(self, manager):
        """Test finding common availability when venue has no availabilities."""
        artist_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        manager.add_availability("artist-1", artist_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 0
    
    def test_find_common_availability_both_empty(self, manager):
        """Test finding common availability when both have no availabilities."""
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 0
    
    def test_find_common_availability_adjacent_periods(self, manager):
        """Test finding common availability when periods are adjacent but don't overlap."""
        # Artist available Jan 1-10
        artist_period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        # Venue available Jan 10-20 (starts exactly when artist ends)
        venue_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        manager.add_availability("artist-1", artist_period)
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        # Adjacent periods with no overlap should return empty
        assert len(common) == 0
    
    def test_find_common_availability_one_day_overlap(self, manager):
        """Test finding common availability with a one-day overlap."""
        # Artist available Jan 1-11
        artist_period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 11)
        )
        # Venue available Jan 10-20
        venue_period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        manager.add_availability("artist-1", artist_period)
        manager.add_availability("venue-1", venue_period)
        
        common = manager.find_common_availability("artist-1", "venue-1")
        
        assert len(common) == 1
        assert common[0].start_date == datetime(2024, 1, 10)
        assert common[0].end_date == datetime(2024, 1, 11)


class TestHasConflict:
    """Test suite for has_conflict method."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh AvailabilityManager for each test."""
        return AvailabilityManager()
    
    def test_has_conflict_no_availabilities(self, manager):
        """Test conflict check when user has no availabilities."""
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        assert manager.has_conflict("user-1", period) is False
    
    def test_has_conflict_no_overlap(self, manager):
        """Test conflict check when periods don't overlap."""
        # Add availability Jan 1-10
        existing = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        manager.add_availability("user-1", existing)
        
        # Check period Jan 15-25 (no overlap)
        period = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        
        assert manager.has_conflict("user-1", period) is False
    
    def test_has_conflict_complete_overlap(self, manager):
        """Test conflict check when new period is completely within existing."""
        # Add availability Jan 1-31
        existing = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        manager.add_availability("user-1", existing)
        
        # Check period Jan 10-20 (completely within)
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        assert manager.has_conflict("user-1", period) is True
    
    def test_has_conflict_partial_overlap_start(self, manager):
        """Test conflict check when new period overlaps start of existing."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Check period Jan 5-15 (overlaps start)
        period = DateRange(
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 15)
        )
        
        assert manager.has_conflict("user-1", period) is True
    
    def test_has_conflict_partial_overlap_end(self, manager):
        """Test conflict check when new period overlaps end of existing."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Check period Jan 15-25 (overlaps end)
        period = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        
        assert manager.has_conflict("user-1", period) is True
    
    def test_has_conflict_exact_match(self, manager):
        """Test conflict check when periods are exactly the same."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Check same period
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        assert manager.has_conflict("user-1", period) is True
    
    def test_has_conflict_adjacent_periods(self, manager):
        """Test conflict check when periods are adjacent but don't overlap."""
        # Add availability Jan 1-10
        existing = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        manager.add_availability("user-1", existing)
        
        # Check period Jan 10-20 (starts exactly when existing ends)
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        # Adjacent periods should not conflict
        assert manager.has_conflict("user-1", period) is False
    
    def test_has_conflict_multiple_availabilities(self, manager):
        """Test conflict check with multiple existing availabilities."""
        # Add two availabilities
        period1 = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        period2 = DateRange(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 10)
        )
        manager.add_availability("user-1", period1)
        manager.add_availability("user-1", period2)
        
        # Check period that overlaps with second availability
        period = DateRange(
            start_date=datetime(2024, 2, 5),
            end_date=datetime(2024, 2, 15)
        )
        
        assert manager.has_conflict("user-1", period) is True
    
    def test_has_conflict_covers_existing(self, manager):
        """Test conflict check when new period completely covers existing."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Check period Jan 1-31 (covers existing)
        period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert manager.has_conflict("user-1", period) is True


class TestMarkAsBooked:
    """Test suite for mark_as_booked method."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh AvailabilityManager for each test."""
        return AvailabilityManager()
    
    def test_mark_as_booked_invalid_date_range(self, manager):
        """Test marking as booked with invalid date range."""
        invalid_period = DateRange(
            start_date=datetime(2024, 1, 20),
            end_date=datetime(2024, 1, 15)
        )
        
        result = manager.mark_as_booked("user-1", invalid_period)
        
        assert result.success is False
        assert result.error.code == ErrorCode.INVALID_DATE_RANGE
    
    def test_mark_as_booked_no_availabilities(self, manager):
        """Test marking as booked when user has no availabilities."""
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Should still have no availabilities
        assert len(manager.get_availabilities("user-1")) == 0
    
    def test_mark_as_booked_no_overlap(self, manager):
        """Test marking as booked when period doesn't overlap with availabilities."""
        # Add availability Jan 1-10
        existing = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        manager.add_availability("user-1", existing)
        
        # Mark Jan 15-25 as booked (no overlap)
        period = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Original availability should remain unchanged
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 1
        assert availabilities[0].start_date == datetime(2024, 1, 1)
        assert availabilities[0].end_date == datetime(2024, 1, 10)
    
    def test_mark_as_booked_exact_match(self, manager):
        """Test marking as booked when period exactly matches availability."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Mark same period as booked
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Availability should be completely removed
        assert len(manager.get_availabilities("user-1")) == 0
    
    def test_mark_as_booked_split_availability(self, manager):
        """Test marking as booked splits availability into two parts."""
        # Add availability Jan 1-31
        existing = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        manager.add_availability("user-1", existing)
        
        # Mark Jan 10-20 as booked (middle section)
        period = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Should have two availabilities: Jan 1-10 and Jan 20-31
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 2
        
        # First part: Jan 1-10
        assert availabilities[0].start_date == datetime(2024, 1, 1)
        assert availabilities[0].end_date == datetime(2024, 1, 10)
        
        # Second part: Jan 20-31
        assert availabilities[1].start_date == datetime(2024, 1, 20)
        assert availabilities[1].end_date == datetime(2024, 1, 31)
    
    def test_mark_as_booked_trim_start(self, manager):
        """Test marking as booked trims the start of availability."""
        # Add availability Jan 10-31
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 31)
        )
        manager.add_availability("user-1", existing)
        
        # Mark Jan 1-20 as booked (overlaps start)
        period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 20)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Should have one availability: Jan 20-31
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 1
        assert availabilities[0].start_date == datetime(2024, 1, 20)
        assert availabilities[0].end_date == datetime(2024, 1, 31)
    
    def test_mark_as_booked_trim_end(self, manager):
        """Test marking as booked trims the end of availability."""
        # Add availability Jan 1-31
        existing = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        manager.add_availability("user-1", existing)
        
        # Mark Jan 20-31 as booked (overlaps end)
        period = DateRange(
            start_date=datetime(2024, 1, 20),
            end_date=datetime(2024, 2, 10)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Should have one availability: Jan 1-20
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 1
        assert availabilities[0].start_date == datetime(2024, 1, 1)
        assert availabilities[0].end_date == datetime(2024, 1, 20)
    
    def test_mark_as_booked_covers_availability(self, manager):
        """Test marking as booked completely covers availability."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Mark Jan 1-31 as booked (covers entire availability)
        period = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Availability should be completely removed
        assert len(manager.get_availabilities("user-1")) == 0
    
    def test_mark_as_booked_multiple_availabilities(self, manager):
        """Test marking as booked affects multiple availabilities."""
        # Add three availabilities
        period1 = DateRange(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10)
        )
        period2 = DateRange(
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        period3 = DateRange(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 10)
        )
        manager.add_availability("user-1", period1)
        manager.add_availability("user-1", period2)
        manager.add_availability("user-1", period3)
        
        # Mark Jan 5-20 as booked (affects first two availabilities)
        booked = DateRange(
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 20)
        )
        result = manager.mark_as_booked("user-1", booked)
        
        assert result.success is True
        # Should have three availabilities: Jan 1-5, Jan 20-25, Feb 1-10
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 3
        
        # First: Jan 1-5 (trimmed)
        assert availabilities[0].start_date == datetime(2024, 1, 1)
        assert availabilities[0].end_date == datetime(2024, 1, 5)
        
        # Second: Jan 20-25 (trimmed)
        assert availabilities[1].start_date == datetime(2024, 1, 20)
        assert availabilities[1].end_date == datetime(2024, 1, 25)
        
        # Third: Feb 1-10 (unchanged)
        assert availabilities[2].start_date == datetime(2024, 2, 1)
        assert availabilities[2].end_date == datetime(2024, 2, 10)
    
    def test_mark_as_booked_adjacent_periods(self, manager):
        """Test marking as booked with adjacent periods."""
        # Add availability Jan 10-20
        existing = DateRange(
            start_date=datetime(2024, 1, 10),
            end_date=datetime(2024, 1, 20)
        )
        manager.add_availability("user-1", existing)
        
        # Mark Jan 20-30 as booked (starts exactly when existing ends)
        period = DateRange(
            start_date=datetime(2024, 1, 20),
            end_date=datetime(2024, 1, 30)
        )
        result = manager.mark_as_booked("user-1", period)
        
        assert result.success is True
        # Should trim the end to Jan 10-20
        availabilities = manager.get_availabilities("user-1")
        assert len(availabilities) == 1
        assert availabilities[0].start_date == datetime(2024, 1, 10)
        assert availabilities[0].end_date == datetime(2024, 1, 20)
