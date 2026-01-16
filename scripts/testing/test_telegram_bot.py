import sys
import os
import asyncio
from dotenv import load_dotenv

# Determine project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Check token via Settings Manager (to test fallback/DB)
from afiliadohub.api.utils.telegram_settings_manager import telegram_settings

print("Testando TelegramSettingsManager...")
print(f"Settings raw: {telegram_settings.get_settings()}")
TELEGRAM_BOT_TOKEN = telegram_settings.get_bot_token()
GROUP_CHAT_ID = telegram_settings.get_group_chat_id()

print(f"Token obtido: {'✅ Sim' if TELEGRAM_BOT_TOKEN else '❌ Não'}")
print(f"Chat ID obtido: {'✅ Sim' if GROUP_CHAT_ID else '❌ Não'}")

if TELEGRAM_BOT_TOKEN:
    print(f"Token (masked): {TELEGRAM_BOT_TOKEN[:10]}...")

if not TELEGRAM_BOT_TOKEN:
    print("ERRO: TELEGRAM_BOT_TOKEN nao encontrado! (Verifique DB ou .env)")
    sys.exit(1)

# Test bot
from telegram import Bot

async def test_bot():
    bot = Bot(TELEGRAM_BOT_TOKEN)
    
    # Get bot info
    me = await bot.get_me()
    print(f"\nBot Information:")
    print(f"   - Nome: {me.first_name}")
    print(f"   - Username: @{me.username}")
    print(f"   - ID: {me.id}")
    
    # Get a sample product
    from api.utils.supabase_client import get_supabase_manager
    supabase = get_supabase_manager()
    
    result = supabase.client.table("products").select("*").limit(1).execute()
    
    if result.data:
        product = result.data[0]
        print(f"\nProduto de Teste:")
        print(f"   - {product['name'][:50]}...")
        print(f"   - R$ {product['current_price']:.2f}")
        
        # Format message
        message = f"""
🛍️ *TESTE - Shopee*

{product['name']}

💰 R$ {product['current_price']:.2f}

🔗 {product['affiliate_link']}
        """
        
        print("\nBot esta funcionando corretamente!")
        print("\nProximos passos:")
        print("1. Adicione o bot como admin do seu canal")
        print(f"2. Use o script send_daily_promo.py para enviar ofertas")
        
    else:
        print("Aviso: Nenhum produto encontrado no banco")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test_bot())
