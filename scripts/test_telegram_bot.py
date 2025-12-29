import sys
import os
import asyncio

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

# Check token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN não encontrado no .env!")
    print("Adicione: BOT_TOKEN=7436127848:AAFVXUbf-JEiJ7DmiusG2JhpSDe74bt7d3s")
    sys.exit(1)

print(f"✅ BOT_TOKEN configurado: {BOT_TOKEN[:20]}...")

# Test bot
from telegram import Bot

async def test_bot():
    bot = Bot(BOT_TOKEN)
    
    # Get bot info
    me = await bot.get_me()
    print(f"\n🤖 Bot Information:")
    print(f"   - Nome: {me.first_name}")
    print(f"   - Username: @{me.username}")
    print(f"   - ID: {me.id}")
    
    # Get a sample product
    from api.utils.supabase_client import get_supabase_manager
    supabase = get_supabase_manager()
    
    result = supabase.client.table("products").select("*").limit(1).execute()
    
    if result.data:
        product = result.data[0]
        print(f"\n📦 Produto de Teste:")
        print(f"   - {product['name'][:50]}...")
        print(f"   - R$ {product['current_price']:.2f}")
        
        # Format message
        message = f"""
🛍️ *TESTE - Shopee*

{product['name']}

💰 R$ {product['current_price']:.2f}

🔗 {product['affiliate_link']}
        """
        
        print(f"\n📝 Mensagem formatada:")
        print(message)
        
        print("\n✅ Bot está funcionando!")
        print("\n📌 Próximo passo:")
        print("1. Crie um canal no Telegram")
        print("2. Adicione o bot como admin")
        print("3. Envie uma mensagem no canal")
        print("4. Acesse: https://api.telegram.org/bot{}/getUpdates".format(BOT_TOKEN))
        print("5. Copie o Chat ID (ex: -1001234567890)")
        
    else:
        print("⚠️ Nenhum produto encontrado no banco")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test_bot())
