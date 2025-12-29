import os
from dotenv import load_dotenv
import requests

load_dotenv()

token = os.getenv("BOT_TOKEN")

print("🔍 Verificando BOT_TOKEN...")
print(f"Token lido: {token}")
print(f"Comprimento: {len(token) if token else 0} caracteres")
print(f"Formato esperado: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
print(f"                  (9 dígitos):(35 caracteres)")

if not token:
    print("\n❌ BOT_TOKEN não encontrado no .env!")
    exit(1)

# Verify format
parts = token.split(':')
if len(parts) != 2:
    print(f"\n❌ Token com formato incorreto! Deve ter exatamente um ':'")
    print(f"   Encontrado: {len(parts)-1} separadores")
    exit(1)

bot_id, auth_token = parts

if not bot_id.isdigit():
    print(f"\n❌ ID do bot inválido! Deve ser apenas números.")
    print(f"   Encontrado: {bot_id}")
    exit(1)

if len(auth_token) < 30:
    print(f"\n⚠️ Token de autenticação parece curto ({len(auth_token)} chars)")

print(f"\n✅ Formato OK!")
print(f"   Bot ID: {bot_id}")
print(f"   Auth Token: {auth_token[:10]}...{auth_token[-5:]}")

# Test with Telegram API
print("\n🌐 Testando com API do Telegram...")
url = f"https://api.telegram.org/bot{token}/getMe"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if response.status_code == 200 and data.get('ok'):
        bot_info = data['result']
        print(f"\n✅ TOKEN VÁLIDO!")
        print(f"   Nome: {bot_info['first_name']}")
        print(f"   Username: @{bot_info['username']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"\n❌ TOKEN INVÁLIDO!")
        print(f"   Código: {response.status_code}")
        print(f"   Erro: {data.get('description', 'Desconhecido')}")
        print(f"\n💡 Solução:")
        print(f"   1. Abra o Telegram")
        print(f"   2. Busque @BotFather")
        print(f"   3. Envie /mybots")
        print(f"   4. Escolha seu bot")
        print(f"   5. Clique em 'API Token'")
        print(f"   6. Copie o token completo (sem espaços)")
        
except Exception as e:
    print(f"\n❌ Erro ao testar: {e}")
