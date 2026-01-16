#!/usr/bin/env python3
"""
ITIL Service: Obtain/Build
OAuth consolidado para MercadoLivre

Consolida: ml_oauth_simple.py, ml_oauth_pkce.py, ml_oauth_server.py, ml_first_auth.py
Suporta: PKCE (recomendado), Simple (legacy), Server (callback local)
"""
import requests
import json
import time
import os
import sys
import argparse
import hashlib
import base64
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ML_APP_ID")
CLIENT_SECRET = os.getenv("ML_SECRET_KEY")
REDIRECT_URI = os.getenv("ML_REDIRECT_URI", "https://afiliadobot.top/ml-callback.html")
TOKEN_FILE = "meli_token.json"

def gerar_pkce():
    """Gera code_verifier e code_challenge para PKCE"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def oauth_pkce():
    """OAuth com PKCE (recomendado - mais seguro)"""
    print("="*70)
    print("MERCADO LIVRE OAuth PKCE (RECOMENDADO)")
    print("="*70)
    
    if not APP_ID:
        print("ERRO: ML_APP_ID nao configurado no .env")
        return False
    
    # Gerar PKCE
    code_verifier, code_challenge = gerar_pkce()
    
    print(f"\\nCode Verifier: {code_verifier[:30]}...")
    print(f"Code Challenge: {code_challenge[:30]}...")
    
    # URL de autorização
    url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    print("\\nPASSO 1: Abra esta URL no navegador:\\n")
    print(url)
    print("\\nPASSO 2: Apos autorizar, copie o CODE da pagina")
    print("PASSO 3: Cole o CODE aqui:\\n")
    
    code = input("CODE: ").strip()
    
    if not code:
        print("ERRO: CODE vazio")
        return False
    
    # Trocar CODE por TOKEN
    print("\\nTrocando CODE por TOKEN (com PKCE)...")
    
    try:
        response = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": APP_ID,
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier  # PKCE!
            },
            timeout=30
        )
        response.raise_for_status()
        
        tokens = response.json()
        tokens["expires_at"] = time.time() + tokens["expires_in"]
        
        # Salvar
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print("\\n" + "="*70)
        print("SUCESSO! Tokens obtidos")
        print("="*70)
        print(f"\\nAccess Token: {tokens['access_token'][:50]}...")
        print(f"Refresh Token: {tokens['refresh_token'][:30]}...")
        print(f"User ID: {tokens['user_id']}")
        
        print("\\n" + "="*70)
        print("ADICIONE AO .env:")
        print("="*70)
        print(f"ML_ACCESS_TOKEN={tokens['access_token']}")
        print(f"ML_REFRESH_TOKEN={tokens['refresh_token']}")
        print(f"ML_USER_ID={tokens['user_id']}")
        print("="*70)
        
        return True
        
    except requests.HTTPError as e:
        print(f"\\nERRO HTTP {e.response.status_code}")
        print(f"Resposta: {e.response.text}")
        return False
    except Exception as e:
        print(f"\\nERRO: {e}")
        return False

def oauth_simple():
    """OAuth simples (sem PKCE - requer desabilitar PKCE no painel ML)"""
    print("="*70)
    print("MERCADO LIVRE OAuth SIMPLES (SEM PKCE)")
    print("="*70)
    
    if not APP_ID or not CLIENT_SECRET:
        print("ERRO: ML_APP_ID e ML_SECRET_KEY nao configurados")
        return False
    
    print("\\nIMP ORTANTE: PKCE deve estar DESATIVADO no painel ML Developer")
    
    url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}"
    )
    
    print("\\nPASSO 1: Abra esta URL:\\n")
    print(url)
    print("\\nPASSO 2: Cole o CODE aqui:\\n")
    
    code = input("CODE: ").strip()
    
    if not code:
        print("ERRO: CODE vazio")
        return False
    
    print("\\nTrocando CODE por TOKEN (sem PKCE)...")
    
    try:
        response = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": APP_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI
            },
            timeout=30
        )
        response.raise_for_status()
        
        tokens = response.json()
        tokens["expires_at"] = time.time() + tokens["expires_in"]
        
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print("\\nSUCESSO! Tokens salvos em", TOKEN_FILE)
        return True
        
    except Exception as e:
        print(f"\\nERRO: {e}")
        return False

class CallbackHandler(BaseHTTPRequestHandler):
    """Handler para servidor callback OAuth"""
    code = None
    
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            CallbackHandler.code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Autorizacao concluida!</h1><p>Pode fechar esta janela.</p>")
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Silenciar logs

def oauth_server(port=8080):
    """OAuth com servidor callback local"""
    print("="*70)
    print("MERCADO LIVRE OAuth com SERVIDOR LOCAL")
    print("="*70)
    
    if not APP_ID:
        print("ERRO: ML_APP_ID nao configurado")
        return False
    
    redirect_local = f"http://localhost:{port}/callback"
    code_verifier, code_challenge = gerar_pkce()
    
    url = (
        f"https://auth.mercadolivre. com.br/authorization?"
        f"response_type=code&"
        f"client_id={APP_ID}&"
        f"redirect_uri={redirect_local}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    print(f"\\n1. Servidor rodando em http://localhost:{port}")
    print("\\n2. Abra esta URL no navegador:\\n")
    print(url)
    print("\\n3. Aguardando autorizacao...")
    
    # Iniciar servidor
    server = HTTPServer(('localhost', port), CallbackHandler)
    server.timeout = 120  # 2 minutos timeout
    server.handle_request()
    
    if CallbackHandler.code:
        print("\\nCODE recebido! Trocando por token...")
        
        try:
            response = requests.post(
                "https://api.mercadolibre.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": APP_ID,
                    "code": CallbackHandler.code,
                    "redirect_uri": redirect_local,
                    "code_verifier": code_verifier
                },
                timeout=30
            )
            response.raise_for_status()
            
            tokens = response.json()
            tokens["expires_at"] = time.time() + tokens["expires_in"]
            
            with open(TOKEN_FILE, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print("\\nSUCESSO! Tokens salvos em", TOKEN_FILE)
            return True
            
        except Exception as e:
            print(f"\\nERRO: {e}")
            return False
    else:
        print("\\nERRO: Timeout ou autorizacao cancelada")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='OAuth consolidado MercadoLivre (ITIL Obtain/Build)'
    )
    parser.add_argument(
        '--mode',
        choices=['pkce', 'simple', 'server'],
        default='pkce',
        help='Modo OAuth: pkce (recomendado), simple (legacy), server (callback local)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Porta para modo server (default: 8080)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'pkce':
        success = oauth_pkce()
    elif args.mode == 'simple':
        success = oauth_simple()
    else:  # server
        success = oauth_server(port=args.port)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
