"""
Base Repository Pattern
ITIL Activity: Obtain/Build (Data Access Layer)
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from abc import ABC, abstractmethod

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository providing common data access operations.
    
    Follows ITIL 4 Obtain/Build activity - abstracting data acquisition.
    """
    
    def __init__(self, client):
        """
        Initialize repository with database client.
        
        Args:
            client: Supabase client or similar
        """
        self.client = client
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Table name for this repository"""
        pass
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity or None if not found
        """
        result = self.client.table(self.table_name).select("*").eq("id", id).execute()
        return result.data[0] if result.data else None
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[T]:
        """
        Get all entities with optional filters.
        
        Args:
            filters: Dict of column: value filters
            limit: Max results
            
        Returns:
            List of entities
        """
        query = self.client.table(self.table_name).select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.limit(limit).execute()
        return result.data if result.data else []
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create new entity.
        
        Args:
            data: Entity data
            
        Returns:
            Created entity
        """
        result = self.client.table(self.table_name).insert(data).execute()
        return result.data[0] if result.data else None
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Update entity by ID.
        
        Args:
            id: Entity ID
            data: Update data
            
        Returns:
            Updated entity or None
        """
        result = self.client.table(self.table_name).update(data).eq("id", id).execute()
        return result.data[0] if result.data else None
    
    def delete(self, id: int) -> bool:
        """
        Delete entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted successfully
        """
        result = self.client.table(self.table_name).delete().eq("id", id).execute()
        return len(result.data) > 0 if result.data else False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filters.
        
        Args:
            filters: Dict of column: value filters
            
        Returns:
            Count of entities
        """
        query = self.client.table(self.table_name).select("id", count="exact")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.count if hasattr(result, 'count') else 0
