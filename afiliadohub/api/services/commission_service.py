"""
Commission Service
ITIL Activity: Deliver & Support (Commission Business Logic)
"""
from typing import Dict, Any, List
from .base_service import BaseService
import logging

logger = logging.getLogger(__name__)


class CommissionService(BaseService):
    """Service for commission calculations and tracking"""
    
    def __init__(self, repository):
        super().__init__(repository)
    
    def calculate_commission(
        self,
        price: float,
        commission_rate: float,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate commission for a sale.
        
        Args:
            price: Product price
            commission_rate: Commission rate (0-100%)
            quantity: Quantity sold
            
        Returns:
            Commission details
        """
        if price <= 0:
            raise ValueError("Price must be positive")
        
        if commission_rate < 0 or commission_rate > 100:
            raise ValueError("Commission rate must be between 0 and 100")
        
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        
        total_price = price * quantity
        commission_amount = (total_price * commission_rate) / 100
        
        return {
            "price": price,
            "quantity": quantity,
            "total_price": round(total_price, 2),
            "commission_rate": commission_rate,
            "commission_amount": round(commission_amount, 2)
        }
    
    def calculate_total_commission(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate total commission for multiple products.
        
        Args:
            products: List of products with price, commission_rate, quantity
            
        Returns:
            Total commission details
        """
        total_sales = 0.0
        total_commission = 0.0
        product_count = 0
        
        for product in products:
            try:
                result = self.calculate_commission(
                    product.get("price", 0),
                    product.get("commission_rate", 0),
                    product.get("quantity", 1)
                )
                total_sales += result["total_price"]
                total_commission += result["commission_amount"]
                product_count += 1
            except ValueError as e:
                logger.warning(f"Skipping product due to error: {e}")
                continue
        
        avg_commission_rate = (
            (total_commission / total_sales * 100) if total_sales > 0 else 0
        )
        
        return {
            "product_count": product_count,
            "total_sales": round(total_sales, 2),
            "total_commission": round(total_commission, 2),
            "average_commission_rate": round(avg_commission_rate, 2)
        }
