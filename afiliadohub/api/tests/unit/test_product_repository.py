"""
Unit tests for ProductRepository
ITIL Activity: Plan & Improve (Quality Assurance)
"""
import pytest
from afiliadohub.api.repositories.product_repository import ProductRepository


class TestProductRepository:
    """Test suite for ProductRepository"""
    
    def test_table_name(self, product_repository):
        """Test table name property"""
        assert product_repository.table_name == "products"
    
    def test_get_by_id(self, product_repository, mock_supabase_client, sample_product):
        """Test get product by ID"""
        # Arrange
        mock_supabase_client.table().select().eq().execute.return_value.data = [sample_product]
        
        # Act
        result = product_repository.get_by_id(1)
        
        # Assert
        assert result == sample_product
        mock_supabase_client.table.assert_called_with("products")
    
    def test_get_by_id_not_found(self, product_repository, mock_supabase_client):
        """Test get product by ID when not found"""
        # Arrange
        mock_supabase_client.table().select().eq().execute.return_value.data = []
        
        # Act
        result = product_repository.get_by_id(999)
        
        # Assert
        assert result is None
    
    def test_get_all(self, product_repository, mock_supabase_client, sample_products_list):
        """Test get all products"""
        # Arrange
        mock_supabase_client.table().select().limit().execute.return_value.data = sample_products_list
        
        # Act
        result = product_repository.get_all(limit=100)
        
        # Assert
        assert len(result) == 2
        assert result == sample_products_list
    
    def test_get_all_with_filters(self, product_repository, mock_supabase_client, sample_product):
        """Test get all with filters"""
        # Arrange
        mock_supabase_client.table().select().eq().limit().execute.return_value.data = [sample_product]
        
        # Act
        result = product_repository.get_all(filters={"store": "shopee"}, limit=50)
        
        # Assert
        assert len(result) == 1
        assert result[0]["store"] == "shopee"
    
    def test_get_by_store(self, product_repository, mock_supabase_client, sample_products_list):
        """Test get products by store"""
        # Arrange
        mock_supabase_client.table().select().eq().limit().execute.return_value.data = sample_products_list
        
        # Act
        result = product_repository.get_by_store("shopee", limit=100)
        
        # Assert
        assert len(result) == 2
    
    def test_get_active_products(self, product_repository, mock_supabase_client, sample_products_list):
        """Test get active products only"""
        # Arrange
        mock_supabase_client.table().select().eq().limit().execute.return_value.data = sample_products_list
        
        # Act
        result = product_repository.get_active_products(limit=100)
        
        # Assert
        assert all(p["active"] for p in result)
    
    def test_search_by_name(self, product_repository, mock_supabase_client, sample_product):
        """Test search products by name"""
        # Arrange
        mock_supabase_client.table().select().ilike().limit().execute.return_value.data = [sample_product]
        
        # Act
        result = product_repository.search_by_name("Test", limit=50)
        
        # Assert
        assert len(result) == 1
        assert "Test" in result[0]["name"]
    
    def test_get_by_price_range(self, product_repository, mock_supabase_client, sample_products_list):
        """Test get products by price range"""
        # Arrange
        mock_supabase_client.table().select().gte().lte().limit().execute.return_value.data = sample_products_list
        
        # Act
        result = product_repository.get_by_price_range(min_price=50.0, max_price=150.0, limit=100)
        
        # Assert
        assert len(result) == 2
    
    def test_get_by_commission_range(self, product_repository, mock_supabase_client, sample_product):
        """Test get products by minimum commission"""
        # Arrange
        mock_supabase_client.table().select().gte().limit().execute.return_value.data = [sample_product]
        
        # Act
        result = product_repository.get_by_commission_range(min_commission=8.0, limit=100)
        
        # Assert
        assert len(result) == 1
        assert result[0]["commission_rate"] >= 8.0
    
    def test_create(self, product_repository, mock_supabase_client, sample_product):
        """Test create product"""
        # Arrange
        new_product = sample_product.copy()
        del new_product["id"]  # No ID for creation
        mock_supabase_client.table().insert().execute.return_value.data = [sample_product]
        
        # Act
        result = product_repository.create(new_product)
        
        # Assert
        assert result["id"] == 1
        assert result["name"] == "Test Product"
    
    def test_update(self, product_repository, mock_supabase_client, sample_product):
        """Test update product"""
        # Arrange
        updated = sample_product.copy()
        updated["current_price"] = 79.90
        mock_supabase_client.table().update().eq().execute.return_value.data = [updated]
        
        # Act
        result = product_repository.update(1, {"current_price": 79.90})
        
        # Assert
        assert result["current_price"] == 79.90
    
    def test_delete(self, product_repository, mock_supabase_client):
        """Test delete product"""
        # Arrange
        mock_supabase_client.table().delete().eq().execute.return_value.data = [{"id": 1}]
        
        # Act
        result = product_repository.delete(1)
        
        # Assert
        assert result is True
    
    def test_count(self, product_repository, mock_supabase_client):
        """Test count products"""
        # Arrange
        mock_result = type('obj', (object,), {'count': 42})()
        mock_supabase_client.table().select().execute.return_value = mock_result
        
        # Act
        result = product_repository.count()
        
        # Assert
        assert result == 42
