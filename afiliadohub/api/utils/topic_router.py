"""
Topic Router — AfiliadoTop

Maps product categories and keywords to Telegram Forum topic thread IDs.
Thread IDs are loaded from environment variables so they can be configured
per-group without touching code.

Usage:
    from .utils.topic_router import get_thread_id, detect_category

    thread_id = get_thread_id(category="roupas")
    thread_id = get_thread_id(keyword="vestido floral")
"""

import os
import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Topic IDs — loaded from env vars (configure on Render Dashboard)
# Each var holds the integer message_thread_id of the forum topic.
# Use /topicos command to discover these IDs inside the group.
# ─────────────────────────────────────────────────────────────────────────────

def _topic(env_key: str) -> Optional[int]:
    """Reads a topic thread ID from an env var. Returns None if not set."""
    val = os.getenv(env_key, "").strip()
    return int(val) if val.isdigit() else None


TOPIC_IDS = {
    "roupas":     _topic("TOPIC_ROUPAS"),       # 👗 Roupas femininas
    "bijuterias": _topic("TOPIC_BIJUTERIAS"),    # 💎 Bijuterias
    "beleza":     _topic("TOPIC_BELEZA"),        # 💆 Cuidados Femininos
    "cupons":     _topic("TOPIC_CUPONS"),        # 🎟️ Cupons
    "videos":     _topic("TOPIC_VIDEOS"),        # 🎬 Vídeos
    "namorados":  _topic("TOPIC_NAMORADOS"),     # 💝 Dia dos namorados
    "geral":      _topic("TOPIC_GERAL"),         # 💬 General (fallback)
}

# ─────────────────────────────────────────────────────────────────────────────
# Keyword → Category mappings
# Each list contains terms that, when found in a product name or keyword,
# route the message to that topic.
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "roupas": [
        "roupa", "vestido", "blusa", "camiseta", "calça", "saia", "moda feminina",
        "conjunto", "cropped", "jaqueta", "casaco", "moletom", "legging",
        "pijama", "shorts", "body", "macacão", "roupas femininas", "calçado feminino",
        "tênis feminino", "sandália", "scarpin", "sapatilha",
    ],
    "bijuterias": [
        "bijuteria", "colar", "anel", "brinco", "pulseira", "corrente",
        "joias", "acessórios femininos", "bolsa", "mochila feminina", "carteira",
        "tiara", "presilha", "broche",
    ],
    "beleza": [
        "skincare", "kit skincare", "perfume feminino", "maquiagem", "batom",
        "hidratante", "creme", "sérum", "esfoliante", "máscara facial",
        "protetor solar", "shampoo", "condicionador", "escova", "secador",
        "chapinha", "cuidados femininos", "beleza",
    ],
    "namorados": [
        "dia dos namorados", "presente namorada", "presente namorado",
        "romance", "kit romântico", "vela aromática", "pétalas", "amor",
        "presente casal", "rose", "coração", "floral", "perfume presente",
    ],
    "cupons": [
        "cupom", "desconto extra", "frete grátis",
    ],
}

# Keywords used in the daily promo script that map to specific topics
PROMO_KEYWORD_TOPIC: dict[str, str] = {
    # Morning
    "fone bluetooth":    "geral",
    "smartwatch":        "geral",
    "carregador rápido": "geral",
    "tênis esportivo":   "roupas",
    "mochila":           "bijuterias",
    "câmera ação":       "geral",
    "tablet android":    "geral",
    # Evening
    "panela air fryer":  "geral",
    "perfume feminino":  "beleza",
    "suplemento whey":   "geral",
    "mouse gamer":       "geral",
    "calçado feminino":  "roupas",
    "kit skincare":      "beleza",
    "jogo playstation":  "geral",
}


def detect_category(
    product_name: str = "",
    keyword: str = "",
    product_category: str = "",
) -> str:
    """
    Detects the best matching topic category for a product.

    Priority:
        1. keyword → PROMO_KEYWORD_TOPIC exact match
        2. product_name / keyword text → CATEGORY_KEYWORDS regex scan
        3. product_category field from API
        4. fallback → "geral"
    """
    # 1. Exact keyword match from daily promo rotation
    if keyword and keyword.lower() in PROMO_KEYWORD_TOPIC:
        return PROMO_KEYWORD_TOPIC[keyword.lower()]

    # 2. Regex scan across name + keyword text
    text = f"{product_name} {keyword} {product_category}".lower()
    for category, terms in CATEGORY_KEYWORDS.items():
        for term in terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text):
                return category

    # 3. Partial match on product_category field
    cat_lower = product_category.lower()
    for category in CATEGORY_KEYWORDS:
        if category in cat_lower:
            return category

    return "geral"


def get_thread_id(
    category: str = "auto",
    product_name: str = "",
    keyword: str = "",
    product_category: str = "",
) -> Optional[int]:
    """
    Returns the message_thread_id for a given category (or auto-detected one).

    Returns None if the topic env var is not configured — caller should then
    send to the group without a thread_id (posts to General).
    """
    if not category or category == "auto":
        category = detect_category(product_name, keyword, product_category)

    return TOPIC_IDS.get(category) or TOPIC_IDS.get("geral")
