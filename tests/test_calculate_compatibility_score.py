"""Tests for the calculate_compatibility_score method."""

import pytest
from src.managers.match_engine import MatchEngine
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


class TestCalculateCompatibilityScore:
    """Tests for the calculate_compatibility_score method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MatchEngine()
    
    def test_perfect_score_all_requirements_satisfied(self):
        """Test that perfect compatibility returns score of 1.0."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3),
            audio_requirements=AudioRequirements(sound_system=True, channels=8),
            lighting_requirements=LightingRequirements(professional_lighting=True),
            power_requirements=PowerRequirements(voltage=220, amperage=50)
        )
        
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=True, channels=16),
            lighting_capabilities=LightingCapabilities(professional_lighting=True, dimmable=True, color_capable=True),
            power_capabilities=PowerCapabilities(voltage=220, amperage=100)
        )
        
        score = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        assert score == 1.0
    
    def test_zero_score_no_requirements_satisfied(self):
        """Test that no compatibility returns score of 0.0."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=500, min_height=10),
            audio_requirements=AudioRequirements(sound_system=True, channels=32),
            lighting_requirements=LightingRequirements(professional_lighting=True),
            power_requirements=PowerRequirements(voltage=220, amperage=200)
        )
        
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=50, height=2, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=False, acoustic_treatment=False, channels=0),
            lighting_capabilities=LightingCapabilities(professional_lighting=False, dimmable=False, color_capable=False),
            power_capabilities=PowerCapabilities(voltage=110, amperage=20)
        )
        
        score = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        assert score == 0.0
    
    def test_partial_score_half_requirements_satisfied(self):
        """Test that partial compatibility returns correct fractional score."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3),
            audio_requirements=AudioRequirements(sound_system=True, channels=16),
            lighting_requirements=LightingRequirements(professional_lighting=True),
            power_requirements=PowerRequirements(voltage=220, amperage=50)
        )
        
        # Venue satisfies space and lighting, but not audio and power
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=False, channels=8),  # Insufficient channels
            lighting_capabilities=LightingCapabilities(professional_lighting=True, dimmable=False, color_capable=False),
            power_capabilities=PowerCapabilities(voltage=110, amperage=50)  # Wrong voltage
        )
        
        score = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        assert score == 0.5  # 2 out of 4 requirements satisfied
    
    def test_score_with_minimal_requirements(self):
        """Test score calculation when artist has only space requirements."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=50, min_height=2.5)
        )
        
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=100, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=True, channels=8),
            lighting_capabilities=LightingCapabilities(professional_lighting=True, dimmable=True, color_capable=True),
            power_capabilities=PowerCapabilities(voltage=220, amperage=50)
        )
        
        score = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        assert score == 1.0
    
    def test_score_two_thirds_satisfied(self):
        """Test that 2 out of 3 requirements gives approximately 0.667 score."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100),
            audio_requirements=AudioRequirements(sound_system=True),
            lighting_requirements=LightingRequirements(professional_lighting=True)
        )
        
        # Venue satisfies space and audio, but not lighting
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=3, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=False, channels=8),
            lighting_capabilities=LightingCapabilities(professional_lighting=False, dimmable=False, color_capable=False)
        )
        
        score = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        assert abs(score - 2/3) < 0.01  # Approximately 0.667
    
    def test_score_one_out_of_two_satisfied(self):
        """Test that 1 out of 2 requirements gives 0.5 score."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100),
            audio_requirements=AudioRequirements(sound_system=True)
        )
        
        # Venue satisfies space but not audio
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=3, type="indoor"),
            audio_capabilities=None
        )
        
        score = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        assert score == 0.5
    
    def test_score_consistency_with_evaluate_compatibility(self):
        """Test that calculate_compatibility_score returns same score as evaluate_compatibility."""
        requirements = TechnicalRequirements(
            space_requirements=SpaceRequirements(min_area=100, min_height=3),
            audio_requirements=AudioRequirements(sound_system=True, channels=8),
            lighting_requirements=LightingRequirements(professional_lighting=True)
        )
        
        capabilities = TechnicalCapabilities(
            space_capabilities=SpaceCapabilities(area=150, height=4, type="indoor"),
            audio_capabilities=AudioCapabilities(sound_system=True, acoustic_treatment=False, channels=16),
            lighting_capabilities=LightingCapabilities(professional_lighting=False, dimmable=False, color_capable=False)
        )
        
        # Get score from calculate_compatibility_score
        score_direct = self.engine.calculate_compatibility_score(requirements, capabilities)
        
        # Get score from evaluate_compatibility
        result = self.engine.evaluate_compatibility(requirements, capabilities)
        score_from_evaluate = result.score
        
        # Both should return the same score
        assert score_direct == score_from_evaluate
