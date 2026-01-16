"""
Integration tests for Products API
ITIL Activity: Plan & Improve (Quality Assurance - Integration)
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


# Mock test client (in real scenario would use actual FastAPI app)
@pytest.fixture
def mock_supabase_for_integration():
    """Mock Supabase for integration tests"""
    with patch('afiliadohub.api.utils.supabase_client.get_supabase_manager') as mock:
        client = Mock()
        manager = Mock()
        manager.client = client
        mock.return_value = manager
        
        # Mock successful responses
        mock_result = Mock()
        mock_result.data = [
            {
                "id": 1,
                "name": "Test Product",
                "store": "shopee",
                "current_price": 99.90,
                "commission_rate": 10.0,
                "active": True
            }
        ]
        
        client.table.return_value.select.return_value.execute.return_value = mock_result
        client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
        client.table.return_value.insert.return_value.execute.return_value = mock_result
        client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_result
        
        yield client


class TestProductsAPIIntegration:
    """Integration tests for Products API endpoints"""
    
    def test_list_products_endpoint(self, mock_supabase_for_integration):
        """Test GET /products endpoint integration"""
        # This would use TestClient(app) in real scenario
        # For now, testing the integration concept
        from afiliadohub.api.repositories.product_repository import ProductRepository
        from afiliadohub.api.services.product_service import ProductService
        
        repo = ProductRepository(mock_supabase_for_integration)
        service = ProductService(repo)
        
        products = service.get_products(None, 100)
        
        assert len(products) == 1
        assert products[0]["name"] == "Test Product"
        assert "estimated_commission" in products[0]
    
    def test_create_product_endpoint(self, mock_supabase_for_integration):
        """Test POST /products endpoint integration"""
        from afiliadohub.api.repositories.product_repository import ProductRepository
        from afiliadohub.api.services.product_service import ProductService
        from afiliadohub.api.models.domain import ProductCreate
        
        repo = ProductRepository(mock_supabase_for_integration)
        service = ProductService(repo)
        
        product_data = ProductCreate(
            name="New Product",
            store="shopee",
            affiliate_link="https://test.com",
            current_price=150.00
        )
        
        result = service.create_product(product_data)
        
        assert result is not None
        assert result["id"] == 1


class TestShopeeServiceIntegration:
    """Integration tests for Shopee service"""
    
    def test_shopee_service_integration(self, mock_supabase_for_integration):
        """Test Shopee repository + service integration"""
        from afiliadohub.api.repositories.shopee_repository import ShopeeRepository
        from afiliadohub.api.services.shopee_service import ShopeeService
        
        repo = ShopeeRepository(mock_supabase_for_integration)
        service = ShopeeService(repo)
        
        products = service.get_shopee_products(limit=50)
        
        assert isinstance(products, list)
        if products:
            assert "platform" in products[0]
            assert products[0]["platform"] == "shopee"


class TestMLServiceIntegration:
    """Integration tests for MercadoLivre service"""
    
    def test_ml_service_integration(self, mock_supabase_for_integration):
        """Test ML repository + service integration"""
        from afiliadohub.api.repositories.ml_repository import MLRepository
        from afiliadohub.api.services.ml_service import MLService
        
        repo = MLRepository(mock_supabase_for_integration)
        service = MLService(repo)
        
        products = service.get_ml_products(limit=50)
        
        assert isinstance(products, list)


class TestCommissionServiceIntegration:
    """Integration tests for Commission service"""
    
    def test_commission_calculation_integration(self):
        """Test commission service calculations"""
        from afiliadohub.api.services.commission_service import CommissionService
        
        service = CommissionService(repository=None)  # No repo needed for pure calculations
        
        result = service.calculate_commission(price=100.0, commission_rate=10.0, quantity=2)
        
        assert result["total_price"] == 200.0
        assert result["commission_amount"] == 20.0
    
    def test_total_commission_integration(self):
        """Test total commission for multiple products"""
        from afiliadohub.api.services.commission_service import CommissionService
        
        service = CommissionService(repository=None)
        
        products = [
            {"price": 100.0, "commission_rate": 10.0, "quantity": 1},
            {"price": 50.0, "commission_rate": 15.0, "quantity": 2}
        ]
        
        result = service.calculate_total_commission(products)
        
        assert result["product_count"] == 2
        assert result["total_sales"] == 200.0
        assert result["total_commission"] == 25.0
