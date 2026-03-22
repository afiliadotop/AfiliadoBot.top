from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
import json

# ==========================================
# 1. SKILL: Coleta de Dados (Data Gathering)
# ==========================================
class ScrapeProductInput(BaseModel):
    """
    Extrai dados de preço, frete e estoque de uma URL de produto.
    Use esta skill quando precisar buscar informações atualizadas de uma loja que não possui API oficial.
    """
    url: HttpUrl = Field(..., description="A URL completa do produto na loja.")
    cep: Optional[str] = Field(None, description="CEP de 8 dígitos (somente números) para calcular o custo e prazo de frete.")

def skill_scrape_product(url: str, cep: str = None) -> Dict[str, Any]:
    # Lógica real acionaria o Playwright/BeautifulSoup aqui [cite: 24, 25, 26]
    return {
        "price": 4499.90,
        "shipping_cost": 25.00 if cep else 0.0,
        "in_stock": True
    }


# ==========================================
# 2. SKILL: Inteligência e Curadoria (Reasoning)
# ==========================================
class DetectFakeDiscountInput(BaseModel):
    """
    Verifica se o 'preço de' (preço original riscado) é falso ou inflado, 
    comparando-o com a média histórica do produto.
    """
    current_price: float = Field(..., description="O preço atual da oferta.")
    declared_from_price: float = Field(..., description="O preço original declarado pela loja (preço riscado).")
    historical_average_price: float = Field(..., description="A média de preço histórico registrada no banco de dados.")

def skill_detect_fake_discount(current_price: float, declared_from_price: float, historical_average_price: float) -> Dict[str, Any]:
    # Lógica do motor de ranking [cite: 220, 221, 222]
    adjusted_from_price = declared_from_price
    if declared_from_price > historical_average_price * 1.1:
        adjusted_from_price = historical_average_price
    
    real_discount = 0.0
    if current_price < adjusted_from_price:
        real_discount = ((adjusted_from_price - current_price) / adjusted_from_price) * 100

    return {
        "is_fake_discount": declared_from_price > historical_average_price * 1.1,
        "adjusted_from_price": adjusted_from_price,
        "real_discount_percentage": round(real_discount, 2)
    }


# ==========================================
# 3. SKILL: Monetização (Affiliate Management)
# ==========================================
class GenerateAffiliateLinkInput(BaseModel):
    """
    Gera o link de afiliado final com as tags corretas e a URL de redirecionamento interno.
    """
    base_url: HttpUrl = Field(..., description="URL limpa do produto na loja.")
    store_name: str = Field(..., description="Nome da loja (ex: 'Amazon', 'Mercado Livre').")
    offer_id: str = Field(..., description="ID interno gerado para esta oferta.")

def skill_generate_affiliate_link(base_url: str, store_name: str, offer_id: str) -> Dict[str, str]:
    # Lógica de injeção de tags [cite: 461, 462]
    tags = {
        "Amazon": {"param": "tag", "value": "afiliadotop-20"},
        "Mercado Livre": {"param": "afiliado", "value": "afiliadotop"}
    }
    
    store_config = tags.get(store_name, {"param": "ref", "value": "afiliadotop"})
    product_url = f"{base_url}?{store_config['param']}={store_config['value']}"
    
    return {
        "monetized_product_url": product_url,
        "internal_click_url": f"https://afiliado.top/go/{offer_id}"
    }


# ==========================================
# 4. SKILL: Persistência (Database)
# ==========================================
class SavePriceHistoryInput(BaseModel):
    """
    Salva o preço atual de uma oferta no banco de dados (PostgreSQL) para manter o histórico atualizado.
    """
    offer_id: str = Field(..., description="O ID da oferta (referência da tabela offers).")
    price: float = Field(..., description="O preço coletado no momento.")

def skill_save_price_history(offer_id: str, price: float) -> Dict[str, Any]:
    # Lógica do banco de dados (SQLAlchemy/Postgres) [cite: 275, 276]
    # INSERT INTO price_history (offer_id, price, scraped_at) VALUES (...)
    return {
        "status": "success",
        "message": f"Preço de R${price} salvo no histórico da oferta {offer_id}."
    }


# ==========================================
# GERAÇÃO DOS SCHEMAS JSON PARA O AGENTE
# ==========================================
agent_tools = [
    {
        "type": "function",
        "function": {
            "name": "skill_scrape_product",
            "description": ScrapeProductInput.__doc__.strip(),
            "parameters": ScrapeProductInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skill_detect_fake_discount",
            "description": DetectFakeDiscountInput.__doc__.strip(),
            "parameters": DetectFakeDiscountInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skill_generate_affiliate_link",
            "description": GenerateAffiliateLinkInput.__doc__.strip(),
            "parameters": GenerateAffiliateLinkInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skill_save_price_history",
            "description": SavePriceHistoryInput.__doc__.strip(),
            "parameters": SavePriceHistoryInput.model_json_schema()
        }
    }
]

if __name__ == "__main__":
    print(json.dumps(agent_tools, indent=2, ensure_ascii=False))
