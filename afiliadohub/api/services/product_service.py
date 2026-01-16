"""
Product Service
ITIL Activity: Deliver & Support (Product Business Logic)
"""
from typing import List, Optional, Dict, Any
from .base_service import BaseService
from ..models.domain import Product, ProductCreate, ProductUpdate, ProductFilter
from ..repositories.product_repository import ProductRepository
import logging

logger = logging.getLogger(__name__)


class ProductService(BaseService[Product]):
    """Service for product business logic"""
    
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
        self.repository: ProductRepository = repository
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get product by ID with business logic.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product data or None
        """
        try:
            product = self.repository.get_by_id(product_id)
            if product:
                return self._enrich_product(product)
            return None
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            raise
    
    def get_products(
        self,
        filters: Optional[ProductFilter] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get products with filters and business logic.
        
        Args:
            filters: Product filters
            limit: Max results
            
        Returns:
            List of products
        """
        try:
            if filters:
                products = self._apply_filters(filters, limit)
            else:
                products = self.repository.get_active_products(limit)
            
            return [self._enrich_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise
    
    def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """
        Create new product with validation.
        
        Args:
            product_data: Product creation data
            
        Returns:
            Created product
        """
        try:
            # Validate
            self._validate_product_data(product_data.dict())
            
            # Create
            product = self.repository.create(product_data.dict())
            
            logger.info(f"Product created: {product.get('id')}")
            return self._enrich_product(product)
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise
    
    def update_product(
        self,
        product_id: int,
        update_data: ProductUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update product with validation.
        
        Args:
            product_id: Product ID
            update_data: Update data
            
        Returns:
            Updated product or None
        """
        try:
            # Get current
            current = self.repository.get_by_id(product_id)
            if not current:
                return None
            
            # Validate
            data_dict = update_data.dict(exclude_unset=True)
            self._validate_product_data(data_dict)
            
            # Update
            product = self.repository.update(product_id, data_dict)
            
            logger.info(f"Product updated: {product_id}")
            return self._enrich_product(product) if product else None
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise
    
    def delete_product(self, product_id: int) -> bool:
        """
        Delete product (soft delete - mark inactive).
        
        Args:
            product_id: Product ID
            
        Returns:
            True if deleted
        """
        try:
            # Soft delete
            result = self.repository.update(product_id, {"active": False})
            
            logger.info(f"Product deleted: {product_id}")
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise
    
    def search_products(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search products by name.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            Matching products
        """
        try:
            products = self.repository.search_by_name(query, limit)
            return [self._enrich_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise
    
    def _apply_filters(self, filters: ProductFilter, limit: int) -> List:
        """Apply filters to product query"""
        filter_dict = {}
        
        if filters.store:
            filter_dict["store"] = filters.store
        
        if filters.category:
            filter_dict["category"] = filters.category
        
        if filters.active is not None:
            filter_dict["active"] = filters.active
        
        # Price range filter
        if filters.min_price or filters.max_price:
            return self.repository.get_by_price_range(
                filters.min_price,
                filters.max_price,
                limit
            )
        
        # Commission filter
        if filters.min_commission:
            return self.repository.get_by_commission_range(filters.min_commission, limit)
        
        return self.repository.get_all(filter_dict, limit)
    
    def _validate_product_data(self, data: dict) -> bool:
        """Validate product data"""
        # Add custom validation logic
        if "current_price" in data and data["current_price"] <= 0:
            raise ValueError("Price must be positive")
        
        if "commission_rate" in data:
            rate = data["commission_rate"]
            if rate < 0 or rate > 100:
                raise ValueError("Commission rate must be between 0 and 100")
        
        return True
    
    def _enrich_product(self, product: dict) -> dict:
        """
        Enrich product data with calculated fields.
        
        Args:
            product: Raw product data
            
        Returns:
            Enriched product
        """
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
        
        return product
