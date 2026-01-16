"""
Product Handler (Refactored with Clean Architecture)
ITIL Activity: Engage (API Interface)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from ..services.product_service import ProductService
from ..repositories.product_repository import ProductRepository
from ..models.domain import Product, ProductCreate, ProductUpdate, ProductFilter
from ..utils.supabase_client import get_supabase_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency Injection
def get_product_repository() -> ProductRepository:
    """Get ProductRepository instance with Supabase client"""
    supabase = get_supabase_manager()
    return ProductRepository(supabase.client)


def get_product_service(
    repository: ProductRepository = Depends(get_product_repository)
) -> ProductService:
    """Get ProductService instance"""
    return ProductService(repository)


# API Endpoints
@router.get("/products", response_model=List[dict])
async def list_products(
    store: Optional[str] = Query(None, description="Filter by store"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, gt=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price"),
    min_commission: Optional[float] = Query(None, ge=0, le=100, description="Minimum commission %"),
    active: Optional[bool] = Query(True, description="Active products only"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    service: ProductService = Depends(get_product_service)
):
    """
    List products with optional filters.
    
    ITIL: Engage activity - User interaction
    """
    try:
        # Build filters
        filters = ProductFilter(
            store=store,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_commission=min_commission,
            active=active
        )
        
        # Get products via service
        products = service.get_products(filters, limit)
        
        return products
    except Exception as e:
        logger.error(f"Error listing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=dict)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Get product by ID.
    
    ITIL: Engage activity
    """
    try:
        product = service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products", response_model=dict, status_code=201)
async def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Create new product.
    
    ITIL: Engage activity
    """
    try:
        created = service.create_product(product)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/products/{product_id}", response_model=dict)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    """
    Update product.
    
    ITIL: Engage activity
    """
    try:
        updated = service.update_product(product_id, product)
        
        if not updated:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Delete product (soft delete).
    
    ITIL: Engage activity
    """
    try:
        deleted = service.delete_product(product_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/search/{query}", response_model=List[dict])
async def search_products(
    query: str,
    limit: int = Query(50, ge=1, le=200),
    service: ProductService = Depends(get_product_service)
):
    """
    Search products by name.
    
    ITIL: Engage activity
    """
    try:
        products = service.search_products(query, limit)
        return products
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))
