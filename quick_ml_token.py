import requests

APP_ID = "3818930890744242"
CLIENT_SECRET = "rxKqweGKOKFBDjsenfvNJ7lrN0Bb2LuN"
CODE = "TG-695d40b1f63ec400010a80b6-2307648221"
REDIRECT_URI = "https://afiliadobot.top/api/ml/callback"

url = "https://api.mercadolibre.com/oauth/token"

# Form-encoded payload
payload = {
    "grant_type": "authorization_code",
    "client_id": APP_ID,
    "client_secret": CLIENT_SECRET,
    "code": CODE,
    "redirect_uri": REDIRECT_URI
}

print("🔄 Trocando CODE por TOKEN...")

try:
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    print("\n" + "=" * 70)
    print("✅ SUCESSO! TOKENS OBTIDOS!")
    print("=" * 70)
    print(f"\nAccess Token: {data['access_token']}")
    print(f"Refresh Token: {data['refresh_token']}")
    print(f"User ID: {data['user_id']}")
    print(f"Expira em: {data['expires_in']} segundos")
    
    print("\n" + "=" * 70)
    print("📝 COPIE E ADICIONE AO .env:")
    print("=" * 70)
    print(f"ML_ACCESS_TOKEN={data['access_token']}")
    print(f"ML_REFRESH_TOKEN={data['refresh_token']}")
    print(f"ML_USER_ID={data['user_id']}")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Erro: {e}")
    if hasattr(e, 'response'):
        print(f"Resposta: {e.response.text}")
