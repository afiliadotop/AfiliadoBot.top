"""
Price History Repository
ITIL Activity: Obtain/Build (Price Tracking Data Access)

Maps to skill_save_price_history from affiliate-bot-tools skill.
Stores per-scrape price snapshots for each product, enabling
historical average calculations used by fake-discount detection.
"""

from typing import List, Optional, Dict, Any
from .base_repository import BaseRepository
from ..models.domain import PriceHistory


class PriceHistoryRepository(BaseRepository[PriceHistory]):
    """Repository for price history data access"""

    @property
    def table_name(self) -> str:
        return "price_history"

    def save_price(
        self,
        product_id: int,
        price: float,
        cep: Optional[str] = None,
        source: str = "scraper",
    ) -> Optional[Dict[str, Any]]:
        """
        Persist a new price snapshot for a product.

        Args:
            product_id: FK to products.id
            price: Scraped price in BRL
            cep: Optional CEP used during freight calculation
            source: Origin label (scraper | manual | api)

        Returns:
            Inserted row dict or None on failure
        """
        payload: Dict[str, Any] = {
            "product_id": product_id,
            "price": price,
            "source": source,
        }
        if cep:
            payload["cep"] = cep

        return self.create(payload)

    def get_price_history(
        self, product_id: int, limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the N most recent price records for a product.

        Args:
            product_id: FK to products.id
            limit: Max records to return (default 30)

        Returns:
            List of price history dicts ordered newest-first
        """
        result = (
            self.client.table(self.table_name)
            .select("*")
            .eq("product_id", product_id)
            .order("scraped_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data if result.data else []

    def get_historical_average(self, product_id: int) -> float:
        """
        Calculate the average price from all recorded history for a product.

        Used by AffiliateService.detect_fake_discount().

        Args:
            product_id: FK to products.id

        Returns:
            Average price as float, or 0.0 if no history exists
        """
        result = (
            self.client.table(self.table_name)
            .select("price")
            .eq("product_id", product_id)
            .execute()
        )

        rows = result.data or []
        if not rows:
            return 0.0

        total = sum(float(row["price"]) for row in rows)
        return round(total / len(rows), 2)

    def get_min_price(self, product_id: int) -> Optional[float]:
        """
        Return the historically lowest recorded price for a product.

        Args:
            product_id: FK to products.id

        Returns:
            Minimum price float or None if no history
        """
        result = (
            self.client.table(self.table_name)
            .select("price")
            .eq("product_id", product_id)
            .order("price", desc=False)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        return float(rows[0]["price"]) if rows else None
