"""Availability manager for managing availability periods."""

from typing import Dict, List
from src.models import DateRange, Result, ErrorDetails, ErrorCode


class AvailabilityManager:
    """Manages availability periods for artists and venues."""
    
    def __init__(self):
        """Initialize the availability manager with in-memory storage."""
        self._availabilities: Dict[str, List[DateRange]] = {}
    
    def add_availability(self, user_id: str, period: DateRange) -> Result[None]:
        """
        Add an availability period for a user.
        
        Args:
            user_id: The ID of the user (artist or venue)
            period: The date range to add
            
        Returns:
            Result indicating success or error details
        """
        # Validate the date range
        if period.end_date <= period.start_date:
            return Result.fail(ErrorDetails(
                code=ErrorCode.INVALID_DATE_RANGE,
                message="La date de fin doit être postérieure à la date de début",
                field="dateRange",
                details={
                    "start_date": period.start_date.isoformat(),
                    "end_date": period.end_date.isoformat()
                }
            ))
        
        # Initialize the user's availability list if it doesn't exist
        if user_id not in self._availabilities:
            self._availabilities[user_id] = []
        
        # Add the period
        self._availabilities[user_id].append(period)
        
        return Result.ok(None)
    
    def remove_availability(self, user_id: str, period_id: str) -> Result[None]:
        """
        Remove an availability period for a user.
        
        Args:
            user_id: The ID of the user (artist or venue)
            period_id: The ID of the period to remove
            
        Returns:
            Result indicating success or error details
        """
        # Check if user has any availabilities
        if user_id not in self._availabilities:
            return Result.fail(ErrorDetails(
                code=ErrorCode.NOT_FOUND,
                message=f"No availabilities found for user '{user_id}'"
            ))
        
        # Find and remove the period
        user_availabilities = self._availabilities[user_id]
        for i, period in enumerate(user_availabilities):
            if period.id == period_id:
                user_availabilities.pop(i)
                return Result.ok(None)
        
        # Period not found
        return Result.fail(ErrorDetails(
            code=ErrorCode.NOT_FOUND,
            message=f"Availability period with ID '{period_id}' not found for user '{user_id}'"
        ))
    
    def get_availabilities(self, user_id: str) -> List[DateRange]:
        """
        Get all availability periods for a user.
        
        Args:
            user_id: The ID of the user (artist or venue)
            
        Returns:
            List of date ranges (empty list if user has no availabilities)
        """
        return self._availabilities.get(user_id, [])
    
    def find_common_availability(self, artist_id: str, venue_id: str) -> List[DateRange]:
        """
        Find common availability periods between an artist and a venue.
        
        This method calculates the intersection of availability periods,
        returning all time periods where both the artist and venue are available.
        
        Args:
            artist_id: The ID of the artist
            venue_id: The ID of the venue
            
        Returns:
            List of DateRange objects representing common availability periods.
            Returns empty list if there are no common periods.
        """
        artist_availabilities = self.get_availabilities(artist_id)
        venue_availabilities = self.get_availabilities(venue_id)
        
        common_periods = []
        
        # For each artist availability, check for overlaps with venue availabilities
        for artist_period in artist_availabilities:
            for venue_period in venue_availabilities:
                # Calculate the intersection of the two periods
                overlap_start = max(artist_period.start_date, venue_period.start_date)
                overlap_end = min(artist_period.end_date, venue_period.end_date)
                
                # If there's a valid overlap (start < end), add it to results
                if overlap_start < overlap_end:
                    common_periods.append(DateRange(
                        start_date=overlap_start,
                        end_date=overlap_end
                    ))
        
        return common_periods
    
    def has_conflict(self, user_id: str, period: DateRange) -> bool:
        """
        Check if a period conflicts with any existing availability periods.

        A conflict exists if the given period overlaps with any existing
        availability period for the user. This is used to prevent double-booking.

        Args:
            user_id: The ID of the user (artist or venue)
            period: The date range to check for conflicts

        Returns:
            True if there is a conflict (overlap), False otherwise
        """
        user_availabilities = self.get_availabilities(user_id)

        # Check if the period overlaps with any existing availability
        for existing_period in user_availabilities:
            # Two periods overlap if:
            # - The new period starts before the existing one ends, AND
            # - The new period ends after the existing one starts
            if (period.start_date < existing_period.end_date and
                period.end_date > existing_period.start_date):
                return True

        return False
    
    def mark_as_booked(self, user_id: str, period: DateRange) -> Result[None]:
        """
        Mark a period as booked by removing it from available periods.
        
        This method removes the booked period from the user's availabilities.
        If the booked period partially overlaps with existing availabilities,
        it will split or trim those availabilities accordingly.
        
        Args:
            user_id: The ID of the user (artist or venue)
            period: The date range to mark as booked
            
        Returns:
            Result indicating success or error details
        """
        # Validate the date range
        if period.end_date <= period.start_date:
            return Result.fail(ErrorDetails(
                code=ErrorCode.INVALID_DATE_RANGE,
                message="La date de fin doit être postérieure à la date de début",
                field="dateRange",
                details={
                    "start_date": period.start_date.isoformat(),
                    "end_date": period.end_date.isoformat()
                }
            ))
        
        # Get current availabilities
        if user_id not in self._availabilities:
            self._availabilities[user_id] = []
        
        user_availabilities = self._availabilities[user_id]
        new_availabilities = []
        
        # Process each existing availability period
        for existing_period in user_availabilities:
            # Case 1: No overlap - keep the existing period as is
            if (period.end_date <= existing_period.start_date or 
                period.start_date >= existing_period.end_date):
                new_availabilities.append(existing_period)
            
            # Case 2: Booked period is completely within existing period
            # Split the existing period into two parts
            elif (period.start_date > existing_period.start_date and 
                  period.end_date < existing_period.end_date):
                # Keep the part before the booked period
                new_availabilities.append(DateRange(
                    start_date=existing_period.start_date,
                    end_date=period.start_date
                ))
                # Keep the part after the booked period
                new_availabilities.append(DateRange(
                    start_date=period.end_date,
                    end_date=existing_period.end_date
                ))
            
            # Case 3: Booked period overlaps the start of existing period
            # Keep only the part after the booked period
            elif (period.start_date <= existing_period.start_date and 
                  period.end_date > existing_period.start_date and
                  period.end_date < existing_period.end_date):
                new_availabilities.append(DateRange(
                    start_date=period.end_date,
                    end_date=existing_period.end_date
                ))
            
            # Case 4: Booked period overlaps the end of existing period
            # Keep only the part before the booked period
            elif (period.start_date > existing_period.start_date and 
                  period.start_date < existing_period.end_date and
                  period.end_date >= existing_period.end_date):
                new_availabilities.append(DateRange(
                    start_date=existing_period.start_date,
                    end_date=period.start_date
                ))
            
            # Case 5: Booked period completely covers existing period
            # Don't add anything (existing period is completely removed)
        
        # Update the user's availabilities
        self._availabilities[user_id] = new_availabilities
        
        return Result.ok(None)
