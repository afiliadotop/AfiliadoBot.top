import sys
import os
import asyncio
from dotenv import load_dotenv

# Determine project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1002499912192")

print("Bot: @Kenzine_bot")
print("Canal: Afiliado.top CUPONS E DESCONTOS")
print(f"Chat ID: {TELEGRAM_CHANNEL_ID}\n")

async def send_test():
    # Get product
    from api.utils.supabase_client import get_supabase_manager
    supabase = get_supabase_manager()
    
    result = supabase.client.table("products").select("*").limit(1).execute()
    
    if not result.data:
        print("Nenhum produto encontrado")
        return
    
    product = result.data[0]
    
    # Format message with HTML (Emojis in Telegram message are fine, only in print() they fail)
    message = f"""
🛍️ <b>Shopee - OFERTA!</b>

<b>{product['name']}</b>

💰 <b>Preço:</b> R$ {product['current_price']:.2f}
"""
    
    if product.get('discount_percentage'):
        message += f"🔥 <b>Desconto:</b> {product['discount_percentage']}% OFF\n"
    
    if product.get('category'):
        message += f"📦 <b>Categoria:</b> {product['category']}\n"
    
    message += f"\n🔗 <a href='{product['affiliate_link']}'>COMPRAR AGORA</a>"
    
    # Send
    bot = Bot(TELEGRAM_BOT_TOKEN)
    
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        print("Sucesso: Mensagem enviada para o canal!")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(send_test())
