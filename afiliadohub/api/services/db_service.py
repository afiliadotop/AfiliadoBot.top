import os
import logging
from typing import Dict, List, Any, Optional
from ..utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)

class DatabaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            try:
                if os.getenv("SUPABASE_URL"):
                    cls._instance.manager = get_supabase_manager()
                    cls._instance.is_mock = False
                    logger.info("DatabaseService initialized in REAL mode")
                else:
                    raise ValueError("Supabase creds missing")
            except Exception as e:
                logger.warning(f"Supabase unavailable, using Mock Mode: {e}")
                cls._instance.manager = None
                cls._instance.is_mock = True
        return cls._instance

    async def get_products(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if self.is_mock:
            return self._mock_products(filters)
        
        # Use SupabaseManager's method
        return await self.manager.get_products(filters)

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        if self.is_mock:
            return self._mock_dashboard_stats()
        
        # Use SupabaseManager's summary
        return await self.manager.get_system_summary()

    def _mock_products(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Mock Data adapted for UUIDs (using strings)
        products = [
            {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "Smartphone XYZ 128GB", "store": "Shopee", "current_price": 999.90, "original_price": 1299.90, "discount_percentage": 23, "category": "Eletrônicos", "image_url": "https://placehold.co/100", "active": True},
            {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Notebook ABC i5 8GB", "store": "AliExpress", "current_price": 2499.90, "original_price": 2999.90, "discount_percentage": 17, "category": "Computadores", "image_url": "https://placehold.co/100", "active": True},
            {"id": "550e8400-e29b-41d4-a716-446655440002", "name": "Fone Bluetooth Pro", "store": "Amazon", "current_price": 129.90, "original_price": 199.90, "discount_percentage": 35, "category": "Áudio", "image_url": "https://placehold.co/100", "active": True},
        ]
        
        if filters:
             if filters.get("active_only"):
                 products = [p for p in products if p.get("active")]
        
        return products

    def _mock_dashboard_stats(self) -> Dict[str, Any]:
        return {
            "total_products": 145,
            "products_with_discount": 45,
            "stores": {"shopee": 50, "amazon": 20},
            "updated_at": "2025-01-01T12:00:00"
        }

db_service = DatabaseService()
