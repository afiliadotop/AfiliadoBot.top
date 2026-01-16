"""
Base Service Layer
ITIL Activity: Deliver & Support (Business Logic)
"""
from abc import ABC
from typing import Generic, TypeVar

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Base service providing common business logic operations.
    
    Follows ITIL 4 Deliver & Support activity - orchestrating business logic.
    """
    
    def __init__(self, repository):
        """
        Initialize service with repository.
        
        Args:
            repository: Repository instance for data access
        """
        self.repository = repository
    
    def _validate_data(self, data: dict) -> bool:
        """
        Validate data before operations.
        
        Override in subclasses for specific validation.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        return True
    
    def _format_response(self, data):
        """
        Format repository response for API.
        
        Override in subclasses for specific formatting.
        
        Args:
            data: Raw data from repository
            
        Returns:
            Formatted data
        """
        return data
