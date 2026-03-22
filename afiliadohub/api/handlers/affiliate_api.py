"""
Affiliate API Handler
ITIL Activity: Deliver & Support (Affiliate Endpoints)

Exposes the affiliate-bot-tools skill capabilities as REST endpoints:
  POST /api/affiliate/link        — generate monetized affiliate link
  GET  /api/products/{id}/price-history  — fetch price history
  POST /api/products/{id}/scrape  — trigger price scrape (admin)
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, HttpUrl
import os

from ..models.domain import AffiliateLinkResult, DiscountAnalysis, PriceHistory
from ..services.affiliate_service import AffiliateService
from ..repositories.price_history_repository import PriceHistoryRepository
from ..utils.supabase_client import get_supabase_manager

router = APIRouter(tags=["Affiliate"])
logger = logging.getLogger(__name__)
security = HTTPBearer()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

def get_affiliate_service() -> AffiliateService:
    return AffiliateService()


def get_price_history_repo() -> PriceHistoryRepository:
    supabase = get_supabase_manager()
    return PriceHistoryRepository(supabase.client)


async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if ADMIN_API_KEY and credentials.credentials != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Admin token inválido")
    return credentials.credentials


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AffiliateLinkRequest(BaseModel):
    base_url: str = Field(..., description="URL limpa do produto na loja")
    store_name: str = Field(..., description="Nome da loja: Amazon, Shopee, Mercado Livre…")
    offer_id: str = Field(..., description="ID interno da oferta")

    class Config:
        json_schema_extra = {
            "example": {
                "base_url": "https://www.amazon.com.br/dp/B09XYZ123",
                "store_name": "Amazon",
                "offer_id": "prod-42",
            }
        }


class ScrapeResponse(BaseModel):
    product_id: int
    scraped_price: Optional[float]
    saved: bool
    scrape_status: str
    message: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "/affiliate/link",
    response_model=AffiliateLinkResult,
    summary="Gerar link de afiliado monetizado",
    description=(
        "Recebe a URL limpa de um produto e retorna a URL com a tag de afiliado "
        "correta para a loja informada, além do link interno de rastreio."
    ),
)
def generate_affiliate_link(
    payload: AffiliateLinkRequest,
    service: AffiliateService = Depends(get_affiliate_service),
) -> AffiliateLinkResult:
    try:
        return service.generate_affiliate_link(
            base_url=payload.base_url,
            store_name=payload.store_name,
            offer_id=payload.offer_id,
        )
    except Exception as exc:
        logger.error(f"[affiliate/link] Erro: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/products/{product_id}/price-history",
    summary="Histórico de preços de um produto",
    description="Retorna os últimos N registros de preço coletados por scraping.",
)
def get_price_history(
    product_id: int,
    limit: int = Query(default=30, ge=1, le=200),
    repo: PriceHistoryRepository = Depends(get_price_history_repo),
):
    try:
        rows = repo.get_price_history(product_id, limit=limit)
        avg = repo.get_historical_average(product_id)
        min_price = repo.get_min_price(product_id)
        return {
            "product_id": product_id,
            "count": len(rows),
            "historical_average": avg,
            "min_price_ever": min_price,
            "records": rows,
        }
    except Exception as exc:
        logger.error(f"[products/{product_id}/price-history] Erro: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/products/{product_id}/scrape",
    response_model=ScrapeResponse,
    summary="Disparar scraping de preço (admin)",
    description=(
        "Realiza um scrape leve da URL original do produto, salva o preço "
        "coletado em price_history e retorna o resultado. Requer autenticação admin."
    ),
    dependencies=[Depends(verify_admin)],
)
async def scrape_product_price(
    product_id: int,
    cep: Optional[str] = Query(default=None, max_length=8, description="CEP para cálculo de frete"),
    service: AffiliateService = Depends(get_affiliate_service),
    repo: PriceHistoryRepository = Depends(get_price_history_repo),
    price_repo: PriceHistoryRepository = Depends(get_price_history_repo),
):
    # 1. Fetch product URL from DB
    supabase = get_supabase_manager()
    product_res = (
        supabase.client.table("products")
        .select("id, name, original_link, affiliate_link")
        .eq("id", product_id)
        .limit(1)
        .execute()
    )

    if not product_res.data:
        raise HTTPException(status_code=404, detail=f"Produto {product_id} não encontrado")

    product = product_res.data[0]
    url = product.get("original_link") or product.get("affiliate_link")

    if not url:
        raise HTTPException(status_code=422, detail="Produto sem URL para scraping")

    # 2. Scrape
    scrape_result = await service.scrape_product_data(url=url, cep=cep)

    scraped_price: Optional[float] = scrape_result.get("price")
    saved = False

    # 3. Save to price_history if price was extracted
    if scraped_price is not None and scraped_price > 0:
        saved_row = repo.save_price(
            product_id=product_id,
            price=scraped_price,
            cep=cep,
            source="scraper",
        )
        saved = saved_row is not None

    return ScrapeResponse(
        product_id=product_id,
        scraped_price=scraped_price,
        saved=saved,
        scrape_status=scrape_result.get("status", "unknown"),
        message=(
            f"Preço R${scraped_price} salvo com sucesso."
            if saved
            else f"Scrape concluído (status={scrape_result.get('status')}), preço não extraído automaticamente."
        ),
    )
