"""
MercadoLivre Service
ITIL Activity: Deliver & Support (ML Business Logic)
"""
from typing import List, Dict, Any, Optional
from .base_service import BaseService
from ..repositories.ml_repository import MLRepository
import logging

logger = logging.getLogger(__name__)


class MLService(BaseService):
    """Service for MercadoLivre business logic"""
    
    def __init__(self, repository: MLRepository):
        super().__init__(repository)
        self.repository: MLRepository = repository
    
    def get_ml_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get MercadoLivre products"""
        try:
            products = self.repository.get_ml_products(limit)
            return [self._enrich_ml_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error getting ML products: {e}")
            raise
    
    def get_featured_deals(
        self,
        min_discount: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get featured deals (high discount products)"""
        try:
            products = self.repository.get_featured_deals(min_discount, limit)
            return [self._enrich_ml_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error getting ML deals: {e}")
            raise
    
    def get_product_by_mlb_id(self, mlb_id: str) -> Optional[Dict[str, Any]]:
        """Get product by MLB ID"""
        try:
            product = self.repository.get_by_mlb_id(mlb_id)
            if product:
                return self._enrich_ml_product(product)
            return None
        except Exception as e:
            logger.error(f"Error getting ML product {mlb_id}: {e}")
            raise
    
    def _enrich_ml_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich ML product with calculated fields"""
        if not product:
            return product
        
        # Add platform
        product["platform"] = "mercadolivre"
        
        # Is featured deal?
        if product.get("discount_percentage", 0) >= 50:
            product["is_hot_deal"] = True
        
        return product
