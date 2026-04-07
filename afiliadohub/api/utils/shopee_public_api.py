import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ShopeePublicAPI:
    """
    Utility to interact with Shopee's public mobile/web API (v2/v4)
    Used for features not available in the official Affiliate GraphQL API,
    such as product videos and customer reviews.
    """
    
    BASE_URL = "https://shopee.com.br"
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._own_session = False

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
            self._own_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self.session:
            await self.session.close()

    async def get_product_extended_details(self, item_id: int, shop_id: int) -> Dict[str, Any]:
        """
        Fetches official product video and meta details.
        """
        try:
            url = f"{self.BASE_URL}/api/v4/item/get"
            params = {"itemid": item_id, "shopid": shop_id}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": f"{self.BASE_URL}/product/{shop_id}/{item_id}",
            }

            if not self.session:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        logger.info(f"[Shopee Public API] Details Response: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            item_data = data.get("data", {})
                            if not item_data:
                                logger.warning(f"[Shopee Public API] No item data found: {data}")
                            return self._parse_details(item_data)
            else:
                async with self.session.get(url, params=params, headers=headers) as response:
                    logger.info(f"[Shopee Public API] Details Response: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        item_data = data.get("data", {})
                        if not item_data:
                            logger.warning(f"[Shopee Public API] No item data found: {data}")
                        return self._parse_details(item_data)
            
            return {}
        except Exception as e:
            logger.error(f"[Shopee Public API] Error fetching details: {e}")
            return {}

    def _parse_details(self, item: Dict) -> Dict:
        details = {
            "video_url": None,
            "cmt_count": item.get("cmt_count", 0),
            "rating_star": item.get("item_rating", {}).get("rating_star", 0),
        }
        
        # Extract video URL
        video_list = item.get("video_info_list", [])
        if video_list and len(video_list) > 0:
            details["video_url"] = video_list[0].get("video_url")
            
        return details

    async def get_product_reviews(self, item_id: int, shop_id: int, limit: int = 3) -> List[Dict]:
        """
        Fetches the best customer reviews (5 stars with text/media).
        """
        try:
            url = f"{self.BASE_URL}/api/v2/item/get_ratings"
            params = {
                "itemid": item_id,
                "shopid": shop_id,
                "offset": 0,
                "limit": limit * 3, # Fetch more to filter better
                "filter": 1,        # 1 = With Photo/Video
                "type": 0           # All types
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }

            if not self.session:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        logger.info(f"[Shopee Public API] Reviews Response: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            ratings = data.get("data", {}).get("ratings", [])
                            logger.info(f"[Shopee Public API] Found {len(ratings)} raw ratings")
                            return self._filter_best_reviews(ratings, limit)
            else:
                async with self.session.get(url, params=params, headers=headers) as response:
                    logger.info(f"[Shopee Public API] Reviews Response: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        ratings = data.get("data", {}).get("ratings", [])
                        logger.info(f"[Shopee Public API] Found {len(ratings)} raw ratings")
                        return self._filter_best_reviews(ratings, limit)
            
            return []
        except Exception as e:
            logger.error(f"[Shopee Public API] Error fetching reviews: {e}")
            return []

    def _filter_best_reviews(self, ratings: List[Dict], limit: int) -> List[Dict]:
        if not ratings:
            return []
            
        best = []
        for r in ratings:
            # Criteria: 5 stars, has comment
            # Relaxed criteria temporarily to see if we get anything
            comment = r.get("comment", "")
            if r.get("rating_star") == 5 and comment:
                # Clean comment (remove excessive newlines)
                clean_comment = " ".join(comment.split())
                if len(clean_comment) > 5: # Minimal length
                    best.append({
                        "author": r.get("author_username", "Cliente Shopee"),
                        "comment": clean_comment,
                        "rating": r.get("rating_star")
                    })
            if len(best) >= limit:
                break
        
        logger.info(f"[Shopee Public API] Extracted {len(best)} filtered reviews")
        return best
