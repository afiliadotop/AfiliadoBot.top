#!/usr/bin/env python3
"""
Scraper automático da Shopee para atualizar produtos diariamente
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopeeScraper:
    def __init__(self, api_key: str = None):
        self.base_url = "https://shopee.com.br"
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_products(self, keyword: str, limit: int = 50) -> List[Dict]:
        """Busca produtos por palavra-chave"""
        try:
            # URL da API de busca da Shopee
            url = f"{self.base_url}/api/v4/search/search_items"
            
            params = {
                "by": "relevancy",
                "keyword": keyword,
                "limit": limit,
                "newest": 0,
                "order": "desc",
                "page_type": "search",
                "scenario": "PAGE_GLOBAL_SEARCH",
                "version": 2
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"{self.base_url}/search?keyword={keyword}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data)
                else:
                    logger.error(f"Erro na busca: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {e}")
            return []
    
    def _parse_search_results(self, data: Dict) -> List[Dict]:
        """Parse dos resultados da busca"""
        products = []
        
        try:
            items = data.get("items", [])
            
            for item in items:
                try:
                    item_basic = item.get("item_basic", {})
                    
                    # Informações básicas
                    product = {
                        "name": item_basic.get("name", "")[:200],
                        "product_id": item_basic.get("itemid"),
                        "shop_id": item_basic.get("shopid"),
                        "price": item_basic.get("price", 0) / 100000,  # Converter para reais
                        "original_price": item_basic.get("price_before_discount", 0) / 100000,
                        "stock": item_basic.get("stock", 0),
                        "sold": item_basic.get("sold", 0),
                        "historical_sold": item_basic.get("historical_sold", 0),
                        "rating": item_basic.get("item_rating", {}).get("rating_star", 0),
                        "rating_count": item_basic.get("item_rating", {}).get("rating_count", [0, 0, 0, 0, 0]),
                        "brand": item_basic.get("brand", ""),
                        "categories": item_basic.get("categories", []),
                        "images": [f"https://cf.shopee.com.br/file/{img}" for img in item_basic.get("images", [])],
                        "location": item_basic.get("shop_location", ""),
                        "shop_rating": item_basic.get("shop_rating", 0),
                        "shop_response_rate": item_basic.get("shopee_verified", False),
                        "has_lowest_price_guarantee": item_basic.get("has_lowest_price_guarantee", False),
                        "show_discount": item_basic.get("show_discount", ""),
                        "raw_data": json.dumps(item_basic)
                    }
                    
                    # Calcula desconto
                    if product["original_price"] and product["original_price"] > product["price"]:
                        discount = ((product["original_price"] - product["price"]) / product["original_price"]) * 100
                        product["discount_percentage"] = int(discount)
                    
                    # Gera link de afiliado
                    product["affiliate_link"] = self._generate_affiliate_link(
                        product["product_id"],
                        product["shop_id"]
                    )
                    
                    products.append(product)
                    
                except Exception as e:
                    logger.warning(f"Erro ao parse produto: {e}")
                    continue
            
            logger.info(f"Parseados {len(products)} produtos")
            return products
            
        except Exception as e:
            logger.error(f"Erro no parse geral: {e}")
            return []
    
    def _generate_affiliate_link(self, product_id: int, shop_id: int) -> str:
        """Gera link de afiliado da Shopee"""
        # Formato: https://shope.ee/{código}
        # Para Shopee Partners API, você precisaria gerar o link apropriado
        return f"https://shope.ee/{product_id}"
    
    async def get_product_details(self, product_id: int, shop_id: int) -> Optional[Dict]:
        """Busca detalhes específicos de um produto"""
        try:
            url = f"{self.base_url}/api/v4/item/get"
            
            params = {
                "itemid": product_id,
                "shopid": shop_id
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"{self.base_url}/product/{shop_id}/{product_id}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_product_details(data)
                else:
                    logger.error(f"Erro nos detalhes: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes: {e}")
            return None
    
    def _parse_product_details(self, data: Dict) -> Optional[Dict]:
        """Parse dos detalhes do produto"""
        try:
            item = data.get("data", {})
            
            details = {
                "description": item.get("description", ""),
                "attributes": item.get("attributes", []),
                "tier_variations": item.get("tier_variations", []),
                "models": item.get("models", []),
                "wholesale_tier_list": item.get("wholesale_tier_list", []),
                "video_info_list": item.get("video_info_list", []),
                "liked_count": item.get("liked_count", 0),
                "cmt_count": item.get("cmt_count", 0),
                "view_count": item.get("view_count", 0),
                "condition": item.get("condition", ""),
                "size_chart": item.get("size_chart", ""),
                "item_rating": item.get("item_rating", {}),
                "is_preferred_plus_seller": item.get("is_preferred_plus_seller", False),
                "is_official_shop": item.get("is_official_shop", False),
                "is_mart": item.get("is_mart", False),
                "is_senior_mall": item.get("is_senior_mall", False)
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Erro no parse de detalhes: {e}")
            return None
    
    async def update_daily_products(self, categories: List[str] = None):
        """Atualiza produtos diariamente de categorias específicas"""
        if categories is None:
            categories = ["smartphone", "notebook", "fone", "relogio", "tenis"]
        
        all_products = []
        
        for category in categories:
            logger.info(f"Buscando produtos da categoria: {category}")
            products = await self.search_products(category, limit=100)
            all_products.extend(products)
            
            # Aguarda para não sobrecarregar
            await asyncio.sleep(2)
        
        # Remove duplicados
        unique_products = []
        seen_ids = set()
        
        for product in all_products:
            pid = product.get("product_id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                unique_products.append(product)
        
        logger.info(f"Total de produtos únicos encontrados: {len(unique_products)}")
        
        # Salva em CSV
        self._save_to_csv(unique_products)
        
        return unique_products
    
    def _save_to_csv(self, products: List[Dict]):
        """Salva produtos em CSV"""
        if not products:
            logger.warning("Nenhum produto para salvar")
            return
        
        df = pd.DataFrame(products)
        
        # Seleciona colunas importantes
        export_cols = ["name", "price", "original_price", "discount_percentage", 
                      "rating", "stock", "sold", "affiliate_link", "brand"]
        
        # Filtra colunas existentes
        available_cols = [col for col in export_cols if col in df.columns]
        df_export = df[available_cols]
        
        # Adiciona timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shopee_products_{timestamp}.csv"
        
        # Salva
        df_export.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Produtos salvos em: {filename}")
        
        return filename

async def main():
    """Função principal"""
    logger.info("🚀 Iniciando scraper da Shopee...")
    
    # Configurações
    KEYWORDS = [
        "smartphone", "notebook", "fone bluetooth", "smartwatch",
        "airfryer", "geladeira", "tv", "monitor", "mouse", "teclado"
    ]
    
    async with ShopeeScraper() as scraper:
        products = await scraper.update_daily_products(KEYWORDS)
        
        logger.info(f"✅ Scraping concluído! {len(products)} produtos encontrados.")
        
        # Aqui você pode integrar com o banco de dados
        # await save_to_database(products)

if __name__ == "__main__":
    asyncio.run(main())
