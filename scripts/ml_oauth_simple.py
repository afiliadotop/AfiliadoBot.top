"""
Mercado Livre OAuth SIMPLES (sem PKCE)
Após desativar PKCE no painel ML Developer
"""
import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ML_APP_ID")
CLIENT_SECRET = os.getenv("ML_SECRET_KEY")
REDIRECT_URI = "https://afiliadobot.top/ml-callback.html"
TOKEN_FILE = "meli_token.json"

def gerar_url_autorizacao():
    """Gera URL simples sem PKCE"""
    url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}"
    )
    return url

def trocar_code_por_token(code):
    """Troca CODE por ACCESS_TOKEN (sem code_verifier)"""
    url = "https://api.mercadolibre.com/oauth/token"
    
    # SEM code_verifier!
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    print("🔄 Trocando CODE por TOKEN (sem PKCE)...")
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        tokens = response.json()
        
        # Adicionar timestamp de expiração
        tokens["expires_at"] = time.time() + tokens["expires_in"]
        
        # Salvar tokens
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ TOKENS OBTIDOS COM SUCESSO!")
        print("=" * 70)
        print(f"\nAccess Token: {tokens['access_token'][:50]}...")
        print(f"Refresh Token: {tokens['refresh_token'][:30]}...")
        print(f"User ID: {tokens['user_id']}")
        print(f"Expira em: {tokens['expires_in']} segundos (~6 horas)")
        
        print("\n" + "=" * 70)
        print("📝 ADICIONE AO .env:")
        print("=" * 70)
        print(f"ML_ACCESS_TOKEN={tokens['access_token']}")
        print(f"ML_REFRESH_TOKEN={tokens['refresh_token']}")
        print(f"ML_USER_ID={tokens['user_id']}")
        print("=" * 70)
        
        print(f"\n✅ Tokens salvos em {TOKEN_FILE}")
        
        return tokens
        
    except requests.HTTPError as e:
        print(f"\n❌ Erro HTTP {e.response.status_code}")
        print(f"Resposta: {e.response.text}")
        
        if "code_verifier" in e.response.text:
            print("\n⚠️  PKCE AINDA ESTÁ ATIVO!")
            print("Você precisa desativar PKCE no painel ML Developer primeiro.")
        
        return None
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return None

def main():
    print("=" * 70)
    print("MERCADO LIVRE OAUTH SIMPLES (SEM PKCE)")
    print("=" * 70)
    
    if not APP_ID or not CLIENT_SECRET:
        print("❌ ML_APP_ID e ML_SECRET_KEY não configurados no .env")
        return
    
    print("\n⚠️  IMPORTANTE: Certifique-se de que PKCE está DESATIVADO")
    print("no painel ML Developer antes de continuar!\n")
    
    print("📋 PASSO 1: Abra esta URL no navegador:\n")
    url = gerar_url_autorizacao()
    print(url)
    
    print("\n📋 PASSO 2: Após autorizar, copie o CODE da página")
    print("📋 PASSO 3: Cole o CODE aqui:\n")
    
    code = input("CODE: ").strip()
    
    if code:
        trocar_code_por_token(code)
    else:
        print("❌ CODE vazio")

if __name__ == "__main__":
    main()
