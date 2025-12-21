from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..config import supabase

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    store: str
    affiliate_link: str
    current_price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[int] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    stock_status: Optional[str] = "available"
    coupon_code: Optional[str] = None
    tags: Optional[List[str]] = []
    is_active: bool = True
    is_featured: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    affiliate_link: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[int] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    stock_status: Optional[str] = None
    coupon_code: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

@router.get("/products")
async def get_products(
    store: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    """List products with optional filters"""
    try:
        query = supabase.table("products").select("*")
        
        if store:
            query = query.eq("store", store)
        if category:
            query = query.eq("category", category)
        if search:
            query = query.ilike("name", f"%{search}%")
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        
        result = query.execute()
        
        return {
            "data": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get single product by ID"""
    try:
        result = supabase.table("products").select("*").eq("id", product_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products")
async def create_product(product: ProductCreate):
    """Create new product"""
    try:
        # Get store_id from store name
        store_result = supabase.table("stores").select("id").eq("name", product.store).execute()
        
        if not store_result.data:
            raise HTTPException(status_code=400, detail=f"Store '{product.store}' not found")
        
        store_id = store_result.data[0]["id"]
        
        # Prepare product data
        product_data = product.dict()
        product_data["store_id"] = store_id
        product_data["created_at"] = datetime.utcnow().isoformat()
        product_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Insert product
        result = supabase.table("products").insert(product_data).execute()
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    """Update existing product"""
    try:
        # Check if product exists
        existing = supabase.table("products").select("id").eq("id", product_id).execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Prepare update data (only non-None fields)
        update_data = {k: v for k, v in product.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update product
        result = supabase.table("products").update(update_data).eq("id", product_id).execute()
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """Delete product (soft delete by setting is_active=false)"""
    try:
        # Soft delete
        result = supabase.table("products").update({
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", product_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
