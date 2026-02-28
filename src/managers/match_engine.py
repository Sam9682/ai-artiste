"""Match engine for evaluating technical compatibility between artists and venues."""

from typing import Union
from src.models.technical import (
    TechnicalRequirements,
    TechnicalCapabilities,
    SpaceRequirements,
    SpaceCapabilities,
    AudioRequirements,
    AudioCapabilities,
    LightingRequirements,
    LightingCapabilities,
    PowerRequirements,
    PowerCapabilities
)


class MatchEngine:
    """Evaluates technical compatibility between artists and venues."""

    def calculate_compatibility_score(
        self,
        artist_requirements: TechnicalRequirements,
        venue_capabilities: TechnicalCapabilities
    ) -> float:
        """
        Calculate a numerical compatibility score based on the percentage of requirements satisfied.

        This method evaluates how well a venue's capabilities match an artist's requirements
        and returns a score between 0.0 (no requirements satisfied) and 1.0 (all requirements satisfied).

        Args:
            artist_requirements: Complete technical requirements from the artist
            venue_capabilities: Complete technical capabilities of the venue

        Returns:
            float: Compatibility score between 0.0 and 1.0, representing the percentage
                   of requirements that are satisfied by the venue

        Examples:
            >>> from src.models.technical import TechnicalRequirements, TechnicalCapabilities
            >>> from src.models.technical import SpaceRequirements, SpaceCapabilities
            >>> artist_reqs = TechnicalRequirements(
            ...     space_requirements=SpaceRequirements(min_area=100, min_height=3)
            ... )
            >>> venue_caps = TechnicalCapabilities(
            ...     space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor")
            ... )
            >>> engine = MatchEngine()
            >>> score = engine.calculate_compatibility_score(artist_reqs, venue_caps)
            >>> score
            1.0
        """
        total_requirements = 0
        satisfied_requirements = 0

        # Check space requirements (always present)
        total_requirements += 1
        if self.check_requirement(artist_requirements.space_requirements, venue_capabilities):
            satisfied_requirements += 1

        # Check audio requirements if specified
        if artist_requirements.audio_requirements is not None:
            total_requirements += 1
            if self.check_requirement(artist_requirements.audio_requirements, venue_capabilities):
                satisfied_requirements += 1

        # Check lighting requirements if specified
        if artist_requirements.lighting_requirements is not None:
            total_requirements += 1
            if self.check_requirement(artist_requirements.lighting_requirements, venue_capabilities):
                satisfied_requirements += 1

        # Check power requirements if specified
        if artist_requirements.power_requirements is not None:
            total_requirements += 1
            if self.check_requirement(artist_requirements.power_requirements, venue_capabilities):
                satisfied_requirements += 1

        # Calculate compatibility score (percentage of satisfied requirements)
        return satisfied_requirements / total_requirements if total_requirements > 0 else 0.0

    def evaluate_compatibility(
        self,
        artist_requirements: TechnicalRequirements,
        venue_capabilities: TechnicalCapabilities
    ) -> 'CompatibilityResult':
        """
        Evaluate the complete technical compatibility between an artist and a venue.

        This method checks all technical requirements of an artist against the venue's
        capabilities, calculates a compatibility score, and identifies any unmatched
        requirements.

        Args:
            artist_requirements: Complete technical requirements from the artist
            venue_capabilities: Complete technical capabilities of the venue

        Returns:
            CompatibilityResult containing:
                - is_compatible: True if all requirements are satisfied
                - score: Compatibility score (0.0 to 1.0)
                - unmatched_requirements: List of requirements that are not satisfied

        Examples:
            >>> from src.models.technical import TechnicalRequirements, TechnicalCapabilities
            >>> from src.models.technical import SpaceRequirements, SpaceCapabilities
            >>> artist_reqs = TechnicalRequirements(
            ...     space_requirements=SpaceRequirements(min_area=100, min_height=3)
            ... )
            >>> venue_caps = TechnicalCapabilities(
            ...     space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor")
            ... )
            >>> engine = MatchEngine()
            >>> result = engine.evaluate_compatibility(artist_reqs, venue_caps)
            >>> result.is_compatible
            True
            >>> result.score
            1.0
        """
        from src.models.compatibility import CompatibilityResult

        unmatched_requirements = []

        # Check space requirements (always present)
        if not self.check_requirement(artist_requirements.space_requirements, venue_capabilities):
            unmatched_requirements.append(artist_requirements.space_requirements)

        # Check audio requirements if specified
        if artist_requirements.audio_requirements is not None:
            if not self.check_requirement(artist_requirements.audio_requirements, venue_capabilities):
                unmatched_requirements.append(artist_requirements.audio_requirements)

        # Check lighting requirements if specified
        if artist_requirements.lighting_requirements is not None:
            if not self.check_requirement(artist_requirements.lighting_requirements, venue_capabilities):
                unmatched_requirements.append(artist_requirements.lighting_requirements)

        # Check power requirements if specified
        if artist_requirements.power_requirements is not None:
            if not self.check_requirement(artist_requirements.power_requirements, venue_capabilities):
                unmatched_requirements.append(artist_requirements.power_requirements)

        # Calculate compatibility score using the dedicated method
        score = self.calculate_compatibility_score(artist_requirements, venue_capabilities)

        # Determine if compatible (all requirements must be satisfied)
        is_compatible = len(unmatched_requirements) == 0

        return CompatibilityResult(
            is_compatible=is_compatible,
            score=score,
            unmatched_requirements=unmatched_requirements
        )

    def check_requirement(
        self,
        requirement: Union[
            SpaceRequirements,
            AudioRequirements,
            LightingRequirements,
            PowerRequirements
        ],
        capabilities: TechnicalCapabilities
    ) -> bool:
        """
        Check if a single technical requirement is satisfied by venue capabilities.

        This method compares a specific requirement (space, audio, lighting, or power)
        against the corresponding capabilities of a venue to determine if the requirement
        is met.

        Args:
            requirement: A technical requirement (space, audio, lighting, or power)
            capabilities: The complete technical capabilities of a venue

        Returns:
            True if the requirement is satisfied, False otherwise

        Examples:
            >>> space_req = SpaceRequirements(min_area=100, min_height=3)
            >>> venue_caps = TechnicalCapabilities(
            ...     space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor")
            ... )
            >>> engine = MatchEngine()
            >>> engine.check_requirement(space_req, venue_caps)
            True
        """
        # Determine the type of requirement and check accordingly
        if isinstance(requirement, SpaceRequirements):
            return self._check_space_requirement(requirement, capabilities.space_capabilities)

        elif isinstance(requirement, AudioRequirements):
            if capabilities.audio_capabilities is None:
                # If venue has no audio capabilities, check if artist requires any
                return not requirement.sound_system
            return self._check_audio_requirement(requirement, capabilities.audio_capabilities)

        elif isinstance(requirement, LightingRequirements):
            if capabilities.lighting_capabilities is None:
                # If venue has no lighting capabilities, check if artist requires any
                return not requirement.professional_lighting
            return self._check_lighting_requirement(requirement, capabilities.lighting_capabilities)

        elif isinstance(requirement, PowerRequirements):
            if capabilities.power_capabilities is None:
                # If venue has no power capabilities, requirement cannot be met
                return False
            return self._check_power_requirement(requirement, capabilities.power_capabilities)

        # Unknown requirement type
        return False

    def _check_space_requirement(
        self,
        requirement: SpaceRequirements,
        capability: SpaceCapabilities
    ) -> bool:
        """
        Check if space requirements are met by venue space capabilities.

        Args:
            requirement: Space requirements from artist
            capability: Space capabilities of venue

        Returns:
            True if all space requirements are satisfied
        """
        # Check minimum area
        if requirement.min_area is not None:
            if capability.area < requirement.min_area:
                return False

        # Check minimum height
        if requirement.min_height is not None:
            if capability.height < requirement.min_height:
                return False

        # Check indoor/outdoor preference
        if requirement.indoor_outdoor is not None:
            if requirement.indoor_outdoor == "both":
                # Artist accepts both, so any venue type is fine
                pass
            elif requirement.indoor_outdoor != capability.type and capability.type != "both":
                # Artist requires specific type and venue doesn't match
                return False

        return True

    def _check_audio_requirement(
        self,
        requirement: AudioRequirements,
        capability: AudioCapabilities
    ) -> bool:
        """
        Check if audio requirements are met by venue audio capabilities.

        Args:
            requirement: Audio requirements from artist
            capability: Audio capabilities of venue

        Returns:
            True if all audio requirements are satisfied
        """
        # Check sound system requirement
        if requirement.sound_system and not capability.sound_system:
            return False

        # Check acoustic treatment if specified
        if requirement.acoustic_treatment is not None:
            if requirement.acoustic_treatment and not capability.acoustic_treatment:
                return False

        # Check channel count if specified
        if requirement.channels is not None:
            if capability.channels < requirement.channels:
                return False

        return True

    def _check_lighting_requirement(
        self,
        requirement: LightingRequirements,
        capability: LightingCapabilities
    ) -> bool:
        """
        Check if lighting requirements are met by venue lighting capabilities.

        Args:
            requirement: Lighting requirements from artist
            capability: Lighting capabilities of venue

        Returns:
            True if all lighting requirements are satisfied
        """
        # Check professional lighting requirement
        if requirement.professional_lighting and not capability.professional_lighting:
            return False

        # Check dimmable if specified
        if requirement.dimmable is not None:
            if requirement.dimmable and not capability.dimmable:
                return False

        # Check color capable if specified
        if requirement.color_capable is not None:
            if requirement.color_capable and not capability.color_capable:
                return False

        return True

    def _check_power_requirement(
        self,
        requirement: PowerRequirements,
        capability: PowerCapabilities
    ) -> bool:
        """
        Check if power requirements are met by venue power capabilities.

        Args:
            requirement: Power requirements from artist
            capability: Power capabilities of venue

        Returns:
            True if all power requirements are satisfied
        """
        # Check voltage match (must be exact)
        if requirement.voltage != capability.voltage:
            return False

        # Check amperage (venue must provide at least what's required)
        if capability.amperage < requirement.amperage:
            return False

        return True


