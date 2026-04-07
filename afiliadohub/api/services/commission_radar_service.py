"""
Commission Radar Service - The Conversion Machine
Logic for hunting top affiliate deals and vouchers.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from ..utils.cj_client import CJAffiliateClient, CJAPIError
from ..utils.awin_client import AwinAffiliateClient, AwinAPIError
from ..handlers.telegram import TelegramBot
from ..utils.telegram_settings_manager import telegram_settings

logger = logging.getLogger(__name__)

class CommissionRadarService:
    def __init__(self):
        self._cj_client: Optional[CJAffiliateClient] = None
        self._awin_client: Optional[AwinAffiliateClient] = None
        self._tg_bot = TelegramBot()

    def _get_cj_client(self) -> CJAffiliateClient:
        if not self._cj_client:
            self._cj_client = CJAffiliateClient()
        return self._cj_client

    def _get_awin_client(self) -> AwinAffiliateClient:
        if not self._awin_client:
            self._awin_client = AwinAffiliateClient()
        return self._awin_client

    async def run_cj_radar(
        self, 
        min_discount: float = 40.0, 
        max_broadcasts: int = 3,
        auto_dispatch: bool = True
    ) -> Dict[str, Any]:
        """
        Scans Commission Junction for high-discount products and dispatches to Telegram.
        """
        try:
            client = self._get_cj_client()
            chat_id = telegram_settings.get_group_chat_id()
            
            # Fetch products (page_size 100 for enough sample)
            res = await client.search_products(page_size=100)
            items = res.get("items", [])
            
            top_deals = []
            for item in items:
                sp = item.get("sale_price")
                op = item.get("original_price")
                if sp and op and op > 0:
                    pct = ((op - sp) / op) * 100
                    if pct >= min_discount:
                        item["_calculated_discount"] = pct
                        top_deals.append(item)
            
            if not top_deals:
                return {"status": "success", "message": f"No CJ deals with +{min_discount}% found.", "dispatched": 0}

            # Sort by highest discount
            top_deals.sort(key=lambda x: x["_calculated_discount"], reverse=True)
            to_dispatch = top_deals[:max_broadcasts]
            
            dispatched_count = 0
            if auto_dispatch and chat_id:
                for deal in to_dispatch:
                    product_dict = self._map_cj_to_product(deal)
                    if await self._tg_bot.send_product_to_channel(chat_id, product_dict):
                        dispatched_count += 1
            
            return {
                "status": "success",
                "deals_found": len(top_deals),
                "dispatched": dispatched_count,
                "items": to_dispatch if not auto_dispatch else []
            }
            
        except CJAPIError as e:
            logger.error(f"[Radar CJ] Client Error: {e}")
            raise
        except Exception as e:
            logger.error(f"[Radar CJ] Unexpected Error: {e}")
            return {"status": "error", "message": str(e)}

    async def run_awin_radar(
        self, 
        max_broadcasts: int = 3,
        auto_dispatch: bool = True
    ) -> Dict[str, Any]:
        """
        Scans Awin for active promotions and vouchers.
        """
        try:
            client = self._get_awin_client()
            chat_id = telegram_settings.get_group_chat_id()
            
            # Get joined programs first to filter relevant offers
            programs = await client.get_programs(relationship="joined")
            if not programs:
                return {"status": "success", "message": "No joined Awin programs found.", "dispatched": 0}
                
            joined_ids = [p["id"] for p in programs]
            
            # Fetch active promotions
            offers_resp = await client.get_offers(
                advertiser_ids=joined_ids[:20], # limit to first 20 programs for performance
                promotion_types=["deal", "voucher"],
                page_size=50
            )
            
            offers = offers_resp.get("data", []) if isinstance(offers_resp, dict) else (offers_resp if isinstance(offers_resp, list) else [])
            
            if not offers:
                return {"status": "success", "message": "No active Awin offers found.", "dispatched": 0}

            # Map and filter
            top_offers = []
            for o in offers:
                # Basic check for quality
                if o.get("urlTracking") or o.get("deeplink"):
                    top_offers.append(o)

            to_dispatch = top_offers[:max_broadcasts]
            dispatched_count = 0
            
            if auto_dispatch and chat_id:
                for offer in to_dispatch:
                    product_dict = self._map_awin_to_product(offer)
                    if await self._tg_bot.send_product_to_channel(chat_id, product_dict):
                        dispatched_count += 1
                        
            return {
                "status": "success",
                "offers_found": len(top_offers),
                "dispatched": dispatched_count,
                "items": to_dispatch if not auto_dispatch else []
            }
            
        except AwinAPIError as e:
            logger.error(f"[Radar Awin] Client Error: {e}")
            raise
        except Exception as e:
            logger.error(f"[Radar Awin] Unexpected Error: {e}")
            return {"status": "error", "message": str(e)}

    async def fetch_vouchers(self) -> List[Dict[str, Any]]:
        """
        Aggregates vouchers from all networks for the /cupom command.
        """
        vouchers = []
        
        # 1. Awin Vouchers
        try:
            awin = self._get_awin_client()
            res = await awin.get_offers(promotion_types=["voucher"], page_size=20)
            items = res.get("data", []) if isinstance(res, dict) else (res if isinstance(res, list) else [])
            for i in items:
                if i.get("code"):
                    vouchers.append(self._map_awin_to_product(i, force_type="voucher"))
        except Exception as e:
            logger.warning(f"[Radar] Failed to fetch Awin vouchers: {e}")
            
        # 2. CJ (CJ doesn't have a direct 'voucher' search in Product Feed, but we hunt for 'coupon' keywords)
        # Note: True Promotion API is different, but for now we search metadata
        try:
            cj = self._get_cj_client()
            res = await cj.search_products(keywords="coupon promo", page_size=20)
            for i in res.get("items", []):
                # If we detect a discount or keyword
                vouchers.append(self._map_cj_to_product(i))
        except Exception as e:
            logger.warning(f"[Radar] Failed to fetch CJ potential vouchers: {e}")
            
        return vouchers

    def _map_cj_to_product(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Maps CJ API item to internal product structure."""
        discount_pct = item.get("_calculated_discount")
        return {
            "id": 0,
            "name": item.get("title", ""),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "affiliate_link": item.get("click_url", ""),
            "short_link": item.get("click_url", ""),
            "category": "radar",
            "original_price": item.get("original_price"),
            "discount_price": item.get("sale_price"),
            "coupon_code": None, # Product Feed rarely has explicit code
            "store": f"CJ/{item.get('advertiser_name') or 'Partner'}",
            "image_url": item.get("image_url"),
            "discount_percentage": discount_pct,
            "is_active": True,
            "tags": ["radar", "cj", "automated"],
        }

    def _map_awin_to_product(self, offer: Dict[str, Any], force_type: Optional[str] = None) -> Dict[str, Any]:
        """Maps Awin offering to internal product structure."""
        adv_name = offer.get("advertiser", {}).get("name") or "Awin Partner"
        return {
            "id": 0,
            "name": offer.get("title", ""),
            "title": offer.get("title", ""),
            "description": offer.get("description", ""),
            "affiliate_link": offer.get("urlTracking") or offer.get("deeplink"),
            "short_link": offer.get("urlTracking") or offer.get("deeplink"),
            "category": force_type or "radar",
            "original_price": None,
            "discount_price": None,
            "coupon_code": offer.get("code"),
            "store": f"Awin/{adv_name}",
            "image_url": None, # Awin Offers API doesn't always provide product image
            "is_active": True,
            "tags": ["radar", "awin", "automated"],
        }
