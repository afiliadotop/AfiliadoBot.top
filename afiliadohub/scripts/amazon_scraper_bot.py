#!/usr/bin/env python3
"""
Amazon Scraper Bot
Raspa as ofertas do dia da Amazon Brasil de forma assíncrona, 
aplica a tag de afiliado universal e salva no Supabase.
"""

import sys
import os
import asyncio
import random
import logging
from datetime import datetime
from typing import Dict, Any, List

# Adiciona o afiliadohub no path para os imports relativos
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega o token/URL do Supabase do .env
load_dotenv()

from api.utils.supabase_client import get_supabase_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

AMAZON_AFFILIATE_TAG = os.getenv("AMAZON_AFFILIATE_TAG", "afiliadotop-20")

# Lista de User-Agents rotativos para mitigar banimento da Amazon
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

class AmazonScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.com.br"
        # Ofertas do Dia (Página básica de Promoções)
        self.deals_url = f"{self.base_url}/deals"

    def _get_headers(self) -> Dict[str, str]:
        """Gera headers aleatórios para dificultar o bloqueio"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
        }

    def _format_affiliate_link(self, raw_url: str) -> str:
        """Limpa a URL da Amazon e injeta a TAG de afiliado puro"""
        # Remove a base se ela não existir e limpa queries de rastreio inúteis
        if not raw_url.startswith("http"):
            raw_url = f"{self.base_url}{raw_url}"
        
        # Manter apenas a base limpa do produto: /dp/B0XYZ...
        import re
        dp_match = re.search(r'(/dp/[A-Z0-9]+)', raw_url)
        if dp_match:
            clean_url = f"{self.base_url}{dp_match.group(1)}"
        else:
            clean_url = raw_url.split('?')[0]
            
        return f"{clean_url}?tag={AMAZON_AFFILIATE_TAG}"

    async def scrape_todays_deals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Extrai as primeiras X ofertas da página principal da Amazon Brasil"""
        logger.info("Iniciando varredura da Amazon Brasil...")
        
        products_captured = []
        
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            try:
                # Opcional: em scrapers da Amazon brutos, as páginas de deals são carregadas via JS.
                # Como alternativa fallback, faremos fallback para buscas direto em categorias comuns.
                fallback_urls = [
                    f"{self.base_url}/s?k=notebook",
                    f"{self.base_url}/s?k=smartphone",
                    f"{self.base_url}/s?k=smart+tv",
                    f"{self.base_url}/s?k=game"
                ]
                
                for search_url in fallback_urls:
                    if len(products_captured) >= limit:
                        break
                        
                    logger.info(f"Raspando URL: {search_url}")
                    async with session.get(search_url, timeout=15) as response:
                        if response.status != 200:
                            logger.warning(f"Amazon bloqueou ou retornou erro {response.status}")
                            continue
                            
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Amazon card clássico
                        items = soup.select('div[data-component-type="s-search-result"]')
                        
                        for item in items:
                            if len(products_captured) >= limit:
                                break
                                
                            try:
                                # Titulo
                                title_elem = item.select_one('h2 a span')
                                title = title_elem.text.strip() if title_elem else ""
                                
                                # Link do produto
                                link_elem = item.select_one('h2 a')
                                link = link_elem.get('href', '') if link_elem else ""
                                
                                # Preço atual
                                price_whole = item.select_one('.a-price-whole')
                                price_fraction = item.select_one('.a-price-fraction')
                                
                                if not price_whole:
                                    continue # Sem preço não entra
                                    
                                current_price_str = price_whole.text.replace('.', '').replace(',', '')
                                current_price = float(current_price_str)
                                
                                # Preço antigo (se tiver)
                                old_price_elem = item.select_one('.a-text-price .a-offscreen')
                                original_price = current_price
                                discount = 0
                                
                                if old_price_elem:
                                    old_str = old_price_elem.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                                    try:
                                        original_price = float(old_str)
                                        if original_price > current_price:
                                            discount = int(round(((original_price - current_price) / original_price) * 100))
                                    except:
                                        pass
                                
                                # Imagem
                                img_elem = item.select_one('.s-image')
                                img_url = img_elem.get('src', '') if img_elem else ""
                                
                                # Affiliate Link Builder
                                affiliate_link = self._format_affiliate_link(link)
                                
                                if title and affiliate_link:
                                    products_captured.append({
                                        'store': 'amazon',
                                        # Amazon não fornece ID de loja. Usaremos store_id = 999 fallback
                                        'store_id': 999, 
                                        'name': title[:255],
                                        'shopee_product_id': None, # Null para amazon
                                        'current_price': current_price,
                                        'original_price': original_price,
                                        'discount_percentage': discount,
                                        'commission_rate': 0, # Genérico (Amazon tem taxa fixa variavel)
                                        'affiliate_link': affiliate_link,
                                        'image_url': img_url,
                                        'sales_count': 0, # Scraper não pega vendas
                                        'rating': 5, # Mock, scraping deep de estrelas demora
                                        'shop_name': 'Amazon Brasil',
                                        'quality_score': 80 if discount > 0 else 50,
                                        'is_active': True,
                                        'is_featured': discount >= 30,
                                        'last_checked': datetime.now().isoformat()
                                    })
                                    
                            except Exception as parse_e:
                                logger.debug(f"Falha ao processar item do scraper: {parse_e}")
                                continue
                                
                    # Delay anti-bot
                    await asyncio.sleep(random.uniform(2.0, 4.0))

            except Exception as e:
                logger.error(f"Erro fatal na conexão scraper: {e}")
                
        return products_captured

async def main():
    logger.info("="*60)
    logger.info("INICIANDO AMAZON SCRAPER BOT")
    logger.info("="*60)
    
    start_time = datetime.now()
    stats = {
        'imported': 0,
        'errors': 0,
        'duration': 0
    }
    
    try:
        scraper = AmazonScraper()
        products = await scraper.scrape_todays_deals(limit=50) # Rasparemos as top 50
        
        if products:
            logger.info(f"Salvando {len(products)} no Supabase...")
            supabase = get_supabase_manager()
            
            # Precisamos criar uma "Store Dummy" se o store_id 999 falhar (FK na tabela).
            # Vamos primeiro tentar buscar/criar a store da Amazon
            store_result = supabase.client.table('stores').select('id').eq('name', 'amazon').execute()
            amazon_store_id = None
            if store_result.data:
                amazon_store_id = store_result.data[0]['id']
            else:
                new_store = supabase.client.table('stores').insert({'name': 'amazon', 'display_name': 'Amazon', 'is_active': True}).execute()
                amazon_store_id = new_store.data[0]['id']
                
            # Corrige os IDs dos produtos capturados
            for p in products:
                p['store_id'] = amazon_store_id
                
            # Salvar no DB
            result = await supabase.bulk_insert_products(products)
            
            stats['imported'] = result['inserted']
            stats['errors'] = result['errors']
            
            # Tentar enviar telegram para destaques (> 30% discount)
            for p in products:
                if p.get('is_featured') and stats['imported'] > 0:
                    logger.info(f"🔥 Oferta Forte Amazon Catalogada: {p['name'][:30]}... ({p['discount_percentage']}% OFF)")
        else:
            logger.warning("Nenhum produto foi filtrado pela varredura da Amazon.")
            
    except Exception as e:
        logger.error(f"Erro no Scraper Master: {e}")
        stats['errors'] += 1
        
    stats['duration'] = (datetime.now() - start_time).total_seconds()
    
    logger.info("="*60)
    logger.info(f"AMAZON FINALIZADA ({stats['duration']:.1f}s) | Novos/Atualizados: {stats['imported']} | Erros: {stats['errors']}")
    return stats

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
