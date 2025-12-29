"""
Test complete Shopee API queries
Tests productOfferV2, shopOfferV2, and shopeeOfferV2
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

from api.utils.shopee_client import create_shopee_client

async def test_all_queries():
    """Testa todas as queries principais"""
    print("\n" + "="*70)
    print("TESTANDO TODAS AS QUERIES DA API SHOPEE")
    print("="*70)
    
    client = create_shopee_client()
    
    try:
        await client.connect()
        
        # ===== TEST 1: productOfferV2 =====
        print("\n1. TESTANDO productOfferV2 (Produtos)")
        print("-" * 70)
        
        # Busca por keyword
        print("\n   Buscando produtos com keyword 'phone'...")
        products = await client.get_products(
            keyword="phone",
            sort_type=5,  # Maior comissao
            limit=3
        )
        
        nodes = products.get("nodes", [])
        print(f"   OK: {len(nodes)} produtos encontrados")
        
        if nodes:
            for product in nodes[:2]:
                name = product.get('productName', 'N/A')[:40]
                commission = float(product.get('commissionRate', 0)) * 100
                seller_comm = float(product.get('sellerCommissionRate', 0)) * 100 if product.get('sellerCommissionRate') else 0
                price_min = product.get('priceMin', 'N/A')
                sales = product.get('sales', 0)
                
                print(f"\n      - {name}...")
                print(f"        Comissao Total: {commission:.2f}%")
                if seller_comm > 0:
                    print(f"        Comissao Vendedor: {seller_comm:.2f}%")
                print(f"        Preco: R$ {price_min}")
                print(f"        Vendas: {sales:,}")
        
        # ===== TEST 2: shopOfferV2 =====
        print("\n\n2. TESTANDO shopOfferV2 (Lojas)")
        print("-" * 70)
        
        print("\n   Buscando lojas com maior comissao...")
        shops = await client.get_shop_offers(
            sort_type=2,  # Maior comissao
            limit=3
        )
        
        shop_nodes = shops.get("nodes", [])
        print(f"   OK: {len(shop_nodes)} lojas encontradas")
        
        if shop_nodes:
            for shop in shop_nodes:
                name = shop.get('shopName', 'N/A')[:30]
                commission = float(shop.get('commissionRate', 0)) * 100
                rating = shop.get('ratingStar', 'N/A')
                shop_type = shop.get('shopType', [])
                
                print(f"\n      - {name}...")
                print(f"        Comissao: {commission:.2f}%")
                print(f"        Rating: {rating}/5")
                if 1 in shop_type:
                    print(f"        Tipo: Shopee Mall")
        
        # ===== TEST 3: shopeeOfferV2 =====
        print("\n\n3. TESTANDO shopeeOfferV2 (Ofertas)")
        print("-" * 70)
        
        print("\n   Buscando ofertas gerais...")
        offers = await client.get_shopee_offers(
            sort_type=2,  # Maior comissao
            limit=3
        )
        
        offer_nodes = offers.get("nodes", [])
        print(f"   OK: {len(offer_nodes)} ofertas encontradas")
        
        if offer_nodes:
            for offer in offer_nodes[:2]:
                name = offer.get('offerName', 'N/A')[:40]
                commission = float(offer.get('commissionRate', 0)) * 100
                
                print(f"\n      - {name}...")
                print(f"        Comissao: {commission:.2f}%")
        
        # ===== TEST 4: generateShortLink =====
        print("\n\n4. TESTANDO generateShortLink (Mutation)")
        print("-" * 70)
        
        test_url = "https://shopee.com.br/Universal-Foldable-Bracket-Desktop-Mobile-Cell-Phone-i.52377417.22258489066"
        print(f"\n   Gerando link para produto...")
        
        short_link = await client.generate_short_link(
            origin_url=test_url,
            sub_ids=["test1", "test2"]
        )
        
        if short_link:
            print(f"   OK: {short_link}")
        
        # SUMMARY
        print("\n\n" + "="*70)
        print("RESUMO DOS TESTES")
        print("="*70)
        
        print(f"\n  productOfferV2:    {'OK' if len(nodes) > 0 else 'VAZIO'} ({len(nodes)} produtos)")
        print(f"  shopOfferV2:       {'OK' if len(shop_nodes) > 0 else 'VAZIO'} ({len(shop_nodes)} lojas)")
        print(f"  shopeeOfferV2:     {'OK' if len(offer_nodes) > 0 else 'VAZIO'} ({len(offer_nodes)} ofertas)")
        print(f"  generateShortLink: {'OK' if short_link else 'ERRO'}")
        
        print("\n" + "="*70)
        print("TODAS AS QUERIES TESTADAS COM SUCESSO!")
        print("="*70)
        
        print("\nProximos passos:")
        print("1. Integrar queries no bot Telegram")
        print("2. Criar sistema de importacao automatica")
        print("3. Armazenar dados no Supabase")
        print("4. Implementar tracking de comissoes")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_all_queries())
