"""
Campanha Especial Shopee 6.6 — Mid-Year Sale
=============================================
5 disparos automáticos ao longo do dia 6 de junho.

Slots BRT → UTC:
  07h → 10h UTC  (slot=morning)
  10h → 13h UTC  (slot=late_morning)
  12h → 15h UTC  (slot=noon)
  16h → 19h UTC  (slot=afternoon)
  20h → 23h UTC  (slot=evening)

Cada slot busca produtos com keyword temática, roteia para o
tópico correto do grupo e usa sub_id rastreável para medir
quais horários convertem mais.

Anti-manopla: exige desconto ≥ 15%, vendas ≥ 10, rating ≥ 4.3
"""

import os
import sys
import math
import html as html_module
import asyncio
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1002499912192")

if not TELEGRAM_BOT_TOKEN:
    print("[CRÍTICO] TELEGRAM_BOT_TOKEN não encontrado!")
    sys.exit(1)

# Importa o roteador de tópicos
try:
    from afiliadohub.api.utils.topic_router import get_thread_id
    TOPICS_ENABLED = True
except ImportError:
    TOPICS_ENABLED = False
    print("[AVISO] topic_router não carregado — mensagens vão para o grupo geral.")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DOS 5 SLOTS DO DIA 6.6
# ─────────────────────────────────────────────────────────────────────────────
SLOTS = {
    "midnight": {
        "label": "🎆 Meia-noite — Abertura do 6.6 & Cupons",
        "utc_hour": 3,
        "keywords": ["kit desconto", "oferta exclusiva"],
        "topic": "cupons",
        "sub_id": "sale6600h",
        "intro": (
            "🚨 <b>O SHOPEE 6.6 COMEÇOU OFICIALMENTE!</b> 🚨\n"
            "Corra para resgatar seus cupons de Frete Grátis e 50% OFF antes que acabem!\n\n"
            "👇 <b>Clique abaixo para resgatar todos os cupons:</b>"
        ),
    },
    "morning": {
        "label": "🌅 Abertura 6.6 — Primeiras Ofertas do Dia",
        "utc_hour": 10,
        "keywords": ["presente namorada", "kit presente namorados"],
        "topic": "namorados",
        "sub_id": "sale6607h",
        "intro": (
            "💥 <b>SHOPEE 6.6 COMEÇOU!</b>\n"
            "🛍️ As maiores ofertas do meio do ano estão ao vivo agora.\n"
            "⚡ Primeiros do grupo têm vantagem — estoque limitado!"
        ),
    },
    "late_morning": {
        "label": "☀️ 6.6 — Moda em Promoção",
        "utc_hour": 13,
        "keywords": ["vestido feminino", "conjunto feminino"],
        "topic": "roupas",
        "sub_id": "sale6610h",
        "intro": (
            "👗 <b>6.6 NA MODA FEMININA!</b>\n"
            "As roupas mais vendidas da Shopee com desconto real agora.\n"
            "🔥 Selecione antes que acabe!"
        ),
    },
    "noon": {
        "label": "⭐ 6.6 — Bijuterias & Acessórios",
        "utc_hour": 15,
        "keywords": ["brinco promoção", "colar feminino desconto"],
        "topic": "bijuterias",
        "sub_id": "sale6612h",
        "intro": (
            "💎 <b>BIJUTERIAS COM PREÇO DE SALE 6.6!</b>\n"
            "Colares, brincos e pulseiras com os maiores descontos do ano.\n"
            "✨ Cada peça verificada pela nossa equipe!"
        ),
    },
    "afternoon": {
        "label": "💆 6.6 — Beleza & Skincare",
        "utc_hour": 19,
        "keywords": ["kit skincare oferta", "perfume feminino 6.6"],
        "topic": "beleza",
        "sub_id": "sale6616h",
        "intro": (
            "✨ <b>CUIDADOS FEMININOS NO 6.6!</b>\n"
            "Skincare, perfumes e beleza com desconto confirmado.\n"
            "💆 Cuide-se por muito menos hoje!"
        ),
    },
    "evening": {
        "label": "🌙 6.6 — Prime Time Namorados",
        "utc_hour": 23,
        "keywords": ["presente namorado desconto", "kit romântico sale"],
        "topic": "namorados",
        "sub_id": "sale6620h",
        "intro": (
            "💝 <b>ÚLTIMAS HORAS DO 6.6!</b>\n"
            "Dia dos Namorados chega em breve — garanta o presente hoje\n"
            "com os preços mais baixos do ano. 🎁"
        ),
    },
}


def real_score(node: dict) -> float:
    """Score anti-manopla: desconto × log(vendas). Penaliza inflação falsa."""
    d = float(node.get("priceDiscountRate", 0))
    s = int(node.get("sales") or 0)
    return d * math.log(s + 1)


def format_66_message(node: dict, sub_id: str) -> str:
    """Formata mensagem temática 6.6 com urgência e prova social."""
    name = html_module.escape(node.get("productName", "Produto Shopee")[:80])
    price = float(node.get("priceMin") or 0)
    discount = int(node.get("priceDiscountRate") or 0)
    sales = int(node.get("sales") or 0)
    rating = float(node.get("ratingStar") or 0)
    shop_type = node.get("shopType") or []
    link = node.get("shortLink") or node.get("offerLink") or "https://shopee.com.br"

    original = price / (1 - discount / 100) if discount > 0 and price > 0 else 0

    # Badge da loja
    if isinstance(shop_type, list):
        is_mall = 1 in shop_type
        is_preferred = 2 in shop_type or 4 in shop_type
    else:
        is_mall = shop_type == 1
        is_preferred = shop_type in (2, 4)
    badge = "👑 Shopee Mall" if is_mall else ("⭐ Loja Preferida" if is_preferred else "🏬 Shopee")

    # Headline por nível de desconto
    if discount >= 50:
        headline = f"🚨 <b>CHOQUE DE PREÇO 6.6: -{discount}% OFF!</b>"
    elif discount >= 30:
        headline = f"🔥 <b>6.6 SALE: {discount}% OFF VERIFICADO</b>"
    elif discount >= 15:
        headline = f"✨ <b>ACHADINHO 6.6: -{discount}% OFF</b>"
    else:
        headline = "🛍️ <b>OFERTA 6.6 SHOPEE</b>"

    msg = f"{headline}\n\n"
    msg += f"📦 <b><a href='{link}'>{name}</a></b>\n\n"

    if original > price > 0:
        savings = original - price
        msg += f"❌ <s>De R$ {original:.2f}</s>\n"
        msg += f"🔥 <b>POR APENAS R$ {price:.2f}</b> 😱\n"
        msg += f"💸 <b>Economia de R$ {savings:.2f}!</b>\n"
    elif price > 0:
        msg += f"💰 <b>R$ {price:.2f}</b>\n"

    msg += "\n"

    if rating > 0:
        msg += f"{badge} · ⭐ {rating:.1f}/5"
        if sales > 0:
            msg += f" · {sales:,} compradores"
        msg += "\n"

    msg += "\n"
    msg += f"✅ <i>Desconto real no 6.6 — {sales:,} pessoas já compraram!</i>\n\n"
    msg += "🛒 <b>GARANTA ANTES DE ACABAR:</b>\n"
    msg += f"👉 <b><a href='{link}'>COMPRAR COM {discount}% OFF ↗</a></b>\n\n"
    msg += "⏳ <i>Ofertas do 6.6 por tempo limitadíssimo!</i>\n\n"
    msg += f"#Shopee66 #Sale66 #MidYearSale #AfiliadoTop #Oferta{discount}OFF"

    return msg


async def fetch_66_products(keyword: str, sub_id: str, topic: str = "geral", limit: int = 20) -> list:
    """Busca produtos ao vivo com 4 camadas de fallback para garantir resultado."""
    from afiliadohub.api.utils.shopee_client import create_shopee_client

    FALLBACK_KW = {
        "roupas":     "vestido feminino",
        "bijuterias": "brinco feminino",
        "beleza":     "kit skincare",
        "namorados":  "presente romântico",
        "geral":      "oferta shopee",
    }

    client = create_shopee_client()

    async with client:
        # Camada 1: key sellers + AMS + filtros premium
        result = await client.get_products(
            keyword=keyword,
            is_key_seller=True,
            is_ams_offer=True,
            sort_type=2,
            limit=limit,
        )
        nodes = result.get("nodes", []) if result else []

        filtered = [
            n for n in nodes
            if float(n.get("priceDiscountRate") or 0) >= 15
            and int(n.get("sales") or 0) >= 10
            and float(n.get("ratingStar") or 0) >= 4.3
        ]

        # Camada 2: relaxa filtros (pré-sale — 6.6 ainda não começou)
        if not filtered:
            filtered = [
                n for n in nodes
                if float(n.get("priceDiscountRate") or 0) >= 5
                and float(n.get("ratingStar") or 0) >= 4.0
            ]

        # Camada 3: qualquer produto da busca, sem filtro
        if not filtered and nodes:
            filtered = sorted(nodes, key=lambda n: float(n.get("ratingStar") or 0), reverse=True)[:3]

        # Camada 4: keyword genérica do tópico
        if not filtered:
            fallback_kw = FALLBACK_KW.get(topic, "oferta shopee")
            print(f"  [FALLBACK] Tentando keyword genérica: '{fallback_kw}'")
            result2 = await client.get_products(keyword=fallback_kw, sort_type=2, limit=10)
            fb_nodes = result2.get("nodes", []) if result2 else []
            filtered = sorted(fb_nodes, key=lambda n: float(n.get("ratingStar") or 0), reverse=True)[:3]

        # Gera short links rastreáveis para o top 2
        top = sorted(filtered, key=real_score, reverse=True)[:2]
        for node in top:
            offer_url = node.get("offerLink") or node.get("productLink")
            if offer_url and not node.get("shortLink"):
                short = await client.generate_short_link(offer_url, sub_ids=[sub_id, "sale66"])
                if short:
                    node["shortLink"] = short

    return sorted(top, key=real_score, reverse=True)


def detect_current_slot() -> str:
    """Detecta qual slot executar baseado na hora UTC atual."""
    utc_hour = datetime.now(timezone.utc).hour

    # Janela de ±1h para cada slot
    for slot_name, cfg in SLOTS.items():
        target = cfg["utc_hour"]
        if abs(utc_hour - target) <= 1:
            return slot_name

    # Fallback: slot mais próximo
    closest = min(SLOTS.items(), key=lambda x: abs(
        (utc_hour if utc_hour >= 3 else utc_hour + 24) - 
        (x[1]["utc_hour"] if x[1]["utc_hour"] >= 3 else x[1]["utc_hour"] + 24)
    ))
    return closest[0]


async def send_66_slot(slot_name: str):
    """Executa um slot da campanha 6.6."""
    slot = SLOTS.get(slot_name)
    if not slot:
        print(f"[ERRO] Slot '{slot_name}' não encontrado. Disponíveis: {list(SLOTS.keys())}")
        sys.exit(1)

    bot = Bot(TELEGRAM_BOT_TOKEN)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print(f"[{now}] 🛍️ Campanha 6.6 — {slot['label']}")
    print(f"  Keywords: {slot['keywords']}")
    print(f"  Tópico: {slot['topic']} | Sub-ID: {slot['sub_id']}")
    print("-" * 60)

    # Thread ID do tópico
    thread_id = None
    if TOPICS_ENABLED:
        thread_id = get_thread_id(category=slot["topic"])
        print(f"  Thread ID: {thread_id or 'não configurado (geral)'}")

    intro_kwargs = dict(
        chat_id=TELEGRAM_CHANNEL_ID,
        text=slot["intro"],
        parse_mode="HTML",
        **( {"message_thread_id": thread_id} if thread_id else {} ),
    )
    
    # Se for midnight, gera um botão direto para a página de cupons
    if slot_name == "midnight":
        try:
            from afiliadohub.api.utils.shopee_client import create_shopee_client
            client = create_shopee_client()
            async with client:
                coupon_link = await client.generate_short_link("https://shopee.com.br/m/cupons-shopee", sub_ids=["cupons66"])
            if coupon_link:
                intro_kwargs["reply_markup"] = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎟️ RESGATAR CUPONS 6.6 AGORA!", url=coupon_link)]
                ])
        except Exception as e:
            print(f"  [AVISO] Erro ao gerar link de cupons: {e}")
    try:
        await bot.send_message(**intro_kwargs)
        await asyncio.sleep(2)
    except Exception as e:
        print(f"  [AVISO] Erro ao enviar intro: {e}")

    # Busca e envia produtos para cada keyword do slot
    sent = 0
    for keyword in slot["keywords"]:
        print(f"\n  🔍 Buscando '{keyword}'...")
        try:
            nodes = await fetch_66_products(keyword, slot["sub_id"])
        except Exception as e:
            print(f"  [ERRO] Falha na API Shopee para '{keyword}': {e}")
            continue

        if not nodes:
            print(f"  [AVISO] Nenhum produto com qualidade para '{keyword}'")
            continue

        for node in nodes:
            caption = format_66_message(node, slot["sub_id"])
            image_url = node.get("imageUrl")
            link = node.get("shortLink") or node.get("offerLink") or "https://shopee.com.br"
            name = node.get("productName", "Ver Produto")[:35]
            discount = int(node.get("priceDiscountRate") or 0)

            btn_label = f"🛒 GARANTIR {discount}% OFF — 6.6" if discount > 0 else "🛒 VER PRODUTO 6.6"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn_label, url=link)],
            ])

            send_kwargs = dict(
                chat_id=TELEGRAM_CHANNEL_ID,
                parse_mode="HTML",
                reply_markup=keyboard,
                **( {"message_thread_id": thread_id} if thread_id else {} ),
            )

            try:
                if image_url:
                    await bot.send_photo(photo=image_url, caption=caption, **send_kwargs)
                    print(f"  ✅ [{sent+1}] FOTO: {name}...")
                else:
                    await bot.send_message(text=caption, disable_web_page_preview=False, **send_kwargs)
                    print(f"  ✅ [{sent+1}] TEXTO: {name}...")

                sent += 1
                await asyncio.sleep(5)

            except Exception as e:
                print(f"  ❌ Erro ao enviar produto: {e}")

        # Pausa entre keywords
        if len(slot["keywords"]) > 1:
            await asyncio.sleep(8)

    print(f"\n✅ Slot '{slot_name}' concluído! {sent} produto(s) enviados.")

    if sent == 0:
        print("[AVISO] Nenhum produto foi enviado. Verifique a API Shopee.")
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=(
                "⚠️ <b>Shopee 6.6</b> — Garimpando as melhores ofertas...\n"
                "🔄 Acompanhe o grupo para não perder nada!"
            ),
            parse_mode="HTML",
            **( {"message_thread_id": thread_id} if thread_id else {} ),
        )


if __name__ == "__main__":
    # O slot é passado como argumento ou auto-detectado pela hora UTC
    slot_arg = sys.argv[1] if len(sys.argv) > 1 else None
    slot_to_run = slot_arg if slot_arg in SLOTS else detect_current_slot()

    print(f"🚀 Slot selecionado: '{slot_to_run}'")

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(send_66_slot(slot_to_run))
