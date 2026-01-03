# -*- coding: utf-8 -*-
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
channel_id = os.getenv("TELEGRAM_CHANNEL_ID")

print("="*60)
print("TESTE DE CONFIGURACAO DO TELEGRAM")
print("="*60)

if bot_token:
    print(f"Bot Token: {bot_token[:15]}...")
else:
    print("ERRO: TELEGRAM_BOT_TOKEN nao configurado")
    exit(1)

if channel_id:
    print(f"Channel ID: {channel_id}")
else:
    print("ERRO: TELEGRAM_CHANNEL_ID nao configurado")
    exit(1)

print("\nTestando bot...")

try:
    response = httpx.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
    bot_info = response.json()
    
    if bot_info.get("ok"):
        print(f"OK: Bot @{bot_info['result']['username']} conectado")
    else:
        print(f"ERRO: {bot_info}")
        exit(1)
except Exception as e:
    print(f"ERRO ao conectar: {e}")
    exit(1)

print(f"\nTestando envio para {channel_id}...")

try:
    response = httpx.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": channel_id,
            "text": "Teste de configuracao - Bot funcionando!"
        },
        timeout=10
    )
    
    result = response.json()
    
    if result.get("ok"):
        print("OK: Mensagem enviada com sucesso!")
        print(f"Message ID: {result['result']['message_id']}")
    else:
        print(f"ERRO ao enviar:")
        print(f"  Codigo: {result.get('error_code')}")
        print(f"  Descricao: {result.get('description')}")
        
        desc = result.get('description', '').lower()
        if 'chat not found' in desc:
            print("\nDICA: Channel ID incorreto ou bot sem acesso")
            print("  - Verifique se o ID esta correto")
            print("  - Para canais, o ID deve comecar com -100")
            print("  - Adicione o bot como admin do canal")
        elif 'bot was blocked' in desc:
            print("\nDICA: O canal/usuario bloqueou o bot")
        elif 'forbidden' in desc.lower():
            print("\nDICA: Bot nao tem permissao")
            print("  - Adicione o bot como admin do canal")
        
        exit(1)
        
except Exception as e:
    print(f"ERRO: {e}")
    exit(1)

print("\n" + "="*60)
print("CONFIGURACAO OK - Bot pronto!")
print("="*60)
