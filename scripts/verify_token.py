import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")

print("Verificando TELEGRAM_BOT_TOKEN...")
print(f"Token lido: {token}")
print(f"Comprimento: {len(token) if token else 0} caracteres")
print("Formato esperado: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
print("                  (9 digitos):(35 caracteres)")

if not token:
    print("\nTELEGRAM_BOT_TOKEN nao encontrado no .env!")
    exit(1)

# Verify format
parts = token.split(':')
if len(parts) != 2:
    print(f"\nToken com formato incorreto! Deve ter exatamente um ':'")
    print(f"   Encontrado: {len(parts)-1} separadores")
    exit(1)

bot_id, auth_token = parts

if not bot_id.isdigit():
    print(f"\nID do bot invalido! Deve ser apenas numeros.")
    print(f"   Encontrado: {bot_id}")
    exit(1)

if len(auth_token) < 30:
    print(f"\nToken de autenticacao parece curto ({len(auth_token)} chars)")

print(f"\nFormato OK!")
print(f"   Bot ID: {bot_id}")
print(f"   Auth Token: {auth_token[:10]}...{auth_token[-5:]}")

# Test with Telegram API
print("\nTestando com API do Telegram...")
url = f"https://api.telegram.org/bot{token}/getMe"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if response.status_code == 200 and data.get('ok'):
        bot_info = data['result']
        print(f"\nTOKEN VALIDO!")
        print(f"   Nome: {bot_info['first_name']}")
        print(f"   Username: @{bot_info['username']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"\nTOKEN INVALIDO!")
        print(f"   Codigo: {response.status_code}")
        print(f"   Erro: {data.get('description', 'Desconhecido')}")
        print(f"\nSolucao:")
        print("   1. Abra o Telegram")
        print("   2. Busque @BotFather")
        print("   3. Envie /mybots")
        print("   4. Escolha seu bot")
        print("   5. Clique em 'API Token'")
        print("   6. Copie o token completo (sem espacos)")
        
except Exception as e:
    print(f"\nErro ao testar: {e}")
