"""
Simple test for Shopee API connection and schema exploration
"""

import sys
import os
import asyncio

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_SECRET")

if not SHOPEE_APP_ID or not SHOPEE_SECRET:
    print("ERRO: Credenciais Shopee nao configuradas!")
    sys.exit(1)

print(f"OK: Credenciais configuradas")

from api.utils.shopee_client import ShopeeAffiliateClient

async def explore_schema():
    """Explora o schema GraphQL da Shopee"""
    print("\n" + "="*60)
    print("EXPLORANDO SCHEMA SHOPEE API")
    print("="*60)
    
    client = ShopeeAffiliateClient(SHOPEE_APP_ID, SHOPEE_SECRET)
    
    try:
        await client.connect()
        
        # Test 1: Basic connection
        print("\n1. Testando conexao basica...")
        test_query = """
        {
            __schema {
                queryType {
                    name
                }
            }
        }
        """
        
        result = await client.graphql_query(test_query)
        if "data" in result:
            print("   OK: API respondeu corretamente!")
        
        # Test 2: Get available query types
        print("\n2. Buscando queries disponiveis...")
        schema_query = """
        {
            __schema {
                queryType {
                    fields {
                        name
                        description
                    }
                }
            }
        }
        """
        
        result = await client.graphql_query(schema_query)
        if "data" in result and "__schema" in result["data"]:
            fields = result["data"]["__schema"]["queryType"]["fields"]
            print(f"   OK: {len(fields)} queries encontradas:")
            for field in fields[:10]:
                print(f"      - {field['name']}")
        
        # Test 3: Try simple product offer query
        print("\n3. Testando query de ofertas...")
        
        # Try a simpler query structure
        offer_query = """
        {
            productOfferV2(first: 5) {
                nodes {
                    productName
                    commissionRate
                }
                pageInfo {
                    hasNextPage
                }
            }
        }
        """
        
        try:
            result = await client.graphql_query(offer_query)
            if "data" in result:
                print("   OK: Query de produtos funcionou!")
                if "productOfferV2" in result["data"]:
                    nodes = result["data"]["productOfferV2"].get("nodes", [])
                    print(f"      Produtos encontrados: {len(nodes)}")
                    if nodes:
                        for product in nodes[:3]:
                            name = product.get('productName', 'N/A')[:40]
                            commission = product.get('commissionRate', 0)
                            print(f"      - {name}... ({commission}%)")
        except Exception as e:
            print(f"   Query nao funcionou: {e}")
            print("   Tentando query alternativa...")
        
        print("\n" + "="*60)
        print("EXPLORACAO CONCLUIDA")
        print("="*60)
        print("\nProximos passos:")
        print("1. Use as queries que funcionaram")
        print("2. Ajuste os metodos do shopee_client.py")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(explore_schema())
