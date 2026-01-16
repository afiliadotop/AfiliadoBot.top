"""
Servidor local para capturar CODE do Mercado Livre automaticamente
"""
from flask import Flask, request
import hashlib
import base64
import secrets
import requests
import json
import webbrowser
import threading

app = Flask(__name__)

APP_ID = "3818930890744242"
CLIENT_SECRET = "rxKqweGKOKFBDjsenfvNJ7lrN0Bb2LuN"
REDIRECT_URI = "http://localhost:5000/callback"

# Variáveis globais
code_verifier = None
tokens = None

def gerar_code_verifier():
    """Gera code_verifier aleatório"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def gerar_code_challenge(verifier):
    """Gera code_challenge (SHA256 do verifier)"""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

@app.route('/')
def index():
    """Página inicial - inicia o processo OAuth"""
    global code_verifier
    
    code_verifier = gerar_code_verifier()
    code_challenge = gerar_code_challenge(code_verifier)
    
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    return f'''
    <html>
    <head><title>ML OAuth</title></head>
    <body style="font-family: Arial; padding: 50px; background: #f5f5f5;">
        <h1>🔐 Mercado Livre - Autorização</h1>
        <p>Clique no botão abaixo para autorizar:</p>
        <a href="{auth_url}" style="background: #3483fa; color: white; padding: 15px 30px; 
           text-decoration: none; border-radius: 5px; display: inline-block;">
           🚀 Autorizar Aplicação
        </a>
        <br><br>
        <p style="color: #666; font-size: 14px;">
        Após autorizar, você será redirecionado automaticamente e os tokens aparecerão aqui.
        </p>
    </body>
    </html>
    '''

@app.route('/callback')
def callback():
    """Callback - recebe o CODE e troca por tokens"""
    global code_verifier, tokens
    
    code = request.args.get('code')
    
    if not code:
        return '<h1>❌ Erro: CODE não recebido</h1>', 400
    
    # Trocar CODE por TOKEN
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        
        tokens = response.json()
        
        # Salvar em arquivo
        with open('meli_token.json', 'w') as f:
            json.dump(tokens, f, indent=2)
        
        return f'''
        <html>
        <head><title>✅ Sucesso!</title></head>
        <body style="font-family: Arial; padding: 50px; background: #f5f5f5;">
            <h1>✅ TOKENS OBTIDOS COM SUCESSO!</h1>
            
            <h2>📝 Copie e adicione ao .env:</h2>
            <div style="background: #fff; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <pre style="background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto;">
ML_ACCESS_TOKEN={tokens['access_token']}
ML_REFRESH_TOKEN={tokens['refresh_token']}
ML_USER_ID={tokens['user_id']}
                </pre>
            </div>
            
            <h3>Informações:</h3>
            <ul>
                <li>User ID: {tokens['user_id']}</li>
                <li>Expira em: {tokens['expires_in']} segundos (~6 horas)</li>
                <li>Tokens salvos em: meli_token.json</li>
            </ul>
            
            <p style="color: green; font-weight: bold;">
            ✅ Pode fechar esta janela e parar o servidor (Ctrl+C no terminal)
            </p>
        </body>
        </html>
        '''
        
    except requests.HTTPError as e:
        return f'''
        <html>
        <body style="font-family: Arial; padding: 50px;">
            <h1>❌ Erro ao trocar CODE</h1>
            <p>Status: {e.response.status_code}</p>
            <pre>{e.response.text}</pre>
        </body>
        </html>
        ''', 400

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 SERVIDOR LOCAL OAUTH ML")
    print("=" * 70)
    print("\n1. Servidor iniciando em http://localhost:5000")
    print("2. Abrindo navegador automaticamente...")
    print("3. Clique em 'Autorizar Aplicação'")
    print("4. Após autorizar, os tokens aparecerão na página")
    print("\n⚠️  IMPORTANTE: Configure no ML Developer:")
    print("   Redirect URI: http://localhost:5000/callback")
    print("\n" + "=" * 70)
    
    # Abrir navegador após 1 segundo
    def abrir_navegador():
        import time
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Iniciar servidor
    app.run(port=5000, debug=False)
