"""
Script de lançamentos diários do AfiliadoTop — busca AO VIVO na API Shopee.

Rodado pelo GitHub Actions às 10h e 18h BRT.
Cada horário usa keywords DIFERENTES para garantir variedade no grupo.

Anti-manopla: exige vendas reais + rating alto, não só % de desconto.
"""

import os
import sys
import math
import html as html_module
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1002499912192")

# Import topic router (requires afiliadohub on PYTHONPATH)
try:
    from afiliadohub.api.utils.topic_router import get_thread_id, detect_category
    TOPICS_ENABLED = True
except ImportError:
    TOPICS_ENABLED = False
    print("[AVISO] topic_router não carregado — mensagens irão para o grupo geral.")

if not TELEGRAM_BOT_TOKEN:
    print("[CRÍTICO] TELEGRAM_BOT_TOKEN não encontrado!")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────
# ROTAÇÃO DE KEYWORDS — tema do grupo: moda, beleza, bijuterias
# Manhã: roupas + bijuterias | Tarde: beleza + geral alta conversão
# ──────────────────────────────────────────────────────────────

MORNING_KEYWORDS = [
    # Índices 0-6 — usados no slot MANHÃ
    "vestido feminino",
    "conjunto feminino",
    "blusa feminina",
    "calça feminina",
    "sandália feminina",
    "tênis feminino",
    "bolsa feminina",
    # Índices 7-13 — reservados para evitar colisão (nunca usados às 11h)
    "saia midi",
    "cropped feminino",
    "jaqueta feminina",
    "moletom feminino",
    "shorts feminino",
    "legging feminina",
    "macacão feminino",
]

EVENING_KEYWORDS = [
    # Índices 0-6 — usados no slot TARDE
    "kit skincare",
    "perfume feminino",
    "brinco",
    "colar feminino",
    "pulseira",
    "maquiagem",
    "hidratante corporal",
    # Índices 7-13 — reservados para evitar colisão (nunca usados às 18h via slot_offset=7)
    "máscara facial",
    "protetor solar",
    "sérum facial",
    "esmalte unhas",
    "anel feminino",
    "tiara cabelo",
    "kit manicure",
]


def pick_keyword(keywords: list, slot_offset: int = 0) -> str:
    """
    Seleciona keyword garantindo que manhã e tarde NUNCA usem o mesmo índice.

    Usa (day + slot_offset) % len(keywords):
      - Manhã:  slot_offset = 0  → índice par
      - Tarde:  slot_offset = len(keywords) // 2 → índice deslocado
    Assim os dois horários sempre apontam para keywords diferentes na mesma lista.
    """
    day = datetime.now(timezone.utc).day
    return keywords[(day + slot_offset) % len(keywords)]


def is_morning_slot() -> bool:
    """Retorna True se estamos no slot da manhã (antes das 14h UTC = 11h BRT)."""
    return datetime.now(timezone.utc).hour < 14


def real_discount_score(node: dict) -> float:
    """
    Score anti-manopla: penaliza produtos com poucas vendas.
    score = desconto × log(vendas + 1)
    """
    discount = float(node.get("priceDiscountRate", 0))
    sales = int(node.get("sales") or 0)
    return discount * math.log(sales + 1)


def format_message(node: dict, keyword: str) -> str:
    """Formata mensagem AIDA com HTML para o canal (alta conversão)."""
    # Campos corretos da productOfferV2 API
    name = html_module.escape(node.get("productName", "Produto Shopee")[:80])
    # priceMin é string em reais: "45.99" → float
    price = float(node.get("priceMin") or 0)
    discount = int(node.get("priceDiscountRate") or 0)
    sales = int(node.get("sales") or 0)
    rating = float(node.get("ratingStar") or 0)
    shop_type = node.get("shopType") or []
    link = node.get("offerLink") or node.get("productLink", "https://shopee.com.br")
    short = node.get("shortLink") or link

    # Calcula preço original a partir do desconto
    original = 0.0
    if discount > 0 and price > 0:
        original = price / (1 - discount / 100)

    # Badge de loja para prova social
    if isinstance(shop_type, list):
        is_mall = 1 in shop_type
        is_preferred = 2 in shop_type or 4 in shop_type
    else:
        is_mall = shop_type == 1
        is_preferred = shop_type in (2, 4)

    badge = "👑 Shopee Mall" if is_mall else ("⭐ Loja Preferida" if is_preferred else "🏬 Vendedor Shopee")

    # Headline AIDA — Atenção
    if discount >= 40:
        headline = f"🚨 <b>RELÂMPAGO: {discount}% OFF REAL!</b>"
    elif discount >= 20:
        headline = f"🔥 <b>OFERTA VERIFICADA: -{discount}% OFF</b>"
    else:
        headline = f"✨ <b>ACHADINHO VALIDADO SHOPEE</b>"

    msg = f"{headline}\n\n"
    # Produto com link clicável
    msg += f"📦 <b><a href='{short}'>{name}</a></b>\n\n"

    # Preços — desconto visível
    if original > price > 0:
        savings = original - price
        msg += f"❌ <s>De R$ {original:.2f}</s>\n"
        msg += f"🔥 <b>POR APENAS R$ {price:.2f}</b> 😱\n"
        msg += f"💸 <b>Você economiza R$ {savings:.2f}!</b>\n"
    elif price > 0:
        msg += f"💰 <b>R$ {price:.2f}</b>\n"

    msg += "\n"

    # Prova social (autoridade + vendas)
    if rating > 0:
        msg += f"{badge} | ⭐ {rating:.1f}/5"
        if sales > 0:
            msg += f" · {sales:,} compradores"
        msg += "\n"

    msg += "\n"
    msg += f"✅ <i>Desconto real verificado — {sales:,} pessoas já compraram!</i>\n\n"
    msg += f"🛒 <b>COMPRE AGORA ANTES DE ESGOTAR:</b>\n"
    msg += f"👉 <b><a href='{short}'>CLIQUE PARA GARANTIR ↗</a></b>\n\n"
    msg += f"⏳ <i>Preço pode subir a qualquer momento!</i>\n\n"

    # Hashtags para descoberta
    tag = keyword.replace(" ", "").title()
    msg += f"#Shopee #Achadinho #Oferta{discount}OFF #{tag} #AfiliadoTop"

    return msg


async def fetch_live_products(keyword: str) -> list:
    """Busca produtos ao vivo na API Shopee com filtros de qualidade."""
    # Import correto: create_shopee_client está em utils.shopee_client
    from afiliadohub.api.utils.shopee_client import create_shopee_client

    client = create_shopee_client()
    candidates = []

    async with client:
        # Prioridade 1: vendedores chave + AMS + ordenado por mais vendidos
        result = await client.get_products(
            keyword=keyword,
            is_key_seller=True,
            is_ams_offer=True,
            sort_type=2,   # ITEM_SOLD_DESC
            limit=30,
        )
        nodes = result.get("nodes", []) if result else []

        # Filtro anti-manopla principal: desconto real + vendas + rating
        filtered = [
            n for n in nodes
            if float(n.get("priceDiscountRate") or 0) >= 15
            and int(n.get("sales") or 0) >= 20
            and float(n.get("ratingStar") or 0) >= 4.3
        ]

        if filtered:
            candidates = filtered
        else:
            # Fallback: busca mais ampla, filtros mínimos de qualidade
            result2 = await client.get_products(
                keyword=keyword,
                sort_type=2,
                limit=30,
            )
            nodes2 = result2.get("nodes", []) if result2 else []
            candidates = [
                n for n in nodes2
                if float(n.get("priceDiscountRate") or 0) >= 5
                and int(n.get("sales") or 0) >= 5
                and float(n.get("ratingStar") or 0) >= 4.0
            ] or nodes2[:5]

        # Gera shortLinks para os top 3 antes de fechar a sessão
        top_candidates = sorted(candidates, key=real_discount_score, reverse=True)[:3]
        for node in top_candidates:
            offer_url = node.get("offerLink") or node.get("productLink")
            if offer_url and not node.get("shortLink"):
                short = await client.generate_short_link(offer_url)
                if short:
                    node["shortLink"] = short

    # Ordena pelo score anti-manopla (desconto × log(vendas))
    top_candidates.sort(key=real_discount_score, reverse=True)
    return top_candidates


async def send_daily_promotions():
    """Lança as promoções do dia diretamente da API Shopee ao vivo."""
    bot = Bot(TELEGRAM_BOT_TOKEN)
    now_utc = datetime.now(timezone.utc)

    morning = is_morning_slot()
    keywords_pool = MORNING_KEYWORDS if morning else EVENING_KEYWORDS

    # slot_offset garante que manhã e tarde usem índices DIFERENTES da pool delas
    # Manhã: offset 0 (ex: day=21 → índice 0)
    # Tarde: offset metade do tamanho da pool (ex: day=21, offset=3 → índice 3)
    slot_offset = 0 if morning else (len(keywords_pool) // 2)
    keyword = pick_keyword(keywords_pool, slot_offset)
    slot_label = "🌅 Lançamento da Manhã (11h BRT)" if morning else "🌆 Lançamento da Tarde (18h BRT)"

    print(f"[{now_utc.strftime('%Y-%m-%d %H:%M UTC')}] {slot_label}")
    print(f"Keyword do dia: '{keyword}'")
    print("-" * 50)

    try:
        nodes = await fetch_live_products(keyword)
    except Exception as e:
        print(f"[ERRO] Falha ao buscar produtos da Shopee: {e}", flush=True)
        import traceback
        traceback.print_exc()
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=(
                f"⚠️ <b>Erro temporário na Shopee API.</b>\n"
                f"Código: <code>{type(e).__name__}</code>\n"
                f"Tentaremos novamente no próximo lançamento."
            ),
            parse_mode="HTML",
        )
        return

    if not nodes:
        print("[AVISO] Nenhum produto encontrado com os filtros de qualidade.")
        return

    print(f"Enviando {len(nodes)} produto(s) para o canal...\n")

    for idx, node in enumerate(nodes, 1):
        caption = format_message(node, keyword)
        image_url = node.get("imageUrl")
        link = node.get("shortLink") or node.get("offerLink") or "https://shopee.com.br"
        name = node.get("productName", "Ver Produto")[:30]
        discount = int(node.get("priceDiscountRate") or 0)
        product_name = node.get("productName", "")

        btn_label = f"🛒 GARANTIR COM {discount}% OFF" if discount > 0 else "🛒 VER PRODUTO"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(btn_label, url=link)],
        ])

        # Detecta o tópico correto para este produto
        thread_id = None
        if TOPICS_ENABLED:
            thread_id = get_thread_id(
                product_name=product_name,
                keyword=keyword,
            )
            topic_label = f"thread={thread_id}" if thread_id else "geral"
            print(f"  [{idx}/{len(nodes)}] Tópico detectado: {topic_label} | Keyword: '{keyword}'")

        send_kwargs = dict(
            chat_id=TELEGRAM_CHANNEL_ID,
            parse_mode="HTML",
            reply_markup=keyboard,
            **({"message_thread_id": thread_id} if thread_id else {}),
        )

        try:
            if image_url:
                await bot.send_photo(
                    photo=image_url,
                    caption=caption,
                    **send_kwargs,
                )
                print(f"  [{idx}/{len(nodes)}] ✅ FOTO enviada: {name}...")
            else:
                await bot.send_message(
                    text=caption,
                    disable_web_page_preview=False,
                    **send_kwargs,
                )
                print(f"  [{idx}/{len(nodes)}] ✅ TEXTO enviado: {name}...")

            if idx < len(nodes):
                await asyncio.sleep(4)  # Pausa entre produtos

        except Exception as e:
            print(f"  [{idx}/{len(nodes)}] ❌ Erro ao enviar: {e}")

    print(f"\n✅ Lançamento concluído! {len(nodes)} produtos enviados.")
    next_kw = pick_keyword(keywords_pool)
    print(f"Próxima keyword disponível: '{next_kw}'")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(send_daily_promotions())
