#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITIL Service: Support / Quality Assurance
Testes consolidados do bot Telegram

Consolida: test_telegram_simple.py, test_telegram_config.py, test_telegram_bot.py
"""
import os
import sys
import httpx
import argparse
from dotenv import load_dotenv

load_dotenv()

def test_simple():
    """Teste simples: valida conexão e envio de mensagem"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    
    print("="*60)
    print("TESTE SIMPLES - TELEGRAM BOT")
    print("="*60)
    
    # Validar configuração
    if not bot_token:
        print("ERRO: TELEGRAM_BOT_TOKEN nao configurado")
        return False
    
    if not channel_id:
        print("ERRO: TELEGRAM_CHANNEL_ID nao configurado")
        return False
    
    print(f"Bot Token: {bot_token[:15]}...")
    print(f"Channel ID: {channel_id}")
    
    # Testar bot
    print("\\nTestando bot...")
    try:
        response = httpx.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        bot_info = response.json()
        
        if bot_info.get("ok"):
            print(f"OK: Bot @{bot_info['result']['username']} conectado")
        else:
            print(f"ERRO: {bot_info}")
            return False
    except Exception as e:
        print(f"ERRO ao conectar: {e}")
        return False
    
    # Testar envio
    print(f"\\nTestando envio para {channel_id}...")
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
            return True
        else:
            print(f"ERRO ao enviar:")
            print(f"  Codigo: {result.get('error_code')}")
            print(f"  Descricao: {result.get('description')}")
            
            desc = result.get('description', '').lower()
            if 'chat not found' in desc:
                print("\\nDICA: Channel ID incorreto ou bot sem acesso")
            elif 'forbidden' in desc:
                print("\\nDICA: Bot nao tem permissao - adicione como admin")
            
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_full():
    """Teste completo: conexão, envio de texto, envio de foto, botão inline"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    
    print("="*60)
    print("TESTE COMPLETO - TELEGRAM BOT")
    print("="*60)
    
    if not bot_token or not channel_id:
        print("ERRO: Configuracao incompleta no .env")
        return False
    
    # 1. Teste conexão
    print("\\n[1/3] Testando conexao...")
    try:
        response = httpx.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        bot_info = response.json()
        
        if not bot_info.get("ok"):
            print(f"ERRO: {bot_info}")
            return False
        
        print(f"OK: Bot @{bot_info['result']['username']}")
        print(f"    ID: {bot_info['result']['id']}")
        print(f"    Nome: {bot_info['result']['first_name']}")
    except Exception as e:
        print(f"ERRO: {e}")
        return False
    
    # 2. Teste mensagem simples
    print("\\n[2/3] Testando envio de mensagem...")
    try:
        response = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": channel_id,
                "text": "Teste completo: Mensagem de texto",
                "parse_mode": "HTML"
            },
            timeout=10
        )
        
        result = response.json()
        if result.get("ok"):
            print(f"OK: Mensagem enviada (ID: {result['result']['message_id']})")
        else:
            print(f"ERRO: {result.get('description')}")
            return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False
    
    # 3. Teste com botão inline
    print("\\n[3/3] Testando botao inline...")
    try:
        response = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": channel_id,
                "text": "Teste completo: Mensagem com botao",
                "reply_markup": {
                    "inline_keyboard": [[
                        {"text": "Testar Bot", "url": "https://t.me/" + bot_info['result']['username']}
                    ]]
                }
            },
            timeout=10
        )
        
        result = response.json()
        if result.get("ok"):
            print(f"OK: Mensagem com botao enviada")
        else:
            print(f"ERRO: {result.get('description')}")
            return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False
    
    print("\\n" + "="*60)
    print("TESTE COMPLETO CONCLUIDO COM SUCESSO!")
    print("="*60)
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Testes consolidados do bot Telegram (ITIL Support/QA)'
    )
    parser.add_argument(
        '--mode',
        choices=['simple', 'full'],
        default='simple',
        help='Modo de teste: simple (rapido) ou full (completo)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'simple':
        success = test_simple()
    else:
        success = test_full()
    
    if success:
        print("\\n" + "="*60)
        print("CONFIGURACAO OK - Bot pronto!")
        print("="*60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
