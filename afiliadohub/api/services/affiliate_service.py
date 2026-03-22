"""
Affiliate Service
ITIL Activity: Deliver & Support (Affiliate Business Logic)

Implements the 3 core affiliate-bot-tools skill capabilities:
  1. skill_generate_affiliate_link  → generate_affiliate_link()
  2. skill_detect_fake_discount     → detect_fake_discount()
  3. skill_scrape_product           → scrape_product_data()
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, urljoin

import httpx

from ..models.domain import AffiliateLinkResult, DiscountAnalysis

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Affiliate tag configuration per store
# Key: store_name (case-insensitive lookup)
# Value: dict with "param" (query param name) and "value" (tag value)
# ---------------------------------------------------------------------------
AFFILIATE_TAGS: Dict[str, Dict[str, str]] = {
    "amazon": {
        "param": "tag",
        "value": os.getenv("AMAZON_AFFILIATE_TAG", "afiliadotop-20"),
    },
    "mercado livre": {
        "param": "afiliado",
        "value": os.getenv("ML_AFFILIATE_ID", "afiliadotop"),
    },
    "mercadolivre": {
        "param": "afiliado",
        "value": os.getenv("ML_AFFILIATE_ID", "afiliadotop"),
    },
    "shopee": {
        "param": "af_siteid",
        "value": os.getenv("SHOPEE_AFFILIATE_ID", "afiliadotop"),
    },
    "aliexpress": {
        "param": "aff_platform",
        "value": os.getenv("ALIEXPRESS_AFFILIATE_ID", "afiliadotop"),
    },
}

# Threshold multiplier for fake-discount detection
# If declared_from_price > historical_average * FAKE_DISCOUNT_THRESHOLD → fake
FAKE_DISCOUNT_THRESHOLD = float(os.getenv("FAKE_DISCOUNT_THRESHOLD", "1.1"))

# Internal redirect base URL
INTERNAL_REDIRECT_BASE = os.getenv("INTERNAL_REDIRECT_BASE", "https://afiliado.top/go")


class AffiliateService:
    """
    Service encapsulating affiliate-bot-tools skill logic.

    Stateless — can be instantiated without any repository dependency.
    When price history lookup is needed (detect_fake_discount), the caller
    must supply the historical_average_price value.
    """

    # ------------------------------------------------------------------
    # 1. Affiliate Link Generation
    # ------------------------------------------------------------------
    def generate_affiliate_link(
        self,
        base_url: str,
        store_name: str,
        offer_id: str,
    ) -> AffiliateLinkResult:
        """
        Inject the affiliate tag into a clean product URL.

        Args:
            base_url: Clean URL of the product on the store
            store_name: Store name (case-insensitive). E.g. "Amazon", "Shopee"
            offer_id: Unique identifier for this offer (used in /go/ redirect)

        Returns:
            AffiliateLinkResult with monetized URL and internal click URL
        """
        store_key = store_name.lower().strip()
        config = AFFILIATE_TAGS.get(store_key, {"param": "ref", "value": "afiliadotop"})

        # Parse and rebuild URL injecting the affiliate param
        parsed = urlparse(base_url)
        existing_params = parse_qs(parsed.query)
        existing_params[config["param"]] = [config["value"]]

        # Flatten multi-value params back to single values
        flat_params = {k: v[0] for k, v in existing_params.items()}
        new_query = urlencode(flat_params)

        monetized_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

        internal_url = f"{INTERNAL_REDIRECT_BASE}/{offer_id}"

        logger.info(
            f"[AffiliateService] Link generated: store={store_name} offer_id={offer_id}"
        )

        return AffiliateLinkResult(
            monetized_product_url=monetized_url,
            internal_click_url=internal_url,
            store_name=store_name,
            offer_id=offer_id,
        )

    # ------------------------------------------------------------------
    # 2. Fake Discount Detection
    # ------------------------------------------------------------------
    def detect_fake_discount(
        self,
        current_price: float,
        declared_from_price: float,
        historical_average_price: float,
    ) -> DiscountAnalysis:
        """
        Determine if the store's declared original price is inflated.

        Logic (from skill_detect_fake_discount):
          - If declared_from_price > historical_average * threshold → it's inflated.
          - Adjusted price is capped at the historical average in that case.
          - Real discount % is calculated against adjusted price.

        Args:
            current_price: The sale price right now
            declared_from_price: The crossed-out "was" price shown by the store
            historical_average_price: Average price from price_history table
                                       (pass 0.0 to skip correction)

        Returns:
            DiscountAnalysis with is_fake_discount, real_discount_percentage, etc.
        """
        is_fake = (
            historical_average_price > 0
            and declared_from_price > historical_average_price * FAKE_DISCOUNT_THRESHOLD
        )

        adjusted_from_price = (
            historical_average_price if is_fake else declared_from_price
        )

        real_discount = 0.0
        if adjusted_from_price > 0 and current_price < adjusted_from_price:
            real_discount = (
                (adjusted_from_price - current_price) / adjusted_from_price
            ) * 100

        return DiscountAnalysis(
            is_fake_discount=is_fake,
            declared_from_price=declared_from_price,
            adjusted_from_price=adjusted_from_price,
            current_price=current_price,
            real_discount_percentage=round(real_discount, 2),
            historical_average_price=historical_average_price,
        )

    # ------------------------------------------------------------------
    # 3. Product Scraping (lightweight async)
    # ------------------------------------------------------------------
    async def scrape_product_data(
        self,
        url: str,
        cep: Optional[str] = None,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Attempt a lightweight HTTP scrape of a product URL.

        For stores with official API integrations (Shopee, Mercado Livre),
        this should be replaced by calls to their respective services.
        This method acts as a universal fallback using plain HTTP.

        Args:
            url: Full product URL
            cep: Optional CEP for freight calculation (not implemented here)
            timeout: Request timeout in seconds

        Returns:
            Dict with keys: url, status, price (None if not parseable),
            in_stock (None), shipping_cost (None), raw_html_length
        """
        result: Dict[str, Any] = {
            "url": url,
            "status": "error",
            "price": None,
            "in_stock": None,
            "shipping_cost": None,
            "cep": cep,
            "raw_html_length": 0,
        }

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "pt-BR,pt;q=0.9",
            }
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                result["status"] = "fetched"
                result["http_status"] = response.status_code
                result["raw_html_length"] = len(response.text)

                logger.info(
                    f"[AffiliateService] Scraped URL={url} "
                    f"HTTP={response.status_code} len={len(response.text)}"
                )

        except httpx.TimeoutException:
            result["status"] = "timeout"
            logger.warning(f"[AffiliateService] Scrape timeout for URL={url}")
        except Exception as exc:
            result["status"] = "error"
            result["error"] = str(exc)
            logger.error(f"[AffiliateService] Scrape error URL={url}: {exc}")

        return result
