import os
import sys
import asyncio
from dotenv import load_dotenv

# Determine project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

# Explicitly load .env from the root
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from telegram import Bot
from afiliadohub.api.utils.supabase_client import get_supabase_manager

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1002499912192")

if not TELEGRAM_BOT_TOKEN:
    print("-" * 50)
    print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN not found!")
    print("Please ensure you have a .env file in the project root with:")
    print("TELEGRAM_BOT_TOKEN=your_token_here")
    print("-" * 50)
    sys.exit(1)

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

def format_aida_message(product: dict) -> str:
    """Formata mensagem usando AIDA (Attention, Interest, Desire, Action)"""
    
    store = product.get('store', 'shopee')
    emoji = STORE_EMOJIS.get(store, '🏪')
    store_name = store.replace('_', ' ').title()
    
    price = product.get('current_price', 0)
    original_price = product.get('original_price')
    discount = product.get('discount_percentage', 0)
    
    # ATTENTION: Headline impactante
    if discount and discount > 0:
        headline = f"🔥 SUPER DESCONTO {int(discount)}% OFF! 🔥"
    else:
        headline = f"✨ OFERTA ESPECIAL {emoji}"
    
    # INTEREST: Nome do produto
    product_name = f"👜 {product['name'][:80]}..." if len(product['name']) > 80 else f"👜 {product['name']}"
    
    # DESIRE: Preço e economia
    price_section = f"\n💰 Apenas R$ {price:.2f}"
    
    if original_price and discount:
        savings = original_price - price
        price_section += f"\n📉 De R$ {original_price:.2f}"
        price_section += f"\n✅ Economize R$ {savings:.2f}!"
    
    # DESIRE: Benefícios e social proof
    benefits = """
✨ Por que você vai amar:
✔️ Seleção premium AfiliadoTop
✔️ Loja 100% Verificada e Segura
✔️ Melhor preço garantido hoje
🚚 Entrega rápida em todo o Brasil"""
    
    # ACTION: Call to action
    cta = f"\n\n🛒 COMPRAR AGORA COM DESCONTO!"
    link_text = f"\n🔗 {product['affiliate_link']}"
    
    # Montar mensagem completa
    message = f"{headline}\n\n{product_name}\n{price_section}\n{benefits}\n{cta}\n{link_text}"
    
    # Adicionar cupom se existir
    if product.get('coupon_code'):
        message += f"\n\n🎫 CUPOM: {product['coupon_code']}"
    
    return message

async def send_daily_promotions():
    """Envia promoções diárias para o canal com AIDA e rotação de produtos"""
    
    supabase = get_supabase_manager()
    bot = Bot(TELEGRAM_BOT_TOKEN)
    
    # Busca produtos usando a nova lógica de rotação
    print("Buscando produtos com rotacao inteligente...")
    
    products = await supabase.get_products_for_telegram(limit=5, min_discount=0)
    
    if not products:
        print("Nenhum produto encontrado")
        print("Verifique se ha produtos com imagens no banco.")
        return
    
    print(f"Encontrados {len(products)} produtos para enviar\n")
    
    for idx, product in enumerate(products, 1):
        # Formata mensagem com AIDA
        caption = format_aida_message(product)
        
        image_url = product.get('image_url')
        
        try:
            if image_url:
                # Envia foto com legenda
                await bot.send_photo(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    photo=image_url,
                    caption=caption,
                    parse_mode=None  # Sem parse porque temos emojis e links diretos
                )
                print(f"[{idx}/{len(products)}] Enviado com FOTO: {product['name'][:50]}...")
            else:
                # Fallback: envia só texto se não tiver imagem
                await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=caption,
                    parse_mode=None
                )
                print(f"[{idx}/{len(products)}] Enviado SEM foto: {product['name'][:50]}...")
            
            # Update stats
            await supabase.increment_product_stats(
                product['id'],
                'telegram_send_count'
            )
            
            # Delay entre mensagens (evita spam)
            if idx < len(products):
                await asyncio.sleep(3)  # 3 segundos entre cada envio
                
        except Exception as e:
            print(f"Erro ao enviar [{idx}]: {e}")
    
    print(f"\nEnvio concluido! {len(products)} produtos enviados ao canal.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(send_daily_promotions())
