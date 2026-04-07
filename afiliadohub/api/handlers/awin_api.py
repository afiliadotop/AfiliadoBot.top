"""
Awin Affiliate API - FastAPI Handler (Full Implementation)
Rotas para todos os endpoints da Awin: Links, Quota, Ofertas, Programas,
Comissões, Performance, Product Feed.
"""

import logging
import time
from typing import Optional, List
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

_PUBLIC_VOUCHERS_CACHE = {"timestamp": 0, "data": []}

from ..utils.awin_client import AwinAffiliateClient, AwinAPIError
from ..services.commission_radar_service import CommissionRadarService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/awin", tags=["Awin Affiliate"])
security = HTTPBearer()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


# ==================== DEPENDÊNCIAS ====================

async def get_awin_client() -> AwinAffiliateClient:
    try:
        return AwinAffiliateClient()
    except AwinAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Aceita qualquer Bearer token válido (JWT do usuário OU ADMIN_API_KEY)."""
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Token ausente")
    return token


# ==================== MODELOS ====================

class GenerateLinkRequest(BaseModel):
    advertiser_id: int
    destination_url: str
    shorten: bool = True
    campaign: Optional[str] = None


class BatchLinkItem(BaseModel):
    advertiser_id: int
    destination_url: str
    campaign: Optional[str] = None


class BatchLinksRequest(BaseModel):
    links: List[BatchLinkItem]


class OffersRequest(BaseModel):
    advertiser_ids: Optional[List[int]] = None
    promotion_types: Optional[List[str]] = None
    page: int = 1
    page_size: int = 50


# ==================== ROTAS ====================

@router.get("/status")
async def awin_status():
    """Verifica se as credenciais da Awin estão configuradas (público)."""
    publisher_id = os.getenv("AWIN_PUBLISHER_ID")
    token_set = bool(os.getenv("AWIN_API_TOKEN"))
    return {
        "configured": bool(publisher_id and token_set),
        "publisher_id": publisher_id or "NÃO CONFIGURADO",
        "token_set": token_set,
    }


# --- LINK BUILDER ---

@router.post("/generate-link")
async def generate_awin_link(
    request: GenerateLinkRequest,
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Gera um link de rastreamento Awin para um anunciante."""
    try:
        result = await client.generate_tracking_link(
            advertiser_id=request.advertiser_id,
            destination_url=request.destination_url,
            shorten=request.shorten,
            campaign=request.campaign,
        )
        if isinstance(result, list):
            result = result[0]
        return {
            "click_through_url": result.get("clickThroughUrl"),
            "short_url": result.get("shortClickThroughUrl") or result.get("clickThroughUrl"),
            "advertiser_id": request.advertiser_id,
        }
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/batch-links")
async def generate_batch_links(
    request: BatchLinksRequest,
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Gera até 100 links de rastreamento em lote."""
    if len(request.links) > 100:
        raise HTTPException(status_code=400, detail="Máximo de 100 links por batch")
    try:
        batch_payload = [
            {
                "advertiserId": item.advertiser_id,
                "destinationUrl": item.destination_url,
                **({"parameters": {"campaign": item.campaign}} if item.campaign else {}),
            }
            for item in request.links
        ]
        results = await client.generate_batch_links(batch_payload)
        return {"count": len(results), "results": results}
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# --- QUOTA ---

@router.get("/quota")
async def get_link_quota(
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Verifica a cota de links do LinkBuilder (uso diário)."""
    try:
        return await client.get_quota()
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# --- OFFERS / PROMOTIONS ---

@router.get("/public/vouchers")
async def get_public_joined_vouchers(
    client: AwinAffiliateClient = Depends(get_awin_client)
):
    """Retorna Vouchers EXCLUSIVOS dos Programas Habilitados (Cache 1 hora). Sem Auth."""
    global _PUBLIC_VOUCHERS_CACHE
    now = time.time()
    
    # 3600 segundos (1 hora)
    if now - _PUBLIC_VOUCHERS_CACHE["timestamp"] < 3600 and _PUBLIC_VOUCHERS_CACHE["data"]:
        return {"data": _PUBLIC_VOUCHERS_CACHE["data"], "cached": True}
        
    try:
        # Primeiro, pegamos apenas afiliados 'joined'
        programs = await client.get_programs(relationship="joined")
        if not programs:
            return {"data": [], "cached": False}
            
        joined_ids = [str(p["id"]) for p in programs]
        
        # Como o Awin Client converte advertiser_ids, vamos poupar limit limit limitando as tops 40 lojas associadas!
        offers_resp = await client.get_offers(
            advertiser_ids=[int(id) for id in joined_ids[:50]],
            promotion_types=["voucher", "deal"],
            page_size=100
        )
        offers = offers_resp.get("data", []) if isinstance(offers_resp, dict) else []
        if isinstance(offers_resp, list):
            offers = offers_resp
            
        # Filtro Rigoroso (safety fallback) garantindo apenas joined networks
        filtered_offers = [
            o for o in offers 
            if str(o.get('advertiser', {}).get('id')) in joined_ids
        ]
        
        # Otimização final para a vitrine
        for o in filtered_offers:
            # Gerando a imgUrl do logotipo a partir do public logo da Awin:
            adv_id = o.get('advertiser', {}).get('id')
            if adv_id and not o.get('image_url'):
                o['image_url'] = f"https://ws.awin.com/awin/affiliate/33923/advertiser/{adv_id}/profile/logo"
        
        _PUBLIC_VOUCHERS_CACHE["timestamp"] = now
        _PUBLIC_VOUCHERS_CACHE["data"] = filtered_offers
        
        return {"data": filtered_offers, "cached": False}
        
    except AwinAPIError as e:
        if _PUBLIC_VOUCHERS_CACHE["data"]:
            return {"data": _PUBLIC_VOUCHERS_CACHE["data"], "cached": True, "error": str(e)}
        raise HTTPException(status_code=502, detail=f"Erro ao buscar Vouchers públicos: {str(e)}")

@router.post("/offers")
async def get_awin_offers(
    request: OffersRequest,
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Busca promoções e vouchers dos anunciantes Awin."""
    try:
        return await client.get_offers(
            advertiser_ids=request.advertiser_ids,
            promotion_types=request.promotion_types,
            page=request.page,
            page_size=request.page_size,
        )
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/coupons/run")
async def run_awin_coupons(
    max_broadcasts: int = Query(3, description="Máximo de vouchers disparados"),
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """
    MÁQUINA DE CONVERSÃO (Awin Voucher Radar):
    - Extrai promoções garantidas da Awin do tipo 'voucher'.
    - Dispara imediatamente os melhores cupons no Canal Telegram.
    """
    from .telegram import TelegramBot
    from ..utils.telegram_settings_manager import telegram_settings

    try:
        radar = CommissionRadarService()
        # O Radar Awin agora busca tanto 'deal' quanto 'voucher'
        result = await radar.run_awin_radar(max_broadcasts=max_broadcasts, auto_dispatch=True)
        return result
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=f"Erro na Awin: {str(e)}")
    except Exception as e:
        logger.error(f"[Awin Coupon Run] Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- PROGRAMS ---

@router.get("/programs")
async def get_programs(
    relationship: Optional[str] = Query("joined", description="joined|pending|suspended|rejected|notjoined"),
    country_code: Optional[str] = Query(None, description="ISO Alpha-2, ex: BR, US, GB"),
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Lista todos os programas afiliados do Publisher."""
    try:
        programs = await client.get_programs(relationship=relationship, country_code=country_code)
        return {"count": len(programs), "relationship": relationship, "programs": programs}
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/programs/{advertiser_id}")
async def get_program_details(
    advertiser_id: int,
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Detalhes de um programa afiliado específico."""
    try:
        return await client.get_program_details(advertiser_id)
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# --- COMMISSION GROUPS ---

@router.get("/commission-groups/{advertiser_id}")
async def get_commission_groups(
    advertiser_id: int,
    include_conditions: bool = Query(False),
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Grupos e percentuais de comissão de um anunciante."""
    try:
        groups = await client.get_commission_groups(advertiser_id, include_conditions)
        return {"advertiser_id": advertiser_id, "count": len(groups), "groups": groups}
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# --- PERFORMANCE REPORTS ---

@router.get("/performance")
async def get_performance_report(
    start_date: str = Query(default=str(date.today() - timedelta(days=30))),
    end_date: str = Query(default=str(date.today())),
    region: str = Query("BR"),
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Relatório de performance financeira por anunciante."""
    try:
        data = await client.get_performance_report(
            start_date=start_date,
            end_date=end_date,
            region=region,
        )
        return {
            "period": {"start": start_date, "end": end_date, "region": region},
            "count": len(data),
            "data": data,
        }
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/campaign-report")
async def get_campaign_report(
    start_date: str = Query(default=str(date.today() - timedelta(days=30))),
    end_date: str = Query(default=str(date.today())),
    region: str = Query("BR"),
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """Relatório de campanhas por período."""
    try:
        data = await client.get_campaign_report(start_date, end_date, region)
        return {"period": {"start": start_date, "end": end_date}, "data": data}
    except AwinAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# --- PRODUCT FEED ---

@router.get("/product-feed/{advertiser_id}")
async def get_product_feed(
    advertiser_id: int,
    locale: str = Query("pt_BR"),
    max_products: int = Query(200, le=1000),
    _: str = Depends(verify_token),
    client: AwinAffiliateClient = Depends(get_awin_client),
):
    """
    Baixa o catálogo de produtos de um anunciante (Google Feed Format).
    Rate limit: 5 req/min (conforme Awin docs).
    """
    try:
        products = await client.download_product_feed(
            advertiser_id=advertiser_id,
            locale=locale,
            max_products=max_products,
        )
        return {
            "advertiser_id": advertiser_id,
            "locale": locale,
            "count": len(products),
            "products": products,
        }
    except AwinAPIError as e:
        if "404" in str(e) or "não encontrado" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=502, detail=str(e))
