"""
Mercado Livre API Handler
Endpoints para busca de produtos e geração de links de afiliado
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging
import httpx
import os

from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/mercadolivre", tags=["mercadolivre"])
logger = logging.getLogger(__name__)

# Configurações ML
ML_ACCESS_TOKEN = os.getenv("ML_ACCESS_TOKEN")
ML_AFFILIATE_TAG = os.getenv("ML_AFFILIATE_TAG", "")
ML_BASE_URL = "https://api.mercadolibre.com"

# Models
class GenerateLinkRequest(BaseModel):
    item_id: str

class MLSearchFilters(BaseModel):
    keyword: str
    limit: int = 50
    sort: str = "price_asc"  # price_asc, price_desc, relevance
    condition: str = "new"  # new, used, not_specified


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/test")
async def test_ml_endpoint():
    """Test endpoint para verificar configuração"""
    return {
        "status": "ok",
        "message": "Mercado Livre API ativa",
        "has_token": bool(ML_ACCESS_TOKEN),
        "has_tag": bool(ML_AFFILIATE_TAG)
    }


@router.get("/search")
async def search_products(
    keyword: str = Query(..., description="Palavra-chave de busca"),
    limit: int = Query(20, ge=1, le=50, description="Limite de resultados"),
    sort: str = Query("price_asc", description="Ordenação: price_asc | price_desc | relevance"),
    condition: str = Query("new", description="Condição: new | used | not_specified"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Busca produtos no Mercado Livre
    Retorna produtos formatados com links de afiliado
    """
    try:
        logger.info(f"[ML API] Buscando: {keyword} (limit={limit})")
        
        url = f"{ML_BASE_URL}/sites/MLB/search"
        params = {
            "q": keyword,
            "limit": limit,
            "offset": 0,
            "condition": condition
        }
        
        # Mapear sort
        sort_map = {
            "price_asc": "price_asc",
            "price_desc": "price_desc",
            "relevance": "relevance"
        }
        if sort in sort_map:
            params["sort"] = sort_map[sort]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Transformar resultados
        products = []
        for item in data.get("results", []):
            # Calcular desconto
            discount = 0
            if "original_price" in item and item["original_price"]:
                discount = int(((item["original_price"] - item["price"]) / item["original_price"]) * 100)
            
            # Imagem em alta resolução
            image_url = item.get("thumbnail", "").replace("-I.jpg", "-O.jpg")
            
            products.append({
                "id": item["id"],
                "name": item["title"],
                "price": item["price"],
                "original_price": item.get("original_price"),
                "discount_percentage": discount,
                "image_url": image_url,
                "seller_name": item.get("seller", {}).get("nickname", "N/A"),
                "condition": item.get("condition", "new"),
                "shipping_free": item.get("shipping", {}).get("free_shipping", False),
                "permalink": item["permalink"],
                "affiliate_link": generate_affiliate_link(item["id"]),
                "store": "mercado_livre"
            })
        
        logger.info(f"[ML API] Retornando {len(products)} produtos")
        
        return {
            "products": products,
            "count": len(products),
            "total": data.get("paging", {}).get("total", 0),
            "filters": {"keyword": keyword, "sort": sort, "condition": condition}
        }
        
    except httpx.HTTPError as e:
        logger.error(f"[ML API] Erro HTTP: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {str(e)}")
    except Exception as e:
        logger.error(f"[ML API] Erro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-link")
async def generate_link_endpoint(
    request: GenerateLinkRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Gera link de afiliado para um produto específico
    """
    try:
        affiliate_link = generate_affiliate_link(request.item_id)
        
        return {
            "item_id": request.item_id,
            "affiliate_link": affiliate_link,
            "has_tag": bool(ML_AFFILIATE_TAG)
        }
        
    except Exception as e:
        logger.error(f"[ML API] Erro ao gerar link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def list_popular_categories(
    current_user: Dict = Depends(get_current_user)
):
    """Lista categorias populares do ML Brasil"""
    categories = [
        {"id": "MLB1051", "name": "Celulares e Telefones"},
        {"id": "MLB1648", "name": "Informática"},
        {"id": "MLB1000", "name": "Eletrônicos, Áudio e Vídeo"},
        {"id": "MLB1499", "name": "Indústria e Comércio"},
        {"id": "MLB1276", "name": "Esportes e Fitness"},
        {"id": "MLB1430", "name": "Ferramentas"},
        {"id": "MLB1403", "name": "Beleza e Cuidado Pessoal"},
        {"id": "MLB1572", "name": "Casa e Jardim"}
    ]
    
    return {"categories": categories}


# ==================== ADMIN ENDPOINTS ====================

@router.get("/stats")
async def get_ml_stats(
    current_admin: Dict = Depends(get_current_admin)
):
    """Estatísticas de produtos ML no banco - ADMIN ONLY"""
    from ..utils.supabase_client import get_supabase_manager
    
    try:
        supabase = get_supabase_manager()
        
        # Contar produtos ML
        response = supabase.client.table("products")\
            .select("id", count="exact")\
            .eq("store", "mercado_livre")\
            .eq("is_active", True)\
            .execute()
        
        count = response.count if hasattr(response, 'count') else 0
        
        return {
            "store": "mercado_livre",
            "total_products": count,
            "has_credentials": bool(ML_ACCESS_TOKEN)
        }
        
    except Exception as e:
        logger.error(f"[ML Stats] Erro: {e}")
        return {"store": "mercado_livre", "total_products": 0}


# ==================== HELPER FUNCTIONS ====================

def generate_affiliate_link(item_id: str) -> str:
    """
    Gera link de afiliado com tag de tracking
    Se ML_AFFILIATE_TAG não estiver configurado, retorna URL padrão
    """
    base_url = f"https://produto.mercadolivre.com.br/MLB-{item_id}"
    
    if ML_AFFILIATE_TAG:
        # Adiciona parâmetro de tracking
        return f"{base_url}?matt_tool=82322591&matt_word={ML_AFFILIATE_TAG}"
    
    return base_url
