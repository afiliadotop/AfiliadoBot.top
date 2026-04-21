"""
Script de lançamentos diários do AfiliadoTop — busca AO VIVO na API Shopee.

Rodado pelo GitHub Actions às 10h e 18h BRT.
Cada horário usa keywords DIFERENTES para garantir variedade no grupo.

Anti-manopla: exige vendas reais + rating alto, não só % de desconto.
"""

import os
import sys
import math
import asyncio
import hashlib
from datetime import datetime, timezone
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1002499912192")

if not TELEGRAM_BOT_TOKEN:
    print("[CRÍTICO] TELEGRAM_BOT_TOKEN não encontrado!")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# ROTAÇÃO DE KEYWORDS — cada horário tem categorias diferentes
# Garante que 10h e 18h nunca postem os mesmos produtos
# ──────────────────────────────────────────────────────────────

MORNING_KEYWORDS = [
    "fone bluetooth",
    "smartwatch",
    "carregador rápido",
    "tênis esportivo",
    "mochila",
    "kindle livro",
    "câmera ação",
]

EVENING_KEYWORDS = [
    "perfume importado",
    "panela air fryer",
    "camiseta",
    "suplemento whey",
    "jogo console",
    "calçado feminino",
    "mouse gamer",
]


def pick_keyword(keywords: list) -> str:
    """Seleciona keyword baseado no dia do mês para rotação automática."""
    day = datetime.now().day
    return keywords[day % len(keywords)]


def is_morning_slot() -> bool:
    """Retorna True se estamos no slot da manhã (antes das 15h UTC = 12h BRT)."""
    return datetime.now(timezone.utc).hour < 15


def real_discount_score(node: dict) -> float:
    """
    Score anti-manopla: penaliza produtos com poucas vendas.
    Vendedores que inflam preço têm poucas vendas reais (compradores percebem).
    score = desconto × log(vendas + 1)
    """
    discount = float(node.get("priceDiscountRate", 0))
    sales = int(node.get("sales") or 0)
    return discount * math.log(sales + 1)


def format_message(node: dict, keyword: str) -> str:
    """Formata mensagem AIDA com HTML para o canal."""
    name = node.get("itemName", "Produto Shopee")[:80]
    price = float(node.get("priceMin", 0)) / 100_000
    original = float(node.get("priceBeforeDiscount", 0)) / 100_000
    discount = int(node.get("priceDiscountRate", 0))
    sales = int(node.get("sales") or 0)
    rating = float(node.get("ratingStar") or 0)
    link = node.get("offerLink") or node.get("itemUrl", "https://shopee.com.br")
    short = node.get("shortLink") or link

    # Headline
    if discount >= 40:
        headline = f"🚨 <b>RELÂMPAGO: {discount}% OFF REAL!</b>"
    elif discount >= 20:
        headline = f"🔥 <b>OFERTA VERIFICADA: {discount}% OFF</b>"
    else:
        headline = f"✨ <b>ACHADINHO VALIDADO SHOPEE</b>"

    msg = f"{headline}\n\n"
    msg += f"📦 <b><a href='{short}'>{name}</a></b>\n\n"

    if original > price > 0:
        savings = original - price
        msg += f"❌ <s>De R$ {original:.2f}</s>\n"
        msg += f"🔥 <b>POR APENAS R$ {price:.2f}</b> 😱\n"
        msg += f"💸 <b>Economia: R$ {savings:.2f}</b>\n"
    elif price > 0:
        msg += f"💰 <b>R$ {price:.2f}</b>\n"

    if rating > 0:
        msg += f"⭐ {rating}/5"
        if sales > 0:
            msg += f" · {sales:,} vendidos"
        msg += "\n"

    msg += "\n"
    msg += f"✅ <i>Desconto real verificado — {sales:,} compradores confirmam o preço!</i>\n\n"
    msg += f"🛒 <b>COMPRE AGORA:</b>\n"
    msg += f"👉 <b><a href='{short}'>CLIQUE PARA GARANTIR</a></b>\n\n"
    msg += f"⚠️ <i>Preço pode subir a qualquer momento!</i>\n\n"
    msg += f"#Shopee #Oferta{discount}OFF #Achadinho #AfiliadoTop"

    return msg


async def fetch_live_products(keyword: str) -> list:
    """Busca produtos ao vivo na API Shopee com filtro anti-manopla."""
    from afiliadohub.api.handlers.shopee_api import create_shopee_client

    client = create_shopee_client()
    candidates = []

    async with client:
        # Tenta primeiro com key_seller + AMS (mais confiável)
        result = await client.get_products(
            keyword=keyword,
            is_key_seller=True,
            is_ams_offer=True,
            sort_type=2,   # ITEM_SOLD_DESC
            limit=30,
        )
        nodes = result.get("nodes", []) if result else []

        # Filtro anti-manopla principal
        filtered = [
            n for n in nodes
            if float(n.get("priceDiscountRate", 0)) >= 15
            and int(n.get("sales") or 0) >= 20
            and float(n.get("ratingStar") or 0) >= 4.3
        ]

        if filtered:
            candidates = filtered
        else:
            # Fallback: relaxa filtros mas mantém qualidade mínima
            result2 = await client.get_products(
                keyword=keyword,
                sort_type=2,
                limit=20,
            )
            nodes2 = result2.get("nodes", []) if result2 else []
            candidates = [
                n for n in nodes2
                if float(n.get("priceDiscountRate", 0)) >= 5
                and int(n.get("sales") or 0) >= 5
                and float(n.get("ratingStar") or 0) >= 4.0
            ] or nodes2[:5]

    # Ordena pelo score anti-manopla
    candidates.sort(key=real_discount_score, reverse=True)
    return candidates


async def send_daily_promotions():
    """Lança as promoções do dia diretamente da API Shopee ao vivo."""
    bot = Bot(TELEGRAM_BOT_TOKEN)
    now_utc = datetime.now(timezone.utc)

    # Determina slot e keyword do lançamento
    morning = is_morning_slot()
    keywords_pool = MORNING_KEYWORDS if morning else EVENING_KEYWORDS
    keyword = pick_keyword(keywords_pool)
    slot_label = "🌅 Lançamento da Manhã" if morning else "🌆 Lançamento da Tarde"

    print(f"[{now_utc.strftime('%Y-%m-%d %H:%M UTC')}] {slot_label}")
    print(f"Keyword do dia: '{keyword}'")
    print("-" * 50)

    try:
        nodes = await fetch_live_products(keyword)
    except Exception as e:
        print(f"[ERRO] Falha ao buscar produtos da Shopee: {e}")
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=f"⚠️ Erro temporário na Shopee API. Tentando novamente no próximo lançamento.",
        )
        return

    if not nodes:
        print("[AVISO] Nenhum produto encontrado com os filtros de qualidade.")
        return

    # Envia até 3 produtos
    top = nodes[:3]
    print(f"Enviando {len(top)} produto(s) para o canal...\n")

    for idx, node in enumerate(top, 1):
        caption = format_message(node, keyword)
        image_url = node.get("imageUrl") or node.get("image")
        link = node.get("shortLink") or node.get("offerLink") or "https://shopee.com.br"
        name = node.get("itemName", "Ver Produto")[:30]
        discount = int(node.get("priceDiscountRate", 0))

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🛒 COMPRAR COM {discount}% OFF", url=link)],
        ])

        try:
            if image_url:
                await bot.send_photo(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    photo=image_url,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
                print(f"  [{idx}/{len(top)}] ✅ FOTO enviada: {name}...")
            else:
                await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=caption,
                    parse_mode="HTML",
                    disable_web_page_preview=False,
                    reply_markup=keyboard,
                )
                print(f"  [{idx}/{len(top)}] ✅ TEXTO enviado: {name}...")

            if idx < len(top):
                await asyncio.sleep(4)  # Pausa entre produtos

        except Exception as e:
            print(f"  [{idx}/{len(top)}] ❌ Erro ao enviar: {e}")

    print(f"\n✅ Lançamento concluído! {len(top)} produtos enviados.")
    print(f"Próxima keyword disponível: '{pick_keyword(keywords_pool)}'")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(send_daily_promotions())
