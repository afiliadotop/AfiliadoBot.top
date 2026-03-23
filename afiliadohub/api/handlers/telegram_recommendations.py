import random
from typing import Dict, List, Optional
from datetime import datetime


class TelegramRecommendationEngine:
    def __init__(self):
        self.user_preferences = {}
        self.recommendation_cache = {}

    async def get_personalized_recommendation(
        self, user_id: int, chat_history: List[Dict]
    ) -> Optional[Dict]:
        """Gera recomendação personalizada baseada no histórico"""
        try:
            from api.utils.supabase_client import get_supabase_manager

            supabase = get_supabase_manager()

            # Analisa histórico para preferências
            preferences = self._analyze_user_preferences(chat_history)

            # Busca produtos que correspondam às preferências
            query = supabase.client.table("products").select("*").eq("is_active", True)

            # Aplica filtros baseados nas preferências
            if preferences.get("favorite_store"):
                query = query.eq("store", preferences["favorite_store"])

            if preferences.get("preferred_category"):
                query = query.ilike(
                    "category", f"%{preferences['preferred_category']}%"
                )

            if preferences.get("price_range"):
                min_price, max_price = preferences["price_range"]
                query = query.gte("current_price", min_price).lte(
                    "current_price", max_price
                )

            # Ordena por relevância
            if preferences.get("prefers_discounts", False):
                query = query.order("discount_percentage", desc=True)
            else:
                query = query.order("created_at", desc=True)

            response = query.limit(5).execute()

            products = response.data if response.data else []

            if products:
                # Escolhe produto baseado em algoritmo de recomendação
                product = self._select_best_product(products, preferences)
                return product

            return None

        except Exception as e:
            print(f"Erro na recomendação: {e}")
            return None

    def _analyze_user_preferences(self, chat_history: List[Dict]) -> Dict:
        """Analisa histórico para extrair preferências do usuário"""
        preferences = {
            "favorite_store": None,
            "preferred_category": None,
            "price_range": (0, 1000),
            "prefers_discounts": False,
            "clicked_products": [],
            "search_terms": [],
        }

        store_counts = {}
        category_counts = {}
        price_sum = 0
        price_count = 0

        for message in chat_history[-50:]:  # Últimas 50 mensagens
            if message.get("type") == "command":
                cmd = message.get("text", "")

                if cmd.startswith("/shopee"):
                    store_counts["shopee"] = store_counts.get("shopee", 0) + 1
                elif cmd.startswith("/aliexpress"):
                    store_counts["aliexpress"] = store_counts.get("aliexpress", 0) + 1
                elif cmd.startswith("/buscar"):
                    term = cmd.replace("/buscar", "").strip()
                    if term:
                        preferences["search_terms"].append(term)

            elif message.get("type") == "product_click":
                product_data = message.get("product", {})

                # Conta lojas
                store = product_data.get("store")
                if store:
                    store_counts[store] = store_counts.get(store, 0) + 1

                # Conta categorias
                category = product_data.get("category")
                if category:
                    category_counts[category] = category_counts.get(category, 0) + 1

                # Preços
                price = product_data.get("current_price")
                if price:
                    price_sum += price
                    price_count += 1

                preferences["clicked_products"].append(product_data.get("id"))

        # Determina loja favorita
        if store_counts:
            preferences["favorite_store"] = max(store_counts, key=store_counts.get)

        # Determina categoria favorita
        if category_counts:
            preferences["preferred_category"] = max(
                category_counts, key=category_counts.get
            )

        # Calcula faixa de preço preferida
        if price_count > 0:
            avg_price = price_sum / price_count
            preferences["price_range"] = (avg_price * 0.5, avg_price * 1.5)

        # Verifica se usuário prefere descontos
        discount_clicks = sum(
            1
            for p in preferences["clicked_products"]
            if p.get("discount_percentage", 0) > 0
        )
        if discount_clicks > len(preferences["clicked_products"]) * 0.7:
            preferences["prefers_discounts"] = True

        return preferences

    def _select_best_product(self, products: List[Dict], preferences: Dict) -> Dict:
        """Seleciona o melhor produto baseado nas preferências"""
        scored_products = []

        for product in products:
            score = 0

            # Pontua por loja favorita
            if product.get("store") == preferences.get("favorite_store"):
                score += 20

            # Pontua por categoria
            if (
                preferences.get("preferred_category")
                and preferences["preferred_category"].lower()
                in product.get("category", "").lower()
            ):
                score += 15

            # Pontua por desconto (se preferir)
            if (
                preferences.get("prefers_discounts", False)
                and product.get("discount_percentage", 0) > 0
            ):
                score += product.get(
                    "discount_percentage", 0
                )  # % de desconto como pontos

            # Pontua por preço dentro da faixa
            price = product.get("current_price", 0)
            min_price, max_price = preferences.get("price_range", (0, 1000))
            if min_price <= price <= max_price:
                score += 10

            # Pontua por novidade
            created_at = product.get("created_at")
            if created_at:
                days_old = (
                    datetime.now()
                    - datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                ).days
                if days_old < 7:  # Produtos recentes
                    score += 30 - days_old * 2

            scored_products.append((score, product))

        # Ordena por score e pega o melhor
        scored_products.sort(reverse=True, key=lambda x: x[0])

        return scored_products[0][1] if scored_products else products[0]

    async def send_recommendation_message(
        self, user_id: int, product: Dict, bot
    ) -> bool:
        """Envia mensagem de recomendação personalizada"""
        try:
            # Formata mensagem especial
            message = self._format_recommendation_message(product)

            # Cria teclado inline
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔗 Ver Produto", url=product.get("affiliate_link")
                    ),
                    InlineKeyboardButton(
                        "⭐ Salvar", callback_data=f"save_{product['id']}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🔄 Outra Sugestão",
                        callback_data=f"recommend_another_{user_id}",
                    ),
                    InlineKeyboardButton(
                        "🚫 Não Gostei", callback_data=f"dislike_{product['id']}"
                    ),
                ],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Envia mensagem
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=False,
            )

            # Registra recomendação
            await self._log_recommendation(user_id, product["id"])

            return True

        except Exception as e:
            print(f"Erro ao enviar recomendação: {e}")
            return False

    def _format_recommendation_message(self, product: Dict) -> str:
        """Formata mensagem de recomendação especial"""
        store_emojis = {
            "shopee": "🛍️",
            "aliexpress": "📦",
            "amazon": "📚",
            "temu": "🎯",
            "shein": "👗",
            "magalu": "🏬",
            "mercado_livre": "🚀",
        }

        emoji = store_emojis.get(product.get("store"), "🎁")
        store_name = product.get("store", "").replace("_", " ").title()

        price = product.get("current_price", 0)
        original_price = product.get("original_price")
        discount = product.get("discount_percentage")

        price_text = (
            f"R$ {price:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        )

        if original_price and discount:
            original_text = (
                f"R$ {original_price:,.2f}".replace(",", "v")
                .replace(".", ",")
                .replace("v", ".")
            )
            price_text = f"~~{original_text}~~ → {price_text} ({discount}% OFF)"

        # Mensagem personalizada
        message = f"""
{emoji} <b>RECOMENDAÇÃO ESPECIAL PARA VOCÊ!</b>

🎯 <b>Pensei que você iria gostar deste produto:</b>

🛍️ <b>{product.get('name', 'Produto')}</b>

💰 <b>Preço:</b> {price_text}
🏪 <b>Loja:</b> {store_name}
📦 <b>Categoria:</b> {product.get('category', 'Não informada')}

⭐ <b>Avaliação:</b> {product.get('rating', 'N/A')}/5 
👥 <b>Avaliações:</b> {product.get('review_count', 0)}

🎁 <b>Por que recomendamos:</b>
• Preço competitivo
• Alta avaliação dos clientes
• Desconto especial
• Entrega rápida

🔗 <a href="{product.get('affiliate_link')}">VER PRODUTO AGORA</a>
        """

        # Adiciona cupom se existir
        coupon = product.get("coupon_code")
        if coupon:
            message += f"\n\n🎫 <b>CUPOM EXCLUSIVO:</b> <code>{coupon}</code>"

        return message.strip()

    async def _log_recommendation(self, user_id: int, product_id: int):
        """Registra recomendação enviada"""
        try:
            from api.utils.supabase_client import get_supabase_manager

            supabase = get_supabase_manager()

            log_data = {
                "user_id": str(user_id),
                "product_id": product_id,
                "sent_at": datetime.now().isoformat(),
                "opened": False,
                "clicked": False,
            }

            supabase.client.table("recommendation_logs").insert(log_data).execute()

        except Exception as e:
            print(f"Erro ao logar recomendação: {e}")


# Integração com o handler principal do Telegram
async def handle_recommendation_command(update, context):
    """Handler para comando /recomendar"""
    user_id = update.effective_user.id

    # Cria engine de recomendação
    engine = TelegramRecommendationEngine()

    # Busca histórico do usuário (simplificado)
    # Na prática, você buscaria do banco de dados
    chat_history = []  # Placeholder

    # Gera recomendação
    product = await engine.get_personalized_recommendation(user_id, chat_history)

    if product:
        await engine.send_recommendation_message(user_id, product, context.bot)
    else:
        await update.message.reply_text(
            "😊 Estou aprendendo suas preferências! "
            "Continue usando o bot e em breve farei recomendações personalizadas para você."
        )
