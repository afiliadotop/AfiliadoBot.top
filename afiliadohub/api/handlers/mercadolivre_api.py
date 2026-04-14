from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging
import httpx
import os
import html as html_module

from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/mercadolivre", tags=["mercadolivre"])
logger = logging.getLogger(__name__)

ML_AFFILIATE_TAG = os.getenv("ML_AFFILIATE_TAG", "")
ML_USER_ID = os.getenv("ML_USER_ID", "")
ML_BASE_URL = "https://api.mercadolibre.com"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


# ==================== MODELS ====================

class GenerateLinkRequest(BaseModel):
    product_url: str


class TelegramBroadcastRequest(BaseModel):
    product_id: str
    title: str
    price: float
    original_price: Optional[float] = None
    discount_percentage: int = 0
    image_url: str
    affiliate_link: str
    seller_name: str
    shipping_free: bool = False
    condition: str = "new"


# ==================== HELPERS ====================

def generate_affiliate_link(item_id: str) -> str:
    """Gera link de afiliado ML com parâmetros de tracking."""
    base_url = f"https://produto.mercadolivre.com.br/MLB-{item_id}"
    if ML_AFFILIATE_TAG:
        return f"{base_url}?matt_tool=82322591&matt_word={ML_AFFILIATE_TAG}"
    return base_url


def build_product_dict(item: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma um resultado raw da API ML em produto normalizado."""
    discount = 0
    original = item.get("original_price")
    price = item.get("price", 0)
    if original and original > price:
        discount = int(((original - price) / original) * 100)

    item_id = item["id"].replace("MLB-", "")
    image_url = item.get("thumbnail", "").replace("-I.jpg", "-O.jpg")

    return {
        "id": item["id"],
        "name": item["title"],
        "price": price,
        "original_price": original,
        "discount_percentage": discount,
        "image_url": image_url,
        "seller_name": item.get("seller", {}).get("nickname", "N/A"),
        "condition": item.get("condition", "new"),
        "shipping_free": item.get("shipping", {}).get("free_shipping", False),
        "permalink": item.get("permalink", ""),
        "affiliate_link": generate_affiliate_link(item_id),
        "store": "mercado_livre",
        "sold_quantity": item.get("sold_quantity"),
    }


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/test")
async def test_ml_endpoint():
    """Test endpoint para verificar configuracao"""
    return {
        "status": "ok",
        "message": "Mercado Livre API ativa",
        "has_affiliate_tag": bool(ML_AFFILIATE_TAG),
        "has_telegram": bool(TELEGRAM_BOT_TOKEN),
    }


@router.get("/search")
async def search_products(
    keyword: str = Query(..., description="Palavra-chave de busca"),
    limit: int = Query(20, ge=1, le=50),
    page: int = Query(1, ge=1),
    sort: str = Query("relevance", description="relevance | price_asc | price_desc | sales"),
    condition: str = Query("new", description="new | used | not_specified"),
    current_user: Dict = Depends(get_current_user),
):
    """Busca produtos no Mercado Livre com paginacao."""
    try:
        logger.info(f"[ML API] Buscando: {keyword} page={page} sort={sort}")

        offset = (page - 1) * limit
        params: Dict[str, Any] = {
            "q": keyword,
            "limit": limit,
            "offset": offset,
            "condition": condition,
        }

        sort_map = {
            "relevance": "relevance",
            "price_asc": "price_asc",
            "price_desc": "price_desc",
            "sales": "sold_quantity",
        }
        if sort in sort_map:
            params["sort"] = sort_map[sort]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{ML_BASE_URL}/sites/MLB/search", params=params)
            response.raise_for_status()
            data = response.json()

        products = [build_product_dict(item) for item in data.get("results", [])]
        paging = data.get("paging", {})
        total = paging.get("total", 0)
        has_more = offset + limit < total

        logger.info(f"[ML API] {len(products)} produtos retornados (total={total})")

        return {
            "products": products,
            "count": len(products),
            "total": total,
            "page": page,
            "has_more": has_more,
            "filters": {"keyword": keyword, "sort": sort, "condition": condition},
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"[ML API] HTTP {e.response.status_code}: {e.response.text}")
        raise HTTPException(status_code=502, detail=f"Erro na API do Mercado Livre: {e.response.status_code}")
    except httpx.HTTPError as e:
        logger.error(f"[ML API] Erro de conexao: {e}")
        raise HTTPException(status_code=502, detail="Nao foi possivel conectar ao Mercado Livre")
    except Exception as e:
        logger.error(f"[ML API] Erro inesperado: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending(
    category_id: Optional[str] = Query(None, description="ID da categoria ML"),
    limit: int = Query(20, ge=1, le=50),
    current_user: Dict = Depends(get_current_user),
):
    """Retorna produtos em destaque / mais vendidos."""
    try:
        params: Dict[str, Any] = {"limit": limit, "sort": "sold_quantity"}
        if category_id:
            params["category"] = category_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{ML_BASE_URL}/sites/MLB/search", params=params)
            response.raise_for_status()
            data = response.json()

        products = [build_product_dict(item) for item in data.get("results", [])]
        return {"products": products, "count": len(products)}

    except Exception as e:
        logger.error(f"[ML Trending] Erro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast-telegram")
async def broadcast_to_telegram(
    req: TelegramBroadcastRequest,
    current_user: Dict = Depends(get_current_user),
):
    """Envia um produto do Mercado Livre para o grupo Telegram configurado."""
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Bot Telegram nao configurado")

    from ..utils.telegram_settings_manager import get_telegram_settings
    settings = get_telegram_settings()
    chat_id = settings.get("group_chat_id") or settings.get("channel_id")

    if not chat_id:
        raise HTTPException(status_code=400, detail="Chat ID do Telegram nao configurado")

    condition_label = "Novo" if req.condition == "new" else "Usado"
    shipping_label = "Frete Gratis" if req.shipping_free else ""
    discount_label = f"-{req.discount_percentage}% OFF" if req.discount_percentage >= 5 else ""

    price_fmt = f"R$ {req.price:,.2f}".replace(",", ".")
    orig_fmt = f"R$ {req.original_price:,.2f}".replace(",", ".") if req.original_price else None

    lines = [f"*{req.title}*", "", f"*{price_fmt}*"]
    if orig_fmt and req.original_price and req.original_price > req.price:
        lines.append(f"De: ~{orig_fmt}~")
    if discount_label:
        lines.append(f"🔥 {discount_label}")
    if shipping_label:
        lines.append(f"🚚 {shipping_label}")
    lines += [
        f"📦 {condition_label}  |  🏪 {req.seller_name}",
        "",
        f"🔗 [Ver no Mercado Livre]({req.affiliate_link})",
        "",
        "_Via AfiliadoBot_",
    ]
    text = "\n".join(lines)

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                json={
                    "chat_id": chat_id,
                    "caption": text,
                    "parse_mode": "Markdown",
                    "photo": req.image_url,
                },
            )
            if not resp.is_success:
                resp2 = await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                )
                resp2.raise_for_status()

        logger.info(f"[ML Telegram] Produto {req.product_id} enviado")
        return {"success": True, "message": "Produto enviado ao Telegram!"}

    except Exception as e:
        logger.error(f"[ML Telegram] Erro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao enviar ao Telegram: {str(e)}")


@router.post("/generate-link")
async def generate_link_endpoint(
    request: GenerateLinkRequest, current_user: Dict = Depends(get_current_user)
):
    """Gera link de afiliado para uma URL de produto ML."""
    import re
    url = request.product_url
    if not url.startswith(("https://produto.mercadolivre.com.br", "https://www.mercadolivre.com.br")):
        raise HTTPException(status_code=400, detail="URL invalida. Deve ser um produto do Mercado Livre.")

    match = re.search(r"MLB-(\d+)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Nao foi possivel extrair o ID do produto da URL.")

    affiliate_link = generate_affiliate_link(match.group(1))
    return {"success": True, "affiliate_link": affiliate_link, "tag": ML_AFFILIATE_TAG}


@router.get("/categories")
async def list_popular_categories(current_user: Dict = Depends(get_current_user)):
    """Lista categorias populares do ML Brasil."""
    return {
        "categories": [
            {"id": "MLB1051", "name": "Celulares e Telefones", "emoji": "📱"},
            {"id": "MLB1648", "name": "Informatica", "emoji": "💻"},
            {"id": "MLB1000", "name": "Eletronicos", "emoji": "🎧"},
            {"id": "MLB1276", "name": "Esportes e Fitness", "emoji": "🏃"},
            {"id": "MLB1403", "name": "Beleza e Cuidado", "emoji": "💄"},
            {"id": "MLB1572", "name": "Casa e Jardim", "emoji": "🏠"},
            {"id": "MLB1430", "name": "Ferramentas", "emoji": "🔧"},
            {"id": "MLB1132", "name": "Roupas e Acessorios", "emoji": "👗"},
        ]
    }


# ==================== ADMIN ENDPOINTS ====================

@router.get("/stats")
async def get_ml_stats(current_admin: Dict = Depends(get_current_admin)):
    """Estatisticas de produtos ML no banco - ADMIN ONLY"""
    from ..utils.supabase_client import get_supabase_manager
    try:
        supabase = get_supabase_manager()
        response = (
            supabase.client.table("products")
            .select("id", count="exact")
            .eq("store", "mercado_livre")
            .eq("is_active", True)
            .execute()
        )
        count = response.count if hasattr(response, "count") else 0
        return {"store": "mercado_livre", "total_products": count, "has_affiliate_tag": bool(ML_AFFILIATE_TAG)}
    except Exception as e:
        logger.error(f"[ML Stats] Erro: {e}")
        return {"store": "mercado_livre", "total_products": 0}
