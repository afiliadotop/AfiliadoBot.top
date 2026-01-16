"""
Shopee Repository
ITIL Activity: Obtain/Build (Shopee Data Access)
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository


class ShopeeRepository(BaseRepository):
    """Repository for Shopee-specific data access"""
    
    @property
    def table_name(self) -> str:
        return "products"
    
    def get_shopee_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all Shopee products"""
        return self.get_all(filters={"store": "shopee"}, limit=limit)
    
    def get_by_item_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get product by Shopee item_id"""
        result = self.client.table(self.table_name)\
            .select("*")\
            .eq("store", "shopee")\
            .contains("affiliate_link", item_id)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def get_high_commission_products(
        self,
        min_commission: float = 10.0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get Shopee products with high commission rates"""
        result = self.client.table(self.table_name)\
            .select("*")\
            .eq("store", "shopee")\
            .gte("commission_rate", min_commission)\
            .order("commission_rate", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
    
    def search_shopee_products(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search Shopee products by name"""
        result = self.client.table(self.table_name)\
            .select("*")\
            .eq("store", "shopee")\
            .ilike("name", f"%{query}%")\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
