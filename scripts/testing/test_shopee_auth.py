"""
Script para testar autenticação Shopee API
Valida se a assinatura SHA256 está correta
"""

import os
import sys
import time
import hashlib
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_APP_SECRET")
SHOPEE_ENDPOINT = os.getenv("SHOPEE_API_ENDPOINT", "https://open-api.affiliate.shopee.com.br/graphql")


def generate_signature(timestamp: int, payload: str, secret: str) -> str:
    """Gera assinatura SHA256 conforme documentação Shopee"""
    # Formato: timestamp + payload + secret
    message = f"{timestamp}{payload}{secret}"
    signature = hashlib.sha256(message.encode('utf-8')).hexdigest()
    return signature


async def test_simple_query():
    """Testa query GraphQL mais simples possível"""
    
    if not SHOPEE_APP_ID or not SHOPEE_SECRET:
        print("❌ ERRO: Credenciais não configuradas!")
        return
    
    print("=" * 60)
    print("🧪 TESTE DE AUTENTICAÇÃO SHOPEE API")
    print("=" * 60)
    print(f"\n📍 Endpoint: {SHOPEE_ENDPOINT}")
    print(f"🆔 App ID: {SHOPEE_APP_ID}")
    print(f"🔑 Secret: {SHOPEE_SECRET[:10]}...")
    
    # Query GraphQL simples - apenas pedir produtos com limite mínimo
    query = """
    {
        productOfferV2(limit: 1) {
            nodes {
                itemId
                productName
            }
        }
    }
    """
    
    timestamp = int(time.time())
    payload = query.strip()
    signature = generate_signature(timestamp, payload, SHOPEE_SECRET)
    
    print(f"\n⏰ Timestamp: {timestamp}")
    print(f"📝 Payload length: {len(payload)} chars")
    print(f"🔐 Signature: {signature}")
    
    headers = {
        "Content-Type": "application/json",
        "AppId": str(SHOPEE_APP_ID),
        "Timestamp": str(timestamp),
        "Signature": signature
    }
    
    print(f"\n📤 Headers:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    body = {
        "query": query
    }
    
    print(f"\n🌐 Fazendo requisição...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SHOPEE_ENDPOINT,
                headers=headers,
                json=body,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                status = response.status
                text = await response.text()
                
                print(f"\n📥 Resposta:")
                print(f"  Status: {status}")
                print(f"  Body: {text[:500]}")
                
                if status == 200:
                    try:
                        data = json.loads(text)
                        if "errors" in data:
                            print(f"\n❌ ERRO GraphQL:")
                            for error in data["errors"]:
                                print(f"  - Code: {error.get('extensions', {}).get('code', 'N/A')}")
                                print(f"    Message: {error.get('message', 'N/A')}")
                        else:
                            print(f"\n✅ SUCESSO! API respondeu corretamente")
                            if "data" in data and "productOfferV2" in data["data"]:
                                products = data["data"]["productOfferV2"]["nodes"]
                                print(f"  Produtos retornados: {len(products)}")
                    except json.JSONDecodeError:
                        print(f"\n⚠️ Resposta não é JSON válido")
                else:
                    print(f"\n❌ Erro HTTP {status}")
                    
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {e}")
        import traceback
        traceback.print_exc()


async def test_with_debug():
    """Teste com debug detalhado da assinatura"""
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG DA ASSINATURA")
    print("=" * 60)
    
    query = '{ productOfferV2(limit: 1) { nodes { itemId } } }'
    timestamp = int(time.time())
    
    # Mostra passo a passo
    print(f"\n1️⃣ Timestamp: {timestamp}")
    print(f"2️⃣ Query: {query}")
    print(f"3️⃣ Secret: {SHOPEE_SECRET}")
    
    # Concatenação
    message = f"{timestamp}{query}{SHOPEE_SECRET}"
    print(f"\n4️⃣ Message (timestamp + query + secret):")
    print(f"   Length: {len(message)} chars")
    print(f"   First 50: {message[:50]}...")
    print(f"   Last 50: ...{message[-50:]}")
    
    # Hash
    signature = hashlib.sha256(message.encode('utf-8')).hexdigest()
    print(f"\n5️⃣ SHA256 Hash: {signature}")
    
    # Teste alternativo: sem espaços na query
    query_no_spaces = query.replace(" ", "")
    message2 = f"{timestamp}{query_no_spaces}{SHOPEE_SECRET}"
    signature2 = hashlib.sha256(message2.encode('utf-8')).hexdigest()
    print(f"\n6️⃣ Teste alternativo (sem espaços):")
    print(f"   Query: {query_no_spaces}")
    print(f"   Signature: {signature2}")


if __name__ == "__main__":
    print("\n🚀 Iniciando testes...\n")
    asyncio.run(test_simple_query())
    asyncio.run(test_with_debug())
    print("\n✅ Testes concluídos!\n")
