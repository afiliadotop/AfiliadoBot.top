"""
Script de Importação de Produtos do Mercado Livre
Busca produtos via API e importa para o banco Supabase
"""

import asyncio
import httpx
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Ajustar path para importar módulos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "afiliadohub"))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from api.utils.supabase_client import get_supabase_manager

ML_AFFILIATE_TAG = os.getenv("ML_AFFILIATE_TAG", "")
ML_BASE_URL = "https://api.mercadolibre.com"

# Headers para evitar bloqueio 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

# Categorias para importar automaticamente
CATEGORIES_TO_IMPORT = [
    {"keyword": "iphone 15", "category": "Celulares", "limit": 20},
    {"keyword": "notebook gamer", "category": "Informática", "limit": 20},
    {"keyword": "smart tv 50", "category": "Eletrônicos", "limit": 15},
    {"keyword": "fone bluetooth", "category": "Áudio", "limit": 15},
    {"keyword": "smartwatch", "category": "Eletrônicos", "limit": 10},
    {"keyword": "tablet", "category": "Eletrônicos", "limit": 10},
]


async def search_ml_products(keyword: str, limit: int = 50, retries: int = 3) -> list:
    """Busca produtos no ML via API com retry logic"""
    url = f"{ML_BASE_URL}/sites/MLB/search"
    params = {
        "q": keyword,
        "limit": limit,
        "offset": 0,
        "condition": "new",
        "sort": "price_asc"
    }
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=HEADERS, follow_redirects=True) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                print(f"  ⚠️  Bloqueio 403 (tentativa {attempt + 1}/{retries}). Aguardando {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            print(f"[ERRO HTTP] {e.response.status_code} ao buscar '{keyword}': {e}")
            return []
        except Exception as e:
            print(f"[ERRO] Falha ao buscar '{keyword}': {e}")
            return []
    
    print(f"[ERRO] Todas as tentativas falharam para '{keyword}'")
    return []


def generate_affiliate_link(item_id: str) -> str:
    """Gera link de afiliado"""
    # Remove prefixo MLB- se existir
    clean_id = item_id.replace("MLB-", "")
    base_url = f"https://produto.mercadolivre.com.br/MLB-{clean_id}"
    
    if ML_AFFILIATE_TAG:
        return f"{base_url}?matt_tool=82322591&matt_word={ML_AFFILIATE_TAG}"
    
    return base_url


def calculate_discount(item: dict) -> int:
    """Calcula desconto percentual"""
    if "original_price" in item and item["original_price"]:
        try:
            discount = ((item["original_price"] - item["price"]) / item["original_price"]) * 100
            return int(discount)
        except:
            return 0
    return 0


async def import_products():
    """Importa produtos do ML para o Supabase"""
    print("=" * 60)
    print("IMPORTAÇÃO MERCADO LIVRE")
    print("=" * 60)
    
    if not ML_AFFILIATE_TAG:
        print("⚠️  [AVISO] ML_AFFILIATE_TAG não configurado - links sem tracking")
    
    supabase = get_supabase_manager()
    total_imported = 0
    total_errors = 0
    
    for cat_config in CATEGORIES_TO_IMPORT:
        keyword = cat_config["keyword"]
        category = cat_config["category"]
        limit = cat_config["limit"]
        
        print(f"\n🔍 Buscando: '{keyword}' (categoria: {category})...")
        
        products = await search_ml_products(keyword, limit)
        print(f"✅ Encontrados {len(products)} produtos")
        
        for item in products:
            try:
                # Calcular desconto
                discount = calculate_discount(item)
                
                # Imagem em alta resolução
                image_url = item.get("thumbnail", "").replace("-I.jpg", "-O.jpg")
                
                # Preparar dados do produto
                product_data = {
                    "store": "mercado_livre",
                    "name": item["title"][:255],  # Limitar tamanho
                    "description": item.get("subtitle", "")[:500] if item.get("subtitle") else None,
                    "affiliate_link": generate_affiliate_link(item["id"]),
                    "current_price": float(item["price"]),
                    "original_price": float(item["original_price"]) if item.get("original_price") else None,
                    "discount_percentage": discount,
                    "category": category,
                    "image_url": image_url,
                    "is_active": True,
                    "is_featured": discount >= 30,  # Destaque para descontos grandes
                    "source": "mercadolivre_api"
                }
                
                # Inserir no banco
                result = await supabase.insert_product(product_data)
                
                if result:
                    total_imported += 1
                    if discount >= 30:
                        print(f"  ⭐ {item['title'][:50]}... - {discount}% OFF")
                else:
                    total_errors += 1
                    
            except Exception as e:
                total_errors += 1
                print(f"  ❌ Erro ao importar {item.get('id', 'N/A')}: {e}")
        
        # Rate limiting para evitar bloqueio
        if products:  # Só espera se encontrou produtos
            print(f"⏳ Aguardando 3s antes da próxima busca...")
            await asyncio.sleep(3)
    
    print("\n" + "=" * 60)
    print("RESUMO DA IMPORTAÇÃO")
    print("=" * 60)
    print(f"✅ Total importado: {total_imported} produtos")
    print(f"❌ Total de erros: {total_errors}")
    
    # Fix para ZeroDivisionError
    total_operations = total_imported + total_errors
    if total_operations > 0:
        success_rate = (total_imported / total_operations * 100)
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    else:
        print(f"📊 Taxa de sucesso: 0.0% (nenhum produto processado)")
    
    print("=" * 60)


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(import_products())
