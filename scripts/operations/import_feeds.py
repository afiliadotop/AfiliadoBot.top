
import asyncio
import sys
import os
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ImportScript")

# Add root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

# Check Env
if not os.getenv("SUPABASE_URL"):
    logger.error("❌ SUPABASE_URL not found. check .env")
    sys.exit(1)

from api.handlers.csv_import import import_shopee_daily_csv

URLS = [
    "https://affiliate.shopee.com.br/api/v1/datafeed/download?id=YWJjZGVmZ2hpamtsbW5vcPNcbnfdFhhQkoz1FtnUm6DtED25ejObtofpYLqHBC0h",
    "https://affiliate.shopee.com.br/api/v1/datafeed/download?id=YWJjZGVmZ2hpamtsbW5vcFMjz35zY_7hscVJ_4QLIFiIR3DQ9hsrLcX6rgIVVFkb"
]

async def main():
    logger.info("🚀 Starting Batch Import of Shopee Feeds...")
    
    total_imported = 0
    
    for i, url in enumerate(URLS):
        logger.info(f"📥 Processing Feed #{i+1}...")
        try:
            result = await import_shopee_daily_csv(url)
            if result:
                total_imported += result.get('imported', 0)
                logger.info(f"✅ Feed #{i+1} Result: {result}")
            else:
                logger.warning(f"⚠️ Feed #{i+1} returned no result.")
        except Exception as e:
            logger.error(f"❌ Error processing feed #{i+1}: {e}")
            
    logger.info(f"🎉 Batch Import Complete! Total Products Imported: {total_imported}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
