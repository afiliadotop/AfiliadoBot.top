"""
Shopee Service
ITIL Activity: Deliver & Support (Shopee Business Logic)
"""
from typing import List, Dict, Any, Optional
from .base_service import BaseService
from ..repositories.shopee_repository import ShopeeRepository
import logging

logger = logging.getLogger(__name__)


class ShopeeService(BaseService):
    """Service for Shopee business logic"""
    
    def __init__(self, repository: ShopeeRepository):
        super().__init__(repository)
        self.repository: ShopeeRepository = repository
    
    def get_shopee_products(
        self,
        min_commission: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get Shopee products with optional commission filter.
        
        Args:
            min_commission: Minimum commission rate
            limit: Max results
            
        Returns:
            List of enriched Shopee products
        """
        try:
            if min_commission:
                products = self.repository.get_high_commission_products(
                    min_commission,
                    limit
                )
            else:
                products = self.repository.get_shopee_products(limit)
            
            return [self._enrich_shopee_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error getting Shopee products: {e}")
            raise
    
    def search_shopee_products(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search Shopee products by name"""
        try:
            products = self.repository.search_shopee_products(query, limit)
            return [self._enrich_shopee_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error searching Shopee products: {e}")
            raise
    
    def get_product_by_item_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get Shopee product by item_id"""
        try:
            product = self.repository.get_by_item_id(item_id)
            if product:
                return self._enrich_shopee_product(product)
            return None
        except Exception as e:
            logger.error(f"Error getting Shopee product {item_id}: {e}")
            raise
    
    def _enrich_shopee_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich Shopee product with calculated fields"""
        if not product:
            return product
        
        # Calculate discount %
        if product.get("original_price") and product.get("current_price"):
            original = product["original_price"]
            current = product["current_price"]
            if original > current:
                discount_pct = ((original - current) / original) * 100
                product["discount_percent"] = round(discount_pct, 2)
        
        # Calculate estimated commission
        if product.get("commission_rate") and product.get("current_price"):
            commission = (product["current_price"] * product["commission_rate"]) / 100
            product["estimated_commission"] = round(commission, 2)
        
        # Add platform
        product["platform"] = "shopee"
        
        return product
