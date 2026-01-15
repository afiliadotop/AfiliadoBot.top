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
ML_AFFILIATE_TAG = os.getenv("ML_AFFILIATE_TAG", "")
ML_USER_ID = os.getenv("ML_USER_ID", "")
ML_BASE_URL = "https://api.mercadolibre.com"

# Models
class GenerateLinkRequest(BaseModel):
    product_url: str

class MLSearchFilters(BaseModel):
    keyword: str
    limit: int = 50
    sort: str = "price_asc"
    condition: str = "new"


# ==================== HELPER FUNCTIONS ====================

def generate_affiliate_link(item_id: str) -> str:
    """
    Gera link de afiliado ML usando o padrão público
    URL: https://produto.mercadolivre.com.br/MLB-{item_id}?matt_tool=82322591&matt_word={tag}
    
    Baseado na documentação do Portal de Afiliados ML
    """
    base_url = f"https://produto.mercadolivre.com.br/MLB-{item_id}"
    
    if ML_AFFILIATE_TAG:
        # Adiciona parâmetro de tracking do programa de afiliados
        return f"{base_url}?matt_tool=82322591&matt_word={ML_AFFILIATE_TAG}"
    
    # Retorna URL sem tracking se não tiver tag
    return base_url


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/test")
async def test_ml_endpoint():
    """Test endpoint para verificar configuração"""
    return {
        "status": "ok",
        "message": "Mercado Livre API ativa (API pública + links manuais)",
        "has_tag": bool(ML_AFFILIATE_TAG),
        "has_user_id": bool(ML_USER_ID),
        "note": "ML não tem API pública para gerar links de afiliado. Usamos padrão manual."
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
    Busca produtos no Mercado Livre (API pública)
    Retorna produtos com links de afiliado gerados manualmente
    """
    try:
        logger.info(f"[ML API] Buscando: {keyword} (limit={limit})")
        
        # API pública do ML - não requer autenticação
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
            
            # Gerar link de afiliado
            item_id = item["id"].replace("MLB-", "")
            affiliate_link = generate_affiliate_link(item_id)
            
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
                "affiliate_link": affiliate_link,
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
    Gera link de afiliado para uma URL de produto ML
    
    Importante: ML não tem API pública para isso.
    Usamos o padrão manual: ?matt_tool=82322591&matt_word={tag}
    """
    try:
        url = request.product_url
        
        # Validar URL
        if not url.startswith(("https://produto.mercadolivre.com.br", "https://www.mercadolivre.com.br")):
            raise HTTPException(status_code=400, detail="URL inválida. Deve ser um produto do Mercado Livre.")
        
        # Extrair item_id da URL
        import re
        match = re.search(r'MLB-(\d+)', url)
        if not match:
            raise HTTPException(status_code=400, detail="Não foi possível extrair o ID do produto da URL.")
        
        item_id = match.group(1)
        
        # Gerar link de afiliado
        affiliate_link = generate_affiliate_link(item_id)
        
        logger.info(f"[ML Generate Link] Link criado: {affiliate_link}")
        
        return {
            "success": True,
            "affiliate_link": affiliate_link,
            "tag": ML_AFFILIATE_TAG,
            "origin_url": url,
            "note": "Link gerado usando padrão manual ML (sem API)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ML Generate Link] Erro: {e}", exc_info=True)
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
            "has_tag": bool(ML_AFFILIATE_TAG)
        }
        
    except Exception as e:
        logger.error(f"[ML Stats] Erro: {e}")
        return {"store": "mercado_livre", "total_products": 0}
