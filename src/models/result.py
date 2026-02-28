"""Result type for explicit error handling."""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Dict, Any
from .enums import ErrorCode


T = TypeVar('T')


@dataclass
class ErrorDetails:
    """Details about an error."""
    
    code: ErrorCode
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class Result(Generic[T]):
    """Result type that can represent success or failure."""
    
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetails] = None
    
    @staticmethod
    def ok(data: T) -> 'Result[T]':
        """Create a successful result."""
        return Result(success=True, data=data, error=None)
    
    @staticmethod
    def fail(error: ErrorDetails) -> 'Result[T]':
        """Create a failed result."""
        return Result(success=False, data=None, error=error)
