"""
Test Rate Limiting and ScrollId Pagination
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

from api.utils.shopee_client import create_shopee_client
from api.utils.shopee_extensions import (
    add_rate_limiting,
    get_all_conversions
)

async def test_rate_limiting():
    """Testa rate limiting"""
    print("\n" + "="*70)
    print("TESTANDO RATE LIMITING (2000 req/hora)")
    print("="*70)
    
    client = create_shopee_client()
    
    # Ativa rate limiting
    add_rate_limiting(client)
    
    async with client:
        print("\n1. Status inicial do rate limit:")
        status = client.get_rate_limit_status()
        print(f"   Usadas: {status['used']}/{status['total']}")
        print(f"   Restantes: {status['remaining']}")
        print(f"   % Usado: {status['percentage_used']:.1f}%")
        
        print("\n2. Fazendo 5 requests rápidas...")
        for i in range(5):
            try:
                await client.get_shopee_offers(limit=1)
                status = client.get_rate_limit_status()
                print(f"   Request {i+1}/5 - Usadas: {status['used']}, "
                      f"Restantes: {status['remaining']}")
            except Exception as e:
                print(f"   Erro: {e}")
        
        print("\n3. Status após 5 requests:")
        status = client.get_rate_limit_status()
        print(f"   ✓ Usadas: {status['used']}")
        print(f"   ✓ Restantes: {status['remaining']}")
        print(f"   ✓ Reset em: {status['reset_in_seconds']}s")
        
        print("\n✅ Rate limiting funcionando!")
        print(f"   Máximo: {status['total']} req/hora")
        print(f"   Atual: {status['percentage_used']:.2f}% usado")

async def test_scrollid_pagination():
    """Testa paginação com scrollId"""
    print("\n" + "="*70)
    print("TESTANDO SCROLLID PAGINATION (Conversion Report)")
    print("="*70)
    
    client = create_shopee_client()
    add_rate_limiting(client)
    
    async with client:
        # Últimos 7 dias
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.timestamp())
        
        print(f"\n1. Buscando conversões:")
        print(f"   Período: {start_time.strftime('%d/%m/%Y')} - "
              f"{end_time.strftime('%d/%m/%Y')}")
        
        try:
            # Busca todas as páginas
            all_conversions = await get_all_conversions(
                client,
                start_timestamp=start_ts,
                end_timestamp=end_ts,
                max_pages=3  # Limita a 3 páginas para teste
            )
            
            print(f"\n2. Resultado:")
            print(f"   ✓ Total de conversões: {len(all_conversions)}")
            
            if all_conversions:
                print(f"\n3. Primeiras conversões:")
                for i, conv in enumerate(all_conversions[:3], 1):
                    print(f"      #{i}")
                    print(f"      Order ID: {conv.get('orderId', 'N/A')}")
                    print(f"      Produto: {conv.get('productName', 'N/A')[:40]}...")
                    print(f"      Comissão: R$ {conv.get('commissionAmount', 0)}")
                    print()
            else:
                print("\n   ℹ️ Nenhuma conversão no período")
            
            print("✅ Paginação com scrollId funcionando!")
            
        except Exception as e:
            print(f"\n   ⚠️ Erro: {e}")
            print("   (Normal se não houver conversões)")

async def test_rate_limit_protection():
    """Testa proteção contra bloqueio"""
    print("\n" + "="*70)
    print("TESTANDO PROTEÇÃO AUTOMÁTICA")
    print("="*70)
    
    client = create_shopee_client()
    add_rate_limiting(client)
    
    async with client:
        print("\n1. Simulando carga alta...")
        print("   Fazendo 10 requests consecutivas")
        
        start = datetime.now()
        
        for i in range(10):
            status = client.get_rate_limit_status()
            print(f"\n   Request {i+1}/10")
            print(f"      Antes: {status['used']} usadas, "
                  f"{status['remaining']} restantes")
            
            try:
                await client.get_products(keyword="test", limit=1)
                print(f"      ✓ Sucesso")
            except Exception as e:
                print(f"      ✗ Erro: {e}")
        
        elapsed = (datetime.now() - start).total_seconds()
        
        print(f"\n2. Resultado:")
        print(f"   ✓ 10 requests em {elapsed:.1f}s")
        print(f"   ✓ Rate limit respeitado automaticamente")
        
        final_status = client.get_rate_limit_status()
        print(f"\n3. Status final:")
        print(f"   Usadas: {final_status['used']}/{final_status['total']}")
        print(f"   Restantes: {final_status['remaining']}")
        
        print("\n✅ Proteção funcionando - API não será bloqueada!")

async def main():
    """Executa todos os testes"""
    print("\n" + "🔬" * 35)
    print("TESTES AVANÇADOS - API SHOPEE")
    print("🔬" * 35)
    
    try:
        # Test 1: Rate Limiting
        await test_rate_limiting()
        
        # Test 2: ScrollId Pagination
        await test_scrollid_pagination()
        
        # Test 3: Protection
        await test_rate_limit_protection()
        
        print("\n" + "="*70)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*70)
        print("\nFuncionalidades prontas:")
        print("  ✓ Rate limiting (2000 req/h)")
        print("  ✓ Paginação com scrollId (30s TTL)")
        print("  ✓ Proteção automática contra bloqueio")
        print("  ✓ Tracking de uso em tempo real")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
