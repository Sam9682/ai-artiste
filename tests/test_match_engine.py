"""Tests for the MatchEngine class."""

import pytest
from src.managers.match_engine import MatchEngine
from src.models.technical import (
    SpaceRequirements,
    SpaceCapabilities,
    AudioRequirements,
    AudioCapabilities,
    LightingRequirements,
    LightingCapabilities,
    PowerRequirements,
    PowerCapabilities,
    TechnicalCapabilities
)


class TestCheckRequirement:
    """Tests for the check_requirement method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MatchEngine()
    
    # Space requirement tests
    
    def test_space_requirement_satisfied_with_exact_match(self):
        """Test that space requirement is satisfied when venue matches exactly."""
        requirement = SpaceRequirements(min_area=100, min_height=3, indoor_outdoor="indoor")
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor")
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_space_requirement_satisfied_with_excess_capacity(self):
        """Test that space requirement is satisfied when venue exceeds requirements."""
        requirement = SpaceRequirements(min_area=100, min_height=3)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=200, height=5, type="indoor")
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_space_requirement_not_satisfied_insufficient_area(self):
        """Test that space requirement fails when area is insufficient."""
        requirement = SpaceRequirements(min_area=100)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=50, height=3, type="indoor")
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_space_requirement_not_satisfied_insufficient_height(self):
        """Test that space requirement fails when height is insufficient."""
        requirement = SpaceRequirements(min_height=5)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor")
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_space_requirement_indoor_outdoor_mismatch(self):
        """Test that space requirement fails when indoor/outdoor type doesn't match."""
        requirement = SpaceRequirements(indoor_outdoor="indoor")
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="outdoor")
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_space_requirement_both_accepts_any_venue_type(self):
        """Test that 'both' requirement accepts any venue type."""
        requirement = SpaceRequirements(indoor_outdoor="both")
        
        # Test with indoor venue
        capabilities_indoor = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor")
        )
        assert self.engine.check_requirement(requirement, capabilities_indoor) is True
        
        # Test with outdoor venue
        capabilities_outdoor = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="outdoor")
        )
        assert self.engine.check_requirement(requirement, capabilities_outdoor) is True
    
    def test_space_requirement_venue_both_accepts_any_artist_preference(self):
        """Test that venue with 'both' type satisfies any artist preference."""
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="both")
        )
        
        # Test with indoor requirement
        requirement_indoor = SpaceRequirements(indoor_outdoor="indoor")
        assert self.engine.check_requirement(requirement_indoor, capabilities) is True
        
        # Test with outdoor requirement
        requirement_outdoor = SpaceRequirements(indoor_outdoor="outdoor")
        assert self.engine.check_requirement(requirement_outdoor, capabilities) is True
    
    def test_space_requirement_no_preferences_specified(self):
        """Test that space requirement with no specific preferences is satisfied."""
        requirement = SpaceRequirements()
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor")
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    # Audio requirement tests
    
    def test_audio_requirement_satisfied_with_sound_system(self):
        """Test that audio requirement is satisfied when venue has sound system."""
        requirement = AudioRequirements(sound_system=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(
                sound_system=True,
                acoustic_treatment=False,
                channels=8
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_audio_requirement_not_satisfied_missing_sound_system(self):
        """Test that audio requirement fails when venue lacks sound system."""
        requirement = AudioRequirements(sound_system=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(
                sound_system=False,
                acoustic_treatment=False,
                channels=0
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_audio_requirement_satisfied_with_acoustic_treatment(self):
        """Test that audio requirement is satisfied when venue has acoustic treatment."""
        requirement = AudioRequirements(sound_system=True, acoustic_treatment=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(
                sound_system=True,
                acoustic_treatment=True,
                channels=8
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_audio_requirement_not_satisfied_missing_acoustic_treatment(self):
        """Test that audio requirement fails when venue lacks acoustic treatment."""
        requirement = AudioRequirements(sound_system=True, acoustic_treatment=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(
                sound_system=True,
                acoustic_treatment=False,
                channels=8
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_audio_requirement_satisfied_with_sufficient_channels(self):
        """Test that audio requirement is satisfied when venue has enough channels."""
        requirement = AudioRequirements(sound_system=True, channels=8)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(
                sound_system=True,
                acoustic_treatment=False,
                channels=16
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_audio_requirement_not_satisfied_insufficient_channels(self):
        """Test that audio requirement fails when venue has too few channels."""
        requirement = AudioRequirements(sound_system=True, channels=16)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(
                sound_system=True,
                acoustic_treatment=False,
                channels=8
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_audio_requirement_no_audio_capabilities_no_requirement(self):
        """Test that no audio requirement is satisfied when venue has no audio capabilities."""
        requirement = AudioRequirements(sound_system=False)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=None
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_audio_requirement_no_audio_capabilities_with_requirement(self):
        """Test that audio requirement fails when venue has no audio capabilities."""
        requirement = AudioRequirements(sound_system=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=None
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    # Lighting requirement tests
    
    def test_lighting_requirement_satisfied_with_professional_lighting(self):
        """Test that lighting requirement is satisfied when venue has professional lighting."""
        requirement = LightingRequirements(professional_lighting=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=LightingCapabilities(
                professional_lighting=True,
                dimmable=False,
                color_capable=False
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_lighting_requirement_not_satisfied_missing_professional_lighting(self):
        """Test that lighting requirement fails when venue lacks professional lighting."""
        requirement = LightingRequirements(professional_lighting=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=LightingCapabilities(
                professional_lighting=False,
                dimmable=False,
                color_capable=False
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_lighting_requirement_satisfied_with_dimmable(self):
        """Test that lighting requirement is satisfied when venue has dimmable lights."""
        requirement = LightingRequirements(professional_lighting=True, dimmable=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=LightingCapabilities(
                professional_lighting=True,
                dimmable=True,
                color_capable=False
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_lighting_requirement_not_satisfied_missing_dimmable(self):
        """Test that lighting requirement fails when venue lacks dimmable lights."""
        requirement = LightingRequirements(professional_lighting=True, dimmable=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=LightingCapabilities(
                professional_lighting=True,
                dimmable=False,
                color_capable=False
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_lighting_requirement_satisfied_with_color_capable(self):
        """Test that lighting requirement is satisfied when venue has color-capable lights."""
        requirement = LightingRequirements(professional_lighting=True, color_capable=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=LightingCapabilities(
                professional_lighting=True,
                dimmable=False,
                color_capable=True
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_lighting_requirement_not_satisfied_missing_color_capable(self):
        """Test that lighting requirement fails when venue lacks color-capable lights."""
        requirement = LightingRequirements(professional_lighting=True, color_capable=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=LightingCapabilities(
                professional_lighting=True,
                dimmable=False,
                color_capable=False
            )
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_lighting_requirement_no_lighting_capabilities_no_requirement(self):
        """Test that no lighting requirement is satisfied when venue has no lighting capabilities."""
        requirement = LightingRequirements(professional_lighting=False)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=None
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_lighting_requirement_no_lighting_capabilities_with_requirement(self):
        """Test that lighting requirement fails when venue has no lighting capabilities."""
        requirement = LightingRequirements(professional_lighting=True)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            lighting_capabilities=None
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    # Power requirement tests
    
    def test_power_requirement_satisfied_with_exact_match(self):
        """Test that power requirement is satisfied when voltage and amperage match."""
        requirement = PowerRequirements(voltage=220, amperage=50)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            power_capabilities=PowerCapabilities(voltage=220, amperage=50)
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_power_requirement_satisfied_with_excess_amperage(self):
        """Test that power requirement is satisfied when venue has more amperage."""
        requirement = PowerRequirements(voltage=220, amperage=50)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            power_capabilities=PowerCapabilities(voltage=220, amperage=100)
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is True
    
    def test_power_requirement_not_satisfied_voltage_mismatch(self):
        """Test that power requirement fails when voltage doesn't match."""
        requirement = PowerRequirements(voltage=220, amperage=50)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            power_capabilities=PowerCapabilities(voltage=110, amperage=50)
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_power_requirement_not_satisfied_insufficient_amperage(self):
        """Test that power requirement fails when amperage is insufficient."""
        requirement = PowerRequirements(voltage=220, amperage=100)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            power_capabilities=PowerCapabilities(voltage=220, amperage=50)
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False
    
    def test_power_requirement_no_power_capabilities(self):
        """Test that power requirement fails when venue has no power capabilities."""
        requirement = PowerRequirements(voltage=220, amperage=50)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            power_capabilities=None
        )
        
        assert self.engine.check_requirement(requirement, capabilities) is False


class TestEvaluateCompatibility:
    """Tests for the evaluate_compatibility method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MatchEngine()
    
    def test_fully_compatible_all_requirements_satisfied(self):
        """Test that fully compatible artist-venue pair returns is_compatible=True and score=1.0."""
        from src.models.technical import TechnicalRequirements
        from src.models.compatibility import CompatibilityResult
        
        # Artist with all types of requirements
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3, indoor_outdoor="indoor"),
            audio_requirements=AudioRequirements(sound_system=True, channels=8),
            lighting_requirements=LightingRequirements(professional_lighting=True, dimmable=True),
            power_requirements=PowerRequirements(voltage=220, amperage=50)
        )
        
        # Venue that satisfies all requirements
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=True, channels=16),
            lighting_capabilities=LightingCapabilities(professional_lighting=True, dimmable=True, color_capable=True),
            power_capabilities=PowerCapabilities(voltage=220, amperage=100)
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert isinstance(result, CompatibilityResult)
        assert result.is_compatible is True
        assert result.score == 1.0
        assert len(result.unmatched_requirements) == 0
    
    def test_incompatible_space_requirement_not_satisfied(self):
        """Test that incompatible pair due to space returns is_compatible=False with unmatched requirements."""
        from src.models.technical import TechnicalRequirements
        
        # Artist requires large space
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=200, min_height=5)
        )
        
        # Venue with insufficient space
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor")
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is False
        assert result.score == 0.0
        assert len(result.unmatched_requirements) == 1
        assert result.unmatched_requirements[0] == requirements.space_requirements
    
    def test_partial_compatibility_some_requirements_not_satisfied(self):
        """Test that partial compatibility returns correct score and unmatched requirements."""
        from src.models.technical import TechnicalRequirements
        
        # Artist with multiple requirements
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3),
            audio_requirements=AudioRequirements(sound_system=True, channels=16),
            lighting_requirements=LightingRequirements(professional_lighting=True),
            power_requirements=PowerRequirements(voltage=220, amperage=50)
        )
        
        # Venue that satisfies space and lighting, but not audio and power
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=False, channels=8),  # Insufficient channels
            lighting_capabilities=LightingCapabilities(professional_lighting=True, dimmable=False, color_capable=False),
            power_capabilities=PowerCapabilities(voltage=110, amperage=50)  # Wrong voltage
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is False
        assert result.score == 0.5  # 2 out of 4 requirements satisfied
        assert len(result.unmatched_requirements) == 2
        assert requirements.audio_requirements in result.unmatched_requirements
        assert requirements.power_requirements in result.unmatched_requirements
    
    def test_compatibility_with_minimal_requirements(self):
        """Test compatibility when artist has only space requirements."""
        from src.models.technical import TechnicalRequirements
        
        # Artist with only space requirements
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=2.5)
        )
        
        # Venue with all capabilities
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=True, channels=8),
            lighting_capabilities=LightingCapabilities(professional_lighting=True, dimmable=True, color_capable=True),
            power_capabilities=PowerCapabilities(voltage=220, amperage=50)
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is True
        assert result.score == 1.0
        assert len(result.unmatched_requirements) == 0
    
    def test_compatibility_score_calculation(self):
        """Test that compatibility score is calculated correctly as percentage of satisfied requirements."""
        from src.models.technical import TechnicalRequirements
        
        # Artist with 3 requirements
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100),
            audio_requirements=AudioRequirements(sound_system=True),
            lighting_requirements=LightingRequirements(professional_lighting=True)
        )
        
        # Venue that satisfies 2 out of 3 requirements (space and audio, but not lighting)
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=False, channels=8),
            lighting_capabilities=LightingCapabilities(professional_lighting=False, dimmable=False, color_capable=False)
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is False
        assert abs(result.score - 2/3) < 0.01  # Approximately 0.667
        assert len(result.unmatched_requirements) == 1
        assert requirements.lighting_requirements in result.unmatched_requirements
    
    def test_compatibility_with_no_optional_capabilities(self):
        """Test compatibility when venue has no optional capabilities (audio, lighting, power)."""
        from src.models.technical import TechnicalRequirements
        
        # Artist with only space requirements (no optional requirements)
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3)
        )
        
        # Venue with only space capabilities
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor"),
            audio_capabilities=None,
            lighting_capabilities=None,
            power_capabilities=None
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is True
        assert result.score == 1.0
        assert len(result.unmatched_requirements) == 0
    
    def test_incompatibility_when_artist_needs_audio_but_venue_has_none(self):
        """Test that artist requiring audio is incompatible with venue having no audio capabilities."""
        from src.models.technical import TechnicalRequirements
        
        # Artist requires audio
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100),
            audio_requirements=AudioRequirements(sound_system=True)
        )
        
        # Venue with no audio capabilities
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=3, type="indoor"),
            audio_capabilities=None
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is False
        assert result.score == 0.5  # 1 out of 2 requirements satisfied
        assert len(result.unmatched_requirements) == 1
        assert requirements.audio_requirements in result.unmatched_requirements
    
    def test_all_requirements_unmatched(self):
        """Test when all requirements are unmatched."""
        from src.models.technical import TechnicalRequirements
        
        # Artist with specific requirements
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=500, min_height=10),
            audio_requirements=AudioRequirements(sound_system=True, channels=32),
            lighting_requirements=LightingRequirements(professional_lighting=True, color_capable=True),
            power_requirements=PowerRequirements(voltage=220, amperage=200)
        )
        
        # Venue with minimal capabilities
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=50, height=2.5, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=False, acoustic_treatment=False, channels=0),
            lighting_capabilities=LightingCapabilities(professional_lighting=False, dimmable=False, color_capable=False),
            power_capabilities=PowerCapabilities(voltage=110, amperage=20)
        )
        
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        
        assert result.is_compatible is False
        assert result.score == 0.0
        assert len(result.unmatched_requirements) == 4
