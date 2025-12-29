"""
Test script for Shopee API authentication and connection
"""

import sys
import os
import asyncio

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

# Check credentials
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_SECRET")

if not SHOPEE_APP_ID or not SHOPEE_SECRET:
    print("ERRO: SHOPEE_APP_ID e SHOPEE_SECRET devem estar configurados no .env!")
    sys.exit(1)

print(f"OK: SHOPEE_APP_ID configurado: {SHOPEE_APP_ID}")
print(f"OK: SHOPEE_SECRET configurado: {SHOPEE_SECRET[:8]}...")

# Import Shopee client
from api.utils.shopee_client import ShopeeAffiliateClient

async def test_shopee_connection():
    """Testa conexão e autenticação com Shopee API"""
    print("\n" + "="*60)
    print("TESTANDO SHOPEE API")
    print("="*60)
    
    try:
        # Create client
        print("\n1. Criando cliente Shopee...")
        client = ShopeeAffiliateClient(
            app_id=SHOPEE_APP_ID,
            secret=SHOPEE_SECRET
        )
        print("   OK: Cliente criado")
        
        # Test connection
        print("\n2. Testando autenticacao...")
        async with client:
            success = await client.test_connection()
            
            if success:
                print("   OK: Autenticacao bem-sucedida!")
            else:
                print("   ERRO: Autenticacao falhou")
                return False
            
            # Get brand offers
            print("\n3. Buscando ofertas de marca...")
            offers = await client.get_brand_offers(limit=3)
            print(f"   OK: {len(offers)} ofertas encontradas")
            
            if offers:
                for offer in offers[:2]:
                    print(f"      - {offer.get('offerName', 'N/A')}")
                    print(f"        Comissao: {offer.get('commissionRate', 0)}%")
            
            # Get products
            print("\n4. Buscando produtos...")
            products = await client.get_products(limit=5, min_commission=5.0)
            print(f"   OK: {len(products)} produtos encontrados")
            
            if products:
                for product in products[:3]:
                    name = product.get('productName', 'N/A')[:40]
                    commission = product.get('commissionRate', 0)
                    price = product.get('price', 0)
                    print(f"      - {name}...")
                    print(f"        Preco: R$ {price:.2f} | Comissao: {commission}%")
            
            print("\n" + "="*60)
            print("TESTE CONCLUIDO COM SUCESSO!")
            print("="*60)
            print("\nProximos passos:")
            print("1. Execute: python scripts/test_shopee_import.py")
            print("2. Para importar: python scripts/shopee_import_manual.py")
            
            return True
            
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(test_shopee_connection())
    sys.exit(0 if success else 1)
