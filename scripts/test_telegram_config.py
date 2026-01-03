"""
Script para testar a configuração do Telegram Bot
"""
import os
import sys
import httpx
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_telegram_config():
    """Testa se o bot está configurado corretamente"""
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    
    print("[INFO] Verificando configuracao do Telegram...")
    print(f"Bot Token: {bot_token[:20]}..." if bot_token else "[ERRO] BOT_TOKEN nao configurado")
    print(f"Channel ID: {channel_id}" if channel_id else "[ERRO] CHANNEL_ID nao configurado")
    
    if not bot_token:
        print("\n[ERRO] TELEGRAM_BOT_TOKEN nao encontrado no .env")
        return False
    
    if not channel_id:
        print("\n[ERRO] TELEGRAM_CHANNEL_ID nao encontrado no .env")
        return False
    
    # Testa se o bot está funcionando
    print("\n[INFO] Testando conexao com a API do Telegram...")
    
    try:
        # Pega informações do bot
        response = httpx.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        response.raise_for_status()
        
        bot_info = response.json()
        
        if bot_info.get("ok"):
            print(f"✅ Bot conectado: @{bot_info['result']['username']}")
            print(f"   Nome: {bot_info['result']['first_name']}")
            print(f"   ID: {bot_info['result']['id']}")
        else:
            print(f"❌ Erro na API: {bot_info}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Telegram: {e}")
        return False
    
    # Testa envio de mensagem
    print(f"\n📤 Testando envio de mensagem para {channel_id}...")
    
    try:
        test_message = "🧪 Teste de configuração do bot - Se você está vendo isso, o bot está funcionando!"
        
        response = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": channel_id,
                "text": test_message
            },
            timeout=10
        )
        
        result = response.json()
        
        if result.get("ok"):
            print("✅ Mensagem enviada com sucesso!")
            print(f"   Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem:")
            print(f"   Código: {result.get('error_code')}")
            print(f"   Descrição: {result.get('description')}")
            
            # Dicas baseadas no erro
            error_code = result.get('error_code')
            description = result.get('description', '')
            
            if error_code == 400:
                if 'chat not found' in description.lower():
                    print("\n💡 DICA: O CHANNEL_ID está incorreto ou o bot não tem acesso a este chat.")
                    print("   - Verifique se o ID está correto")
                    print("   - Se for um canal, o ID deve começar com -100")
                    print("   - Adicione o bot como administrador do canal")
                elif 'bot was blocked' in description.lower():
                    print("\n💡 DICA: O usuário/canal bloqueou o bot.")
                else:
                    print("\n💡 DICA: Parâmetros inválidos na requisição.")
            elif error_code == 403:
                print("\n💡 DICA: O bot não tem permissão para enviar mensagens.")
                print("   - Certifique-se de que o bot foi adicionado como admin do canal")
            elif error_code == 404:
                print("\n💡 DICA: Bot não encontrado. Verifique o token.")
            
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar envio: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CONFIGURACAO DO TELEGRAM BOT")
    print("=" * 60)
    
    success = test_telegram_config()
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] CONFIGURACAO OK - Bot pronto para uso!")
    else:
        print("[ERRO] CONFIGURACAO COM PROBLEMAS - Verifique os erros acima")
    print("=" * 60)
