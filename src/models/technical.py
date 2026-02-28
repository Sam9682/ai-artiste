"""Technical requirements and capabilities models."""

from dataclasses import dataclass, field
from typing import Optional, List, Literal


@dataclass
class SpaceRequirements:
    """Space requirements for an artist."""
    
    min_area: Optional[float] = None  # in m²
    min_height: Optional[float] = None  # in m
    indoor_outdoor: Optional[Literal["indoor", "outdoor", "both"]] = None


@dataclass
class AudioRequirements:
    """Audio requirements for an artist."""
    
    sound_system: bool = False
    acoustic_treatment: Optional[bool] = None
    channels: Optional[int] = None


@dataclass
class LightingRequirements:
    """Lighting requirements for an artist."""
    
    professional_lighting: bool = False
    dimmable: Optional[bool] = None
    color_capable: Optional[bool] = None


@dataclass
class PowerRequirements:
    """Power requirements for an artist."""
    
    voltage: int
    amperage: int


@dataclass
class TechnicalRequirements:
    """Complete technical requirements for an artist."""
    
    space_requirements: SpaceRequirements = field(default_factory=SpaceRequirements)
    audio_requirements: Optional[AudioRequirements] = None
    lighting_requirements: Optional[LightingRequirements] = None
    power_requirements: Optional[PowerRequirements] = None
    other_requirements: List[str] = field(default_factory=list)


@dataclass
class SpaceCapabilities:
    """Space capabilities of a venue."""
    
    area: float  # in m²
    height: float  # in m
    type: Literal["indoor", "outdoor", "both"]


@dataclass
class AudioCapabilities:
    """Audio capabilities of a venue."""
    
    sound_system: bool
    acoustic_treatment: bool
    channels: int


@dataclass
class LightingCapabilities:
    """Lighting capabilities of a venue."""
    
    professional_lighting: bool
    dimmable: bool
    color_capable: bool


@dataclass
class PowerCapabilities:
    """Power capabilities of a venue."""
    
    voltage: int
    amperage: int


@dataclass
class TechnicalCapabilities:
    """Complete technical capabilities of a venue."""
    
    space_capabilities: SpaceCapabilities
    audio_capabilities: Optional[AudioCapabilities] = None
    lighting_capabilities: Optional[LightingCapabilities] = None
    power_capabilities: Optional[PowerCapabilities] = None
    other_capabilities: List[str] = field(default_factory=list)
