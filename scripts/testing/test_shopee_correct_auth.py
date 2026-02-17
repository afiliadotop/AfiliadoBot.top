"""
Teste com formato correto do header Authorization
Conforme documentação: SHA256 Credential={AppId}, Timestamp={Timestamp}, Signature={Signature}
"""

import os
import sys
import time
import hashlib
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_APP_SECRET")
SHOPEE_ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"


async def test_correct_auth_format():
    """Testa com o formato CORRETO do header"""
    
    print("=" * 70)
    print("✅ TESTE COM FORMATO CORRETO DE AUTENTICAÇÃO")
    print("=" * 70)
    
    # Query simples
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
    
    # Prepara body
    body = {"query": query}
    payload = json.dumps(body, separators=(',', ':'))
    
    # Gera timestamp
    timestamp = int(time.time())
    
    #Gera signature: SHA256(AppId + Timestamp + Payload + Secret)
    signature_string = f"{SHOPEE_APP_ID}{timestamp}{payload}{SHOPEE_SECRET}"
    signature = hashlib.sha256(signature_string.encode('utf-8')).hexdigest()
    
    # Constrói header Authorization CORRETO
    auth_header = f"SHA256 Credential={SHOPEE_APP_ID}, Timestamp={timestamp}, Signature={signature}"
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    print(f"\n📍 Endpoint: {SHOPEE_ENDPOINT}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"🔐 Signature: {signature}")
    print(f"\n📤 Header Authorization:")
    print(f"   {auth_header[:80]}...")
    
    print(f"\n🌐 Enviando requisição...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SHOPEE_ENDPOINT,
                data=payload,  # usa data, não json!
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                status = response.status
                text = await response.text()
                
                print(f"\n📥 Resposta:")
                print(f"  Status: {status}")
                
                if status == 200:
                    try:
                        data = json.loads(text)
                        
                        if "errors" in data:
                            print(f"\n❌ ERRO GraphQL:")
                            for error in data["errors"]:
                                code = error.get('extensions', {}).get('code', 'N/A')
                                msg = error.get('message', 'N/A')
                                print(f"  - Code {code}: {msg}")
                        else:
                            print(f"\n✅ ✅ ✅ SUCESSO TOTAL! ✅ ✅ ✅")
                            print(f"\n📦 Dados retornados:")
                            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                            
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️ Erro ao parsear JSON: {e}")
                        print(f"  Body: {text[:300]}")
                else:
                    print(f"\n❌ Erro HTTP {status}")
                    print(f"  Body: {text[:300]}")
                    
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Testando formato CORRETO de autenticação...\n")
    asyncio.run(test_correct_auth_format())
    print("\n✅ Teste concluído!\n")
