"""
Test Shopee shopeeOfferV2 query with pagination and filters
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

from api.utils.shopee_client import ShopeeAffiliateClient
import os

async def test_offers():
    """Testa busca de ofertas"""
    print("\n" + "="*60)
    print("TESTANDO SHOPEE OFFERS (shopeeOfferV2)")
    print("="*60)
    
    client = ShopeeAffiliateClient(
        os.getenv("SHOPEE_APP_ID"),
        os.getenv("SHOPEE_SECRET")
    )
    
    try:
        await client.connect()
        
        # Test 1: Busca sem filtros (mais recentes)
        print("\n1. Buscando ofertas mais recentes (sem keyword)...")
        result = await client.get_shopee_offers(
            sort_type=1,  # Mais recente
            page=1,
            limit=5
        )
        
        nodes = result.get("nodes", [])
        page_info = result.get("pageInfo", {})
        
        print(f"   OK: {len(nodes)} ofertas encontradas")
        print(f"   Pagina: {page_info.get('page', 1)}")
        print(f"   Tem proxima: {page_info.get('hasNextPage', False)}")
        
        if nodes:
            print("\n   Primeiras ofertas:")
            for i, offer in enumerate(nodes[:3], 1):
                print(f"      {i}. {offer.get('offerName', 'N/A')}")
                print(f"         Comissao: {float(offer.get('commissionRate', 0)) * 100:.2f}%")
                print(f"         Link: {offer.get('offerLink', 'N/A')[:50]}...")
        
        # Test 2: Busca por keyword
        print("\n2. Buscando ofertas por keyword 'phone'...")
        result2 = await client.get_shopee_offers(
            keyword="phone",
            sort_type=2,  # Maior comissao
            page=1,
            limit=3
        )
        
        nodes2 = result2.get("nodes", [])
        print(f"   OK: {len(nodes2)} ofertas com 'phone'")
        
        if nodes2:
            for offer in nodes2:
                print(f"      - {offer.get('offerName', 'N/A')[:40]}...")
        
        # Test 3: Paginacao
        if page_info.get('hasNextPage'):
            print("\n3. Testando paginacao (pagina 2)...")
            result3 = await client.get_shopee_offers(
                page=2,
                limit=5
            )
            nodes3 = result3.get("nodes", [])
            print(f"   OK: {len(nodes3)} ofertas na pagina 2")
        
        # Test 4: Ordenacao por comissao
        print("\n4. Top ofertas por comissao...")
        result4 = await client.get_shopee_offers(
            sort_type=2,  # Maior comissao primeiro
            limit=3
        )
        
        nodes4 = result4.get("nodes", [])
        print(f"   OK: {len(nodes4)} ofertas ordenadas por comissao:")
        
        for i, offer in enumerate(nodes4, 1):
            commission = float(offer.get('commissionRate', 0)) * 100
            print(f"      #{i} - {commission:.2f}% - {offer.get('offerName', 'N/A')[:30]}...")
        
        print("\n" + "="*60)
        print("TESTE CONCLUIDO COM SUCESSO!")
        print("="*60)
        print("\nProximos passos:")
        print("1. Integrar no importer para importacao automatica")
        print("2. Adicionar comando do bot /shopee_ofertas")
        print("3. Armazenar ofertas no Supabase")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_offers())
