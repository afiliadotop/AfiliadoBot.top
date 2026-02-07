"""
Shopee Daily Auto-Import Script
Imports top commission products from Shopee API to Supabase
Run daily via cron/Task Scheduler
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Fix encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

from api.utils.shopee_client import create_shopee_client
from api.utils.shopee_extensions import add_rate_limiting
from api.utils.supabase_client import get_supabase_manager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
MIN_COMMISSION = 30.0  # Comissão mínima em %
NOTIFY_HIGH_COMMISSION = 50.0  # Comissão alta para destacar
IMPORT_LIMIT = 50  # Limite de produtos por execução
MIN_QUALITY_SCORE = 60  # Score mínimo de qualidade (0-100) para importar


def calculate_quality_score(product: Dict[str, Any], commission_rate: float) -> int:
    """
    Calcula score de qualidade de um produto (0-100)
    
    Critérios:
    - Rating (0-30 pts)
    - Sales volume (0-30 pts)
    - Commission rate (0-25 pts)
    - Price stability/discount (0-15 pts)
    """
    score = 0
    
    # Rating (0-30 pontos)
    rating = float(product.get('ratingStar', 0))
    if rating > 0:
        score += int((rating / 5.0) * 30)
    
    # Sales volume (0-30 pontos)
    sales = int(product.get('sales', 0))
    if sales >= 1000:
        score += 30
    elif sales >= 500:
        score += 20
    elif sales >= 100:
        score += 10
    elif sales >= 50:
        score += 5
    
    # Commission (0-25 pontos)
    if commission_rate >= 50:
        score += 25
    elif commission_rate >= 40:
        score += 20
    elif commission_rate >= 30:
        score += 15
    
    # Price stability (0-15 pontos)
    price_min = float(product.get('priceMin', 0))
    price_max = float(product.get('priceMax', 0))
    
    if price_max > price_min:
        discount = ((price_max - price_min) / price_max) * 100
        if 10 <= discount <= 50:
            score += 15
        elif discount > 50:
            score += 5
    
    return min(score, 100)


async def import_top_products() -> Dict[str, Any]:
    """Importa produtos com alta comissão"""
    logger.info("="*60)
    logger.info("INICIANDO IMPORTACAO DIARIA SHOPEE")
    logger.info("="*60)
    
    stats = {
        'imported': 0,
        'updated': 0,
        'high_commission': 0,
        'errors': 0,
        'filtered_low_quality': 0,  # NEW: produtos filtrados por baixa qualidade
        'duration': 0
    }
    
    start_time = datetime.now()
    
    try:
        # Conecta ao Shopee com rate limiting
        client = create_shopee_client()
        add_rate_limiting(client)  # Protege contra bloqueio (2000 req/h)
        
        supabase = get_supabase_manager()
        
        async with client:
            logger.info(f"Buscando produtos com comissao >= {MIN_COMMISSION}%...")
            
            # Busca produtos ordenados por comissão
            result = await client.get_products(
                sort_type=5,  # COMMISSION_DESC
                limit=IMPORT_LIMIT,
                page=1
            )
            
            products = result.get('nodes', [])
            logger.info(f"Encontrados {len(products)} produtos")
            
            # Busca ou cria store Shopee
            store_result = supabase.client.table('stores')\
                .select('id')\
                .eq('name', 'shopee')\
                .execute()
            
            if store_result.data:
                store_id = store_result.data[0]['id']
            else:
                # Cria store se não existir
                new_store = supabase.client.table('stores')\
                    .insert({'name': 'shopee', 'display_name': 'Shopee', 'is_active': True})\
                    .execute()
                store_id = new_store.data[0]['id']
            
            logger.info(f"Store ID Shopee: {store_id}")
            
            for product in products:
                try:
                    commission_rate = float(product.get('commissionRate', 0)) * 100
                    
                    # Filtra por comissão mínima
                    if commission_rate < MIN_COMMISSION:
                        continue
                    
                    # NOVO: Calcula score de qualidade (0-100)
                    quality_score = calculate_quality_score(product, commission_rate)
                    
                    # NOVO: Filtra por qualidade mínima
                    if quality_score < MIN_QUALITY_SCORE:
                        stats['filtered_low_quality'] += 1
                        logger.debug(f"Produto filtrado (score={quality_score}): {product.get('productName', '')[:50]}")
                        continue
                    
                    # Mapeia dados para Supabase
                    product_data = {
                        'store': 'shopee',
                        'store_id': store_id,  # FIX: Adiciona store_id obrigatório
                        'name': product.get('productName', '')[:255],
                        'shopee_product_id': product.get('itemId'),
                        'current_price': float(product.get('priceMin', 0)),
                        'original_price': float(product.get('priceMax', 0)),
                        'commission_rate': int(round(commission_rate)),  # FIX: Converte para int (banco espera integer)
                        'commission_amount': float(product.get('commission', 0)),
                        'affiliate_link': product.get('offerLink', ''),
                        'image_url': product.get('imageUrl', ''),
                        'sales_count': int(product.get('sales', 0)),  # FIX: Converte para int
                        'rating': int(float(product.get('ratingStar', 0))) if product.get('ratingStar') else None,  # FIX: Converte para int
                        'shop_name': product.get('shopName', ''),
                        'quality_score': quality_score,  # NOVO: Salva score de qualidade
                        'is_active': True,
                        'is_featured': commission_rate >= NOTIFY_HIGH_COMMISSION,
                        'last_checked': datetime.now().isoformat()
                    }
                    
                    # Calcula desconto
                    if product_data['original_price'] > product_data['current_price']:
                        discount = ((product_data['original_price'] - product_data['current_price']) / product_data['original_price']) * 100
                        product_data['discount_percentage'] = int(round(discount))  # FIX: Converte para int
                    
                    # Verifica se já existe
                    existing = supabase.client.table('products')\
                        .select('id')\
                        .eq('shopee_product_id', product.get('itemId'))\
                        .execute()
                    
                    if existing.data:
                        # Atualiza
                        supabase.client.table('products')\
                            .update(product_data)\
                            .eq('shopee_product_id', product.get('itemId'))\
                            .execute()
                        stats['updated'] += 1
                    else:
                        # Insere novo
                        supabase.client.table('products')\
                            .insert(product_data)\
                            .execute()
                        stats['imported'] += 1
                    
                    # Conta alta comissão
                    if commission_rate >= NOTIFY_HIGH_COMMISSION:
                        stats['high_commission'] += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao processar produto: {e}")
                    stats['errors'] += 1
                    continue
        
        # Calcula duração
        stats['duration'] = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*60)
        logger.info("IMPORTACAO CONCLUIDA")
        logger.info("="*60)
        logger.info(f"Produtos importados: {stats['imported']}")
        logger.info(f"Produtos atualizados: {stats['updated']}")
        logger.info(f"Filtrados baixa qualidade: {stats['filtered_low_quality']}")  # NOVO
        logger.info(f"Alta comissao (>={NOTIFY_HIGH_COMMISSION}%): {stats['high_commission']}")
        logger.info(f"Erros: {stats['errors']}")
        logger.info(f"Duracao: {stats['duration']:.1f}s")
        
        # Registra no log do Supabase (DESABILITADO - causa erro RLS)
        # TODO: Corrigir RLS policy em shopee_sync_log antes de reativar
        # try:
        #     import json
        #     supabase.client.rpc('log_shopee_sync', {
        #         'p_sync_type': 'daily',
        #         'p_products_imported': stats['imported'],
        #         'p_products_updated': stats['updated'],
        #         'p_errors': stats['errors'],
        #         'p_metadata': json.dumps({
        #             'min_comm': MIN_COMMISSION,
        #             'high_count': stats['high_commission'],
        #             'duration': stats['duration']
        #         })
        #     }).execute()
        # except Exception as e:
        #     logger.warning(f"Erro ao registrar log: {e}")
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO NA IMPORTACAO: {e}")
        import traceback
        traceback.print_exc()
        stats['errors'] += 1
        return stats

async def notify_high_commission_products():
    """Notifica produtos com alta comissão no Telegram"""
    try:
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not bot_token or not channel_id:
            logger.warning("BOT_TOKEN ou TELEGRAM_CHANNEL_ID nao configurado")
            return
        
        # Busca produtos com alta comissão importados hoje
        supabase = get_supabase_manager()
        
        response = supabase.client.table('products')\
            .select('*')\
            .eq('store', 'shopee')\
            .eq('is_featured', True)\
            .gte('last_checked', datetime.now().date().isoformat())\
            .order('commission_rate', desc=True)\
            .limit(5)\
            .execute()
        
        products = response.data
        
        if products:
            bot = Bot(token=bot_token)
            
            for product in products:
                # MENSAGEM FOCADA EM PROMOÇÃO (não em comissão)
                message = f"""
🔥 *OFERTA IMPERDÍVEL!* 🔥

{product['name'][:100]}

💰 *R$ {product['current_price']:.2f}*
"""
                
                # Adiciona desconto se houver
                if product.get('discount_percentage', 0) > 0:
                    message += f"🏷️ {product['discount_percentage']:.0f}% OFF\n"
                
                message += f"""
📦 {product['sales_count']:,} vendidos
⭐ {product.get('rating', 'N/A')}/5

🔗 {product['affiliate_link']}
                """
                
                try:
                    await bot.send_message(
                        chat_id=channel_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=False
                    )
                    logger.info(f"Notificação enviada: {product['name'][:30]}...")
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação: {e}")
        
        logger.info(f"{len(products)} notificações enviadas")
        
    except Exception as e:
        logger.error(f"Erro ao notificar produtos: {e}")

async def main():
    """Função principal"""
    logger.info(f"Iniciando import diario - {datetime.now()}")
    
    # Importa produtos
    stats = await import_top_products()
    
    # Notifica se houver produtos com alta comissão
    if stats['high_commission'] > 0:
        logger.info(f"Enviando notificações de {stats['high_commission']} produtos...")
        await notify_high_commission_products()
    
    logger.info("Script concluido!")
    return stats

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        result = asyncio.run(main())
        exit_code = 0 if result['errors'] == 0 else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Script cancelado pelo usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"ERRO FATAL: {e}")
        sys.exit(1)
