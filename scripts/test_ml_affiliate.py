"""
Script de teste para API de afiliados do Mercado Livre
Testa o endpoint /affiliate-program/api/v2/affiliates/createLink
"""
import asyncio
import sys
import os

# Ajustar path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from afiliadohub.api.utils.ml_token_manager import get_ml_token
import httpx

ML_AFFILIATE_BASE_URL = "https://api.mercadolibre.com/affiliate-program/api/v2/affiliates"

async def test_create_link():
    """Testa criação de link de afiliado"""
    print("=" * 70)
    print("TESTE - ML AFFILIATE API")
    print("=" * 70)
    
    try:
        # Obter token
        print("\n1️⃣ Obtendo token...")
        token = await get_ml_token()
        print(f"✅ Token obtido: {token[:50]}...")
        
        # URL de teste (produto real do ML)
        test_url = "https://produto.mercadolivre.com.br/MLB-1234567890"
        
        # Preparar request
        url = f"{ML_AFFILIATE_BASE_URL}/createLink"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-custom-origin": "https://afiliadobot.top"
        }
        
        payload = {
            "url": test_url
        }
        
        print(f"\n2️⃣ Testando endpoint: {url}")
        print(f"URL do produto: {test_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"\n📊 Status Code: {response.status_code}")
            print(f"📦 Response:")
            print(response.text)
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCESSO!")
                print(f"Short URL: {data.get('short_url')}")
                print(f"Tag: {data.get('tag')}")
            elif response.status_code == 403:
                print("\n⚠️  ERRO 403 - Possíveis causas:")
                print("1. Conta não cadastrada como afiliado ML")
                print("2. Falta completar cadastro de afiliados")
                print("3. Token sem permissões de afiliado")
            elif response.status_code == 401:
                print("\n⚠️  ERRO 401 - Token inválido ou expirado")
            else:
                print(f"\n❌ ERRO {response.status_code}")
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


async def test_get_tags():
    """Testa busca de tags"""
    print("\n" + "=" * 70)
    print("TESTE - GET TAGS")
    print("=" * 70)
    
    try:
        token = await get_ml_token()
        
        url = f"{ML_AFFILIATE_BASE_URL}/getTags"
        headers = {
            "Authorization": f"Bearer {token}",
            "x-custom-origin": "https://afiliadobot.top"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Tags encontradas: {len(data.get('tags', []))}")
                print(f"Tag em uso: {data.get('tag_in_use')}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test_create_link())
    asyncio.run(test_get_tags())
