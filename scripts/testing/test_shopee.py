#!/usr/bin/env python3
"""
ITIL Service: Support / Quality Assurance
Testes consolidados da API Shopee

Consolida: test_shopee_auth.py, test_shopee_complete.py, test_shopee_offers.py, test_shopee_shortlink.py
"""
import sys
import os
import asyncio
import argparse

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_APP_SECRET") or os.getenv("SHOPEE_SECRET")

async def test_auth():
    """Testa apenas autenticação"""
    print("="*60)
    print("TESTE DE AUTENTICACAO SHOPEE")
    print("="*60)
    
    if not SHOPEE_APP_ID or not SHOPEE_SECRET:
        print("ERRO: SHOPEE_APP_ID e SHOPEE_APP_SECRET nao configurados")
        return False
    
    print(f"\\nApp ID: {SHOPEE_APP_ID}")
    print(f"Secret: {SHOPEE_SECRET[:8]}...")
    
    try:
        from api.utils.shopee_client import ShopeeAffiliateClient
        
        print("\\nTestando autenticacao...")
        client = ShopeeAffiliateClient(
            app_id=SHOPEE_APP_ID,
            secret=SHOPEE_SECRET
        )
        
        async with client:
            success = await client.test_connection()
            
            if success:
                print("OK: Autenticacao bem-sucedida!")
                return True
            else:
                print("ERRO: Autenticacao falhou")
                return False
                
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_products():
    """Testa busca de produtos"""
    print("="*60)
    print("TESTE DE PRODUTOS SHOPEE")
    print("="*60)
    
    if not SHOPEE_APP_ID or not SHOPEE_SECRET:
        print("ERRO: Credenciais nao configuradas")
        return False
    
    try:
        from api.utils.shopee_client import ShopeeAffiliateClient
        
        print("\\n1. Conectando...")
        client = ShopeeAffiliateClient(
            app_id=SHOPEE_APP_ID,
            secret=SHOPEE_SECRET
        )
        
        async with client:
            print("\\n2. Buscando produtos...")
            products = await client.get_products(limit=5, min_commission=5.0)
            print(f"OK: {len(products)} produtos encontrados")
            
            if products:
                for i, product in enumerate(products[:3], 1):
                    name = product.get('productName', 'N/A')[:40]
                    commission = product.get('commissionRate', 0)
                    price = product.get('price', 0)
                    print(f"\\n{i}. {name}...")
                    print(f"   Preco: R$ {price:.2f} | Comissao: {commission}%")
            
            return True
                
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_offers():
    """Testa busca de ofertas"""
    print("="*60)
    print("TESTE DE OFERTAS SHOPEE")
    print("="*60)
    
    if not SHOPEE_APP_ID or not SHOPEE_SECRET:
        print("ERRO: Credenciais nao configuradas")
        return False
    
    try:
        from api.utils.shopee_client import ShopeeAffiliateClient
        
        client = ShopeeAffiliateClient(
            app_id=SHOPEE_APP_ID,
            secret=SHOPEE_SECRET
        )
        
        async with client:
            print("\\nBuscando ofertas de marca...")
            offers = await client.get_brand_offers(limit=5)
            print(f"OK: {len(offers)} ofertas encontradas")
            
            if offers:
                for i, offer in enumerate(offers[:3], 1):
                    name = offer.get('offerName', 'N/A')
                    commission = offer.get('commissionRate', 0)
                    print(f"{i}. {name}")
                    print(f"   Comissao: {commission}%")
            
            return True
                
    except Exception as e:
        print(f"ERRO: {e}")
        return False

async def test_complete():
    """Teste completo: auth + produtos + ofertas"""
    print("="*60)
    print("TESTE COMPLETO SHOPEE API")
    print("="*60)
    
    if not SHOPEE_APP_ID or not SHOPEE_SECRET:
        print("ERRO: Credenciais nao configuradas")
        return False
    
    try:
        from api.utils.shopee_client import ShopeeAffiliateClient
        
        print("\\n1. Testando autenticacao...")
        client = ShopeeAffiliateClient(
            app_id=SHOPEE_APP_ID,
            secret=SHOPEE_SECRET
        )
        
        async with client:
            success = await client.test_connection()
            if not success:
                print("ERRO: Autenticacao falhou")
                return False
            print("OK: Autenticado")
            
            print("\\n2. Buscando ofertas...")
            offers = await client.get_brand_offers(limit=3)
            print(f"OK: {len(offers)} ofertas")
            
            print("\\n3. Buscando produtos...")
            products = await client.get_products(limit=5)
            print(f"OK: {len(products)} produtos")
            
            if products:
                print("\\nExemplos de produtos:")
                for product in products[:2]:
                    name = product.get('productName', 'N/A')[:35]
                    price = product.get('price', 0)
                    commission = product.get('commissionRate', 0)
                    print(f"  - {name}...")
                    print(f"    R$ {price:.2f} | Comissao: {commission}%")
            
            print("\\n" + "="*60)
            print("TESTE COMPLETO CONCLUIDO COM SUCESSO!")
            print("="*60)
            return True
                
    except Exception as e:
        print(f"\\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Testes consolidados da API Shopee (ITIL Support/QA)'
    )
    parser.add_argument(
        '--mode',
        choices=['auth', 'products', 'offers', 'complete'],
        default='complete',
        help='Modo de teste'
    )
    
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    if args.mode == 'auth':
        success = asyncio.run(test_auth())
    elif args.mode == 'products':
        success = asyncio.run(test_products())
    elif args.mode == 'offers':
        success = asyncio.run(test_offers())
    else:  # complete
        success = asyncio.run(test_complete())
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
