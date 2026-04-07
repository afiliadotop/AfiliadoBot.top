"""
Commission Junction (CJ) Affiliate API — FastAPI Handler (CORRECTED)

Routes:
  GET  /cj/status         — verifica credenciais (público)
  GET  /cj/status/live    — valida token ao vivo
  GET  /cj/links          — busca produtos por keywords (shoppingProducts)
  GET  /cj/feeds          — lista feeds disponíveis (shoppingProductFeeds)
  GET  /cj/advertisers    — lista anunciantes via REST Advertiser Lookup API
  POST /cj/broadcast      — envia oferta CJ ao Telegram
  POST /cj/radar/run      — MÁQUINA DE CONVERSÃO: caça descontos >50%
  POST /cj/coupons/run    — MÁQUINA DE CONVERSÃO: caça promoções/cupons
"""

import logging
import os
from typing import Optional, List

from ..utils.cj_client import CJAffiliateClient, CJAPIError
from ..services.commission_radar_service import CommissionRadarService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cj", tags=["CJ Affiliate"])
security = HTTPBearer()


# ==================== DEPENDÊNCIAS ====================

async def get_cj_client() -> CJAffiliateClient:
    try:
        return CJAffiliateClient()
    except CJAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Aceita qualquer Bearer token válido (JWT do usuário)."""
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Token ausente")
    return token


# ==================== MODELOS ====================

class BroadcastRequest(BaseModel):
    title: str
    description: Optional[str] = None
    click_url: str
    image_url: Optional[str] = None
    advertiser_name: Optional[str] = None
    coupon_code: Optional[str] = None
    sale_price: Optional[float] = None
    original_price: Optional[float] = None
    currency: str = "USD"
    promotion_type: Optional[str] = None


# ==================== ROTAS ====================

@router.get("/status")
async def cj_status():
    """Verifica se as credenciais CJ estão configuradas (público)."""
    token_set = bool(os.getenv("CJ_API_TOKEN"))
    company_id = os.getenv("CJ_COMPANY_ID", "")
    return {
        "configured": bool(token_set and company_id),
        "company_id": company_id or "NÃO CONFIGURADO",
        "token_set": token_set,
    }


@router.get("/status/live")
async def cj_status_live(
    client: CJAffiliateClient = Depends(get_cj_client),
):
    """
    Valida token ao vivo com introspection do schema da Product Feed API.
    Retorna os query types disponíveis para confirmar acesso.
    """
    try:
        return await client.check_credentials()
    except CJAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/links")
async def search_cj_products(
    keywords: Optional[str] = Query(None, description="Palavras-chave"),
    advertiser_ids: Optional[str] = Query(None, description="IDs de anunciantes separados por vírgula"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    _: str = Depends(verify_token),
    client: CJAffiliateClient = Depends(get_cj_client),
):
    """
    Busca produtos CJ via shoppingProducts (Product Feed GraphQL API).
    Parâmetros opcionais: keywords, advertiser_ids (partnerIds).
    """
    ids: Optional[List[str]] = None
    if advertiser_ids:
        ids = [a.strip() for a in advertiser_ids.split(",") if a.strip()]

    try:
        result = await client.search_products(
            keywords=keywords,
            advertiser_ids=ids,
            page_size=page_size,
            page_number=page,
        )
        return result
    except CJAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/feeds")
async def get_cj_feeds(
    _: str = Depends(verify_token),
    client: CJAffiliateClient = Depends(get_cj_client),
):
    """Lista feeds de produtos disponíveis (shoppingProductFeeds)."""
    try:
        return await client.get_product_feeds()
    except CJAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/advertisers")
async def get_cj_advertisers(
    relationship_status: str = Query(
        "joined",
        description="Status: joined | not-joined | applied | rejected | suspended | inactive",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    _: str = Depends(verify_token),
    client: CJAffiliateClient = Depends(get_cj_client),
):
    """
    Lista anunciantes CJ via REST Advertiser Lookup API.
    Retorna anunciantes com seus dados de programa.
    """
    try:
        result = await client.get_advertisers(
            relationship_status=relationship_status,
            page=page,
            records_per_page=page_size,
        )
        return result
    except CJAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/broadcast")
async def broadcast_cj_offer(
    payload: BroadcastRequest,
    _: str = Depends(verify_token),
):
    """
    Envia uma oferta CJ diretamente para o canal do Telegram configurado.
    """
    from ..handlers.telegram import TelegramBot
    from ..utils.telegram_settings_manager import telegram_settings

    try:
        tg_helper = TelegramBot()
        chat_id = telegram_settings.get_group_chat_id()
        if not chat_id:
            raise HTTPException(
                status_code=400,
                detail="Chat ID do Telegram não configurado. Configure no painel.",
            )

        # Calcular desconto se possível
        discount_pct: Optional[str] = None
        if payload.sale_price and payload.original_price and payload.original_price > 0:
            pct = ((payload.original_price - payload.sale_price) / payload.original_price) * 100
            if pct > 0:
                discount_pct = f"{pct:.0f}%"

        product_dict = {
            "id": 0,
            "name": payload.title,
            "title": payload.title,
            "description": payload.description or "",
            "affiliate_link": payload.click_url,
            "short_link": payload.click_url,
            "category": payload.promotion_type or "cj",
            "original_price": payload.original_price,
            "discount_price": payload.sale_price,
            "coupon_code": payload.coupon_code,
            "store": f"CJ/{payload.advertiser_name or 'Affiliate'}",
            "image_url": payload.image_url,
            "discount_pct": discount_pct,
            "is_active": True,
            "tags": ["cj", "afiliado"],
        }

        success = await tg_helper.send_product_to_channel(chat_id, product_dict)
        if not success:
            raise HTTPException(
                status_code=500, detail="Erro ao enviar mensagem para o Telegram"
            )

        logger.info(f"[CJ] Oferta '{payload.title}' enviada para {chat_id}")
        return {
            "status": "success",
            "message": f"Oferta '{payload.title}' enviada ao Telegram",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CJ Broadcast] Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/radar/run")
async def run_cj_radar(
    target_discount_pct: float = Query(50.0, description="Mínimo de desconto percentual (ex: 50)"),
    max_broadcasts: int = Query(3, description="Máximo de ofertas enviadas de uma vez"),
    _: str = Depends(verify_token),
    client: CJAffiliateClient = Depends(get_cj_client),
):
    """
    Executa a MÁQUINA DE CONVERSÃO de forma manual:
    - Busca os 100 primeiros produtos (pode ser ajustado)
    - Filtra aqueles cujo desconto é maior ou igual ao `target_discount_pct`
    - Dispara no máximo as X (`max_broadcasts`) melhores ofertas para o Canal Telegram
    """
    from ..handlers.telegram import TelegramBot
    from ..utils.telegram_settings_manager import telegram_settings

    try:
        radar = CommissionRadarService()
        result = await radar.run_cj_radar(
            min_discount=target_discount_pct,
            max_broadcasts=max_broadcasts,
            auto_dispatch=True
        )
        return result

    except CJAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"[CJ Radar Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coupons/run")
async def run_cj_coupons(
    keyword: str = Query("coupon", description="Palavra para caçar promoções (ex: cupons, coupon, promo)"),
    _: str = Depends(verify_token),
    client: CJAffiliateClient = Depends(get_cj_client),
):
    """
    MÁQUINA DE CONVERSÃO: Consulta de Cupons ativa.
    Como best-effort, pesquisa na fonte de produtos usando a sintaxe de coupon, 
    já que a GraphQL tem limitação na API direta de promotions.
    """
    try:
        radar = CommissionRadarService()
        vouchers = await radar.fetch_vouchers()
        # Filtra apenas CJ se desejar, ou retorna todos os detectados pelo keyword
        cj_vouchers = [v for v in vouchers if "CJ" in v.get("store", "")]
        
        if not cj_vouchers:
            return {"status": "success", "message": "Nenhum cupom ou promoção associada encontrada agora.", "found": 0}
            
        return {
            "status": "success",
            "message": "Itens com potencial cupom encontrados na CJ.",
            "found": len(cj_vouchers),
            "items": cj_vouchers
        }
    except CJAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))

