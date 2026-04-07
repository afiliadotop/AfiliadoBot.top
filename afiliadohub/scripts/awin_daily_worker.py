import os
import sys
import asyncio
import logging
from datetime import datetime

from dotenv import load_dotenv
from afiliadohub.api.utils.awin_client import AwinAffiliateClient, AwinAPIError
from afiliadohub.api.utils.supabase_client import get_supabase_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AwinETLWorker")

MAX_PRODUCTS_PER_STORE = 300 
MAX_STORES_PER_RUN = 30
DELAY_BETWEEN_FEEDS = 12

async def run_awin_etl():
    load_dotenv()
    
    supabase = get_supabase_manager()
    try:
        awin = AwinAffiliateClient()
    except Exception as e:
        logger.error(f"Failed to start AWIN Client. Missing ENV vars? {e}")
        return

    logger.info("📡 Iniciando Sincronização de DataFeeds AWIN (Modo Cirúrgico)")

    try:
        programs = await awin.get_programs(relationship="joined")
    except Exception as e:
        logger.error(f"Erro crítico listando programas da Awin: {e}")
        return

    if not programs:
        logger.warning("Nenhum programa afiliado 'Joined' encontrado.")
        return

    joined_programs = programs[:MAX_STORES_PER_RUN]
    logger.info(f"📋 Extraindo dos seus primeiros {len(joined_programs)} programas habilitados.")

    total_inserted = 0

    for idx, program in enumerate(joined_programs):
        advertiser_id = program.get("id")
        store_name = program.get("name", f"Awin_Store_{advertiser_id}")
        
        logger.info(f"[{idx+1}/{len(joined_programs)}] Baixando feed da loja: {store_name} ({advertiser_id})")
        
        feed_data = None
        for locale_attempt in ["en_GB", "en_US", "de_DE"]:
            try:
                feed_data = await awin.download_product_feed(
                    advertiser_id=advertiser_id,
                    locale=locale_attempt,
                    max_products=MAX_PRODUCTS_PER_STORE
                )
                if feed_data:
                    logger.info(f"  ✅ Feed encontrado com locale: {locale_attempt}")
                    break
            except AwinAPIError as e:
                if "406" in str(e) or "not found" in str(e).lower():
                    logger.info(f"  🔄 Locale '{locale_attempt}' não disponível para {store_name}, tentando próximo...")
                    continue
                raise
        
        if not feed_data:
            logger.warning(f"  ➜ Feed indisponível para {store_name}. Pulando.")
            continue
            
        db_batch = []
        for item in feed_data:
            name = item.get("title") or item.get("product_name") or item.get("name")
            link = item.get("link") or item.get("aw_deep_link") or item.get("aw_track_link")
            price_str = item.get("price") or item.get("search_price") or "0"
            
            try:
                price = float(price_str.replace(" BRL", "").replace(" USD", "").replace(" GBP", "").replace(" EUR", ""))
            except:
                price = 0.0
                
            if not name or not link:
                continue 
                
            img_url = item.get("image_link") or item.get("merchant_image_url") or item.get("image_url")
            category = item.get("product_type") or item.get("merchant_category") or "Awin Catalog"
            discount_pct = 0.0
            
            sale_price = item.get("sale_price")
            if sale_price:
                try:
                    sale = float(sale_price.replace(" BRL", "").replace(" USD", "").replace(" GBP", "").replace(" EUR", ""))
                    if sale > 0 and sale < price:
                        discount_pct = round(((price - sale) / price) * 100)
                        price = sale
                except:
                    pass
            
            db_batch.append({
                "store": store_name,
                "name": name,
                "affiliate_link": link,
                "current_price": price,
                "image_url": img_url,
                "category": category,
                "discount_percentage": discount_pct if discount_pct > 0 else 0,
                "provider": "awin",
                "is_active": True
            })
        
        if db_batch:
            results = await supabase.bulk_insert_products(db_batch, batch_size=500)
            added = results.get("inserted", 0)
            total_inserted += added
            logger.info(f"  ✅ {added} produtos indexados de {store_name}.")
        
        if idx < len(joined_programs) - 1:
            await asyncio.sleep(DELAY_BETWEEN_FEEDS)

    logger.info(f"🎉 ETL AWIN FINALIZADO. Total de produtos validados no BD: {total_inserted}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_awin_etl())
