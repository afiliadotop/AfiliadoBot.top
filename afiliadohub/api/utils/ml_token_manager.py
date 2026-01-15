"""
Mercado Livre Token Manager
Gerencia access_token e refresh_token com auto-renovação
Baseado nas boas práticas ML (refresh token de uso único)
"""
import httpx
import json
import os
import time
from typing import Optional, Dict

TOKEN_FILE = "meli_token.json"

class MLTokenManager:
    """Gerenciador de tokens ML com auto-refresh"""
    
    def __init__(self, app_id: str, client_secret: str):
        self.app_id = app_id
        self.client_secret = client_secret
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Optional[Dict]:
        """Carrega tokens do arquivo JSON"""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        return None
    
    def _save_tokens(self, data: Dict):
        """Salva tokens com timestamp de expiração"""
        data["expires_at"] = time.time() + data["expires_in"]
        with open(TOKEN_FILE, "w") as f:
            json.dump(data, f, indent=2)
        self.tokens = data
        print(f"[ML Token] Tokens atualizados. Expira em {data['expires_in']}s (~6h)")
    
    async def get_valid_token(self) -> str:
        """Retorna access_token válido, renovando se necessário"""
        if not self.tokens:
            # Carregar do .env se não tiver arquivo
            from dotenv import load_dotenv
            load_dotenv()
            
            access_token = os.getenv("ML_ACCESS_TOKEN")
            refresh_token = os.getenv("ML_REFRESH_TOKEN")
            
            if not access_token or not refresh_token:
                raise Exception("Tokens ML não configurados nem no arquivo nem no .env")
            
            # Criar arquivo inicial
            self.tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": 21600,
                "expires_at": time.time() + 21600
            }
            self._save_tokens(self.tokens)
        
        # Se faltar menos de 5 minutos para expirar, renova agora
        if time.time() > (self.tokens.get("expires_at", 0) - 300):
            print("[ML Token] Próximo da expiração, renovando...")
            return await self._refresh_token()
        
        return self.tokens["access_token"]
    
    async def _refresh_token(self) -> str:
        """Renova access_token usando refresh_token (uso único!)"""
        if not self.tokens or not self.tokens.get("refresh_token"):
            raise Exception("Refresh token não disponível")
        
        url = "https://api.mercadolibre.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.app_id,
            "client_secret": self.client_secret,
            "refresh_token": self.tokens["refresh_token"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                new_tokens = response.json()
                self._save_tokens(new_tokens)
                print(f"[ML Token] ✅ Token renovado com sucesso!")
                return new_tokens["access_token"]
            else:
                error = response.json()
                raise Exception(f"Falha no refresh: {error.get('message', response.text)}")


# Funções auxiliares para uso fácil
async def get_ml_token() -> str:
    """Helper para obter token válido"""
    from dotenv import load_dotenv
    load_dotenv()
    
    app_id = os.getenv("ML_APP_ID")
    client_secret = os.getenv("ML_SECRET_KEY")
    
    if not app_id or not client_secret:
        raise Exception("ML_APP_ID e ML_SECRET_KEY não configurados")
    
    manager = MLTokenManager(app_id, client_secret)
    return await manager.get_valid_token()


# Script de teste
async def test_token():
    """Testa se os tokens estão funcionando"""
    print("=" * 70)
    print("TESTE DE TOKENS ML")
    print("=" * 70)
    
    try:
        token = await get_ml_token()
        print(f"\n✅ Token obtido: {token[:50]}...")
        
        # Testar chamada à API ML
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            # Buscar produtos
            response = await client.get(
                "https://api.mercadolibre.com/sites/MLB/search?q=iphone&limit=3",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ API funcionando! Encontrados {len(data.get('results', []))} produtos")
                
                # Mostrar primeiro produto
                if data.get("results"):
                    p = data["results"][0]
                    print(f"\nProduto de teste:")
                    print(f"  - {p['title']}")
                    print(f"  - R$ {p['price']}")
                    
            else:
                print(f"\n❌ Erro na API: {response.status_code}")
                print(response.text)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_token())
