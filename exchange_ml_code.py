"""
Troca CODE por ACCESS TOKEN do Mercado Livre (sem PKCE)
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ML_APP_ID = os.getenv("ML_APP_ID")
ML_SECRET_KEY = os.getenv("ML_SECRET_KEY")
CODE = "TG-695d2ec34ff75f00019fb064-2307648221"
REDIRECT_URI = "https://afiliadobot.top/api/ml/callback"

url = "https://api.mercadolibre.com/oauth/token"

# Usar form-encoded ao invés de JSON
payload = {
    "grant_type": "authorization_code",
    "client_id": ML_APP_ID,
    "client_secret": ML_SECRET_KEY,
    "redirect_uri": REDIRECT_URI,
    "code": CODE
}

print("🔄 Trocando CODE por ACCESS TOKEN (method 2 - form-encoded)...")
print(f"CODE: {CODE}")

try:
    # Usar data= ao invés de json= para enviar como form
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    print("\n" + "=" * 70)
    print("✅ TOKENS OBTIDOS COM SUCESSO!")
    print("=" * 70)
    print(f"\nAccess Token: {data.get('access_token')}")
    print(f"Refresh Token: {data.get('refresh_token')}")
    print(f"Expira em: {data.get('expires_in')} segundos (~6 horas)")
    print(f"User ID: {data.get('user_id')}")
    print("\n" + "=" * 70)
    print("📝 COPIE ESTAS LINHAS E SUBSTITUA NO SEU .env:")
    print("=" * 70)
    print(f"ML_ACCESS_TOKEN={data.get('access_token')}")
    print(f"ML_REFRESH_TOKEN={data. get('refresh_token')}")
    print("=" * 70)
    print("\n✅ Agora você pode deletar o line com o CODE do .env!")
    
except requests.HTTPError as e:
    print(f"\n❌ Erro HTTP {e.response.status_code}")
    print(f"Resposta: {e.response.text}")
    
    if "code_verifier" in e.response.text or "invalid" in e.response.text:
        print("\n⚠️  O CODE provavelmente expirou (válido por apenas 10 minutos)")
        print("\n🔄 Gere um novo CODE abrindo novamente:")
        print(f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={ML_APP_ID}&redirect_uri={REDIRECT_URI}")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")
