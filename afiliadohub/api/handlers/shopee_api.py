import os
import httpx
import html
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query

from ..utils.shopee_client import create_shopee_client
from ..utils.shopee_extensions import add_rate_limiting
from ..utils.supabase_client import get_supabase_manager
from ..utils.shopee_public_api import ShopeePublicAPI
from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/shopee", tags=["shopee"])
logger = logging.getLogger(__name__)

# ==================== MODELS ====================


class ShopeeProduct(BaseModel):
    """Product model with optional admin fields"""

    itemId: int
    productName: str
    priceMin: str
    priceMax: str
    imageUrl: str
    sales: int
    rating: Optional[str] = Field(None, alias="ratingStar")
    discountRate: int = Field(alias="priceDiscountRate")
    shopName: str
    shopId: int
    offerLink: str

    # Admin only fields
    commissionRate: Optional[str] = None
    commissionAmount: Optional[str] = Field(None, alias="commission")
    sellerCommissionRate: Optional[str] = None
    shopeeCommissionRate: Optional[str] = None

    class Config:
        extra = "allow"  # Allow extra fields from API
        populate_by_name = True  # Accept both field name and alias


class PaginationInfo(BaseModel):
    """Pagination metadata"""

    page: int
    limit: int
    total: int
    hasMore: bool
    totalPages: int


class ProductsResponse(BaseModel):
    """Response with products and pagination"""

    products: List[ShopeeProduct]
    pagination: PaginationInfo
    appliedFilters: Dict[str, Any]


class GenerateLinkRequest(BaseModel):
    url: str = Field(..., description="URL original do produto Shopee")
    subIds: Optional[List[str]] = Field(default=None, max_items=5)


class ProductSearchRequest(BaseModel):
    keyword: str
    sortType: int = Field(default=5, ge=1, le=5)
    limit: int = Field(default=20, le=50)


# ==================== PUBLIC ENDPOINTS ====================


@router.get("/test")
async def test_endpoint():
    """Test endpoint without auth to verify CORS"""
    return {"status": "ok", "message": "Shopee API working!", "cors": "enabled"}


@router.get("/products", response_model=ProductsResponse)
async def get_products(
    # Search & Sort
    keyword: Optional[str] = Query(None, description="Palavra-chave"),
    sort_by: str = Query("commission", description="commission | sales | price"),
    # Pagination
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
    # Advanced Filters
    price_min: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    price_max: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    min_rating: Optional[float] = Query(
        None, ge=0, le=5, description="Avaliação mínima"
    ),
    min_sales: Optional[int] = Query(None, ge=0, description="Vendas mínimas"),
    min_discount: Optional[int] = Query(
        None, ge=0, le=100, description="Desconto mínimo %"
    ),
    is_ams_offer: Optional[bool] = Query(
        None, description="Apenas ofertas com comissão extra de vendedor"
    ),
    is_key_seller: Optional[bool] = Query(
        None, description="Apenas vendedores chave/mall"
    ),
    # Auth
    current_user: Dict = Depends(get_current_user),
):
    """
    Lista produtos Shopee com paginação e filtros avançados
    - Usuários comuns: SEM dados de comissão
    - Admin: COM todos os dados
    """
    logger.info(f"[Shopee API] Products endpoint - page={page}, filters active")

    try:
        # Map sort_by to Shopee API sort_type
        sort_map = {
            "commission": 5,  # COMMISSION_DESC
            "sales": 2,  # ITEM_SOLD_DESC
            "price": 4,  # PRICE_ASC
        }
        sort_type = sort_map.get(sort_by, 5)

        # Fetch from Shopee API with pagination
        client = create_shopee_client()
        add_rate_limiting(client)

        async with client:
            result = await client.get_products(
                keyword=keyword, 
                sort_type=sort_type, 
                page=page, 
                limit=limit,
                is_ams_offer=is_ams_offer,
                is_key_seller=is_key_seller
            )

        products = result.get("nodes", [])
        page_info = result.get("pageInfo", {})

        # Apply client-side filters
        filtered_products = products

        if price_min is not None or price_max is not None:
            filtered_products = [
                p
                for p in filtered_products
                if (price_min is None or float(p.get("priceMin", 0)) >= price_min)
                and (price_max is None or float(p.get("priceMax", 999999)) <= price_max)
            ]

        if min_rating is not None:
            filtered_products = [
                p
                for p in filtered_products
                if p.get("ratingStar") and float(p.get("ratingStar", 0)) >= min_rating
            ]

        if min_sales is not None:
            filtered_products = [
                p for p in filtered_products if p.get("sales", 0) >= min_sales
            ]

        if min_discount is not None:
            filtered_products = [
                p
                for p in filtered_products
                if p.get("priceDiscountRate", 0) >= min_discount
            ]

        # PRIVACY: Remove commission data for non-admin users
        is_admin = current_user.get("role") == "admin"

        if not is_admin:
            for product in filtered_products:
                product.pop("commissionRate", None)
                product.pop("commission", None)
                product.pop("sellerCommissionRate", None)
                product.pop("shopeeCommissionRate", None)

        # Calculate pagination metadata
        total_products = len(filtered_products)
        has_more = (
            page_info.get("hasNextPage", False) or len(filtered_products) >= limit
        )
        total_pages = (total_products // limit) + (
            1 if total_products % limit > 0 else 0
        )

        # Build applied filters dict
        applied_filters = {}
        if keyword:
            applied_filters["keyword"] = keyword
        if price_min is not None:
            applied_filters["priceMin"] = price_min
        if price_max is not None:
            applied_filters["priceMax"] = price_max
        if min_rating is not None:
            applied_filters["minRating"] = min_rating
        if min_sales is not None:
            applied_filters["minSales"] = min_sales
        if min_discount is not None:
            applied_filters["minDiscount"] = min_discount
        if is_ams_offer is not None:
            applied_filters["isAmsOffer"] = is_ams_offer
        if is_key_seller is not None:
            applied_filters["isKeySeller"] = is_key_seller

        logger.info(
            f"[Shopee API] Returning {len(filtered_products)} products (admin={is_admin}, filters={len(applied_filters)})"
        )

        return {
            "products": filtered_products,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_products,
                "hasMore": has_more,
                "totalPages": max(total_pages, 1),
            },
            "appliedFilters": applied_filters,
        }

    except Exception as e:
        logger.error(f"[Shopee API] Error fetching products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_products(
    request: ProductSearchRequest, current_user: Dict = Depends(get_current_user)
):
    """
    Busca produtos por keyword
    """
    try:
        client = create_shopee_client()
        add_rate_limiting(client)

        async with client:
            result = await client.get_products(
                keyword=request.keyword, sort_type=request.sortType, limit=request.limit
            )

        products = result.get("nodes", [])

        # Privacy filter
        is_admin = current_user.get("role") == "admin"
        if not is_admin:
            for product in products:
                product.pop("commissionRate", None)
                product.pop("commission", None)
                product.pop("sellerCommissionRate", None)
                product.pop("shopeeCommissionRate", None)

        return {
            "products": products,
            "count": len(products),
            "hasMore": result.get("pageInfo", {}).get("hasNextPage", False),
        }

    except Exception as e:
        logger.error(f"[Shopee API] Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{item_id}/{shop_id}/extended")
async def get_extended_product_details(
    item_id: int, shop_id: int, current_user: Dict = Depends(get_current_user)
):
    """
    Busca detalhes estendidos (Vídeo e Depoimentos) via Shopee Public API
    """
    try:
        shopee_public = ShopeePublicAPI()
        
        async with shopee_public:
            # Busca vídeo e meta
            details = await shopee_public.get_product_extended_details(item_id, shop_id)
            # Busca melhores depoimentos (reviews)
            reviews = await shopee_public.get_product_reviews(item_id, shop_id, limit=3)
            
            return {
                "itemId": item_id,
                "shopId": shop_id,
                "videoUrl": details.get("video_url"),
                "reviews": reviews,
                "details": details
            }
    except Exception as e:
        logger.error(f"[Shopee API] Extended details error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar detalhes estendidos")


@router.post("/generate-link")
async def generate_short_link(
    request: GenerateLinkRequest, current_user: Dict = Depends(get_current_user)
):
    """
    Gera short link de afiliado
    Adiciona user_id aos sub_ids para tracking
    """
    try:
        client = create_shopee_client()
        add_rate_limiting(client)

        # Add user tracking
        sub_ids = request.subIds or []
        sub_ids.insert(0, str(current_user.get("id", "unknown")))
        sub_ids = sub_ids[:5]  # Max 5

        async with client:
            short_link = await client.generate_short_link(
                origin_url=request.url, sub_ids=sub_ids
            )

        if not short_link:
            raise HTTPException(status_code=400, detail="Failed to generate link")

        logger.info(f"[Shopee API] Link generated for user {current_user.get('id')}")

        return {"shortLink": short_link, "originalUrl": request.url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Shopee API] Link generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offers")
async def get_offers(
    keyword: Optional[str] = None,
    sort_type: int = Query(2, ge=1, le=2),
    limit: int = Query(10, le=20),
    current_user: Dict = Depends(get_current_user),
):
    """Lista ofertas gerais Shopee"""
    try:
        client = create_shopee_client()
        add_rate_limiting(client)

        async with client:
            result = await client.get_shopee_offers(
                keyword=keyword, sort_type=sort_type, limit=limit
            )

        return result

    except Exception as e:
        logger.error(f"[Shopee API] Offers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN ENDPOINTS ====================


@router.get("/stats")
async def get_stats(current_admin: Dict = Depends(get_current_admin)):
    """
    Estatísticas Shopee - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()

        # Try to get stats from RPC function
        try:
            stats_result = supabase.client.rpc("get_shopee_statistics").execute()

            if stats_result.data:
                return stats_result.data
        except Exception as rpc_error:
            logger.warning(
                f"[Shopee API] RPC function not found, using fallback: {rpc_error}"
            )

        # Fallback: Calculate stats manually
        products = (
            supabase.client.table("products")
            .select("commission_rate")
            .eq("store", "shopee")
            .eq("is_active", True)
            .execute()
        )

        if not products.data:
            return {
                "totalProducts": 0,
                "avgCommission": 0.0,
                "topCommission": 0.0,
                "todayImports": 0,
            }

        commission_rates = [
            float(p.get("commission_rate", 0))
            for p in products.data
            if p.get("commission_rate")
        ]

        return {
            "totalProducts": len(products.data),
            "avgCommission": (
                sum(commission_rates) / len(commission_rates)
                if commission_rates
                else 0.0
            ),
            "topCommission": max(commission_rates) if commission_rates else 0.0,
            "todayImports": 0,  # Would need separate tracking
        }

    except Exception as e:
        logger.error(f"[Shopee API] Stats error: {e}")
        # Return default values instead of error
        return {
            "totalProducts": 0,
            "avgCommission": 0.0,
            "topCommission": 0.0,
            "todayImports": 0,
        }


@router.get("/sync-status")
async def get_sync_status(current_admin: Dict = Depends(get_current_admin)):
    """
    Status do último sync - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()

        # Try to get latest sync log
        try:
            # Corrigido: campo correto é started_at (não created_at)
            result = (
                supabase.client.table("shopee_sync_log")
                .select("*")
                .order("started_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                return result.data[0]
        except Exception as table_error:
            logger.warning(f"[Shopee API] sync_log table not found: {table_error}")

        # Return null if no data
        return None

    except Exception as e:
        logger.error(f"[Shopee API] Sync status error: {e}")
        return None


@router.get("/top-commission")
async def get_top_commission_products(
    limit: int = Query(10, le=50), current_admin: Dict = Depends(get_current_admin)
):
    """
    Top produtos por comissão - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()

        # Try RPC function first
        try:
            result = supabase.client.rpc(
                "get_top_commission_products", {"p_limit": limit}
            ).execute()

            if result.data:
                return {"products": result.data, "count": len(result.data)}
        except Exception as rpc_error:
            logger.warning(
                f"[Shopee API] RPC function not found, using fallback: {rpc_error}"
            )

        # Fallback: Manual query
        result = (
            supabase.client.table("products")
            .select("*")
            .eq("store", "shopee")
            .eq("is_active", True)
            .order("commission_rate", desc=True)
            .limit(limit)
            .execute()
        )

        return {
            "products": result.data or [],
            "count": len(result.data) if result.data else 0,
        }

    except Exception as e:
        logger.error(f"[Shopee API] Top commission error: {e}")
        return {"products": [], "count": 0}


@router.get("/top-sales")
async def get_top_sales_products(
    limit: int = Query(10, le=50), current_admin: Dict = Depends(get_current_admin)
):
    """
    Top produtos por vendas - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()

        try:
            result = supabase.client.rpc(
                "get_top_sales_products", {"p_limit": limit}
            ).execute()

            if result.data:
                return {"products": result.data, "count": len(result.data)}
        except Exception as rpc_error:
            logger.warning(
                f"[Shopee API] RPC get_top_sales_products error: {rpc_error}"
            )

        return {"products": [], "count": 0}

    except Exception as e:
        logger.error(f"[Shopee API] Top sales error: {e}")
        return {"products": [], "count": 0}


@router.get("/top-popular")
async def get_top_popular_products(
    limit: int = Query(10, le=50), current_admin: Dict = Depends(get_current_admin)
):
    """
    Top produtos mais populares (Review/Search proxy) - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()

        try:
            result = supabase.client.rpc(
                "get_most_popular_products", {"p_limit": limit}
            ).execute()

            if result.data:
                return {"products": result.data, "count": len(result.data)}
        except Exception as rpc_error:
            logger.warning(
                f"[Shopee API] RPC get_most_popular_products error: {rpc_error}"
            )

        return {"products": [], "count": 0}

    except Exception as e:
        logger.error(f"[Shopee API] Top popular error: {e}")
        return {"products": [], "count": 0}


@router.get("/rate-limit-status")
async def get_rate_limit_status(current_admin: Dict = Depends(get_current_admin)):
    """
    Status do rate limiting - ADMIN ONLY
    """
    try:
        client = create_shopee_client()
        add_rate_limiting(client)

        status = client.get_rate_limit_status()

        return status

    except Exception as e:
        logger.error(f"[Shopee API] Rate limit status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/{item_id}/send-to-telegram")
async def send_product_to_telegram(
    item_id: int,
    product_data: Dict[str, Any],  # Recebe dados do produto do frontend
    current_user: Dict = Depends(get_current_user),
):
    """
    Envia um produto Shopee ao Telegram do usuário
    Requer configuração de bot token e channel ID
    """
    try:
        import os
        import httpx
        from datetime import datetime

        # Verifica configuração do Telegram
        from ..utils.telegram_settings_manager import telegram_settings

        bot_token = telegram_settings.get_bot_token()
        channel_id = telegram_settings.get_group_chat_id()

        if not bot_token or not channel_id:
            raise HTTPException(
                status_code=400,
                detail="Telegram não configurado. Configure no Dashboard -> Telegram",
            )

        # Usa os dados do produto enviados pelo frontend
        product = product_data

        # Funções de segurança: às vezes o frontend manda o dado dentro de array [valor]
        def safe_float(val, default=0.0):
            if isinstance(val, list): val = val[0] if val else default
            try: return float(val or default)
            except (ValueError, TypeError): return default

        def safe_int(val, default=0):
            if isinstance(val, list): val = val[0] if val else default
            try: return int(val or default)
            except (ValueError, TypeError): return default

        def safe_str(val, default=""):
            if isinstance(val, list): val = val[0] if val else default
            return str(val or default)

        # Formata mensagem para Telegram estilo "Brutalist / Alta Conversão"
        price    = safe_float(product.get("priceMin", 0))
        discount = safe_float(product.get("priceDiscountRate", 0))
        sales    = safe_int(product.get("sales", 0))
        rating   = safe_str(product.get("ratingStar", "N/A"))
        shop_type = safe_int(product.get("shopType", 0))
        product_name = safe_str(product.get("productName", "Produto"))

        # Trunca e escapa o nome (evita HTML inválido)
        if len(product_name) > 60:
            product_name = product_name[:57] + "..."
        product_name = html.escape(product_name)

        # AIDA: Attention
        if discount >= 40:
            attention = f"🚨 <b>RELÂMPAGO COM {int(discount)}% OFF!</b>\n\n"
        elif discount > 0:
            attention = f"🔥 <b>ACHADINHO COM {int(discount)}% OFF!</b>\n\n"
        else:
            attention = f"✨ <b>OFERTA IMPERDÍVEL!</b>\n\n"

        # AIDA: Interest
        interest = f"📦 {product_name}\n\n"
        if discount > 0:
            original_price = price / (1 - discount / 100)
            interest += f"❌ <s>De: R$ {original_price:.2f}</s>\n"
        interest += f"✅ <b>Por apenas: R$ {price:.2f}</b>\n\n"

        # AIDA: Desire
        badge = "👑 Loja Oficial" if shop_type == 1 else "⭐ Loja Indicada" if shop_type in (2, 4) else "🏬 Loja Shopee"
        desire = f"{badge} | ⭐ {rating}"
        desire += f" ({sales:,}+ Vendidos)\n\n" if sales > 0 else "\n\n"

        # AIDA: Action + Prova Social
        action = "⏳ <i>Vai esgotar rápido! Preço sujeito a alteração.</i>"
        reviews = product_data.get("reviews", [])
        if reviews:
            action = "💬 <b>O QUE DIZEM OS COMPRADORES:</b>\n"
            for r in reviews[:2]:
                comment = html.escape((r.get("comment") or "Produto excelente!")[:80])
                action += f"⭐ {comment}\n"
            action += "\n⏳ <i>Vai esgotar rápido! Preço sujeito a alteração.</i>"

        message = attention + interest + desire + action

        # Detecta mídia (vídeo > foto)
        video_url = product_data.get("videoUrl") or None
        raw_image = product.get("imageUrl") or ""

        # URLs Shopee não têm extensão → adiciona _tn.jpg para susercontent.com
        if raw_image and not any(
            raw_image.lower().endswith(ext)
            for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")
        ):
            image_url = (raw_image + "_tn.jpg") if "susercontent.com" in raw_image else raw_image
        else:
            image_url = raw_image

        media_url = video_url or image_url or None

        # Força HTTPS
        if media_url and media_url.startswith("http://"):
            media_url = media_url.replace("http://", "https://", 1)

        media_field = "video" if video_url else ("photo" if media_url else None)

        # Detecta tópico
        from ..utils.topic_router import get_thread_id
        thread_id = get_thread_id(
            product_name=product.get("productName", ""),
            keyword=product.get("keyword", ""),
            product_category=str(
                product.get("productCatIds", [""])[0]
                if product.get("productCatIds") else ""
            ),
        )

        # Link do botão
        offer_link = product.get("shortLink") or product.get("offerLink") or "https://afiliado.top"

        # Botão inline
        btn_text = f"🛒 COMPRAR {int(discount)}% OFF AGORA!" if discount else "🛒 COMPRAR AGORA!"
        reply_markup = {"inline_keyboard": [[{"text": btn_text, "url": offer_link}]]}

        logger.info(
            f"[TG] item={item_id} media={media_field} thread={thread_id} "
            f"url={str(media_url)[:80]} msg_len={len(message)}"
        )

        # ─────────────────────────────────────────────
        # 4 CAMADAS DE FALLBACK (garante entrega sempre)
        # L1: mídia  + tópico
        # L2: mídia  + sem tópico
        # L3: texto  + tópico
        # L4: texto  + sem tópico   ← nunca falha
        # ─────────────────────────────────────────────
        async def tg_post(client: httpx.AsyncClient, url: str, payload: dict) -> bool:
            """Tenta enviar; retorna True se OK, loga detalhes se 400."""
            resp = await client.post(url, json=payload, timeout=30.0)
            if resp.status_code == 200:
                return True
            logger.warning(
                f"[TG] {resp.status_code} ao chamar {url.split('/')[-1]}: {resp.text[:300]}"
            )
            return False

        tg_base   = f"https://api.telegram.org/bot{bot_token}"
        media_tg  = f"{tg_base}/send{'Video' if video_url else 'Photo'}"
        text_tg   = f"{tg_base}/sendMessage"

        common = {"chat_id": channel_id, "parse_mode": "HTML", "reply_markup": reply_markup}

        try:
            async with httpx.AsyncClient() as client:
                sent = False

                # L1: foto/vídeo + tópico
                if media_url and media_field and thread_id:
                    sent = await tg_post(client, media_tg, {
                        **common,
                        media_field: media_url,
                        "caption": message,
                        "message_thread_id": thread_id,
                        **({"supports_streaming": True} if video_url else {}),
                    })

                # L2: foto/vídeo sem tópico
                if not sent and media_url and media_field:
                    sent = await tg_post(client, media_tg, {
                        **common,
                        media_field: media_url,
                        "caption": message,
                        **({"supports_streaming": True} if video_url else {}),
                    })

                # L3: texto + tópico
                if not sent and thread_id:
                    sent = await tg_post(client, text_tg, {
                        **common,
                        "text": message,
                        "message_thread_id": thread_id,
                        "disable_web_page_preview": True,
                    })

                # L4: texto sem tópico (último recurso — sempre funciona)
                if not sent:
                    ok_resp = await client.post(text_tg, json={
                        **common,
                        "text": message,
                        "disable_web_page_preview": True,
                    }, timeout=15.0)
                    ok_resp.raise_for_status()
                    sent = True

            logger.info(f"[TG] Produto {item_id} entregue (topic={thread_id} mídia={media_field})")
            return {
                "success": True,
                "message": "Produto enviado para o Telegram com sucesso!",
                "product_name": product.get("productName", str(item_id)),
                "sent_at": datetime.now().isoformat(),
                "topic": thread_id,
                "has_media": bool(media_url),
            }

        except httpx.HTTPError as e:
            logger.error(f"[TG] Erro HTTP final ao enviar {item_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao enviar para Telegram: {str(e)}")

    except HTTPException:
        raise
    except httpx.HTTPError as e:
        logger.error(f"[Telegram] Erro HTTP ao enviar: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar para Telegram: {str(e)}")
    except Exception as e:
        logger.error(f"[Telegram] Erro ao enviar produto {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar produto: {str(e)}")
