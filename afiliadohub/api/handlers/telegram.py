import os
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)

from ..utils.supabase_client import get_supabase_manager
from ..utils.link_processor import normalize_link, detect_store
from ..utils.telegram_settings_manager import telegram_settings
from ..utils.awin_client import AwinAffiliateClient, AwinAPIError
from ..services.commission_radar_service import CommissionRadarService

logger = logging.getLogger(__name__)

# Emojis para diferentes lojas
STORE_EMOJIS = {
    "shopee": "🛍️",
    "aliexpress": "📦",
    "amazon": "📚",
    "temu": "🎯",
    "shein": "👗",
    "magalu": "🏬",
    "mercado_livre": "🚀",
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
                logger.warning(
                    "[TELEGRAM] Bot token não configurado no banco de dados nem nas variáveis de ambiente."
                )
                return None

            self.application = Application.builder().token(self.token).build()

            # Registra handlers
            self._register_handlers()

            # Configura menu de comandos (SEO)
            await self.set_bot_commands()

            # Inicializa a aplicação (Obrigatório para Webhook ou Polling via v20+)
            await self.application.initialize()

            # Inicia polling locamente se não estiver configurado para webhook
            render_url = os.getenv("RENDER_EXTERNAL_URL")
            if not render_url:
                logger.info("[TELEGRAM] Iniciando polling para recepção de comandos locais...")
                await self.application.start()
                if getattr(self.application, "updater", None):
                    await self.application.updater.start_polling()
                else:
                    logger.warning("[TELEGRAM] Sem updater disponível na application.")

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
        self.application.add_handler(
            CommandHandler("produtos", self.produtos_command, has_args=1)
        )  # Requer 1 argumento
        self.application.add_handler(CommandHandler("top", self.top_command))
        self.application.add_handler(
            CommandHandler("preferencias", self.preferencias_command)
        )
        self.application.add_handler(
            CommandHandler("recomendar", self.recomendar_command)
        )

        # Comandos Shopee API
        self.application.add_handler(
            CommandHandler("shopee_sync", self.shopee_sync_command)
        )
        self.application.add_handler(
            CommandHandler("shopee_stats", self.shopee_stats_command)
        )
        self.application.add_handler(
            CommandHandler("top_comissao", self.top_commission_command)
        )
        # TODO: Implementar shopee_link_command e shopee_ofertas_command
        # self.application.add_handler(CommandHandler("shopee_link", self.shopee_link_command, has_args=1))
        # self.application.add_handler(CommandHandler("shopee_ofertas", self.shopee_ofertas_command))
        # self.application.add_handler(CommandHandler("shopee_buscar", self.shopee_buscar_command))

        # Comandos por loja (legado - mantido para compatibilidade)
        self.application.add_handler(
            CommandHandler("shopee", lambda u, c: self.store_command(u, c, "shopee"))
        )
        self.application.add_handler(
            CommandHandler(
                "aliexpress", lambda u, c: self.store_command(u, c, "aliexpress")
            )
        )
        self.application.add_handler(
            CommandHandler("amazon", lambda u, c: self.store_command(u, c, "amazon"))
        )
        self.application.add_handler(
            CommandHandler("temu", lambda u, c: self.store_command(u, c, "temu"))
        )
        self.application.add_handler(
            CommandHandler("shein", lambda u, c: self.store_command(u, c, "shein"))
        )
        self.application.add_handler(
            CommandHandler("magalu", lambda u, c: self.store_command(u, c, "magalu"))
        )
        self.application.add_handler(
            CommandHandler("mercado", lambda u, c: self.store_command(u, c, "mercado_livre"))
        )

        # Comandos CJ e Awin Radar
        self.application.add_handler(CommandHandler("awin_radar", self.awin_radar_command))
        self.application.add_handler(CommandHandler("cj_radar", self.cj_radar_command))

        # Comandos Story
        self.application.add_handler(CommandHandler("story", self.story_command))

        # Comandos de busca
        self.application.add_handler(CommandHandler("buscar", self.search_command))
        self.application.add_handler(CommandHandler("hoje", self.today_command))
        self.application.add_handler(CommandHandler("aleatorio", self.random_command))
        self.application.add_handler(
            CommandHandler("categorias", self.categories_command)
        )

        # Comandos admin
        self.application.add_handler(CommandHandler("stats", self.stats_command))

        # Handler para novos membros (Boas-vindas AIDA)
        self.application.add_handler(
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome_new_members)
        )
        # Limpeza de saída de membros (opcional para manter o foco)
        self.application.add_handler(
            MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, self.delete_status_message)
        )

        # Handler para mensagens
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler)
        )

        # Handler para callback queries (botões)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    # ==================== HANDLERS DE COMANDOS ====================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /start"""
        user = update.effective_user
        welcome_text = f"""
👋 Olá {user.first_name}! Bem-vindo ao *AfiliadoHub*!

🎯 *Comandos disponíveis:*

🌟 <b>BEM-VINDO(A) AO AFILIADOHUB!</b>

Olá {update.effective_user.first_name}, que bom ter você aqui! 👋

Eu sou seu <b>Garimpeiro de Ofertas VIP</b>. Minha missão é monitorar as maiores lojas do Brasil (Mercado Livre, Shopee, Amazon...) 24h por dia para encontrar os <b>preços mais baixos e cupons escondidos</b>.

🛍️ <b>O que eu faço por você?</b>
- 🔍 Busco qualquer produto (digite /buscar [nome])
- 🤝 Mostro Ofertas do Mercado Livre (digite /mercado)
- 🎟️ Entrego Cupons VIP (digite /cupom)
- 🔥 Mostro a melhor oferta AGORA (digite /promo)

👇 <b>Escolha uma opção abaixo para começar agora mesmo:</b>
        """

        keyboard = [
            [
                InlineKeyboardButton("🔥 Melhor Promoção", callback_data="today_promo"),
                InlineKeyboardButton("🎟️ Pegar Cupom VIP", callback_data="random_coupon"),
            ],
            [
                InlineKeyboardButton("🤝 Ofertas Mercado Livre", callback_data="store_mercado_livre"),
            ],
            [
                InlineKeyboardButton("🛍️ Ver na Shopee", callback_data="store_shopee"),
                InlineKeyboardButton("📦 Ver na Amazon", callback_data="store_amazon"),
            ],
            [
                InlineKeyboardButton("🔍 Como Buscar?", callback_data="help_search"),
                InlineKeyboardButton("🏆 Top 5 Descontos", callback_data="top_deals"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            welcome_text, parse_mode="HTML", reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /help centralizado"""
        help_text = """
🆘 <b>AJUDA AFILIADOHUB</b>

Aqui estão os principais comandos para você economizar muito:

🔍 <b>BUSCAS</b>
/buscar [nome] - Busca rápida de produtos
/lojas - Ver todas as lojas parceiras
/hoje - O que chegou de NOVO hoje
/top - Os 5 maiores descontos agora

🎟️ <b>CUPONS</b>
/cupom - Recebe um cupom aleatório VIP

🔄 <b>DICA:</b> No grupo público, eu envio as melhores ofertas automaticamente. Mas se você busca algo específico, <b>sempre use o chat privado comigo!</b>
        """
        await update.message.reply_text(help_text, parse_mode="HTML")

    async def cupom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /cupom — Central de Benefícios VIP Shopee com links rastreáveis fixos."""
        await self._apply_reaction(update, "🤩")
        try:
            # Links rastreáveis próprios — sempre válidos, sem depender de API ou campanha
            CUPONS_URL  = "https://s.shopee.com.br/30kEKr2OAA"  # Cupons Diários
            FRETE_URL   = "https://s.shopee.com.br/4fsSJyLqi6"  # Frete Grátis
            OFERTAS_URL = "https://s.shopee.com.br/4AwBj7QT3W"  # Super Ofertas

            message = (
                "🎟️ <b>CENTRAL DE BENEFÍCIOS VIP SHOPEE</b>\n\n"
                "✨ Os melhores benefícios do momento, renovados diariamente:\n\n"
                "🎁 <b>Cupons Diários</b> — Ative antes de esgotar\n"
                "📦 <b>Frete Grátis</b> — Sem mínimo de compra\n"
                "🔥 <b>Super Ofertas</b> — As maiores promoções ativas agora\n\n"
                "<i>⚠️ Benefícios por tempo limitado. Clique rápido!</i>"
            )
            keyboard = [
                [
                    InlineKeyboardButton("🎁 Cupons Diários", url=CUPONS_URL),
                    InlineKeyboardButton("📦 Frete Grátis", url=FRETE_URL),
                ],
                [
                    InlineKeyboardButton("🔥 Super Ofertas", url=OFERTAS_URL),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Erro crítico no comando /cupom: {e}")
            await update.message.reply_text("❌ Tivemos um erro temporário. Tente novamente!")

    async def store_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, store: str
    ):
        """Handler para comandos de loja específica"""
        try:
            # Processa link passado diretamente com o comando (ex: /mercado https://bit.ly/...)
            if context.args and len(context.args) > 0:
                url = context.args[0]
                if "http" in url:
                    if store == "mercado_livre":
                        success = await self._process_ml_link(url, update, is_private=(update.message.chat.type == "private"))
                        if success:
                            return
                        else:
                            await update.message.reply_text("❌ O link fornecido é inválido, está quebrado ou não é do Mercado Livre.")
                            return
                    else:
                        await update.message.reply_text("🔗 O processamento automático de links diretos está disponível apenas para Mercado Livre no momento.")
                        return

            # Busca 3 produtos da loja
            filters = {"store": store, "min_discount": 10, "limit": 3}

            logger.info(f"[Bot] Buscando ofertas para loja: {store}")
            products = await self.supabase.get_products(filters)

            if products:
                for product in products:
                    message = self._format_product_message(product)
                    await self._send_formatted_product_reply(update, product, message)

                    # Atualiza estatísticas (Ignore erros aqui para não travar o envio)
                    try:
                        await self.supabase.increment_product_stats(
                            product["id"], "telegram_send_count"
                        )
                    except Exception as stats_err:
                        logger.warning(f"Erro ao incrementar status: {stats_err}")

                    import asyncio
                    await asyncio.sleep(0.5)
            else:
                emoji = STORE_EMOJIS.get(store, "🏪")
                await update.message.reply_text(
                    f"{emoji} Nenhuma oferta encontrada para {store.replace('_', ' ').title()} no momento."
                )

        except Exception as e:
            logger.error(f"Erro crítico no comando de loja {store}: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Ops! Tive um probleminha ao buscar ofertas da {store.title()}. Tente novamente em instantes!")

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /buscar [termo] — busca em 3 camadas progressivas, resultado apenas no privado."""
        await self._apply_reaction(update, "👀")
        try:
            if not context.args:
                await update.message.reply_text(
                    "🔍 Use: /buscar [produto]\nEx: /buscar fone bluetooth"
                )
                return

            import asyncio
            import math
            from ..handlers.shopee_api import create_shopee_client

            search_term = " ".join(context.args)
            client = create_shopee_client()

            msg = await update.message.reply_text(
                f"🔄 Procurando os melhores resultados para <b>{search_term}</b>...",
                parse_mode="HTML",
            )

            valid_nodes = []
            layer_used = 0

            try:
                async with client:
                    # Camada 1 — Premium: lojas chave, mais vendidos, qualidade alta
                    r1 = await client.get_products(keyword=search_term, is_key_seller=True, sort_type=2, limit=20)
                    nodes1 = r1.get("nodes", [])
                    layer1 = [
                        n for n in nodes1
                        if float(n.get("priceDiscountRate", 0)) >= 5
                        and int(n.get("sales") or 0) > 10
                        and float(n.get("ratingStar") or 0) >= 4.5
                    ]
                    if layer1:
                        valid_nodes = layer1
                        layer_used = 1
                    else:
                        # Camada 2 — Padrão: qualquer loja, avaliação boa
                        r2 = await client.get_products(keyword=search_term, sort_type=1, limit=20)
                        nodes2 = r2.get("nodes", [])
                        layer2 = [
                            n for n in nodes2
                            if float(n.get("ratingStar") or 0) >= 4.0
                            and int(n.get("sales") or 0) > 0
                        ]
                        if layer2:
                            valid_nodes = layer2
                            layer_used = 2
                        else:
                            # Camada 3 — Fallback: melhor resultado disponível
                            fallback = nodes2 or nodes1
                            if fallback:
                                valid_nodes = fallback[:5]
                                layer_used = 3

                if valid_nodes:
                    valid_nodes.sort(key=lambda x: int(x.get("sales") or 0), reverse=True)
                    top_nodes = valid_nodes[:3]

                    quality_label = {
                        1: "✅ Lojas Oficiais · Mais Vendidos · Alta Avaliação",
                        2: "⭐ Boa Avaliação · Com Vendas Reais",
                        3: "📦 Mais Relevante Disponível",
                    }.get(layer_used, "")

                    await msg.edit_text(
                        f"🔍 <b>Resultados para '{search_term}'</b>\n<i>{quality_label}</i>",
                        parse_mode="HTML",
                    )

                    for node in top_nodes:
                        product = self._map_shopee_node_to_product(node)
                        message = self._format_product_message(product)
                        # allow_mirror=False — resultado fica apenas no privado do usuário
                        await self._send_formatted_product_reply(update, product, message, allow_mirror=False)
                        await asyncio.sleep(0.5)

                    # Botões de refinamento APÓS os resultados
                    keyword_encoded = search_term.replace(" ", "+")
                    keyboard = [
                        [
                            InlineKeyboardButton("🏆 Mais Vendidos", callback_data=f"shopee_filter_sales|{search_term}"),
                            InlineKeyboardButton("💰 Menor Preço", callback_data=f"shopee_filter_price|{search_term}"),
                        ],
                        [
                            InlineKeyboardButton("⭐ Melhor Avaliação", callback_data=f"shopee_filter_rating|{search_term}"),
                            InlineKeyboardButton("🔍 Ver Mais na Shopee", url=f"https://shopee.com.br/search?keyword={keyword_encoded}"),
                        ],
                    ]
                    await update.message.reply_text(
                        "🎯 <b>Refinar busca:</b>",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
                else:
                    await msg.edit_text(
                        f"😕 Não encontrei resultados para <b>{search_term}</b>.\n\n"
                        "💡 Dicas:\n• Tente palavras mais simples\n"
                        "• Use o nome em português\n"
                        f"• Experimente: /buscar fone, /buscar tênis",
                        parse_mode="HTML",
                    )

            except Exception as e:
                logger.error(f"Erro ao buscar '{search_term}' na Shopee API: {e}")
                await msg.edit_text("❌ Erro nos servidores da Shopee. Tente novamente em instantes!")

        except Exception as e:
            logger.error(f"Erro no comando /buscar: {e}")
            await update.message.reply_text("❌ Erro ao buscar produtos. Tente novamente!")

    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /hoje - O que está bombando Hoje na Shopee"""
        await self._apply_reaction(update, "🔥")
        try:
            today = datetime.now().date().strftime("%d/%m")
            from ..handlers.shopee_api import create_shopee_client
            client = create_shopee_client()
            
            async with client:
                # sort_type=2 -> ITEM_SOLD_DESC. Retorna os mais vendidos no período recente
                result = await client.get_products(is_key_seller=True, sort_type=2, limit=5)

            nodes = result.get("nodes", [])

            if nodes:
                await update.message.reply_text(
                    f"🆕 *Estourando de Vendas em {today}:*\n Produtos Oficiais Mais Vendidos AGORA na Shopee:", 
                    parse_mode="Markdown"
                )

                import asyncio
                for node in nodes:
                    product = self._map_shopee_node_to_product(node)
                    message = self._format_product_message(product)
                    # allow_mirror=False — /hoje fica apenas no chat do usuário
                    await self._send_formatted_product_reply(update, product, message, allow_mirror=False)
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(
                    "📭 A API não retornou tendências de vendas no momento. Tente /top!"
                )

        except Exception as e:
            logger.error(f"Erro no comando /hoje: {e}")
            await update.message.reply_text(
                "❌ Erro ao buscar novidades ao vivo."
            )

    async def random_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /aleatorio - Produto totalmente aleatório"""
        try:
            product = await self.supabase.get_random_product()

            if product:
                message = self._format_product_message(product)
                await self._send_formatted_product_reply(update, product, message)
            else:
                await update.message.reply_text("🎲 Nenhum produto encontrado.")

        except Exception as e:
            logger.error(f"Erro no comando /aleatorio: {e}")
            await update.message.reply_text("❌ Erro ao buscar produto aleatório.")

    async def categories_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler para /categorias - Lista categorias disponíveis"""
        try:
            # Busca categorias distintas
            response = (
                self.supabase.client.table("products")
                .select("category")
                .not_.is_("category", "null")
                .eq("is_active", True)
                .execute()
            )

            categories = list(
                set([p["category"] for p in response.data if p["category"]])
            )

            if categories:
                categories.sort()
                categories_text = "\n".join([f"• {cat}" for cat in categories])

                message = f"""
📁 *Categorias Disponíveis:*

{categories_text}

💡 Use: /buscar [categoria]
Ex: /buscar eletrônicos
                """

                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    "📂 Nenhuma categoria cadastrada ainda."
                )

        except Exception as e:
            logger.error(f"Erro no comando /categorias: {e}")
            await update.message.reply_text("❌ Erro ao buscar categorias.")

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

            stores = stats.get("stores", {})
            for store, count in stores.items():
                emoji = STORE_EMOJIS.get(store, "🏪")
                message += f"{emoji} {store.title()}: {count:,}\n"

            message += f"\n🔄 *Atualizado:* {stats.get('updated_at', 'N/A')}"

            await update.message.reply_text(message, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Erro no comando /stats: {e}")
            await update.message.reply_text("📊 Estatísticas indisponíveis no momento.")

    async def _apply_reaction(self, update: Update, emoji: str = "👀"):
        """Aplica uma reação dinâmica na mensagem do usuário."""
        try:
            if update.message:
                await update.message.set_reaction(reaction=[ReactionTypeEmoji(emoji)])
        except Exception as e:
            logger.debug(f"[Reação] Erro ao adicionar reação {emoji}: {e}")

    async def _post_product_story(self, bot: Bot, chat_id: str, product: Dict[str, Any]):
        """Publica uma oferta destacada diretamente no Story do Telegram via API v21+."""
        try:
            image_url = product.get("image_url")
            store = product.get("store", "Lojas").replace("_", " ").title()
            discount = product.get("discount_percentage", 0)
            
            caption = f"🔥 {discount}% OFF na {store}!\n" + self._format_product_message(product, highlight=True)
            
            if image_url:
                await bot.post_story(
                    chat_id=chat_id,
                    media=image_url,
                    caption=caption
                )
                logger.info(f"Story publicado com sucesso para: {product.get('id', '')}")
            else:
                logger.warning(f"Produto sem foto, story não gerado: {product.get('id', '')}")
        except AttributeError:
            logger.warning("[Telegram VIP] O python-telegram-bot atual não suporta post_story.")
        except Exception as e:
            logger.error(f"Erro ao postar story da oferta: {e}")

    async def story_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /story [id_produto] - Permite admin forçar criação de Story."""
        try:
            user_id = update.effective_user.id
            if str(user_id) not in str(os.getenv("ADMIN_IDS", "")):
                await update.message.reply_text("⛔️ Apenas admins podem forçar stories manuais.")
                return

            if not context.args:
                await update.message.reply_text("🔍 Use: /story [id_produto]")
                return

            search_term = context.args[0]
            # Busca simples para carregar o produto
            response = self.supabase.client.table("products").select("*").ilike("id", f"%{search_term}%").limit(1).execute()
            products = response.data

            if not products:
                await update.message.reply_text("❌ Produto não encontrado no banco.")
                return

            product = products[0]
            await update.message.reply_text(f"⏳ Publicando Story para o produto...")
            
            chat_to_post = os.getenv("TELEGRAM_CHANNEL_ID", update.effective_chat.id)
            await self._post_product_story(context.bot, chat_to_post, product)
            
            await update.message.reply_text("✅ Story postado/tentado com sucesso!")

        except Exception as e:
            logger.error(f"Erro no /story: {e}")
            await update.message.reply_text("❌ Falha ao postar Story.")

    def _map_shopee_node_to_product(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Converte o retorno da API GraphQL Live da Shopee para o formato local Supabase"""
        price = float(node.get("priceMin", 0))
        discount = float(node.get("priceDiscountRate", 0))
        
        # Calculate original price based on discount rate
        original_price = price / (1 - (discount / 100)) if discount < 100 else price
        
        # Merge seller extra commission with platform commission
        commission_rate = float(node.get("sellerCommissionRate", 0)) + float(node.get("shopeeCommissionRate", 0))
        
        return {
            "id": node.get("itemId"),
            "name": node.get("productName", "Produto Shopee (AMS Extra)"),
            "original_price": original_price,
            "current_price": price,
            "discount_percentage": discount,
            "affiliate_link": node.get("offerLink"),
            "image_url": node.get("imageUrl"),
            "store": "shopee",
            "category": "Achadinhos Premium",
            "commission_rate": commission_rate,
            "is_active": True
        }

    async def promo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /promo — garimpador anti-manopla: exige desconto real, vendas reais e lojas confiáveis."""
        await self._apply_reaction(update, "🤩")
        try:
            import math
            from ..handlers.shopee_api import create_shopee_client

            client = create_shopee_client()
            msg = await update.message.reply_text("🔎 Garimpando promoção real... isso pode levar alguns segundos.")

            async with client:
                # AMS + lojas chave = vendedores comprometidos com a campanha, menos manopla
                result = await client.get_products(
                    is_key_seller=True,
                    is_ams_offer=True,
                    sort_type=2,  # ITEM_SOLD_DESC — mais vendidos primeiro
                    limit=30,
                )

            nodes = result.get("nodes", [])

            # Filtro anti-manopla principal:
            # — discount >= 20%: desconto significativo
            # — sales >= 50: se 50+ pessoas compraram, o preço é real
            # — rating >= 4.5: compradores satisfeitos = produto entrega o valor prometido
            # — shopType oficial ou preferido: lojas auditadas pela Shopee
            valid_nodes = [
                n for n in nodes
                if float(n.get("priceDiscountRate", 0)) >= 20
                and int(n.get("sales") or 0) >= 50
                and float(n.get("ratingStar") or 0) >= 4.5
                and any(t in (n.get("shopType") or []) for t in [1, 2, 4])
            ]

            # Fallback: relaxa sales mas mantém qualidade
            if not valid_nodes:
                valid_nodes = [
                    n for n in nodes
                    if float(n.get("priceDiscountRate", 0)) >= 15
                    and int(n.get("sales") or 0) >= 10
                    and float(n.get("ratingStar") or 0) >= 4.5
                ]

            if valid_nodes:
                # Score anti-manopla: balança desconto real × volume real
                # log(sales) penaliza produtos com 1-2 vendas que inflacionaram desconto
                def real_score(n):
                    d = float(n.get("priceDiscountRate", 0))
                    s = int(n.get("sales") or 0)
                    return d * math.log(s + 1)

                valid_nodes.sort(key=real_score, reverse=True)
                best = valid_nodes[0]
                product = self._map_shopee_node_to_product(best)

                discount = float(best.get("priceDiscountRate", 0))
                sales = int(best.get("sales") or 0)
                rating = float(best.get("ratingStar") or 0)

                await msg.delete()

                message = self._format_product_message(product, highlight=True)
                badge = (
                    f"\n\n✅ <i>Desconto verificado: {int(discount)}% OFF"
                    f" · {sales:,} compradores reais · ⭐ {rating}</i>"
                )
                # allow_mirror=True — /promo espelha no grupo para engajamento
                await self._send_formatted_product_reply(update, product, message + badge, allow_mirror=True)

                # Tenta postar como Story
                chat_to_post = os.getenv("TELEGRAM_CHANNEL_ID", update.effective_chat.id)
                await self._post_product_story(context.bot, chat_to_post, product)
            else:
                await msg.edit_text(
                    "🔥 Ainda não encontrei uma promoção com desconto realmente verdadeiro agora.\n"
                    "Use /buscar [produto] ou /cupom para descontos garantidos!"
                )

        except Exception as e:
            logger.error(f"Erro crítico no comando /promo: {e}", exc_info=True)
            await update.message.reply_text("❌ A Shopee não está respondendo agora. Tente o /cupom enquanto isso!")

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

                message += (
                    "\n💬 *Dica:* Use `/produtos [loja]` para ver produtos específicos!"
                )

                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    "😕 Nenhuma loja disponível no momento."
                )

        except Exception as e:
            logger.error(f"Erro no comando /lojas: {e}")
            await update.message.reply_text("❌ Erro ao buscar lojas. Tente novamente!")

    async def produtos_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
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
            filters = {"store": store["name"], "min_discount": 10, "limit": 5}

            products = await self.supabase.get_products(filters)

            if products:
                emoji = STORE_EMOJIS.get(store["name"], "🏪")
                await update.message.reply_text(
                    f"{emoji} *Produtos - {store['display_name']}*\n"
                    f"Mostrando {len(products)} produtos:",
                    parse_mode="Markdown",
                )

                for product in products:
                    message = self._format_product_message(product)
                    await self._send_formatted_product_reply(update, product, message)

                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"], "telegram_send_count"
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
        """Handler para /top - Top 5 Ofertas Reais de Mais Vendidos da Shopee"""
        await self._apply_reaction(update, "🏆")
        try:
            from ..handlers.shopee_api import create_shopee_client
            client = create_shopee_client()
            
            async with client:
                # Credibilidade e Confiança: Lojas oficiais, sort by vendas!
                result = await client.get_products(is_key_seller=True, sort_type=2, limit=20)
                
            nodes = result.get("nodes", [])

            valid_nodes = [
                n for n in nodes 
                if float(n.get("priceDiscountRate", 0)) >= 10
            ]

            if valid_nodes:
                # Re-ordena pelas vendas no caso de a ordem ter bagunçado e pega os 5 melhores
                valid_nodes.sort(key=lambda x: int(x.get("sales", 0) if x.get("sales") else 0), reverse=True)
                top_nodes = valid_nodes[:5]

                await update.message.reply_text(
                    "🏆 *TOP 5 ACHADINHOS REAIS (AO VIVO)*\n"
                    f"Os favoritos com mais vendas e descontos *verdadeiros* nas Lojas Oficiais:",
                    parse_mode="Markdown",
                )

                import asyncio
                for idx, node in enumerate(top_nodes, 1):
                    product = self._map_shopee_node_to_product(node)
                    message = f"*#{idx}* - " + self._format_product_message(product)
                    # allow_mirror=False — /top fica apenas no chat do usuário
                    await self._send_formatted_product_reply(update, product, message, allow_mirror=False)
                    await asyncio.sleep(0.8)
            else:
                await update.message.reply_text(
                    "😕 O radar da Shopee não retornou ofertas super especiais desta vez."
                )

        except Exception as e:
            logger.error(f"Erro no comando /top: {e}")
            await update.message.reply_text("❌ Erro ao buscar top ofertas aos vivo da Shopee.")

    async def preferencias_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
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

            await update.message.reply_text(message, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Erro no comando /preferencias: {e}")
            await update.message.reply_text("❌ Erro ao buscar preferências.")

    async def recomendar_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler para /recomendar - Busca produtos Premium na Shopee via Categorias Preferidas"""
        try:
            user = update.effective_user
            telegram_user_id = user.id

            await self.supabase.save_user_preference(
                telegram_user_id=telegram_user_id,
                telegram_username=user.username,
                telegram_first_name=user.first_name,
            )

            # Busca preferências atuais
            prefs = await self.supabase.get_user_preferences(telegram_user_id)
            categories = prefs.get("preferred_categories", [])
            keyword = categories[0] if categories else "Promoção Oferta AMS"

            from ..handlers.shopee_api import create_shopee_client
            client = create_shopee_client()
            
            async with client:
                result = await client.get_products(keyword=keyword, is_ams_offer=True, sort_type=1, limit=5)

            nodes = result.get("nodes", [])

            if nodes:
                await update.message.reply_text(
                    f"✨ *Recomendações Especiais para {user.first_name}* (Ao Vivo)\n"
                    f"Filtrado com base no seu perfil ({keyword}):",
                    parse_mode="Markdown",
                )

                for node in nodes:
                    product = self._map_shopee_node_to_product(node)
                    message = self._format_product_message(product)
                    await self._send_formatted_product_reply(update, product, message)

                    import asyncio
                    await asyncio.sleep(0.5)

                await update.message.reply_text(
                    "💡 *Dica:* Use /preferencias para ajustar seus interesses e refinar a busca!",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text(
                    f"😕 Nenhuma recomendação de alta comissão encontrada para '{keyword}'.\n"
                    f"Continue explorando com /cupom, /top ou /lojas!"
                )

        except Exception as e:
            logger.error(f"Erro no comando /recomendar: {e}")
            await update.message.reply_text("❌ Erro ao buscar recomendações.")

    # ==================== COMANDOS SHOPEE API ====================

    async def shopee_sync_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler para /shopee_sync - Sincronização manual com Shopee API"""
        try:
            await update.message.reply_text(
                "🔄 *Iniciando sincronização com Shopee API...*\n"
                "Isso pode levar alguns minutos.",
                parse_mode="Markdown",
            )

            # Importa o módulo aqui para evitar import circular
            from ..utils.shopee_importer import run_shopee_import

            # Executa importação
            result = await run_shopee_import(
                import_type="all", limit=50, min_commission=5.0
            )

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

            if result.get("errors", 0) > 0:
                message += f"\n⚠️ Alguns erros ocorreram. Verifique os logs."

            await update.message.reply_text(message, parse_mode="Markdown")

            # Se import successful, mostra amostra
            if result.get("imported", 0) > 0:
                await update.message.reply_text(
                    "💡 Use /top_comissao para ver produtos com melhor comissão!",
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Erro no comando /shopee_sync: {e}")
            await update.message.reply_text(
                f"❌ Erro na sincronização: {str(e)}\n"
                "Verifique as credenciais no .env"
            )

    async def shopee_stats_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler para /shopee_stats - Estatísticas dos produtos Shopee"""
        try:
            # Busca estatísticas
            response = self.supabase.client.rpc("get_shopee_statistics").execute()

            if response.data:
                stats = response.data

                last_sync = stats.get("last_sync")
                if last_sync:
                    last_sync_str = datetime.fromisoformat(
                        last_sync.replace("Z", "+00:00")
                    ).strftime("%d/%m/%Y %H:%M")
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

                await update.message.reply_text(message, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    "📊 Nenhuma estatística disponível ainda.\n"
                    "Use /shopee_sync para importar produtos."
                )

        except Exception as e:
            logger.error(f"Erro no comando /shopee_stats: {e}")
            await update.message.reply_text("❌ Erro ao buscar estatísticas Shopee.")

    async def top_commission_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handler para /top_comissao - Produtos com maior comissão"""
        try:
            # Busca produtos
            response = self.supabase.client.rpc(
                "get_top_commission_products", {"p_limit": 5}
            ).execute()

            products = response.data

            if products:
                await update.message.reply_text(
                    "💰 *TOP 5 - Maiores Comissões Shopee*", parse_mode="Markdown"
                )

                for idx, product in enumerate(products, 1):
                    commission_rate = product.get("commission_rate", 0)
                    commission_amount = product.get("commission_amount", 0)

                    message = f"*#{idx} - {commission_rate}% de comissão*\n"
                    message += f"💵 R$ {commission_amount:.2f} por venda\n\n"
                    message += self._format_product_message(product)
                    await self._send_formatted_product_reply(update, product, message)

                    # Atualiza estatísticas
                    await self.supabase.increment_product_stats(
                        product["id"], "telegram_send_count"
                    )

                    # Pequena pausa
                    import asyncio

                    await asyncio.sleep(0.5)

                await update.message.reply_text(
                    "✨ *Dica:* Use /shopee_sync para atualizar produtos!",
                    parse_mode="Markdown",
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

    # ==================== HANDLERS DE ENGAJAMENTO ====================

    async def welcome_new_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AIDA Welcome: Recepciona novos membros com foco em conversão e SEO"""
        for new_member in update.message.new_chat_members:
            if new_member.is_bot:
                continue

            first_name = new_member.first_name
            
            # AIDA + CTO Message
            welcome_text = f"""
🚨 <b>{first_name.upper()}, VOCÊ ACABA DE ENTRAR NO CLUBE DE OFERTAS AFILIADOTOP!</b> 🎯

Aqui você não perde mais tempo procurando cupons. Nós garimpamos as melhores ofertas da <b>Shopee, Amazon, AliExpress e Awin</b> 24h por dia para você! 🚀

🔥 <b>POR QUE FICAR AQUI?</b>
• Descontos reais de até 80% 💸
• Cupons exclusivos que expiram rápido ⏳
• Seleção feita por especialistas em economia 🧠

👉 <b>PARA COMEÇAR A ECONOMIZAR AGORA:</b>
Clique no link abaixo e veja os <b>ACHADINHOS DE HOJE</b>:
🔗 <a href="https://afiliado.top"><b>VER OPORTUNIDADES IMPERDÍVEIS</b></a>

<i>Seja bem-vindo(a) e boas compras!</i>
#Ofertas #Cupons #Economia #Shopee #Amazon
            """
            
            # Botão de ação (CTO)
            keyboard = [
                [InlineKeyboardButton("🛒 VER MELHORES OFERTAS", url="https://afiliado.top")],
                [InlineKeyboardButton("🎁 PEGAR CUPOM ALEATÓRIO", callback_data="random_coupon")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                welcome_text, 
                parse_mode="HTML", 
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )

    async def delete_status_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Limpa as mensagens de saída de membros para manter o grupo focado nas vendas"""
        try:
            await update.message.delete()
        except:
            pass

    async def set_bot_commands(self):
        """Configura o menu de comandos oficial do Bot no Telegram (SEO + UX)"""
        from telegram import BotCommand
        
        commands = [
            BotCommand("start", "🚀 Começar e Ver Ofertas VIP"),
            BotCommand("mercado", "🤝 Ver Ofertas do Mercado Livre"),
            BotCommand("cupom", "🎟️ Pegar Cupom de Desconto VIP"),
            BotCommand("promo", "🔥 Ver Melhor Oferta do Momento"),
            BotCommand("buscar", "🔍 Buscar Produto (ex: /buscar fone)"),
            BotCommand("hoje", "🆕 Ver Novidades de Hoje"),
            BotCommand("lojas", "🏪 Listar Lojas Parceiras"),
            BotCommand("top", "🏆 Ver TOP 5 Descontos"),
            BotCommand("recomendar", "✨ Ver Recomendações para Você"),
            BotCommand("help", "🆘 Ajuda e Suporte"),
        ]
        
        try:
            await self.application.bot.set_my_commands(commands)
            logger.info("[TELEGRAM] Menu de comandos SEO configurado com sucesso")
        except Exception as e:
            logger.error(f"[TELEGRAM] Erro ao configurar comandos: {e}")

    async def awin_radar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Executa radar Awin via Telegram (Admin)"""
        # Checagem simples de admin (pode ser expandida)
        user_id = update.effective_user.id
        # TODO: Adicionar checagem de admin real se necessário
        
        await update.message.reply_text("🔎 <b>Iniciando Radar Awin (MÁQUINA DE DINHEIRO)...</b>", parse_mode="HTML")
        
        try:
            radar = CommissionRadarService()
            # O usuário pediu "1.automaticamente": auto_dispatch=True
            res = await radar.run_awin_radar(max_broadcasts=3, auto_dispatch=True)
            
            dispatched = res.get("dispatched", 0)
            if dispatched > 0:
                await update.message.reply_text(f"✅ <b>RADAR AWIN CONCLUÍDO!</b>\n\n🚀 {dispatched} ofertas quentes foram disparadas para o grupo!", parse_mode="HTML")
            else:
                await update.message.reply_text("📭 Nenhuma oferta nova encontrada no Radar Awin agora.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"[Bot Radar Awin] {e}")
            await update.message.reply_text(f"❌ Erro ao rodar radar Awin: {str(e)}")
            
    async def cj_radar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Executa radar CJ via Telegram (Admin)"""
        await update.message.reply_text("🔎 <b>Iniciando Radar CJ (MÁQUINA DE DINHEIRO)...</b>", parse_mode="HTML")
        
        try:
            radar = CommissionRadarService()
            # Rodar com 40% de desconto conforme discutido no plano
            res = await radar.run_cj_radar(min_discount=40.0, max_broadcasts=3, auto_dispatch=True)
            
            dispatched = res.get("dispatched", 0)
            if dispatched > 0:
                await update.message.reply_text(f"✅ <b>RADAR CJ CONCLUÍDO!</b>\n\n🚀 {dispatched} achadinhos VIP disparados para o grupo!", parse_mode="HTML")
            else:
                await update.message.reply_text("📭 Nenhuma oferta de +40% encontrada na CJ no momento.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"[Bot Radar CJ] {e}")
            await update.message.reply_text(f"❌ Erro ao rodar radar CJ: {str(e)}")

    # ==================== HANDLERS AUXILIARES ====================

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens de texto (Acolhimento + NLP Lite)"""
        if not update.message or not update.message.text:
            return
            
        text = update.message.text.lower().strip()
        user_name = update.effective_user.first_name
        is_private = update.message.chat.type == "private"

        # 1. Detecção de Saudações (Apenas no Privado para ser amigável)
        greetings = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem", "opa"]
        if any(greet in text for greet in greetings) and is_private:
            greeting_msg = f"Olá, {user_name}! Que alegria falar com você! 😊\n\nEu sou o seu assistente de ofertas do AfiliadoHub. Estou aqui para te ajudar a economizar.\n\n<b>Como posso te ajudar agora?</b>"
            keyboard = [
                [InlineKeyboardButton("🔍 Buscar um Produto", callback_data="help_search")],
                [InlineKeyboardButton("🔥 Ver Ofertas de Hoje", callback_data="today_promo")],
                [InlineKeyboardButton("🎟️ Pegar um Cupom VIP", callback_data="random_coupon")]
            ]
            await update.message.reply_text(
                greeting_msg, 
                parse_mode="HTML", 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # 2. Verifica se é um link
        if "http" in text:
            import re
            
            urls = re.findall(r'(https?://[^\s]+)', text)
            if urls:
                url = urls[0]
                # Se for Mercado Livre ou um encurtador comum (ex: bit.ly)
                if "mercadolivre.com" in url or "mlb.ml" in url or "bit.ly" in url or "/sho" in url or "amzn.to" in url:
                    processed = await self._process_ml_link(url, update, is_private)
                    if processed:
                        return

            if is_private:
                await update.message.reply_text(
                    "🔗 <b>Detectei um link!</b>\n\nNenhuma automação compatível com esse formato ainda. Para converter outros links ou adicionar produtos, fale com o Administrador.",
                    parse_mode="HTML",
                )
            return

    async def _process_ml_link(self, url: str, update: Update, is_private: bool) -> bool:
        """Helper para resolver links e enviar para o canal (Se for ML)."""
        try:
            from .mercadolivre_api import fetch_ml_item
            import httpx
            import re
            
            # Resolve shortened links if it seems shortened or belongs to ML
            redirect_url = url
            if any(x in url for x in ["/sec/", "mlb.ml", "bit.ly", "tinyurl"]):
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.head(url, follow_redirects=True)
                    redirect_url = str(resp.url)
                    
            if "mercadolivre.com" not in redirect_url and "mlb.ml" not in redirect_url:
                # Não é um link ML mesmo após redirect
                return False

            # Extrai ID do Mercado Livre
            match = re.search(r'MLB-?(\d+)', redirect_url, re.IGNORECASE)
            if match:
                mlb_id = match.group(1)
                
                if is_private:
                    # Envia status
                    await update.message.reply_text("🔄 Processando link do Mercado Livre...", parse_mode="HTML")
                
                product = await fetch_ml_item(mlb_id)
                if product:
                    # Enviamos para o canal automaticamente
                    from ..utils.telegram_settings_manager import telegram_settings
                    chat_id = telegram_settings.get_group_chat_id() or telegram_settings.get_channel_id()
                    if chat_id:
                        success = await self.send_product_to_channel(chat_id, product)
                        if success and is_private:
                            await update.message.reply_text(
                                "✅ <b>MÁQUINA DE OFERTAS!</b>\nO produto do Mercado Livre foi gerado com seu link de afiliado e enviado para o canal/grupo com sucesso!",
                                parse_mode="HTML",
                                disable_web_page_preview=True
                            )
                            return True
                else:
                    if is_private:
                        await update.message.reply_text("❌ Falha ao obter dados do produto no Mercado Livre. Verifique se o produto está ativo.", parse_mode="HTML")
                    return True
                    
        except Exception as e:
            logger.error(f"[TELEGRAM ML Bot] Erro processando link: {e}")
            
        return False

        # 3. Caso contrário, resposta padrão educada (Apenas se for no privado)
        if is_private:
            await update.message.reply_text(
                f"🤔 <b>Não entendi essa mensagem, {user_name}.</b>\n\nMas não se preocupe! Você pode usar o menu de comandos ou digitar /help para eu te mostrar o caminho das ofertas! ✨",
                parse_mode="HTML"
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
        elif data.startswith("shopee_filter_"):
            parts = data.replace("shopee_filter_", "").split("|")
            filter_type = parts[0]
            keyword = parts[1] if len(parts) > 1 else ""

            filter_labels = {
                "sales": "🏆 Mais Vendidos",
                "price": "💰 Menor Preço",
                "rating": "⭐ Melhor Avaliação",
            }
            filter_name = filter_labels.get(filter_type, "Shopee")
            msg = await update.callback_query.message.reply_text(
                f"⏳ Buscando <b>{keyword}</b> — {filter_name}...", parse_mode="HTML"
            )

            try:
                import asyncio
                from ..handlers.shopee_api import create_shopee_client

                client = create_shopee_client()

                sort_type_map = {"sales": 2, "price": 4, "rating": 1}
                sort_type = sort_type_map.get(filter_type, 1)

                async with client:
                    result = await client.get_products(keyword=keyword, sort_type=sort_type, limit=10)

                nodes = result.get("nodes", [])

                # Para rating: ordena client-side por avaliação decrescente
                if filter_type == "rating" and nodes:
                    nodes.sort(key=lambda n: float(n.get("ratingStar") or 0), reverse=True)

                top_nodes = nodes[:3]

                if top_nodes:
                    await msg.delete()
                    for node in top_nodes:
                        product = self._map_shopee_node_to_product(node)
                        message = self._format_product_message(product)
                        await self._send_formatted_product_reply(update, product, message, allow_mirror=False)
                        await asyncio.sleep(0.5)
                else:
                    await msg.edit_text("😕 Nenhum resultado encontrado com este filtro.")
            except Exception as e:
                logger.error(f"Erro no filtro shopee: {e}")
                await update.callback_query.message.reply_text("❌ Serviço indisponível no momento.")

    # ==================== MÉTODOS UTILITÁRIOS ====================

    def _build_product_reply_markup(self, product: Dict[str, Any]) -> InlineKeyboardMarkup:
        """Constrói um botão Inline com Link para Comprar"""
        offer_link = product.get('short_link') or product.get('affiliate_link') or "https://afiliado.top"
        keyboard = [[InlineKeyboardButton("🛒 COMPRAR AGORA", url=offer_link)]]
        return InlineKeyboardMarkup(keyboard)

    async def _send_formatted_product_reply(
        self,
        update: Update,
        product: Dict[str, Any],
        message: str,
        allow_mirror: bool = False,
    ):
        """Helper para enviar o produto no chat do bot com foto (se houver) e botões.

        Args:
            allow_mirror: Se True e o chat for privado, espelha no grupo quando
                          desconto >= 40%. Use False para busca, hoje, top — que
                          devem ficar privados. Use True apenas para /promo.
        """
        markup = self._build_product_reply_markup(product)
        image_url = product.get('image_url')
        discount = product.get("discount_percentage", 0)
        is_private = update.effective_chat.type == "private"

        async def send_msg(chat_id, repl_markup=markup):
            try:
                if image_url:
                    return await self.application.bot.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=message,
                        parse_mode="HTML",
                        reply_markup=repl_markup
                    )
                else:
                    return await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="HTML",
                        disable_web_page_preview=False,
                        reply_markup=repl_markup
                    )
            except Exception as e:
                logger.error(f"[TELEGRAM] Erro ao enviar mensagem para {chat_id}: {e}")
                return None

        # 1. Envia para o chat atual (Privado ou Grupo)
        await send_msg(update.effective_chat.id)

        # 2. ESPELHAMENTO INTELIGENTE — apenas quando allow_mirror=True
        # Evita que buscas privadas dos usuários apareçam no grupo sem permissão.
        # Somente /promo passa allow_mirror=True.
        if allow_mirror and is_private and discount and discount >= 40:
            from ..utils.telegram_settings_manager import telegram_settings
            group_id = telegram_settings.get_group_chat_id()

            if group_id:
                user_name = update.effective_user.first_name
                mirror_header = (
                    f"🔥 <b>MÁQUINA DE ACHADINHOS!</b>\n"
                    f"🏆 <i>{user_name} garimpou essa oferta VIP no nosso bot!</i>\n\n"
                )
                mirror_message = mirror_header + message

                # Envia versão com cabeçalho de prova social para o grupo
                async def send_mirror(chat_id, repl_markup=markup):
                    try:
                        if image_url:
                            return await self.application.bot.send_photo(
                                chat_id=chat_id,
                                photo=image_url,
                                caption=mirror_message,
                                parse_mode="HTML",
                                reply_markup=repl_markup,
                            )
                        else:
                            return await self.application.bot.send_message(
                                chat_id=chat_id,
                                text=mirror_message,
                                parse_mode="HTML",
                                disable_web_page_preview=False,
                                reply_markup=repl_markup,
                            )
                    except Exception as e:
                        logger.error(f"[TELEGRAM Mirror] Erro ao espelhar no grupo {chat_id}: {e}")
                        return None

                await send_mirror(group_id)
                logger.info(f"[Bot] Oferta {discount}% OFF espelhada no grupo {group_id} via /promo")

    def _format_product_message(
        self, product: Dict[str, Any], highlight: bool = False
    ) -> str:
        """AIDA + SEO + CTO: Formatação de alta conversão para o Telegram"""

        store = product.get("store", "shopee").lower()
        emoji = STORE_EMOJIS.get(store, "🏪")
        store_name = store.replace("_", " ").title()

        price = product.get("current_price", 0)
        original_price = product.get("original_price")
        discount = product.get("discount_percentage", 0)
        
        product_name = product.get("name", "Produto")
        offer_link = product.get('short_link') or product.get('affiliate_link') or "https://afiliado.top"

        # ========== A (Attention): Headline impactante com SEO ==========
        if discount and discount >= 40:
            headline = f"🚨 <b>RELÂMPAGO: {int(discount)}% OFF EM {store_name.upper()}!</b>\n\n"
        elif highlight:
            headline = f"⚡ <b>IMPERDÍVEL: SELECIONADO PARA VOCÊ!</b>\n\n"
        else:
            headline = f"🔥 <b>ACHADINHO {store_name.upper()} DETECTADO!</b>\n\n"

        # ========== I (Interest): Detalhes do Produto e Benefício ==========
        interest = f"📦 <b><a href='{offer_link}'>{product_name}</a></b>\n\n"

        # ========== D (Desire): Comparação de Preço e Social Proof ==========
        desire = ""
        if original_price and original_price > price:
            desire += f"❌ <s>De: R$ {original_price:.2f}</s>\n"
        
        if price > 0:
            desire += f"🔥 <b>POR APENAS: R$ {price:.2f}</b> 😱\n"
        else:
            desire += f"💰 <b>Consulte o super preço no site!</b>\n"

        rating = product.get("rating")
        review_count = product.get("review_count", 0)
        if rating and rating > 0:
            desire += f"⭐ Avaliação: {rating}/5"
            if review_count > 0:
                desire += f" ({review_count:,}+ vendas)"
            desire += "\n"
        
        desire += "\n"

        # ========== A (Action / CTO): Call to Order Direto no Texto ==========
        action = f"🛒 <b>COMPRE AQUI COM SEGURANÇA:</b>\n"
        action += f"👉 <b><a href='{offer_link}'>CLIQUE PARA GARANTIR O SEU</a></b>\n\n"
        action += "⚠️ <i>Atenção: Os preços podem subir a qualquer momento!</i>"

        # Adiciona cupom se existir
        coupon = product.get("coupon_code")
        if coupon:
            action += f"\n\n🎫 <b>CUPOM:</b> <code>{coupon}</code>"

        # ========== SEO Tags (Hashtags Relevantes) ==========
        category = product.get("category", "")
        tags = [store_name.replace(" ", ""), "Oferta", "Cupom", "Desconto"]
        if category:
            tags.append(category.replace(" ", ""))
        
        meta = "\n\n" + " ".join([f"#{tag}" for tag in tags[:5]])

        message = headline + interest + desire + action + meta
        return message

    async def send_product_to_channel(
        self, chat_id: Optional[str], product: Dict[str, Any]
    ):
        """Envia produto para um canal/grupo utilizando botão inline e imagem"""
        try:
            # Garante que temos um token
            if not self.token:
                self.token = telegram_settings.get_bot_token()

            if not self.token:
                logger.error(
                    "[TELEGRAM] Impossível enviar mensagem: Token não configurado"
                )
                return False

            # Se chat_id não informado, tenta pegar do banco
            if not chat_id:
                chat_id = telegram_settings.get_group_chat_id()

            if not chat_id:
                logger.error(
                    "[TELEGRAM] Impossível enviar mensagem: Chat ID não configurado"
                )
                return False

            bot = self.application.bot if self.application else Bot(self.token)

            message = self._format_product_message(product)
            markup = self._build_product_reply_markup(product)
            image_url = product.get('image_url')

            if image_url:
                try:
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=message,
                        parse_mode="HTML",
                        reply_markup=markup,
                    )
                except Exception as e:
                    logger.warning(f"[TELEGRAM] Erro no send_photo do canal, tentando texto de fallback: {e}")
                    await bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="HTML",
                        disable_web_page_preview=False,
                        reply_markup=markup,
                    )
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML",
                    disable_web_page_preview=False,
                    reply_markup=markup,
                )

            # Atualiza estatísticas
            await self.supabase.increment_product_stats(
                product["id"], "telegram_send_count"
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
