"""Search engine for finding compatible matches between artists and venues."""

from typing import List, Optional
from dataclasses import dataclass

from src.models import ArtistProfile, VenueProfile, DateRange, Result, ArtType
from src.models.address import Coordinates
from .match_engine import MatchEngine
from .availability_manager import AvailabilityManager
from .profile_manager import ProfileManager


@dataclass
class VenueMatch:
    """Result of matching a venue with an artist."""
    
    venue: VenueProfile
    compatibility_score: float
    is_compatible: bool
    common_availabilities: List[DateRange]
    unmatched_requirements: List
    
    def format_for_display(self) -> dict:
        """
        Format venue match information for display.
        
        Extracts and formats key information from the venue profile
        for presentation in search results.
        
        Returns:
            Dictionary containing formatted venue information with keys:
            - name: Venue name
            - address: Full formatted address
            - description: Venue description
            - contact_email: Contact email
            - compatibility_score: Compatibility score
            - is_compatible: Whether the venue is compatible
            - common_availabilities: List of common availability periods
            
        Requirements:
            - 4.4: Presents key information from venue profile
        """
        return {
            'name': self.venue.basic_info.name,
            'address': self._format_address(self.venue.basic_info.address),
            'description': self.venue.basic_info.description,
            'contact_email': self.venue.basic_info.contact_email,
            'compatibility_score': self.compatibility_score,
            'is_compatible': self.is_compatible,
            'common_availabilities': [
                self._format_date_range(dr) for dr in self.common_availabilities
            ]
        }
    
    def _format_address(self, address: 'Address') -> str:
        """
        Format an address as a single string.
        
        Args:
            address: Address object to format
            
        Returns:
            Formatted address string
        """
        return f"{address.street}, {address.city}, {address.region}, {address.country} {address.postal_code}"
    
    def _format_date_range(self, date_range: DateRange) -> dict:
        """
        Format a date range for display.
        
        Args:
            date_range: DateRange object to format
            
        Returns:
            Dictionary with formatted start and end dates
        """
        return {
            'start_date': date_range.start_date.isoformat(),
            'end_date': date_range.end_date.isoformat()
        }


@dataclass
class ArtistMatch:
    """Result of matching an artist with a venue."""
    
    artist: ArtistProfile
    compatibility_score: float
    is_compatible: bool
    common_availabilities: List[DateRange]
    unmatched_requirements: List
    
    def format_for_display(self) -> dict:
        """
        Format artist match information for display.
        
        Extracts and formats key information from the artist profile
        for presentation in search results.
        
        Returns:
            Dictionary containing formatted artist information with keys:
            - name: Artist name
            - art_type: Type of art
            - description: Artist description
            - contact_email: Contact email
            - compatibility_score: Compatibility score
            - is_compatible: Whether the artist is compatible
            - common_availabilities: List of common availability periods
            
        Requirements:
            - 3.4: Presents key information from artist profile
        """
        return {
            'name': self.artist.basic_info.name,
            'art_type': self.artist.basic_info.art_type.value,
            'description': self.artist.basic_info.description,
            'contact_email': self.artist.basic_info.contact_email,
            'compatibility_score': self.compatibility_score,
            'is_compatible': self.is_compatible,
            'common_availabilities': [
                self._format_date_range(dr) for dr in self.common_availabilities
            ]
        }
    
    def _format_date_range(self, date_range: DateRange) -> dict:
        """
        Format a date range for display.
        
        Args:
            date_range: DateRange object to format
            
        Returns:
            Dictionary with formatted start and end dates
        """
        return {
            'start_date': date_range.start_date.isoformat(),
            'end_date': date_range.end_date.isoformat()
        }


@dataclass
class VenueSearchFilters:
    """Filters for venue search."""
    
    date_range: Optional[DateRange] = None
    location: Optional['GeographicArea'] = None
    min_compatibility_score: Optional[float] = None


@dataclass
class ArtistSearchFilters:
    """Filters for artist search."""
    
    date_range: Optional[DateRange] = None
    art_type: Optional[List[ArtType]] = None
    min_compatibility_score: Optional[float] = None


@dataclass
class GeographicArea:
    """Geographic area for location filtering."""
    
    center: Coordinates
    radius_km: float


class SearchEngine:
    """Orchestrates searches and applies filters for artist-venue matching."""
    
    def __init__(
        self,
        profile_manager: ProfileManager,
        match_engine: MatchEngine,
        availability_manager: AvailabilityManager
    ):
        """
        Initialize the search engine with required dependencies.
        
        Args:
            profile_manager: Manager for accessing artist and venue profiles
            match_engine: Engine for evaluating technical compatibility
            availability_manager: Manager for checking availability overlaps
        """
        self.profile_manager = profile_manager
        self.match_engine = match_engine
        self.availability_manager = availability_manager
    
    def search_venues_for_artist(
        self,
        artist_id: str,
        filters: Optional[VenueSearchFilters] = None
    ) -> Result[List[VenueMatch]]:
        """
        Search for venues compatible with an artist.
        
        This method:
        1. Retrieves the artist profile
        2. Gets all venue profiles
        3. Evaluates technical compatibility using MatchEngine
        4. Checks for common availability using AvailabilityManager
        5. Applies filters (availability, location, min compatibility score)
        6. Sorts results by compatibility score (descending)
        
        Args:
            artist_id: The ID of the artist searching for venues
            filters: Optional filters to apply to the search results
            
        Returns:
            Result containing a list of VenueMatch objects sorted by compatibility score,
            or error details if the artist profile is not found
            
        Requirements:
            - 4.1: Returns venues with technical compatibility
            - 4.2: Filters by availability when specified
            - 4.3: Filters by geographic location when specified
        """
        # Retrieve the artist profile
        artist_result = self.profile_manager.get_artist_profile(artist_id)
        if not artist_result.success:
            return artist_result
        
        artist = artist_result.data
        
        # Get all venue profiles
        all_venues = self._get_all_venues()
        
        # Evaluate each venue and create matches
        matches = []
        for venue in all_venues:
            # Evaluate technical compatibility
            compatibility = self.match_engine.evaluate_compatibility(
                artist.technical_requirements,
                venue.technical_capabilities
            )
            
            # Only include technically compatible venues (Requirement 4.1)
            if not compatibility.is_compatible:
                continue
            
            # Find common availability periods
            common_availabilities = self.availability_manager.find_common_availability(
                artist_id,
                venue.id
            )
            
            # Exclude venues with no common availability (Requirement 6.4)
            if not common_availabilities:
                continue
            
            # Create the match object
            match = VenueMatch(
                venue=venue,
                compatibility_score=compatibility.score,
                is_compatible=compatibility.is_compatible,
                common_availabilities=common_availabilities,
                unmatched_requirements=compatibility.unmatched_requirements
            )
            
            matches.append(match)
        
        # Apply filters if provided
        if filters:
            matches = self._apply_venue_filters(matches, filters, artist_id)
        
        # Sort by compatibility score in descending order (Requirement 5.5)
        matches.sort(key=lambda m: m.compatibility_score, reverse=True)
        
        return Result.ok(matches)
    
    def search_artists_for_venue(
        self,
        venue_id: str,
        filters: Optional[ArtistSearchFilters] = None
    ) -> Result[List[ArtistMatch]]:
        """
        Search for artists compatible with a venue.
        
        This method:
        1. Retrieves the venue profile
        2. Gets all artist profiles
        3. Evaluates technical compatibility using MatchEngine
        4. Checks for common availability using AvailabilityManager
        5. Applies filters (availability, art type, min compatibility score)
        6. Sorts results by compatibility score (descending)
        
        Args:
            venue_id: The ID of the venue searching for artists
            filters: Optional filters to apply to the search results
            
        Returns:
            Result containing a list of ArtistMatch objects sorted by compatibility score,
            or error details if the venue profile is not found
            
        Requirements:
            - 3.1: Returns artists with technical compatibility
            - 3.2: Filters by availability when specified
            - 3.3: Filters by art type when specified
        """
        # Retrieve the venue profile
        venue_result = self.profile_manager.get_venue_profile(venue_id)
        if not venue_result.success:
            return venue_result
        
        venue = venue_result.data
        
        # Get all artist profiles
        all_artists = self._get_all_artists()
        
        # Evaluate each artist and create matches
        matches = []
        for artist in all_artists:
            # Evaluate technical compatibility
            compatibility = self.match_engine.evaluate_compatibility(
                artist.technical_requirements,
                venue.technical_capabilities
            )
            
            # Only include technically compatible artists (Requirement 3.1)
            if not compatibility.is_compatible:
                continue
            
            # Find common availability periods
            common_availabilities = self.availability_manager.find_common_availability(
                artist.id,
                venue_id
            )
            
            # Exclude artists with no common availability (Requirement 6.4)
            if not common_availabilities:
                continue
            
            # Create the match object
            match = ArtistMatch(
                artist=artist,
                compatibility_score=compatibility.score,
                is_compatible=compatibility.is_compatible,
                common_availabilities=common_availabilities,
                unmatched_requirements=compatibility.unmatched_requirements
            )
            
            matches.append(match)
        
        # Apply filters if provided
        if filters:
            matches = self._apply_artist_filters(matches, filters, venue_id)
        
        # Sort by compatibility score in descending order (Requirement 5.5)
        matches.sort(key=lambda m: m.compatibility_score, reverse=True)
        
        return Result.ok(matches)
    
    def _get_all_venues(self) -> List[VenueProfile]:
        """
        Get all venue profiles from the profile manager.
        
        Returns:
            List of all venue profiles
        """
        result = self.profile_manager.get_all_venue_profiles()
        if result.success:
            return result.data
        return []
    
    def _get_all_artists(self) -> List[ArtistProfile]:
        """
        Get all artist profiles from the profile manager.
        
        Returns:
            List of all artist profiles
        """
        result = self.profile_manager.get_all_artist_profiles()
        if result.success:
            return result.data
        return []
    
    def _apply_venue_filters(
        self,
        matches: List[VenueMatch],
        filters: VenueSearchFilters,
        artist_id: str
    ) -> List[VenueMatch]:
        """
        Apply search filters to venue matches.
        
        Args:
            matches: List of venue matches to filter
            filters: Filters to apply
            artist_id: ID of the artist (for availability filtering)
            
        Returns:
            Filtered list of venue matches
        """
        filtered_matches = matches
        
        # Filter by availability date range (Requirement 4.2)
        if filters.date_range:
            filtered_matches = [
                match for match in filtered_matches
                if self._has_availability_in_range(
                    match.common_availabilities,
                    filters.date_range
                )
            ]
        
        # Filter by geographic location (Requirement 4.3)
        if filters.location:
            filtered_matches = [
                match for match in filtered_matches
                if self._is_within_geographic_area(
                    match.venue.basic_info.address,
                    filters.location
                )
            ]
        
        # Filter by minimum compatibility score
        if filters.min_compatibility_score is not None:
            filtered_matches = [
                match for match in filtered_matches
                if match.compatibility_score >= filters.min_compatibility_score
            ]
        
        return filtered_matches
    
    def _apply_artist_filters(
        self,
        matches: List[ArtistMatch],
        filters: ArtistSearchFilters,
        venue_id: str
    ) -> List[ArtistMatch]:
        """
        Apply search filters to artist matches.
        
        Args:
            matches: List of artist matches to filter
            filters: Filters to apply
            venue_id: ID of the venue (for availability filtering)
            
        Returns:
            Filtered list of artist matches
        """
        filtered_matches = matches
        
        # Filter by availability date range (Requirement 3.2)
        if filters.date_range:
            filtered_matches = [
                match for match in filtered_matches
                if self._has_availability_in_range(
                    match.common_availabilities,
                    filters.date_range
                )
            ]
        
        # Filter by art type (Requirement 3.3)
        if filters.art_type:
            filtered_matches = [
                match for match in filtered_matches
                if match.artist.basic_info.art_type in filters.art_type
            ]
        
        # Filter by minimum compatibility score
        if filters.min_compatibility_score is not None:
            filtered_matches = [
                match for match in filtered_matches
                if match.compatibility_score >= filters.min_compatibility_score
            ]
        
        return filtered_matches
    
    def _has_availability_in_range(
        self,
        common_availabilities: List[DateRange],
        date_range: DateRange
    ) -> bool:
        """
        Check if any common availability overlaps with the specified date range.
        
        Args:
            common_availabilities: List of common availability periods
            date_range: Date range to check for overlap
            
        Returns:
            True if there is at least one overlapping period
        """
        for availability in common_availabilities:
            # Check if there's any overlap
            if (availability.start_date < date_range.end_date and
                availability.end_date > date_range.start_date):
                return True
        return False
    
    def _is_within_geographic_area(
        self,
        address,
        geographic_area: GeographicArea
    ) -> bool:
        """
        Check if a venue's address is within the specified geographic area.
        
        Args:
            address: The venue's address
            geographic_area: The geographic area to check
            
        Returns:
            True if the venue is within the specified radius
        """
        # If the venue doesn't have coordinates, we can't filter by location
        if not address.coordinates:
            return False
        
        # Calculate distance using Haversine formula
        distance_km = self._calculate_distance(
            address.coordinates,
            geographic_area.center
        )
        
        return distance_km <= geographic_area.radius_km
    
    def _calculate_distance(
        self,
        coord1: Coordinates,
        coord2: Coordinates
    ) -> float:
        """
        Calculate the distance between two coordinates using the Haversine formula.
        
        Args:
            coord1: First coordinate
            coord2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        import math
        
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert latitude and longitude to radians
        lat1 = math.radians(coord1.latitude)
        lon1 = math.radians(coord1.longitude)
        lat2 = math.radians(coord2.latitude)
        lon2 = math.radians(coord2.longitude)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return distance
