from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import httpx
import re
import logging
from ..utils.supabase_client import get_supabase_manager
from .auth import get_current_user

# Get supabase instance
supabase = get_supabase_manager().client

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

class MLProductAdd(BaseModel):
    product_url: str
    category: str

logger = logging.getLogger(__name__)

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


@router.post("/add-ml-product")
async def add_ml_product(
    request: MLProductAdd,
    current_user: Dict = Depends(get_current_user)
):
    """
    Adiciona produto Mercado Livre manualmente
    Usa OAuth token para buscar info do produto via ML API
    """
    try:
        # 1. Validar e extrair item_id
        match = re.search(r'MLB-(\d+)', request.product_url)
        if not match:
            raise HTTPException(
                status_code=400, 
                detail="URL inválida. Use formato: https://produto.mercadolivre.com.br/MLB-xxxxx"
            )
        
        item_id = match.group(1)
        logger.info(f"[ML Add] Adicionando produto MLB-{item_id}")
        
        # 2. Buscar info do produto via ML API (COM TOKEN OAuth)
        from ..utils.ml_token_manager import get_ml_token
        
        token = await get_ml_token()
        ml_url = f"https://api.mercadolibre.com/items/MLB-{item_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(ml_url, headers=headers)
            response.raise_for_status()
            product_info = response.json()
        
        logger.info(f"[ML Add] Produto encontrado: {product_info.get('title', 'N/A')[:50]}")
        
        # 3. Gerar link de afiliado
        from .mercadolivre_api import generate_affiliate_link
        affiliate_link = generate_affiliate_link(item_id)
        
        # 4. Calcular desconto
        discount = 0
        if "original_price" in product_info and product_info["original_price"]:
            try:
                discount = int((
                    (product_info["original_price"] - product_info["price"]) / 
                    product_info["original_price"]
                ) * 100)
            except:
                discount = 0
        
        # 5. Preparar dados do produto
        product_data = {
            "store": "mercado_livre",
            "name": product_info["title"][:255],
            "description": product_info.get("subtitle", "")[:500] if product_info.get("subtitle") else None,
            "affiliate_link": affiliate_link,
            "current_price": float(product_info["price"]),
            "original_price": float(product_info.get("original_price")) if product_info.get("original_price") else None,
            "discount_percentage": discount,
            "category": request.category,
            "image_url": product_info.get("pictures", [{}])[0].get("url") if product_info.get("pictures") else None,
            "is_active": True,
            "is_featured": discount >= 30,
            "source": "mercadolivre_manual",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # 6. Buscar store_id
        store_result = supabase.table("stores").select("id").eq("name", "mercado_livre").execute()
        if store_result.data:
            product_data["store_id"] = store_result.data[0]["id"]
        
        # 7. Salvar no banco
        result = supabase.table("products").insert(product_data).execute()
        
        logger.info(f"[ML Add] Produto salvo com sucesso! ID: {result.data[0].get('id')}")
        
        return {
            "success": True,
            "product": result.data[0],
            "affiliate_link": affiliate_link,
            "message": f"Produto '{product_info['title'][:50]}...' adicionado com sucesso!"
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Produto não encontrado no Mercado Livre")
        logger.error(f"[ML Add] Erro HTTP {e.response.status_code}: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produto: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ML Add] Erro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LEGACY COMPATIBILITY FUNCTIONS ====================
# These functions are used by index.py which expects specific function names
# independent of FastAPI routers.

async def add_product(product_data: dict):
    """Legacy wrapper for create_product"""
    try:
        # Convert dict to pydantic model for validation
        product = ProductCreate(**product_data)
        
        # Call the logic directly (reusing router logic would be harder due to dependency injection)
        store_result = supabase.table("stores").select("id").eq("name", product.store).execute()
        if not store_result.data:
            return {"success": False, "error": f"Store '{product.store}' not found"}
        
        store_id = store_result.data[0]["id"]
        
        data = product.dict()
        data["store_id"] = store_id
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.table("products").insert(data).execute()
        return {"success": True, "data": result.data[0]}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_products(filters: dict):
    """Legacy wrapper for specific filter format"""
    try:
        query = supabase.table("products").select("*")
        
        if filters.get("store"):
            query = query.eq("store", filters["store"])
        
        if filters.get("min_discount"):
            query = query.gte("discount_percentage", filters["min_discount"])
            
        if filters.get("limit"):
            query = query.limit(filters["limit"])
            
        result = query.execute()
        return result.data  # Return list directly as expected by legacy code
    except Exception as e:
        return []

async def get_random_product(min_discount: int = 0):
    """Legacy wrapper for random product fetch"""
    try:
        query = supabase.table("products").select("*").eq("is_active", True)
        
        if min_discount > 0:
            query = query.gte("discount_percentage", min_discount)
            
        # Get random product using random() function if db supports it or fetch sample
        # Since Supabase via REST doesn't support random() easily in select, we fetch a batch and pick one
        result = query.limit(20).execute()
        
        if result.data:
            import random
            return random.choice(result.data)
        return None
    except Exception as e:
        return None
