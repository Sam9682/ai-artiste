"""Compatibility result models."""

from dataclasses import dataclass
from typing import List, Union

from .technical import (
    SpaceRequirements,
    AudioRequirements,
    LightingRequirements,
    PowerRequirements
)


# Type alias for any technical requirement
TechnicalRequirement = Union[
    SpaceRequirements,
    AudioRequirements,
    LightingRequirements,
    PowerRequirements
]


@dataclass
class CompatibilityResult:
    """Result of evaluating compatibility between an artist and a venue."""
    
    is_compatible: bool
    score: float
    unmatched_requirements: List[TechnicalRequirement]
