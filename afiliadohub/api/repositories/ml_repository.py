"""
MercadoLivre Repository
ITIL Activity: Obtain/Build (ML Data Access)
"""
from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository


class MLRepository(BaseRepository):
    """Repository for MercadoLivre-specific data access"""
    
    @property
    def table_name(self) -> str:
        return "products"
    
    def get_ml_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all MercadoLivre products"""
        return self.get_all(filters={"store": "mercado_livre"}, limit=limit)
    
    def get_by_mlb_id(self, mlb_id: str) -> Optional[Dict[str, Any]]:
        """Get product by MLB ID"""
        result = self.client.table(self.table_name)\
            .select("*")\
            .eq("store", "mercado_livre")\
            .contains("affiliate_link", mlb_id)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def get_featured_deals(self, min_discount: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """Get ML products with high discounts (deals)"""
        result = self.client.table(self.table_name)\
            .select("*")\
            .eq("store", "mercado_livre")\
            .gte("discount_percentage", min_discount)\
            .order("discount_percentage", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data if result.data else []
