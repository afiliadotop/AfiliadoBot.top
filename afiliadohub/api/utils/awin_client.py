"""
Awin Affiliate API Client - Full Implementation
Covers: LinkBuilder, Quota, Offers, Programs, Commission, Performance, Product Feed
Documentation: https://help.awin.com/apidocs/introduction-1
"""

import os
import logging
import json
from typing import Optional, List, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)

AWIN_API_BASE = "https://api.awin.com"


class AwinAPIError(Exception):
    """Erro genérico da API Awin"""
    pass


class AwinAffiliateClient:
    """
    Cliente completo para a API REST da Awin (Publisher).

    Endpoints cobertos:
    - LinkBuilder (single + batch)
    - Link Quota
    - Offers/Promotions
    - Programs (list + details)
    - Commission Groups
    - Performance Report
    - Campaign Report
    - Product Feed (Google Format / JSONL)
    """

    def __init__(
        self,
        publisher_id: Optional[int] = None,
        api_token: Optional[str] = None,
    ):
        self.publisher_id = publisher_id or int(os.getenv("AWIN_PUBLISHER_ID", "0"))
        self.api_token = api_token or os.getenv("AWIN_API_TOKEN", "")

        if not self.publisher_id or not self.api_token:
            raise AwinAPIError(
                "Awin não configurada. Verifique AWIN_PUBLISHER_ID e AWIN_API_TOKEN no .env"
            )

        logger.info(f"[Awin] Cliente inicializado para Publisher ID: {self.publisher_id}")

    def _headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

    # ==================== LINK BUILDER ====================

    async def generate_tracking_link(
        self,
        advertiser_id: int,
        destination_url: str,
        shorten: bool = True,
        campaign: Optional[str] = None,
    ) -> dict:
        """Gera um único link de rastreamento Awin."""
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/linkbuilder/generate"
        payload: dict = {
            "advertiserId": advertiser_id,
            "destinationUrl": destination_url,
            "shorten": shorten,
        }
        if campaign:
            payload["parameters"] = {"campaign": campaign}

        logger.info(f"[Awin] Gerando link para Anunciante {advertiser_id}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    # Se falhar pelo encurtador (quota limits), refaz sem shorten
                    if shorten and ("quota" in body.lower() or "limit" in body.lower() or resp.status == 429):
                        logger.warning(f"[Awin] Limite de links curtos atingido. Gerando url longa como fallback.")
                        payload["shorten"] = False
                        async with session.post(url, json=payload, headers=self._headers()) as retry_resp:
                            if retry_resp.status != 200:
                                raise AwinAPIError(f"Awin LinkBuilder (Fallback) retornou {retry_resp.status}: {await retry_resp.text()}")
                            return await retry_resp.json()
                            
                    raise AwinAPIError(f"Awin LinkBuilder retornou {resp.status}: {body}")
                return await resp.json()

    async def generate_batch_links(
        self,
        requests: List[Dict[str, Any]],
    ) -> List[dict]:
        """
        Gera até 100 links de rastreamento de uma só vez.
        Cada item em `requests` deve ter: advertiserId, destinationUrl.
        Nota: Batch não suporta shorten=true (limitação da Awin).
        """
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/linkbuilder/generate-batch"
        payload = {"requests": requests}
        logger.info(f"[Awin] Gerando batch de {len(requests)} links")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Batch retornou {resp.status}: {body}")
                data = await resp.json()
                # Resposta: { "responses": [...] }
                return data.get("responses", data) if isinstance(data, dict) else data

    # ==================== QUOTA ====================

    async def get_quota(self) -> dict:
        """Verifica a cota de links restante do Publisher."""
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/linkbuilder/quota"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Quota retornou {resp.status}: {body}")
                return await resp.json()

    # ==================== OFFERS / PROMOTIONS ====================

    async def get_offers(
        self,
        advertiser_ids: Optional[List[int]] = None,
        promotion_types: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """
        Busca promoções e vouchers dos anunciantes Awin.
        Tipos de promoção: voucher, deal, product
        """
        url = f"{AWIN_API_BASE}/publisher/{self.publisher_id}/promotions"
        
        payload: dict = {
            "page": page,
            "pageSize": page_size,
        }
        
        if advertiser_ids or promotion_types or True: # adding status filter
            filters = {"status": "active"}
            if advertiser_ids:
                filters["advertiserIds"] = advertiser_ids
            if promotion_types:
                filters["promotionTypes"] = promotion_types
            payload["filters"] = filters

        logger.info(f"[Awin] Buscando ofertas (página {page})")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self._headers()) as resp:
                if resp.status >= 300:
                    body = await resp.text()
                    logger.error(f"[Awin] Erro {resp.status} em {url}: {body}")
                    raise AwinAPIError(f"Awin Offers retornou {resp.status}: {body}")
                return await resp.json()

    # ==================== PROGRAMS ====================

    async def get_programs(
        self,
        relationship: Optional[str] = "joined",
        country_code: Optional[str] = None,
    ) -> List[dict]:
        """
        Lista programas afiliados do Publisher.
        relationship: joined | pending | suspended | rejected | notjoined
        """
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/programmes"
        params: dict = {}
        if relationship:
            params["relationship"] = relationship
        if country_code:
            params["countryCode"] = country_code

        logger.info(f"[Awin] Listando programas (relationship={relationship})")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Programs retornou {resp.status}: {body}")
                return await resp.json()

    async def get_program_details(self, advertiser_id: int) -> dict:
        """Detalhes e comissões de um programa específico."""
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/programmecommissions/{advertiser_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Program Details retornou {resp.status}: {body}")
                return await resp.json()

    # ==================== COMMISSION GROUPS ====================

    async def get_commission_groups(
        self,
        advertiser_id: int,
        include_conditions: bool = False,
    ) -> List[dict]:
        """
        Grupos de comissão de um anunciante.
        Mostra percentuais por categoria de produto.
        """
        url = f"{AWIN_API_BASE}/advertisers/{advertiser_id}/commissiongroups"
        params: dict = {"publisherId": self.publisher_id}
        if include_conditions:
            params["includeConditionValues"] = "true"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin CommGroups retornou {resp.status}: {body}")
                return await resp.json()

    # ==================== PERFORMANCE REPORTS ====================

    async def get_performance_report(
        self,
        start_date: str,
        end_date: str,
        region: str = "BR",
        timezone: str = "America/Sao_Paulo",
        date_type: str = "transaction",
    ) -> List[dict]:
        """
        Relatório de performance agregado por anunciante.
        start_date / end_date: formato YYYY-MM-DD
        """
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/reports/advertiser"
        params = {
            "accessToken": self.api_token,
            "startDate": start_date,
            "endDate": end_date,
            "region": region,
            "timezone": timezone,
            "dateType": date_type,
        }
        logger.info(f"[Awin] Relatório de performance: {start_date} -> {end_date}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Performance retornou {resp.status}: {body}")
                return await resp.json()

    async def get_campaign_report(
        self,
        start_date: str,
        end_date: str,
        region: str = "BR",
        timezone: str = "America/Sao_Paulo",
    ) -> List[dict]:
        """Relatório de dados de campanha por período."""
        url = f"{AWIN_API_BASE}/publishers/{self.publisher_id}/reports/campaign"
        params = {
            "accessToken": self.api_token,
            "startDate": start_date,
            "endDate": end_date,
            "region": region,
            "timezone": timezone,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._headers()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Campaign retornou {resp.status}: {body}")
                return await resp.json()

    # ==================== PRODUCT FEED (GOOGLE FORMAT) ====================

    async def download_product_feed(
        self,
        advertiser_id: int,
        locale: str = "pt_BR",
        max_products: int = 500,
    ) -> List[dict]:
        """
        Faz o download do catálogo de produtos de um anunciante (formato Google JSONL).
        Retorna lista de produtos parseados.
        Limite: 5 req/min conforme docs da Awin.
        max_products: Limite de segurança para evitar memória excessiva.
        """
        url = (
            f"{AWIN_API_BASE}/publishers/{self.publisher_id}"
            f"/awinfeeds/download/{advertiser_id}-retail-{locale}.jsonl"
        )
        logger.info(f"[Awin] Baixando Feed do Anunciante {advertiser_id} (locale: {locale})")

        products = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers()) as resp:
                if resp.status == 404:
                    raise AwinAPIError(
                        f"Feed não encontrado para Anunciante {advertiser_id} locale {locale}. "
                        "Verifique se tem permissão e se o locale está correto."
                    )
                if resp.status != 200:
                    body = await resp.text()
                    raise AwinAPIError(f"Awin Feed retornou {resp.status}: {body}")

                # Stream JSONL: uma linha = um produto JSON
                async for raw_line in resp.content:
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        # Ignorar a última linha de erro caso exista
                        if "error" in obj:
                            logger.warning(f"[Awin] Feed error na última linha: {obj}")
                            break
                        products.append(obj)
                        if len(products) >= max_products:
                            logger.info(f"[Awin] Atingiu limite de {max_products} produtos")
                            break
                    except json.JSONDecodeError:
                        continue

        logger.info(f"[Awin] Feed baixado: {len(products)} produtos do anunciante {advertiser_id}")
        return products
