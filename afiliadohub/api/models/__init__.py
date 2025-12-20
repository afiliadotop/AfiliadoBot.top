"""
Modelos de dados do AfiliadoHub
"""

from .product import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductInDB
)

__all__ = [
    'Product',
    'ProductCreate',
    'ProductUpdate',
    'ProductInDB'
]
