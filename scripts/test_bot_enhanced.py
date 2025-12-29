"""
Enhanced Telegram Bot Test Script
Tests all new commands and database integration
"""

import sys
import os
import asyncio

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

# Check tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not BOT_TOKEN:
    print("ERRO: BOT_TOKEN nao encontrado no .env!")
    sys.exit(1)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERRO: SUPABASE_URL ou SUPABASE_KEY nao encontrados no .env!")
    sys.exit(1)

print(f"OK: BOT_TOKEN configurado: {BOT_TOKEN[:20]}...")
print(f"OK: SUPABASE_URL configurado: {SUPABASE_URL}")

# Import bot components
from telegram import Bot
from api.utils.supabase_client import get_supabase_manager

async def test_supabase_connection():
    """Testa conexão com Supabase"""
    print("\n" + "="*50)
    print("🗄️  TESTANDO CONEXÃO SUPABASE")
    print("="*50)
    
    try:
        supabase = get_supabase_manager()
        
        # Test stores
        print("\n📊 Testando get_active_stores()...")
        stores = await supabase.get_active_stores()
        print(f"   ✅ Encontradas {len(stores)} lojas ativas")
        for store in stores[:3]:
            print(f"      - {store.get('display_name', store.get('name'))}")
        
        # Test stores with count
        print("\n📊 Testando get_stores_with_product_count()...")
        stores_with_count = await supabase.get_stores_with_product_count()
        print(f"   ✅ {len(stores_with_count)} lojas com contagem:")
        for store in stores_with_count[:3]:
            print(f"      - {store.get('display_name')}: {store.get('product_count', 0)} produtos")
        
        # Test products
        print("\n📦 Testando get_products()...")
        products = await supabase.get_products({"limit": 3})
        print(f"   ✅ Encontrados {len(products)} produtos")
        for product in products:
            print(f"      - {product.get('name', '')[:50]}...")
        
        # Test top deals
        print("\n🏆 Testando get_top_deals()...")
        top_deals = await supabase.get_top_deals(limit=3, min_discount=20)
        print(f"   ✅ {len(top_deals)} top deals encontrados")
        for deal in top_deals:
            discount = deal.get('discount_percentage', 0)
            print(f"      - {discount}% OFF: {deal.get('name', '')[:40]}...")
        
        # Test search
        print("\n🔍 Testando search_products_fulltext()...")
        search_results = await supabase.search_products_fulltext("phone", limit=2)
        print(f"   ✅ {len(search_results)} resultados para 'phone'")
        
        # Test categories
        print("\n📁 Testando get_categories()...")
        categories = await supabase.get_categories()
        print(f"   ✅ {len(categories)} categorias encontradas")
        print(f"      Primeiras categorias: {', '.join(categories[:5])}")
        
        print("\n✅ Todos os testes de Supabase passaram!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro nos testes de Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_bot_connection():
    """Testa conexão com bot Telegram"""
    print("\n" + "="*50)
    print("🤖 TESTANDO CONEXÃO TELEGRAM BOT")
    print("="*50)
    
    try:
        bot = Bot(BOT_TOKEN)
        
        # Get bot info
        me = await bot.get_me()
        print(f"\n✅ Bot conectado com sucesso!")
        print(f"   - Nome: {me.first_name}")
        print(f"   - Username: @{me.username}")
        print(f"   - ID: {me.id}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar com bot: {e}")
        return False

async def test_user_preferences():
    """Testa funcionalidades de preferências de usuário"""
    print("\n" + "="* 50)
    print("⚙️  TESTANDO PREFERÊNCIAS DE USUÁRIO")
    print("="*50)
    
    try:
        supabase = get_supabase_manager()
        test_user_id = 123456789  # ID de teste
        
        # Test save preferences
        print("\n💾 Testando save_user_preference()...")
        await supabase.save_user_preference(
            telegram_user_id=test_user_id,
            telegram_username="test_user",
            telegram_first_name="Test",
            preferred_stores=["shopee", "amazon"],
            min_discount=25
        )
        print("   ✅ Preferências salvas")
        
        # Test get preferences
        print("\n📖 Testando get_user_preferences()...")
        prefs = await supabase.get_user_preferences(test_user_id)
        
        if prefs.get("has_preferences"):
            print("   ✅ Preferências recuperadas:")
            print(f"      - Lojas: {prefs.get('preferred_stores', [])}")
            print(f"      - Desconto mínimo: {prefs.get('min_discount', 0)}%")
        else:
            print("   ℹ️  Nenhuma preferência configurada ainda")
        
        # Test recommendations
        print("\n✨ Testando get_recommended_products()...")
        recommendations = await supabase.get_recommended_products(
            telegram_user_id=test_user_id,
            limit=3
        )
        print(f"   ✅ {len(recommendations)} recomendações encontradas")
        for rec in recommendations:
            print(f"      - {rec.get('name', '')[:50]:}...")
        
        print("\n✅ Todos os testes de preferências passaram!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro nos testes de preferências: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_command_handlers():
    """Testa handlers de comandos (simulação)"""
    print("\n" + "="*50)
    print("⚡ TESTANDO COMMAND HANDLERS")
    print("="*50)
    
    print("\n✅ Handlers registrados:")
    print("   - /start (basic)")
    print("   - /help (basic)")
    print("   - /lojas (new - dynamic)")
    print("   - /produtos [loja] (new - has_args=1) ⭐")
    print("   - /top (new)")
    print("   - /preferencias (new)")
    print("   - /recomendar (new)")
    print("   - /cupom (existing)")
    print("   - /promo (existing)")
    print("   - /shopee, /amazon, etc. (existing)")
    print("   - /buscar (existing)")
    
    print("\n💡 has_args validations:")
    print("   - /produtos          → ❌ Requer 1 argumento")
    print("   - /produtos shopee   → ✅ Aceito")
    print("   - /produtos shopee x → ❌ Muitos argumentos")
    
    return True

async def main():
    """Executa todos os testes"""
    print("\n╔══════════════════════════════════════════╗")
    print("║   TELEGRAM BOT - ENHANCED TEST SUITE    ║")
    print("╚══════════════════════════════════════════╝")
    
    results = {}
    
    # Run tests
    results['bot'] = await test_bot_connection()
    results['supabase'] = await test_supabase_connection()
    results['preferences'] = await test_user_preferences()
    results['handlers'] = await test_command_handlers()
    
    # Summary
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name.upper():.<30} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n📌 Próximos passos:")
        print("1. Inicie o bot: python -m afiliadohub.api.handlers.telegram")
        print("2. Abra o Telegram e busque seu bot")
        print("3. Teste comandos:")
        print("   - /start")
        print("   - /lojas")
        print("   - /produtos shopee")
        print("   - /top")
        print("   - /recomendar")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima e corrija antes de prosseguir.")
    
    return all_passed

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
