"""
Unit tests for ProductService
ITIL Activity: Plan & Improve (Quality Assurance)
"""
import pytest
from unittest.mock import Mock
from afiliadohub.api.services.product_service import ProductService
from afiliadohub.api.models.domain import ProductCreate, ProductUpdate, ProductFilter


class TestProductService:
    """Test suite for ProductService"""
    
    def test_get_product_by_id(self, product_service, sample_product):
        """Test get product by ID"""
        # Arrange
        product_service.repository.get_by_id = Mock(return_value=sample_product)
        
        # Act
        result = product_service.get_product_by_id(1)
        
        # Assert
        assert result["id"] == 1
        assert "discount_percent" in result  # Enriched
        product_service.repository.get_by_id.assert_called_once_with(1)
    
    def test_get_product_by_id_not_found(self, product_service):
        """Test get product when not found"""
        # Arrange
        product_service.repository.get_by_id = Mock(return_value=None)
        
        # Act
        result = product_service.get_product_by_id(999)
        
        # Assert
        assert result is None
    
    def test_get_products_no_filters(self, product_service, sample_products_list):
        """Test get all products without filters"""
        # Arrange
        product_service.repository.get_active_products = Mock(return_value=sample_products_list)
        
        # Act
        result = product_service.get_products(None, 100)
        
        # Assert
        assert len(result) == 2
        assert all("estimated_commission" in p for p in result)  # Enriched
    
    def test_get_products_with_store_filter(self, product_service, sample_products_list):
        """Test get products filtered by store"""
        # Arrange
        filters = ProductFilter(store="shopee")
        product_service.repository.get_all = Mock(return_value=sample_products_list)
        
        # Act
        result = product_service.get_products(filters, 100)
        
        # Assert
        assert len(result) == 2
        product_service.repository.get_all.assert_called_once()
    
    def test_create_product(self, product_service, sample_product):
        """Test create product"""
        # Arrange
        product_data = ProductCreate(
            name="Test Product",
            store="shopee",
            affiliate_link="https://shope.ee/test",
            current_price=99.90
        )
        product_service.repository.create = Mock(return_value=sample_product)
        
        # Act
        result = product_service.create_product(product_data)
        
        # Assert
        assert result["id"] == 1
        product_service.repository.create.assert_called_once()
    
    def test_create_product_invalid_price(self, product_service):
        """Test create product with invalid price"""
        # Arrange
        product_data = ProductCreate(
            name="Test",
            store="shopee",
            affiliate_link="https://test.com",
            current_price=-10.0  # Invalid
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Price must be positive"):
            product_service.create_product(product_data)
    
    def test_update_product(self, product_service, sample_product):
        """Test update product"""
        # Arrange
        update_data = ProductUpdate(current_price=79.90)
        product_service.repository.get_by_id = Mock(return_value=sample_product)
        updated = sample_product.copy()
        updated["current_price"] = 79.90
        product_service.repository.update = Mock(return_value=updated)
        
        # Act
        result = product_service.update_product(1, update_data)
        
        # Assert
        assert result["current_price"] == 79.90
    
    def test_update_product_not_found(self, product_service):
        """Test update nonexistent product"""
        # Arrange
        update_data = ProductUpdate(current_price=79.90)
        product_service.repository.get_by_id = Mock(return_value=None)
        
        # Act
        result = product_service.update_product(999, update_data)
        
        # Assert
        assert result is None
    
    def test_delete_product(self, product_service, sample_product):
        """Test delete product (soft delete)"""
        # Arrange
        product_service.repository.update = Mock(return_value=sample_product)
        
        # Act
        result = product_service.delete_product(1)
        
        # Assert
        assert result is True
        product_service.repository.update.assert_called_with(1, {"active": False})
    
    def test_search_products(self, product_service, sample_product):
        """Test search products by name"""
        # Arrange
        product_service.repository.search_by_name = Mock(return_value=[sample_product])
        
        # Act
        result = product_service.search_products("Test", 50)
        
        # Assert
        assert len(result) == 1
        assert result[0]["name"] == "Test Product"
    
    def test_enrich_product_with_discount(self, product_service):
        """Test product enrichment calculates discount"""
        # Arrange
        product = {
            "current_price": 99.90,
            "original_price": 149.90,
            "commission_rate": 10.0
        }
        
        # Act
        result = product_service._enrich_product(product)
        
        # Assert
        assert "discount_percent" in result
        assert result["discount_percent"] == pytest.approx(33.36, rel=0.01)
    
    def test_enrich_product_with_commission(self, product_service):
        """Test product enrichment calculates commission"""
        # Arrange
        product = {
            "current_price": 100.00,
            "commission_rate": 15.0
        }
        
        # Act
        result = product_service._enrich_product(product)
        
        # Assert
        assert "estimated_commission" in result
        assert result["estimated_commission"] == 15.00
    
    def test_validate_invalid_commission_rate(self, product_service):
        """Test validation fails for invalid commission rate"""
        # Arrange
        data = {"commission_rate": 150.0}  # > 100%
        
        # Act & Assert
        with pytest.raises(ValueError, match="Commission rate must be between 0 and 100"):
            product_service._validate_product_data(data)
