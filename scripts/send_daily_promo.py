import sys
import os
import asyncio
import random

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

from telegram import Bot
from api.utils.supabase_client import get_supabase_manager

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "-1002499912192"  # Afiliado.top CUPONS E DESCONTOS

# Emojis por loja
STORE_EMOJIS = {
    'shopee': '🛍️',
    'aliexpress': '📦',
    'amazon': '📚',
    'temu': '🎯',
    'shein': '👗',
    'magalu': '🏬',
    'mercado_livre': '🚀'
}

async def send_daily_promotions():
    """Envia promoções diárias para o canal"""
    
    supabase = get_supabase_manager()
    bot = Bot(BOT_TOKEN)
    
    # Busca 5 produtos mais recentes (com ou sem desconto)
    print("Buscando produtos no banco...")
    
    result = supabase.client.table("products")\
        .select("*")\
        .eq("is_active", True)\
        .order("created_at", desc=True)\
        .limit(5)\
        .execute()
    
    if not result.data:
        print("Nenhum produto encontrado")
        print("Verifique se a importação foi concluída com sucesso.")
        return
    
    products = result.data
    print(f"Encontrados {len(products)} produtos para enviar\n")
    
    for idx, product in enumerate(products, 1):
        # Format message
        store = product.get('store', 'shopee')
        emoji = STORE_EMOJIS.get(store, '🏪')
        store_name = store.replace('_', ' ').title()
        
        price = product.get('current_price', 0)
        original_price = product.get('original_price')
        discount = product.get('discount_percentage', 0)
        
        message = f"{emoji} <b>{store_name}</b>\n\n"
        message += f"🛍️ <b>{product['name']}</b>\n\n"
        
        if original_price and discount:
            message += f"💰 <s>R$ {original_price:.2f}</s> → <b>R$ {price:.2f}</b>\n"
            message += f"🔥 <b>{discount}% DE DESCONTO!</b>\n\n"
        else:
            message += f"💰 <b>R$ {price:.2f}</b>\n\n"
        
        if product.get('category'):
            message += f"📦 {product['category']}\n"
        
        message += f"\n🔗 <a href='{product['affiliate_link']}'>COMPRAR AGORA</a>"
        
        if product.get('coupon_code'):
            message += f"\n\n🎫 Cupom: <code>{product['coupon_code']}</code>"
        
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            print(f"[{idx}/{len(products)}] Enviado: {product['name'][:50]}...")
            
            # Update stats
            await supabase.increment_product_stats(
                product['id'],
                'telegram_send_count'
            )
            
            # Delay entre mensagens (evita spam)
            if idx < len(products):
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"Erro ao enviar [{idx}]: {e}")
    
    print(f"\nEnvio concluído! {len(products)} produtos enviados ao canal.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(send_daily_promotions())
