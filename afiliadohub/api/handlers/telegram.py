import os
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters,
    CallbackQueryHandler,
    ContextTypes
)

from ..utils.supabase_client import get_supabase_manager
from ..utils.link_processor import normalize_link, detect_store
from ..utils.telegram_settings_manager import telegram_settings

logger = logging.getLogger(__name__)

# Emojis para diferentes lojas
STORE_EMOJIS = {
    'shopee': '🛍️',
    'aliexpress': '📦',
    'amazon': '📚',
    'temu': '🎯',
    'shein': '👗',
    'magalu': '🏬',
    'mercado_livre': '🚀'
}

class TelegramBot:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.application = None
        self.supabase = get_supabase_manager()
        
    async def initialize(self):
        """Inicializa o bot Telegram"""
        try:
            # 1. Tenta pegar do banco (prioridade)
            if not self.token:
                self.token = telegram_settings.get_bot_token()
            
            # 2. Fallback para variáveis de ambiente (retrocompatibilidade)
            if not self.token:
                self.token = os.getenv("TELEGRAM_BOT_TOKEN")
                if self.token:
                    logger.info("[TELEGRAM] Usando token do .env (Fallback)")

            if not self.token:
                logger.warning("[TELEGRAM] Bot token não configurado no banco de dados nem nas variáveis de ambiente.")
                return None

            self.application = Application.builder().token(self.token).build()
            
            # Registra handlers
            self._register_handlers()
            
            # Inicia polling (para desenvolvimento)
            # await self.application.initialize()
            # await self.application.start()
            # await self.application.updater.start_polling()
            
            logger.info("[OK] Bot Telegram inicializado")
            return self.application
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao inicializar bot Telegram: {e}")
            # Não lança erro para não derrubar a API se o telegram estiver desconfigurado
            return None
    
    def _register_handlers(self):
        """Registra todos os handlers de comandos"""
        
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("cupom", self.cupom_command))
        self.application.add_handler(CommandHandler("promo", self.promo_command))
        
        # Novos comandos dinâmicos
        self.application.add_handler(CommandHandler("lojas", self.lojas_command))
        self.application.add_handler(CommandHandler("produtos", self.produtos_command, has_args=1))  # Requer 1 argumento
        self.application.add_handler(CommandHandler("top", self.top_command))
        self.application.add_handler(CommandHandler("preferencias", self.preferencias_command))
        self.application.add_handler(CommandHandler("recomendar", self.recomendar_command))
        
        # Comandos Shopee API
        self.application.add_handler(CommandHandler("shopee_sync", self.shopee_sync_command))
        self.application.add_handler(CommandHandler("shopee_stats", self.shopee_stats_command))
        self.application.add_handler(CommandHandler("top_comissao", self.top_commission_command))
        # TODO: Implementar shopee_link_command e shopee_ofertas_command
        # self.application.add_handler(CommandHandler("shopee_link", self.shopee_link_command, has_args=1))
        # self.application.add_handler(CommandHandler("shopee_ofertas", self.shopee_ofertas_command))
        # self.application.add_handler(CommandHandler("shopee_buscar", self.shopee_buscar_command))
        
        # Comandos por loja (legado - mantido para compatibilidade)
        self.application.add_handler(CommandHandler("shopee", lambda u, c: self.store_command(u, c, "shopee")))
        self.application.add_handler(CommandHandler("aliexpress", lambda u, c: self.store_command(u, c, "aliexpress")))
        self.application.add_handler(CommandHandler("amazon", lambda u, c: self.store_command(u, c, "amazon")))
        self.application.add_handler(CommandHandler("temu", lambda u, c: self.store_command(u, c, "temu")))
        self.application.add_handler(CommandHandler("shein", lambda u, c: self.store_command(u, c, "shein")))
        self.application.add_handler(CommandHandler("magalu", lambda u, c: self.store_command(u, c, "magalu")))
        self.application.add_handler(CommandHandler("mercado", lambda u, c: self.store_command(u, c, "mercado_livre")))
        
        # Comandos de busca
        self.application.add_handler(CommandHandler("buscar", self.search_command))
        self.application.add_handler(CommandHandler("hoje", self.today_command))
        self.application.add_handler(CommandHandler("aleatorio", self.random_command))
        self.application.add_handler(CommandHandler("categorias", self.categories_command))
        
        # Comandos admin
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Handler para mensagens
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Handler para callback queries (botões)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    # ==================== HANDLERS DE COMANDOS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /start"""
        user = update.effective_user
        welcome_text = f"""
👋 Olá {user.first_name}! Bem-vindo ao *AfiliadoHub*!

🎯 *Comandos disponíveis:*

🛒 *Por Loja:*
/shopee - Melhores cupons da Shopee
/aliexpress - Ofertas do AliExpress  
/amazon - Promoções Amazon
/temu - Novidades do Temu
/shein - Descontos Shein
/magalu - Ofertas Magazine Luiza
/mercado - Mercado Livre

🔍 *Busca:*
/cupom - Cupom aleatório
/promo - Promoção do momento
/buscar [produto] - Buscar produto
/hoje - Novidades de hoje
/aleatorio - Produto aleatório
/categorias - Ver categorias

📊 *Info:*
/stats - Estatísticas do bot
/help - Ajuda

💡 *Dica:* Use /buscar seguido do que procura!
Ex: /buscar fone bluetooth
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🛍️ Shopee", callback_data="store_shopee"),
                InlineKeyboardButton("📦 AliExpress", callback_data="store_aliexpress"),
            ],
            [
                InlineKeyboardButton("📚 Amazon", callback_data="store_amazon"),
                InlineKeyboardButton("🎯 Temu", callback_data="store_temu"),
            ],
            [
                InlineKeyboardButton("🎁 Cupom Aleatório", callback_data="random_coupon"),
                InlineKeyboardButton("🔥 Promoção Hoje", callback_data="today_promo"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /help"""
        help_text = """
🆘 *Ajuda do AfiliadoHub*

*Como usar:*
1. Use /cupom para receber um cupom aleatório
2. Use /shopee, /aliexpress, etc para ofertas específicas
3. Use /buscar [produto] para buscar algo específico
4. Use /hoje para ver as novidades do dia

*Exemplos:*
/cupom - Recebe um cupom aleatório
/buscar smartphone - Busca smartphones
/shopee - Cupons da Shopee
/hoje - Novidades de hoje

*Admin:* Para adicionar produtos, use o painel web ou envie CSV.
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cupom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /cupom - Retorna um cupom aleatório"""
        try:
            product = await self.supabase.get_random_product(min_discount=20)
            
            if product:
                message = self._format_product_message(product)
                await update.message.reply_text(
                    message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
                
                # Atualiza estatísticas
                await self.supabase.increment_product_stats(
                    product["id"],
                    "telegram_send_count"
                )
            else:
                await update.message.reply_text(
                    "😕 Nenhum cupom disponível no momento. Tente novamente mais tarde!"
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /cupom: {e}")
            await update.message.reply_text(
                "❌ Ocorreu um erro ao buscar cupons. Tente novamente!"
            )
    
    async def store_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, store: str):
        """Handler para comandos de loja específica"""
        try:
            # Busca 3 produtos da loja
            filters = {
                "store": store,
                "min_discount": 10,
                "limit": 3
            }
            
            products = await self.supabase.get_products(filters)
            
            if products:
                for product in products:
                    message = self._format_product_message(product)
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"],
                        "telegram_send_count"
                    )
                    
                    # Pequena pausa entre mensagens
                    import asyncio
                    await asyncio.sleep(0.5)
            else:
                emoji = STORE_EMOJIS.get(store, '🏪')
                await update.message.reply_text(
                    f"{emoji} Nenhuma oferta encontrada para {store.replace('_', ' ').title()} no momento."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando de loja {store}: {e}")
            await update.message.reply_text(
                f"❌ Erro ao buscar ofertas da loja."
            )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /buscar [termo]"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "🔍 Use: /buscar [produto]\nEx: /buscar fone bluetooth"
                )
                return
            
            search_term = " ".join(context.args)
            
            # Busca no banco (simples - poderia usar full-text search)
            query = f"""
            SELECT * FROM products 
            WHERE is_active = TRUE 
            AND (name ILIKE '%{search_term}%' OR description ILIKE '%{search_term}%' OR category ILIKE '%{search_term}%')
            ORDER BY discount_percentage DESC NULLS LAST
            LIMIT 5
            """
            
            # Executa query raw (simplificado)
            # Na prática, usar prepared statements
            response = self.supabase.client.table("products")\
                .select("*")\
                .ilike("name", f"%{search_term}%")\
                .eq("is_active", True)\
                .limit(5)\
                .execute()
            
            products = response.data
            
            if products:
                await update.message.reply_text(
                    f"🔍 *Resultados para '{search_term}':*",
                    parse_mode='Markdown'
                )
                
                for product in products:
                    message = self._format_product_message(product)
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    # Pequena pausa
                    import asyncio
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(
                    f"😕 Nenhum produto encontrado para '{search_term}'"
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /buscar: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar produtos. Tente novamente!"
            )
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /hoje - Produtos adicionados hoje"""
        try:
            today = datetime.now().date().isoformat()
            
            response = self.supabase.client.table("products")\
                .select("*")\
                .gte("created_at", f"{today}T00:00:00")\
                .lte("created_at", f"{today}T23:59:59")\
                .eq("is_active", True)\
                .limit(5)\
                .execute()
            
            products = response.data
            
            if products:
                await update.message.reply_text(
                    f"🆕 *Novidades de Hoje ({today}):*",
                    parse_mode='Markdown'
                )
                
                for product in products:
                    message = self._format_product_message(product)
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    import asyncio
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(
                    "📭 Nenhuma novidade hoje ainda. Volte mais tarde!"
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /hoje: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar novidades. Tente novamente!"
            )
    
    async def random_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /aleatorio - Produto totalmente aleatório"""
        try:
            product = await self.supabase.get_random_product()
            
            if product:
                message = self._format_product_message(product)
                await update.message.reply_text(
                    message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
            else:
                await update.message.reply_text(
                    "🎲 Nenhum produto encontrado."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /aleatorio: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar produto aleatório."
            )
    
    async def categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /categorias - Lista categorias disponíveis"""
        try:
            # Busca categorias distintas
            response = self.supabase.client.table("products")\
                .select("category")\
                .not_.is_("category", "null")\
                .eq("is_active", True)\
                .execute()
            
            categories = list(set([p["category"] for p in response.data if p["category"]]))
            
            if categories:
                categories.sort()
                categories_text = "\n".join([f"• {cat}" for cat in categories])
                
                message = f"""
📁 *Categorias Disponíveis:*

{categories_text}

💡 Use: /buscar [categoria]
Ex: /buscar eletrônicos
                """
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "📂 Nenhuma categoria cadastrada ainda."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /categorias: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar categorias."
            )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /stats - Estatísticas do bot"""
        try:
            stats = await self.supabase.get_system_summary()
            
            message = f"""
📊 *Estatísticas do AfiliadoHub*

📈 *Total de Produtos:* {stats.get('total_products', 0):,}
🎯 *Com Desconto:* {stats.get('products_with_discount', 0):,}

🏪 *Por Loja:*
"""
            
            stores = stats.get('stores', {})
            for store, count in stores.items():
                emoji = STORE_EMOJIS.get(store, '🏪')
                message += f"{emoji} {store.title()}: {count:,}\n"
            
            message += f"\n🔄 *Atualizado:* {stats.get('updated_at', 'N/A')}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro no comando /stats: {e}")
            await update.message.reply_text(
                "📊 Estatísticas indisponíveis no momento."
            )
    
    async def promo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /promo - Promoção em destaque"""
        try:
            # Busca produto com maior desconto
            response = self.supabase.client.table("products")\
                .select("*")\
                .not_.is_("discount_percentage", "null")\
                .eq("is_active", True)\
                .order("discount_percentage", desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                product = response.data[0]
                message = self._format_product_message(product, highlight=True)
                
                await update.message.reply_text(
                    message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
            else:
                await update.message.reply_text(
                    "🔥 Nenhuma promoção em destaque no momento."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /promo: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar promoção."
            )
    
    # ==================== NOVOS COMANDOS DINÂMICOS ====================
    
    async def lojas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /lojas - Lista todas as lojas disponíveis dinamicamente"""
        try:
            stores = await self.supabase.get_stores_with_product_count()
            
            if stores:
                message = "🏪 *Lojas Disponíveis:*\n\n"
                
                for store in stores:
                    emoji = STORE_EMOJIS.get(store["name"], "🏪")
                    display_name = store.get("display_name", store["name"].title())
                    product_count = store.get("product_count", 0)
                    
                    message += f"{emoji} *{display_name}*\n"
                    message += f"   📦 {product_count:,} produtos disponíveis\n"
                    message += f"   💡 Use: `/produtos {store['name']}`\n\n"
                
                message += "\n💬 *Dica:* Use `/produtos [loja]` para ver produtos específicos!"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "😕 Nenhuma loja disponível no momento."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /lojas: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar lojas. Tente novamente!"
            )
    
    async def produtos_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /produtos [loja] - Mostra produtos de uma loja (requer argumento)"""
        try:
            # has_args=1 garante que context.args terá exatamente 1 elemento
            # Se o usuário não passar argumento, o handler nem será chamado
            store_name = context.args[0].lower()
            
            # Verifica se a loja existe
            store = await self.supabase.get_store_by_name(store_name)
            
            if not store:
                await update.message.reply_text(
                    f"❌ Loja '{store_name}' não encontrada.\n"
                    f"Use /lojas para ver lojas disponíveis."
                )
                return
            
            # Busca produtos da loja
            filters = {
                "store": store["name"],
                "min_discount": 10,
                "limit": 5
            }
            
            products = await self.supabase.get_products(filters)
            
            if products:
                emoji = STORE_EMOJIS.get(store["name"], "🏪")
                await update.message.reply_text(
                    f"{emoji} *Produtos - {store['display_name']}*\n"
                    f"Mostrando {len(products)} produtos:",
                    parse_mode='Markdown'
                )
                
                for product in products:
                    message = self._format_product_message(product)
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"],
                        "telegram_send_count"
                    )
                    
                    # Pequena pausa
                    import asyncio
                    await asyncio.sleep(0.5)
            else:
                emoji = STORE_EMOJIS.get(store["name"], "🏪")
                await update.message.reply_text(
                    f"{emoji} Nenhum produto encontrado para {store['display_name']} no momento."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /produtos: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar produtos. Tente novamente!"
            )
    
    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /top - Melhores ofertas do momento"""
        try:
            # Busca top deals
            top_deals = await self.supabase.get_top_deals(limit=5, min_discount=30)
            
            if top_deals:
                await update.message.reply_text(
                    "🏆 *TOP OFERTAS DO MOMENTO*\n"
                    f"Os {len(top_deals)} melhores descontos:",
                    parse_mode='Markdown'
                )
                
                for idx, product in enumerate(top_deals, 1):
                    message = f"*#{idx}* - " + self._format_product_message(product)
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"],
                        "telegram_send_count"
                    )
                    
                    # Pequena pausa
                    import asyncio
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(
                    "😕 Nenhuma oferta especial no momento."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /top: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar top ofertas."
            )
    
    async def preferencias_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /preferencias - Gerenciar preferências do usuário"""
        try:
            user = update.effective_user
            telegram_user_id = user.id
            
            # Busca preferências atuais
            prefs = await self.supabase.get_user_preferences(telegram_user_id)
            
            if prefs.get("has_preferences"):
                # Formata preferências
                pref_data = prefs
                stores = pref_data.get("preferred_stores", [])
                categories = pref_data.get("preferred_categories", [])
                min_discount = pref_data.get("min_discount", 0)
                max_price = pref_data.get("max_price")
                
                message = f"""
⚙️ *Suas Preferências*

👤 *Usuário:* {user.first_name}

🏪 *Lojas Preferidas:*
{', '.join(stores) if stores else 'Nenhuma selecionada'}

📁 *Categorias:*
{', '.join(categories) if categories else 'Nenhuma selecionada'}

💰 *Desconto Mínimo:* {min_discount}%
💵 *Preço Máximo:* {'R$ {:.2f}'.format(max_price) if max_price else 'Sem limite'}

💡 *Dica:* Use /recomendar para ver produtos personalizados!
                """
            else:
                message = f"""
⚙️ *Configurar Preferências*

Olá {user.first_name}! Você ainda não configurou suas preferências.

Configure suas preferências para receber recomendações personalizadas!

*Como configurar:*
1. Escolha suas lojas favoritas com /lojas
2. Use /recomendar para ver produtos personalizados
3. Suas preferências serão salvas automaticamente

💡 *Dica:* Quanto mais você interage, melhores as recomendações!
                """
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro no comando /preferencias: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar preferências."
            )
    
    async def recomendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /recomendar - Produtos recomendados baseados em preferências"""
        try:
            user = update.effective_user
            telegram_user_id = user.id
            
            # Salva informações básicas do usuário
            await self.supabase.save_user_preference(
                telegram_user_id=telegram_user_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name
            )
            
            # Busca recomendações
            recommendations = await self.supabase.get_recommended_products(
                telegram_user_id=telegram_user_id,
                limit=5
            )
            
            if recommendations:
                await update.message.reply_text(
                    f"✨ *Recomendações para {user.first_name}*\n"
                    f"Baseado em suas preferências:",
                    parse_mode='Markdown'
                )
                
                for product in recommendations:
                    message = self._format_product_message(product)
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"],
                        "telegram_send_count"
                    )
                    
                    # Pequena pausa
                    import asyncio
                    await asyncio.sleep(0.5)
                    
                await update.message.reply_text(
                    "💡 *Dica:* Use /preferencias para ajustar suas preferências!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"😕 Nenhuma recomendação disponível no momento.\n"
                    f"Continue explorando com /cupom, /top ou /lojas!"
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /recomendar: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar recomendações."
            )
    
    # ==================== COMANDOS SHOPEE API ====================
    
    async def shopee_sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /shopee_sync - Sincronização manual com Shopee API"""
        try:
            await update.message.reply_text(
                "🔄 *Iniciando sincronização com Shopee API...*\n"
                "Isso pode levar alguns minutos.",
                parse_mode='Markdown'
            )
            
            # Importa o módulo aqui para evitar import circular
            from ..utils.shopee_importer import run_shopee_import
            
            # Executa importação
            result = await run_shopee_import(import_type="all", limit=50, min_commission=5.0)
            
            # Formata resposta
            duration = result.get("duration", 0)
            message = f"""
✅ *Sincronização Concluída!*

📦 *Produtos Importados:* {result.get('imported', 0)}
🔄 *Produtos Atualizados:* {result.get('updated', 0)}
❌ *Erros:* {result.get('errors', 0)}
⏱️ *Duração:* {duration:.1f}s

💰 *Comissão Mínima:* 5%
            """
            
            if result.get('errors', 0) > 0:
                message += f"\n⚠️ Alguns erros ocorreram. Verifique os logs."
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
            # Se import successful, mostra amostra
            if result.get('imported', 0) > 0:
                await update.message.reply_text(
                    "💡 Use /top_comissao para ver produtos com melhor comissão!",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /shopee_sync: {e}")
            await update.message.reply_text(
                f"❌ Erro na sincronização: {str(e)}\n"
                "Verifique as credenciais no .env"
            )
    
    async def shopee_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /shopee_stats - Estatísticas dos produtos Shopee"""
        try:
            # Busca estatísticas
            response = self.supabase.client.rpc("get_shopee_statistics").execute()
            
            if response.data:
                stats = response.data
                
                last_sync = stats.get('last_sync')
                if last_sync:
                    last_sync_str = datetime.fromisoformat(last_sync.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')
                else:
                    last_sync_str = "Nunca"
                
                message = f"""
📊 *Estatísticas Shopee*

📦 *Produtos Totais:* {stats.get('total_products', 0):,}
✅ *Produtos Ativos:* {stats.get('active_products', 0):,}
💰 *Comissão Média:* {stats.get('average_commission', 0):.2f}%
🛒 *Total de Vendas:* {stats.get('total_sales', 0):,}

🔄 *Última Sincronização:* {last_sync_str}
⚙️ *Sync Automático:* {'Ativado' if stats.get('sync_enabled') else 'Desativado'}

💡 *Comandos:*
/shopee_sync - Sincronizar manualmente
/top_comissao - Ver melhores comissões
                """
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "📊 Nenhuma estatística disponível ainda.\n"
                    "Use /shopee_sync para importar produtos."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /shopee_stats: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar estatísticas Shopee."
            )
    
    async def top_commission_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /top_comissao - Produtos com maior comissão"""
        try:
            # Busca produtos
            response = self.supabase.client.rpc(
                "get_top_commission_products",
                {"p_limit": 5}
            ).execute()
            
            products = response.data
            
            if products:
                await update.message.reply_text(
                    "💰 *TOP 5 - Maiores Comissões Shopee*",
                    parse_mode='Markdown'
                )
                
                for idx, product in enumerate(products, 1):
                    commission_rate = product.get('commission_rate', 0)
                    commission_amount = product.get('commission_amount', 0)
                    
                    message = f"*#{idx} - {commission_rate}% de comissão*\n"
                    message += f"💵 R$ {commission_amount:.2f} por venda\n\n"
                    message += self._format_product_message(product)
                    
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    
                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"],
                        "telegram_send_count"
                    )
                    
                    # Pequena pausa
                    import asyncio
                    await asyncio.sleep(0.5)
                    
                await update.message.reply_text(
                    "✨ *Dica:* Use /shopee_sync para atualizar produtos!",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "😕 Nenhum produto Shopee encontrado.\n"
                    "Use /shopee_sync para importar produtos da API."
                )
                
        except Exception as e:
            logger.error(f"Erro no comando /top_comissao: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar produtos com maior comissão."
            )
    
    # ==================== HANDLERS AUXILIARES ====================

    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens de texto"""
        text = update.message.text
        
        # Verifica se é um link
        if "http" in text.lower():
            await update.message.reply_text(
                "🔗 Detectei um link! Para adicionar produtos automaticamente, "
                "use o painel web ou envie um arquivo CSV.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "🤔 Não entendi. Use /help para ver os comandos disponíveis."
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para botões inline"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("store_"):
            store = data.replace("store_", "")
            await self.store_command(update, context, store)
        elif data == "random_coupon":
            await self.cupom_command(update, context)
        elif data == "today_promo":
            await self.today_command(update, context)
    
    # ==================== MÉTODOS UTILITÁRIOS ====================
    
    def _format_product_message(self, product: Dict[str, Any], highlight: bool = False) -> str:
        """Formata mensagem do produto para Telegram"""
        store = product.get("store", "shopee")
        emoji = STORE_EMOJIS.get(store, '🏪')
        store_name = store.replace('_', ' ').title()
        
        # Formata preço
        price = product.get("current_price", 0)
        original_price = product.get("original_price")
        discount = product.get("discount_percentage")
        
        price_text = f"R$ {price:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
        
        if original_price and discount:
            original_text = f"R$ {original_price:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
            price_text = f"~~{original_text}~~ → {price_text} ({discount}% OFF)"
        
        # Formata mensagem
        message = f"""
{emoji} *{store_name}*
        
🛍️ *{product.get('name', 'Produto')}*

💰 *Preço:* {price_text}
📦 *Categoria:* {product.get('category', 'Não informada')}
⭐ *Avaliação:* {product.get('rating', 'N/A')}/5 ({product.get('review_count', 0)} reviews)

🔗 [Ver Produto]({product.get('affiliate_link')})
        """
        
        # Adiciona cupom se existir
        coupon = product.get("coupon_code")
        if coupon:
            expiry = product.get("coupon_expiry")
            expiry_text = f" (Válido até {expiry[:10]})" if expiry else ""
            message += f"\n🎫 *Cupom:* `{coupon}`{expiry_text}"
        
        # Adiciona destaque se for promoção
        if highlight:
            message = f"🔥 *PROMOÇÃO EM DESTAQUE!*\n" + message
        
        # Adiciona tags se existirem
        tags = product.get("tags", [])
        if tags:
            tags_text = " ".join([f"#{tag}" for tag in tags[:3]])
            message += f"\n🏷️ {tags_text}"
        
        return message.strip()
    
    async def send_product_to_channel(self, chat_id: Optional[str], product: Dict[str, Any]):
        """Envia produto para um canal/grupo"""
        try:
            # Garante que temos um token
            if not self.token:
                self.token = telegram_settings.get_bot_token()
                
            if not self.token:
                logger.error("[TELEGRAM] Impossível enviar mensagem: Token não configurado")
                return False
                
            # Se chat_id não informado, tenta pegar do banco
            if not chat_id:
                chat_id = telegram_settings.get_group_chat_id()
                
            if not chat_id:
                logger.error("[TELEGRAM] Impossível enviar mensagem: Chat ID não configurado")
                return False

            bot = self.application.bot if self.application else Bot(self.token)
            
            message = self._format_product_message(product)
            
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            
            # Atualiza estatísticas
            await self.supabase.increment_product_stats(
                product["id"],
                "telegram_send_count"
            )
            
            logger.info(f"[OK] Produto {product['id']} enviado para {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao enviar produto para canal: {e}")
            return False

# Função para inicializar o bot
async def setup_telegram_handlers(token: Optional[str] = None):
    """Configura e retorna a aplicação Telegram"""
    bot = TelegramBot(token)
    return await bot.initialize()
