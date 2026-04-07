"""
Commission Junction (CJ) Affiliate API Client — v3 (Corrigido conforme apicj.md)

APIs utilizadas:
  1. Product Feed API  → https://ads.api.cj.com/query      (GraphQL)
     - shoppingProducts(companyId, keywords, partnerIds, limit, offset)
     - shoppingProductFeeds(companyId, partnerIds)

  2. Program Terms API → https://programs.api.cj.com/query (GraphQL)
     - publisher { contracts(publisherId, limit, filters) { ... } }

Variáveis de ambiente necessárias:
  CJ_API_TOKEN   — Personal Access Token (Bearer)
  CJ_COMPANY_ID  — CID da conta (7533850)
  CJ_PID         — ID do site Afiliado.Top na CJ (101432134, usado em linkCode)
"""

import logging
import os
from typing import Optional, List, Dict, Any

import httpx

logger = logging.getLogger(__name__)

# ==================== ENDPOINTS (conforme apicj.md) ====================
PRODUCT_FEED_URL = "https://ads.api.cj.com/query"
PROGRAM_TERMS_URL = "https://programs.api.cj.com/query"
TIMEOUT = 30.0


class CJAPIError(Exception):
    pass


class CJAffiliateClient:
    """Cliente para as APIs GraphQL da Commission Junction."""

    def __init__(self):
        self.token = os.getenv("CJ_API_TOKEN", "").strip()
        self.company_id = os.getenv("CJ_COMPANY_ID", "").strip()
        self.pid = os.getenv("CJ_PID", "").strip()

        if not self.token:
            raise CJAPIError("CJ_API_TOKEN não configurado no .env")
        if not self.company_id:
            raise CJAPIError("CJ_COMPANY_ID não configurado no .env")

        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    # ==================== CORE ====================

    async def _query(self, url: str, query: str, variables: Optional[Dict] = None) -> Dict:
        """Executa uma query GraphQL e retorna o campo 'data'."""
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                resp = await client.post(url, json=payload, headers=self._headers)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                body = e.response.text[:500]
                raise CJAPIError(f"HTTP {e.response.status_code}: {body}") from e
            except httpx.RequestError as e:
                raise CJAPIError(f"Erro de conexão CJ: {e}") from e

        body = resp.json()
        if "errors" in body:
            msgs = "; ".join(err.get("message", "") for err in body["errors"])
            raise CJAPIError(f"GraphQL errors: {msgs}")

        return body.get("data", {})

    # ==================== PRODUCT FEED API ====================

    async def search_products(
        self,
        keywords: Optional[str] = None,
        advertiser_ids: Optional[List[str]] = None,
        page_size: int = 50,
        page_number: int = 1,
        partner_status: str = "joined",
    ) -> Dict:
        """
        Busca produtos via shoppingProducts (Product Feed API).

        Args:
            keywords:       palavra-chave de busca
            advertiser_ids: partnerIds — CIDs dos anunciantes
            page_size:      max 10000 por request
            page_number:    usado como offset = (page_number-1) * page_size
            partner_status: 'joined' | 'not-joined'
        """
        offset = (page_number - 1) * page_size

        # Constrói os args dinâmicos
        args = [f'companyId: "{self.company_id}"']
        if keywords:
            # keywords é [String!] — array de strings
            kw_list = ', '.join(f'"{k.strip()}"' for k in keywords.split() if k.strip())
            args.append(f"keywords: [{kw_list}]")
        if advertiser_ids:
            ids = ", ".join(f'"{i}"' for i in advertiser_ids)
            args.append(f"partnerIds: [{ids}]")
        args.append(f'partnerStatus: {partner_status.upper().replace("-", "_")}')
        args.append(f"limit: {page_size}")
        args.append(f"offset: {offset}")

        args_str = ", ".join(args)

        # Se temos PID, incluímos o linkCode rastreável; senão só o link direto
        link_code_field = ""
        if self.pid:
            link_code_field = f'linkCode(pid: "{self.pid}") {{ clickUrl }}'

        query = f"""
        {{
          shoppingProducts({args_str}) {{
            totalCount
            count
            limit
            resultList {{
              id
              title
              description
              advertiserId
              advertiserName
              adId
              availability
              brand
              condition
              imageLink
              link
              {link_code_field}
              price {{
                amount
                currency
              }}
              salePrice {{
                amount
                currency
              }}
            }}
          }}
        }}
        """

        data = await self._query(PRODUCT_FEED_URL, query)
        raw = data.get("shoppingProducts", {})
        items = []

        for p in raw.get("resultList", []):
            price = p.get("price") or {}
            sale = p.get("salePrice") or {}
            link_code = p.get("linkCode") or {}

            # Usa linkCode.clickUrl se disponível (link rastreável), senão link direto
            click_url = link_code.get("clickUrl") or p.get("link") or ""

            try:
                sale_price = float(sale.get("amount", 0)) if sale.get("amount") else None
                orig_price = float(price.get("amount", 0)) if price.get("amount") else None
            except (TypeError, ValueError):
                sale_price = None
                orig_price = None

            items.append({
                "link_id": p.get("id", ""),
                "title": p.get("title", ""),
                "description": p.get("description", ""),
                "click_url": click_url,
                "image_url": p.get("imageLink"),
                "advertiser_name": p.get("advertiserName"),
                "advertiser_id": p.get("advertiserId"),
                "ad_id": p.get("adId"),
                "sale_price": sale_price,
                "original_price": orig_price,
                "currency": sale.get("currency") or price.get("currency", "USD"),
                "availability": p.get("availability"),
                "brand": p.get("brand"),
                "condition": p.get("condition"),
                "promotion_type": None,
                "coupon_code": None,
            })

        return {
            "total": raw.get("totalCount", 0),
            "count": raw.get("count", len(items)),
            "page_size": page_size,
            "page": page_number,
            "items": items,
        }

    async def get_product_feeds(
        self,
        advertiser_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Lista feeds disponíveis via shoppingProductFeeds.
        Para publisher, retorna feeds de todos os anunciantes joined.
        """
        args = [f'companyId: "{self.company_id}"', 'limit: 100']
        if advertiser_ids:
            ids = ", ".join(f'"{i}"' for i in advertiser_ids)
            args.append(f"partnerIds: [{ids}]")

        query = f"""
        {{
          shoppingProductFeeds({", ".join(args)}) {{
            totalCount
            count
            resultList {{
              adId
              feedName
              advertiserId
              advertiserName
              productCount
              advertiserCountry
              lastUpdated
              language
              currency
              sourceFeedType
            }}
          }}
        }}
        """

        data = await self._query(PRODUCT_FEED_URL, query)
        raw = data.get("shoppingProductFeeds", {})

        return {
            "total": raw.get("totalCount", 0),
            "count": raw.get("count", 0),
            "items": raw.get("resultList", []),
        }

    # ==================== PROGRAM TERMS API ====================

    async def get_advertisers(
        self,
        relationship_status: str = "joined",
        page: int = 1,
        records_per_page: int = 50,
        advertiser_id: Optional[str] = None,
    ) -> Dict:
        """
        Lista anunciantes/contratos via Program Terms API GraphQL.

        URL: https://programs.api.cj.com/query
        Query: publisher { contracts(publisherId, limit, offset, filters) }

        Note: O 'relationship_status' não é filtro direto aqui —
        filtramos por status do contrato (ACTIVE = joined).
        """
        offset = (page - 1) * records_per_page

        # Monta filtros opcionais
        filter_parts = []
        if advertiser_id:
            filter_parts.append(f'advertiserId: "{advertiser_id}"')

        filters_arg = f"filters: {{ {', '.join(filter_parts)} }}" if filter_parts else ""

        query = f"""
        {{
          publisher {{
            contracts(
              publisherId: "{self.company_id}"
              limit: {records_per_page}
              offset: {offset}
              {filters_arg}
            ) {{
              totalCount
              count
              resultList {{
                advertiserId
                status
                startTime
                endTime
                programTerms {{
                  id
                  name
                  isDefault
                  actionTerms {{
                    id
                    actionTracker {{
                      id
                      name
                      type
                    }}
                    referralPeriod
                    commissions {{
                      rank
                      rate {{
                        type
                        value
                        currency
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        data = await self._query(PROGRAM_TERMS_URL, query)
        contracts = data.get("publisher", {}).get("contracts", {})

        # Como a API de contratos não retorna o nome do anunciante,
        # usamos a API de feeds para fazer um mapeamento (best-effort)
        advertiser_names = {}
        try:
            feed_data = await self.get_product_feeds()
            for f in feed_data.get("items", []):
                adv_id = f.get("advertiserId")
                adv_name = f.get("advertiserName")
                if adv_id and adv_name:
                    advertiser_names[adv_id] = adv_name
        except Exception as e:
            logger.warning(f"[CJ] Erro ao buscar nomes mapeados: {e}")

        items = []
        for c in contracts.get("resultList", []):
            status = c.get("status", "")
            # Filtra por status conforme relação solicitada
            if relationship_status == "joined" and status != "ACTIVE":
                continue
            if relationship_status == "applied" and status not in ("PENDING_OFFER",):
                continue

            adv_id = c.get("advertiserId")
            adv_name = advertiser_names.get(adv_id, f"Advertiser {adv_id}")

            terms = c.get("programTerms") or {}
            # Extrai a primeira comissão base (rank 0) para exibição
            action_terms = terms.get("actionTerms", []) or []
            commission_info = None
            if action_terms:
                commissions = action_terms[0].get("commissions", []) or []
                base = next((cm for cm in commissions if cm.get("rank") == 0), None)
                if base:
                    rate = base.get("rate", {})
                    commission_info = {
                        "commissionType": rate.get("type"),
                        "commissionAmount": rate.get("value"),
                        "currency": rate.get("currency"),
                    }

            items.append({
                "id": adv_id,
                "name": adv_name,
                "logoUrl": None,
                "primaryUrl": None,
                "joined": status == "ACTIVE",
                "category": None,
                "country": None,
                "programTerms": [commission_info] if commission_info else [],
                "contractStatus": status,
                "programTermsId": terms.get("id"),
                "programTermsName": terms.get("name"),
            })

        return {
            "total": contracts.get("totalCount", 0),
            "count": len(items),
            "page": page,
            "items": items,
        }

    async def check_credentials(self) -> Dict:
        """
        Valida as credenciais fazendo uma query leve de Product Feeds.
        Retorna info do schema disponível.
        """
        query = f"""
        {{
          shoppingProductFeeds(companyId: "{self.company_id}", limit: 1) {{
            totalCount
            count
            resultList {{
              adId
              feedName
              advertiserName
            }}
          }}
        }}
        """
        data = await self._query(PRODUCT_FEED_URL, query)
        feeds = data.get("shoppingProductFeeds", {})
        return {
            "status": "ok",
            "company_id": self.company_id,
            "pid": self.pid or "NÃO CONFIGURADO",
            "feeds_count": feeds.get("totalCount", 0),
            "sample_feeds": feeds.get("resultList", [])[:3],
        }
