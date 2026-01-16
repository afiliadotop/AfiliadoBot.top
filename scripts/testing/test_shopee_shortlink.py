"""
Test Shopee generateShortLink mutation
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

async def test_short_link():
    """Testa geração de short link"""
    print("\n" + "="*60)
    print("TESTANDO SHOPEE SHORT LINK")
    print("="*60)
    
    client = ShopeeAffiliateClient(
        os.getenv("SHOPEE_APP_ID"),
        os.getenv("SHOPEE_SECRET")
    )
    
    try:
        await client.connect()
        
        # Test URL (exemplo da documentação)
        test_url = "https://shopee.com.br/Apple-Iphone-11-128GB-Local-Set-i.52377417.6309028319"
        
        print(f"\n1. Gerando short link para:")
        print(f"   {test_url}")
        
        short_link = await client.generate_short_link(
            origin_url=test_url,
            sub_ids=["s1", "s2", "s3", "s4", "s5"]
        )
        
        if short_link:
            print(f"\n   OK: Short link gerado!")
            print(f"   Link: {short_link}")
        else:
            print("\n   ERRO: Nao foi possivel gerar short link")
        
        # Test sem sub_ids
        print(f"\n2. Gerando short link sem sub_ids...")
        
        short_link2 = await client.generate_short_link(
            origin_url=test_url
        )
        
        if short_link2:
            print(f"   OK: {short_link2}")
        
        print("\n" + "="*60)
        print("TESTE CONCLUIDO")
        print("="*60)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_short_link())
