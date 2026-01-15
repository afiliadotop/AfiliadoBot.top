"""
Mercado Livre OAuth com PKCE (Proof Key for Code Exchange)
Gera code_verifier, code_challenge e faz o fluxo completo
"""
import hashlib
import base64
import secrets
import requests
import json

# Configurações
APP_ID = "3818930890744242"
CLIENT_SECRET = "rxKqweGKOKFBDjsenfvNJ7lrN0Bb2LuN"
REDIRECT_URI = "https://afiliadobot.top/api/ml/callback"

def gerar_code_verifier():
    """Gera code_verifier aleatório (43-128 caracteres)"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def gerar_code_challenge(verifier):
    """Gera code_challenge (SHA256 do verifier)"""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

def gerar_url_autorizacao():
    """Gera URL de autorização com PKCE"""
    code_verifier = gerar_code_verifier()
    code_challenge = gerar_code_challenge(code_verifier)
    
    # Salvar code_verifier para usar depois
    with open('ml_pkce.json', 'w') as f:
        json.dump({'code_verifier': code_verifier}, f)
    
    url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    print("=" * 70)
    print("STEP 1: GERAR URL COM PKCE")
    print("=" * 70)
    print(f"\n✅ Code Verifier gerado e salvo em ml_pkce.json")
    print(f"✅ Code Challenge: {code_challenge[:30]}...")
    print(f"\n📋 ABRA ESTA URL NO NAVEGADOR:\n")
    print(url)
    print("\n" + "=" * 70)
    
    return code_verifier

def trocar_code_por_token(code, code_verifier):
    """Troca CODE por ACCESS_TOKEN usando PKCE"""
    url = "https://api.mercadolibre.com/oauth/token"
    
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier  # PKCE
    }
    
    print("\n" + "=" * 70)
    print("STEP 2: TROCAR CODE POR TOKEN")
    print("=" * 70)
    print(f"CODE: {code[:30]}...")
    print(f"Code Verifier: {code_verifier[:30]}...")
    print("\n🔄 Enviando requisição...")
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Salvar tokens
        with open('meli_token.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ TOKENS OBTIDOS COM SUCESSO!")
        print("=" * 70)
        print(f"\nAccess Token: {data['access_token'][:50]}...")
        print(f"Refresh Token: {data['refresh_token'][:30]}...")
        print(f"User ID: {data['user_id']}")
        print(f"Expira em: {data['expires_in']} segundos (~6 horas)")
        
        print("\n" + "=" * 70)
        print("📝 COPIE E ADICIONE AO .env:")
        print("=" * 70)
        print(f"ML_ACCESS_TOKEN={data['access_token']}")
        print(f"ML_REFRESH_TOKEN={data['refresh_token']}")
        print(f"ML_USER_ID={data['user_id']}")
        print("=" * 70)
        
        print(f"\n✅ Tokens salvos em meli_token.json")
        
        return data
        
    except requests.HTTPError as e:
        print(f"\n❌ Erro HTTP {e.response.status_code}")
        print(f"Resposta: {e.response.text}")
        return None
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return None

def main():
    print("\n" + "=" * 70)
    print("MERCADO LIVRE OAUTH COM PKCE")
    print("=" * 70)
    
    # Opção 1: Gerar nova URL
    print("\n📋 OPÇÕES:")
    print("1. Gerar nova URL de autorização (com PKCE)")
    print("2. Já tenho o CODE - trocar por token")
    
    opcao = input("\nEscolha (1 ou 2): ").strip()
    
    if opcao == "1":
        code_verifier = gerar_url_autorizacao()
        print("\n📋 Após autorizar, copie o CODE e execute este script novamente escolhendo opção 2")
        
    elif opcao == "2":
        # Carregar code_verifier salvo
        try:
            with open('ml_pkce.json', 'r') as f:
                data = json.load(f)
                code_verifier = data['code_verifier']
        except FileNotFoundError:
            print("❌ Arquivo ml_pkce.json não encontrado!")
            print("Execute primeiro a opção 1 para gerar a URL com PKCE")
            return
        
        code = input("\nCole o CODE aqui: ").strip()
        if code:
            trocar_code_por_token(code, code_verifier)
        else:
            print("❌ CODE vazio")
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    main()
