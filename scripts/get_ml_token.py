"""
Script para obter Access Token do Mercado Livre
Método manual - sem necessidade de callback endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

ML_APP_ID = os.getenv("ML_APP_ID")
ML_SECRET_KEY = os.getenv("ML_SECRET_KEY")
REDIRECT_URI = "https://afiliadobot.top/api/ml/callback"

def generate_auth_url():
    """Gera URL de autorização"""
    url = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={ML_APP_ID}&redirect_uri={REDIRECT_URI}"
    return url


def exchange_code_for_token(code: str):
    """Troca o CODE por ACCESS_TOKEN"""
    url = "https://api.mercadolibre.com/oauth/token"
    
    payload = {
        "grant_type": "authorization_code",
        "client_id": ML_APP_ID,
        "client_secret": ML_SECRET_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("=" * 60)
        print("✅ TOKENS OBTIDOS COM SUCESSO!")
        print("=" * 60)
        print(f"\nAcesso Token: {data.get('access_token')}")
        print(f"Refresh Token: {data.get('refresh_token')}")
        print(f"Expira em: {data.get('expires_in')} segundos (~6 horas)")
        print("\n" + "=" * 60)
        print("COPIE E ADICIONE AO SEU .env:")
        print("=" * 60)
        print(f"ML_ACCESS_TOKEN={data.get('access_token')}")
        print(f"ML_REFRESH_TOKEN={data.get('refresh_token')}")
        print("=" * 60)
        
        return data
        
    except requests.HTTPError as e:
        print(f"❌ Erro HTTP: {e}")
        print(f"Resposta: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def main():
    print("=" * 60)
    print("MERCADO LIVRE - OBTER ACCESS TOKEN")
    print("=" * 60)
    
    if not ML_APP_ID or not ML_SECRET_KEY:
        print("❌ ML_APP_ID e ML_SECRET_KEY não configurados no .env")
        return
    
    print("\n📋 PASSO 1: Abra esta URL no navegador:\n")
    auth_url = generate_auth_url()
    print(auth_url)
    
    print("\n📋 PASSO 2: Após autorizar, você será redirecionado para:")
    print(f"{REDIRECT_URI}?code=TG-XXXXXXX")
    print("\n⚠️  O site pode dar erro 404 - IGNORE! Olhe apenas a URL")
    
    print("\n📋 PASSO 3: Copie o valor do 'code=' da URL e cole aqui:")
    code = input("\nCODE: ").strip()
    
    if not code:
        print("❌ Nenhum código fornecido")
        return
    
    print("\n🔄 Trocando CODE por ACCESS TOKEN...")
    exchange_code_for_token(code)


if __name__ == "__main__":
    main()
