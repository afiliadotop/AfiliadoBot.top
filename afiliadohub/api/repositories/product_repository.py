"""
Product Repository
ITIL Activity: Obtain/Build (Product Data Access)
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from ..models.domain import Product


class ProductRepository(BaseRepository[Product]):
    """Repository for product data access"""
    
    @property
    def table_name(self) -> str:
        return "products"
    
    def get_by_store(self, store: str, limit: int = 100) -> List[Product]:
        """
        Get products by store.
        
        Args:
            store: Store name
            limit: Max results
            
        Returns:
            List of products
        """
        return self.get_all(filters={"store": store}, limit=limit)
    
    def get_active_products(self, limit: int = 100) -> List[Product]:
        """
        Get active products only.
        
        Args:
            limit: Max results
            
        Returns:
            List of active products
        """
        return self.get_all(filters={"active": True}, limit=limit)
    
    def search_by_name(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search products by name.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching products
        """
        result = self.client.table(self.table_name)\
            .select("*")\
            .ilike("name", f"%{query}%")\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    
    def get_by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get products within price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            limit: Max results
            
        Returns:
            List of products
        """
        query = self.client.table(self.table_name).select("*")
        
        if min_price is not None:
            query = query.gte("current_price", min_price)
        
        if max_price is not None:
            query = query.lte("current_price", max_price)
        
        result = query.limit(limit).execute()
        return result.data if result.data else []
    
    def get_by_commission_range(
        self,
        min_commission: float,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get products with minimum commission rate.
        
        Args:
            min_commission: Minimum commission %
            limit: Max results
            
        Returns:
            List of products
        """
        result = self.client.table(self.table_name)\
            .select("*")\
            .gte("commission_rate", min_commission)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
