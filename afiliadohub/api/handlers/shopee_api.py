"""
Shopee API Endpoints for Frontend Integration
FastAPI router with privacy-aware product listings and admin features
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import logging

from ..utils.shopee_client import create_shopee_client
from ..utils.shopee_extensions import add_rate_limiting
from ..utils.supabase_client import get_supabase_manager
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
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Avaliação mínima"),
    min_sales: Optional[int] = Query(None, ge=0, description="Vendas mínimas"),
    min_discount: Optional[int] = Query(None, ge=0, le=100, description="Desconto mínimo %"),
    
    # Auth
    current_user: Dict = Depends(get_current_user)
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
            "sales": 2,       # ITEM_SOLD_DESC
            "price": 4,       # PRICE_ASC
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
                limit=limit
            )
        
        products = result.get("nodes", [])
        page_info = result.get("pageInfo", {})
        
        # Apply client-side filters
        filtered_products = products
        
        if price_min is not None or price_max is not None:
            filtered_products = [
                p for p in filtered_products
                if (price_min is None or float(p.get("priceMin", 0)) >= price_min) and
                   (price_max is None or float(p.get("priceMax", 999999)) <= price_max)
            ]
        
        if min_rating is not None:
            filtered_products = [
                p for p in filtered_products
                if p.get("ratingStar") and float(p.get("ratingStar", 0)) >= min_rating
            ]
        
        if min_sales is not None:
            filtered_products = [
                p for p in filtered_products
                if p.get("sales", 0) >= min_sales
            ]
        
        if min_discount is not None:
            filtered_products = [
                p for p in filtered_products
                if p.get("priceDiscountRate", 0) >= min_discount
            ]
        
        # PRIVACY: Remove commission data for non-admin users
        is_admin = current_user.get("role") == "admin"
        
        if not is_admin:
            for product in filtered_products:
                product.pop('commissionRate', None)
                product.pop('commission', None)
                product.pop('sellerCommissionRate', None)
                product.pop('shopeeCommissionRate', None)
        
        # Calculate pagination metadata
        total_products = len(filtered_products)
        has_more = page_info.get("hasNextPage", False) or len(filtered_products) >= limit
        total_pages = (total_products // limit) + (1 if total_products % limit > 0 else 0)
        
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
        
        logger.info(f"[Shopee API] Returning {len(filtered_products)} products (admin={is_admin}, filters={len(applied_filters)})")
        
        return {
            "products": filtered_products,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_products,
                "hasMore": has_more,
                "totalPages": max(total_pages, 1)
            },
            "appliedFilters": applied_filters
        }
        
    except Exception as e:
        logger.error(f"[Shopee API] Error fetching products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_products(
    request: ProductSearchRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Busca produtos por keyword
    """
    try:
        client = create_shopee_client()
        add_rate_limiting(client)
        
        async with client:
            result = await client.get_products(
                keyword=request.keyword,
                sort_type=request.sortType,
                limit=request.limit
            )
        
        products = result.get("nodes", [])
        
        # Privacy filter
        is_admin = current_user.get("role") == "admin"
        if not is_admin:
            for product in products:
                product.pop('commissionRate', None)
                product.pop('commission', None)
                product.pop('sellerCommissionRate', None)
                product.pop('shopeeCommissionRate', None)
        
        return {
            "products": products,
            "count": len(products),
            "hasMore": result.get("pageInfo", {}).get("hasNextPage", False)
        }
        
    except Exception as e:
        logger.error(f"[Shopee API] Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-link")
async def generate_short_link(
    request: GenerateLinkRequest,
    current_user: Dict = Depends(get_current_user)
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
                origin_url=request.url,
                sub_ids=sub_ids
            )
        
        if not short_link:
            raise HTTPException(status_code=400, detail="Failed to generate link")
        
        logger.info(f"[Shopee API] Link generated for user {current_user.get('id')}")
        
        return {
            "shortLink": short_link,
            "originalUrl": request.url
        }
        
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
    current_user: Dict = Depends(get_current_user)
):
    """Lista ofertas gerais Shopee"""
    try:
        client = create_shopee_client()
        add_rate_limiting(client)
        
        async with client:
            result = await client.get_shopee_offers(
                keyword=keyword,
                sort_type=sort_type,
                limit=limit
            )
        
        return result
        
    except Exception as e:
        logger.error(f"[Shopee API] Offers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ENDPOINTS ====================

@router.get("/stats")
async def get_stats(
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Estatísticas Shopee - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()
        
        # Try to get stats from RPC function
        try:
            stats_result = supabase.client.rpc('get_shopee_statistics').execute()
            
            if stats_result.data:
                return stats_result.data
        except Exception as rpc_error:
            logger.warning(f"[Shopee API] RPC function not found, using fallback: {rpc_error}")
        
        # Fallback: Calculate stats manually
        products = supabase.client.table('products')\
            .select('commission_rate')\
            .eq('store', 'shopee')\
            .eq('is_active', True)\
            .execute()
        
        if not products.data:
            return {
                "totalProducts": 0,
                "avgCommission": 0.0,
                "topCommission": 0.0,
                "todayImports": 0
            }
        
        commission_rates = [float(p.get('commission_rate', 0)) for p in products.data if p.get('commission_rate')]
        
        return {
            "totalProducts": len(products.data),
            "avgCommission": sum(commission_rates) / len(commission_rates) if commission_rates else 0.0,
            "topCommission": max(commission_rates) if commission_rates else 0.0,
            "todayImports": 0  # Would need separate tracking
        }
        
    except Exception as e:
        logger.error(f"[Shopee API] Stats error: {e}")
        # Return default values instead of error
        return {
            "totalProducts": 0,
            "avgCommission": 0.0,
            "topCommission": 0.0,
            "todayImports": 0
        }

@router.get("/sync-status")
async def get_sync_status(
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Status do último sync - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()
        
        # Try to get latest sync log
        try:
            result = supabase.client.table('shopee_sync_log')\
                .select('*')\
                .order('started_at', desc=True)\  # Corrigido: campo correto é started_at
                .limit(1)\
                .execute()
            
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
    limit: int = Query(10, le=50),
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Top produtos por comissão - ADMIN ONLY
    """
    try:
        supabase = get_supabase_manager()
        
        # Try RPC function first
        try:
            result = supabase.client.rpc('get_top_commission_products', {
                'p_limit': limit  # Corrigido: nome do parâmetro correto
            }).execute()
            
            if result.data:
                return {
                    "products": result.data,
                    "count": len(result.data)
                }
        except Exception as rpc_error:
            logger.warning(f"[Shopee API] RPC function not found, using fallback: {rpc_error}")
        
        # Fallback: Manual query
        result = supabase.client.table('products')\
            .select('*')\
            .eq('store', 'shopee')\
            .eq('is_active', True)\
            .order('commission_rate', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "products": result.data or [],
            "count": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        logger.error(f"[Shopee API] Top commission error: {e}")
        return {
            "products": [],
            "count": 0
        }

@router.get("/rate-limit-status")
async def get_rate_limit_status(
    current_admin: Dict = Depends(get_current_admin)
):
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
    current_user: Dict = Depends(get_current_user)
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
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
        
        if not bot_token or not channel_id:
            raise HTTPException(
                status_code=400,
                detail="Telegram não configurado. Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHANNEL_ID no .env"
            )
        
        # Usa os dados do produto enviados pelo frontend
        product = product_data
        
        # Formata mensagem para Telegram usando AIDA
        price = float(product.get("priceMin", 0))
        discount = product.get("priceDiscountRate", 0)
        sales = product.get('sales', 0)
        rating = product.get('ratingStar', 'N/A')
        
        # AIDA: Attention (Atenção) - Título chamativo com emoji e desconto
        attention = f"🔥 <b>OFERTA IMPERDÍVEL!</b> 🔥"
        if discount > 0:
            attention = f"🔥 <b>SUPER DESCONTO {discount}% OFF!</b> 🔥"
        
        # AIDA: Interest (Interesse) - Produto e preço atrativo
        interest = f"\n\n🛍️ <b>{product['productName']}</b>"
        interest += f"\n\n💰 <b>Apenas R$ {price:.2f}</b>"
        
        if discount > 0:
            original_price = price / (1 - discount/100)
            interest += f"\n<s>De R$ {original_price:.2f}</s>"
            interest += f"\n<b>Economize R$ {(original_price - price):.2f}!</b>"
        
        # AIDA: Desire (Desejo) - Social proof e urgência
        desire = "\n\n✨ <b>Por que você vai amar:</b>"
        
        if sales > 1000:
            desire += f"\n✅ Mais de {sales:,} pessoas já compraram!"
        elif sales > 100:
            desire += f"\n✅ {sales:,}+ vendas confirmadas"
        
        if rating and rating != 'N/A':
            desire += f"\n⭐ Avaliação {rating}/5.0 - Produto aprovado!"
        
        desire += f"\n🏪 Loja verificada: {product.get('shopName', 'N/A')}"
        desire += "\n📦 Entrega rápida e segura"
        desire += "\n🔒 Compra 100% protegida"
        
        if discount > 0:
            desire += f"\n\n⚡ <b>ATENÇÃO: Promoção por tempo limitado!</b>"
        
        # AIDA: Action (Ação) - Call to action claro
        action = "\n\n👇 <b>GARANTA O SEU AGORA!</b> 👇"
        
        # Monta mensagem final
        message = attention + interest + desire + action
        
        # Envia para Telegram via API
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        # Valida URL da imagem
        image_url = product.get("imageUrl", "")
        
        # Garante que a URL seja HTTPS
        if image_url.startswith("http://"):
            image_url = image_url.replace("http://", "https://", 1)
        
        payload = {
            "chat_id": channel_id,
            "photo": image_url,
            "caption": message,
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [[
                    {
                        "text": "🛒 COMPRAR AGORA COM DESCONTO!",
                        "url": product.get('offerLink', '#')
                    }
                ]]
            }
        }
        
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(telegram_url, json=payload, timeout=10.0)
                
                if response.status_code == 200:
                    logger.info(f"[Telegram] Produto {item_id} enviado com sucesso para {channel_id}")
                    
                    return {
                        "success": True,
                        "message": "Produto enviado para o Telegram com sucesso!",
                        "product_name": product['productName'],
                        "sent_at": datetime.now().isoformat()
                    }
                else:
                    # Se falhar com foto, tenta enviar só texto
                    logger.warning(f"[Telegram] Falha ao enviar foto, tentando enviar apenas texto: {response.text}")
                    
                    # Fallback: envia como mensagem de texto
                    text_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    text_payload = {
                        "chat_id": channel_id,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False,
                        "reply_markup": {
                            "inline_keyboard": [[
                                {
                                    "text": "🛒 COMPRAR AGORA COM DESCONTO!",
                                    "url": product.get('offerLink', '#')
                                }
                            ]]
                        }
                    }
                    
                    text_response = await http_client.post(text_url, json=text_payload, timeout=10.0)
                    text_response.raise_for_status()
                    
                    logger.info(f"[Telegram] Produto {item_id} enviado como texto para {channel_id}")
                    
                    return {
                        "success": True,
                        "message": "Produto enviado para o Telegram (sem imagem)",
                        "product_name": product['productName'],
                        "sent_at": datetime.now().isoformat()
                    }
        
        except httpx.HTTPError as e:
            logger.error(f"[Telegram] Erro HTTP ao enviar: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao enviar para Telegram: {str(e)}"
            )
        
    except HTTPException:
        raise
    except httpx.HTTPError as e:
        logger.error(f"[Telegram] Erro HTTP ao enviar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar para Telegram: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[Telegram] Erro ao enviar produto {item_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar produto: {str(e)}"
        )
