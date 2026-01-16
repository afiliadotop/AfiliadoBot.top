"""
Pytest configuration and fixtures
ITIL Activity: Plan & Improve (Testing Infrastructure)
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from unittest.mock import Mock, MagicMock
from afiliadohub.api.repositories.product_repository import ProductRepository
from afiliadohub.api.services.product_service import ProductService


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    client = Mock()
    
    # Mock table()
    table_mock = Mock()
    client.table.return_value = table_mock
    
    # Mock query chain
    table_mock.select.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.gte.return_value = table_mock
    table_mock.lte.return_value = table_mock
    table_mock.ilike.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.delete.return_value = table_mock
    
    # Mock execute()
    execute_mock = Mock()
    execute_mock.data = []
    table_mock.execute.return_value = execute_mock
    
    return client


@pytest.fixture
def product_repository(mock_supabase_client):
    """ProductRepository with mocked client"""
    return ProductRepository(mock_supabase_client)


@pytest.fixture
def product_service(product_repository):
    """ProductService with mocked repository"""
    return ProductService(product_repository)


@pytest.fixture
def sample_product():
    """Sample product data for testing"""
    return {
        "id": 1,
        "name": "Test Product",
        "store": "shopee",
        "affiliate_link": "https://shope.ee/test123",
        "current_price": 99.90,
        "original_price": 149.90,
        "category": "electronics",
        "image_url": "https://example.com/image.jpg",
        "coupon_code": "TEST10",
        "tags": ["tech", "sale"],
        "active": True,
        "commission_rate": 8.5
    }


@pytest.fixture
def sample_products_list():
    """Sample list of products"""
    return [
        {
            "id": 1,
            "name": "Product A",
            "store": "shopee",
            "current_price": 50.00,
            "commission_rate": 10.0,
            "active": True
        },
        {
            "id": 2,
            "name": "Product B",
            "store": "shopee",
            "current_price": 100.00,
            "commission_rate": 15.0,
            "active": True
        }
    ]
