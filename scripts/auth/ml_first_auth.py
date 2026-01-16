"""
Mercado Livre - Primeira Autorização (Setup Manual)
Troca CODE por TOKEN usando form-encoded conforme documentação ML
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ML_APP_ID")
CLIENT_SECRET = os.getenv("ML_SECRET_KEY")
REDIRECT_URI = "https://afiliadobot.top/api/ml/callback"
TOKEN_FILE = "meli_token.json"

def salvar_token(token_data):
    """Salva tokens no arquivo JSON"""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"✅ Token salvo em {TOKEN_FILE}")

def trocar_code_por_token(code):
    """Troca authorization code por access token"""
    url = "https://api.mercadolibre.com/oauth/token"
    
    # IMPORTANTE: usar data= (form-encoded) ao invés de json=
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    print("🔄 Trocando CODE por ACCESS TOKEN...")
    print(f"CODE: {code[:30]}...")
    
    try:
        # Usar data= para enviar como application/x-www-form-urlencoded
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        
        print("\n" + "=" * 70)
        print("✅ TOKENS OBTIDOS COM SUCESSO!")
        print("=" * 70)
        print(f"Access Token: {token_data.get('access_token')[:50]}...")
        print(f"Refresh Token: {token_data.get('refresh_token')[:30]}...")
        print(f"Expira em: {token_data.get('expires_in')} segundos (~6 horas)")
        print(f"Token Type: {token_data.get('token_type')}")
        print(f"User ID: {token_data.get('user_id')}")
        
        # Salvar no arquivo JSON
        salvar_token(token_data)
        
        print("\n" + "=" * 70)
        print("📝 ADICIONE AO SEU .env:")
        print("=" * 70)
        print(f"ML_ACCESS_TOKEN={token_data.get('access_token')}")
        print(f"ML_REFRESH_TOKEN={token_data.get('refresh_token')}")
        print(f"ML_USER_ID={token_data.get('user_id')}")
        print("=" * 70)
        
        return token_data
        
    except requests.HTTPError as e:
        print(f"\n❌ Erro HTTP {e.response.status_code}")
        print(f"Resposta: {e.response.text}")
        
        if e.response.status_code == 400:
            error_data = e.response.json()
            if "invalid" in error_data.get("message", "").lower():
                print("\n⚠️  CODE INVÁLIDO OU EXPIRADO!")
                print("\n🔄 Gere um novo CODE:")
                print(f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={APP_ID}&redirect_uri={REDIRECT_URI}")
        
        return None
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return None


def main():
    print("=" * 70)
    print("MERCADO LIVRE - PRIMEIRA AUTORIZAÇÃO")
    print("=" * 70)
    
    if not APP_ID or not CLIENT_SECRET:
        print("❌ ML_APP_ID e ML_SECRET_KEY não configurados no .env")
        return
    
    print("\n📋 OPÇÕES:")
    print("1. Tentar o CODE que você já tem")
    print("2. Gerar novo CODE")
    
    opcao = input("\nEscolha (1 ou 2): ").strip()
    
    if opcao == "1":
        # Usar o CODE que você já copiou
        code = input("\nCole o CODE aqui: ").strip()
        if code:
            trocar_code_por_token(code)
        else:
            print("❌ CODE vazio")
    else:
        # Gerar URL para novo CODE
        auth_url = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={APP_ID}&redirect_uri={REDIRECT_URI}"
        print("\n📋 PASSO 1: Abra esta URL no navegador:\n")
        print(auth_url)
        print("\n📋 PASSO 2: Após autorizar, copie o CODE da URL")
        print("📋 PASSO 3: Cole aqui:")
        
        code = input("\nCODE: ").strip()
        if code:
            trocar_code_por_token(code)
        else:
            print("❌ CODE vazio")


if __name__ == "__main__":
    main()
