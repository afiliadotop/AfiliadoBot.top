"""
Manual Shopee Import Script
Run this to manually import products from Shopee API to Supabase
"""

import sys
import os
import asyncio

# Fix encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from dotenv import load_dotenv
load_dotenv()

from api.utils.shopee_importer import run_shopee_import

async def main():
    """Executa importação manual"""
    print("\n" + "="*60)
    print("SHOPEE PRODUCT IMPORT")
    print("="*60)
    
    print("\nOpcoes de importacao:")
    print("1. Importar todos os produtos (limit: 100)")
    print("2. Atualizar produtos existentes")
    print("3. Importar ofertas de marca")
    
    choice = input("\nEscolha uma opcao (1-3): ")
    
    import_type = "all"
    limit = 100
    min_commission = 5.0
    
    if choice == "1":
        import_type = "all"
        limit_input = input("Limite de produtos (enter para 100): ")
        if limit_input:
            limit = int(limit_input)
        
        commission_input = input("Comissao minima % (enter para 5.0): ")
        if commission_input:
            min_commission = float(commission_input)
    
    elif choice == "2":
        import_type = "update"
    
    elif choice == "3":
        import_type = "offers"
    
    else:
        print("Opcao invalida!")
        return
    
    print(f"\nIniciando importacao...")
    print(f"Tipo: {import_type}")
    if import_type == "all":
        print(f"Limite: {limit}")
        print(f"Comissao minima: {min_commission}%")
    
    # Execute import
    result = await run_shopee_import(
        import_type=import_type,
        limit=limit,
        min_commission=min_commission
    )
    
    # Show results
    print("\n" + "="*60)
    print("RESULTADO DA IMPORTACAO")
    print("="*60)
    print(f"\nProdutos Importados: {result.get('imported', 0)}")
    print(f"Produtos Atualizados: {result.get('updated', 0)}")
    print(f"Erros: {result.get('errors', 0)}")
    print(f"Duracao: {result.get('duration', 0):.1f}s")
    
    if result.get('error_messages'):
        print("\nErros:")
        for error in result.get('error_messages', [])[:5]:
            print(f"  - {error}")
    
    print("\nImportacao concluida!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nImportacao cancelada pelo usuario.")
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
