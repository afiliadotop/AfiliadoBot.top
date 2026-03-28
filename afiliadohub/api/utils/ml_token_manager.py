"""
Mercado Livre Token Manager
Armazena tokens no Supabase (persistente) com fallback para arquivo local e .env
Garante que tokens sobrevivem a restarts no Render (ephemeral filesystem)
"""
import httpx
import json
import os
import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Arquivo local como fallback para desenvolvimento
TOKEN_FILE = "meli_token.json"
SUPABASE_SETTINGS_KEY = "ml_tokens"


def _get_supabase_headers() -> Optional[Dict[str, str]]:
    """Retorna headers para chamadas diretas à Supabase REST API"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def _get_supabase_rest_url() -> Optional[str]:
    """Retorna URL base da Supabase REST API"""
    url = os.getenv("SUPABASE_URL")
    if not url:
        return None
    return f"{url}/rest/v1"


class MLTokenManager:
    """
    Gerenciador de tokens ML com auto-refresh.
    Storage priority: Supabase → arquivo local → variáveis de ambiente
    """

    def __init__(self, app_id: str, client_secret: str):
        self.app_id = app_id
        self.client_secret = client_secret
        self.tokens: Optional[Dict] = None

    # ==================== LOAD ====================

    def _load_from_supabase(self) -> Optional[Dict]:
        """Carrega tokens do Supabase via REST API direta"""
        try:
            headers = _get_supabase_headers()
            rest_url = _get_supabase_rest_url()
            if not headers or not rest_url:
                return None
            import urllib.request
            url = f"{rest_url}/settings?key=eq.{SUPABASE_SETTINGS_KEY}&select=value&limit=1"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data and len(data) > 0:
                    tokens = data[0]["value"]
                    logger.info("[ML Token] Tokens carregados do Supabase")
                    return tokens
        except Exception as e:
            logger.warning(f"[ML Token] Erro ao carregar do Supabase: {e}")
        return None

    def _load_from_file(self) -> Optional[Dict]:
        """Carrega tokens do arquivo local"""
        try:
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as f:
                    tokens = json.load(f)
                logger.info("[ML Token] Tokens carregados do arquivo local")
                return tokens
        except Exception as e:
            logger.warning(f"[ML Token] Erro ao carregar arquivo: {e}")
        return None

    def _load_from_env(self) -> Optional[Dict]:
        """Carrega tokens das variáveis de ambiente"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            access_token = os.getenv("ML_ACCESS_TOKEN")
            refresh_token = os.getenv("ML_REFRESH_TOKEN")
            if access_token and refresh_token:
                logger.info("[ML Token] Tokens carregados do ambiente (.env)")
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": 21600,
                    "expires_at": time.time() + 21600  # assume válido por agora
                }
        except Exception as e:
            logger.warning(f"[ML Token] Erro ao carregar .env: {e}")
        return None

    def _load_tokens(self) -> Optional[Dict]:
        """Carrega tokens com prioridade: Supabase → arquivo → .env"""
        return (
            self._load_from_supabase()
            or self._load_from_file()
            or self._load_from_env()
        )

    # ==================== SAVE ====================

    def _save_tokens(self, data: Dict):
        """Salva tokens no Supabase e arquivo local"""
        data["expires_at"] = time.time() + data.get("expires_in", 21600)
        self.tokens = data

        # 1. Salvar no Supabase (storage primário)
        self._save_to_supabase(data)

        # 2. Salvar no arquivo local (fallback dev)
        self._save_to_file(data)

        logger.info(f"[ML Token] ✅ Tokens salvos. Expira em {data.get('expires_in', 21600)}s (~6h)")

    def _save_to_supabase(self, data: Dict):
        """Persiste tokens no Supabase settings via REST API direta"""
        try:
            headers = _get_supabase_headers()
            rest_url = _get_supabase_rest_url()
            if not headers or not rest_url:
                logger.warning("[ML Token] Supabase não configurado, pulando save")
                return
            payload = {
                "key": SUPABASE_SETTINGS_KEY,
                "value": {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token"),
                    "expires_in": data.get("expires_in", 21600),
                    "expires_at": data.get("expires_at"),
                    "user_id": data.get("user_id"),
                },
                "description": "Tokens OAuth ML - gerenciado automaticamente"
            }
            import urllib.request
            upsert_headers = {**headers, "Prefer": "resolution=merge-duplicates,return=minimal"}
            body = json.dumps(payload).encode()
            req = urllib.request.Request(
                f"{rest_url}/settings",
                data=body,
                headers=upsert_headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp.read()
            logger.info("[ML Token] ✅ Tokens salvos no Supabase")
        except Exception as e:
            logger.error(f"[ML Token] Erro ao salvar no Supabase: {e}")

    def _save_to_file(self, data: Dict):
        """Salva tokens no arquivo local (fallback)"""
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"[ML Token] Erro ao salvar arquivo local: {e}")

    # ==================== TOKEN LOGIC ====================

    async def get_valid_token(self) -> str:
        """Retorna access_token válido, renovando automaticamente se necessário"""
        if not self.tokens:
            self.tokens = self._load_tokens()

        if not self.tokens:
            raise Exception(
                "Tokens ML não encontrados. Configure ML_ACCESS_TOKEN e ML_REFRESH_TOKEN "
                "ou rode o fluxo OAuth: python scripts/auth/ml_oauth.py"
            )

        # Renova se faltar menos de 5 minutos para expirar
        expires_at = self.tokens.get("expires_at", 0)
        if time.time() > (expires_at - 300):
            logger.info("[ML Token] Token próximo da expiração, renovando...")
            return await self._refresh_token()

        return self.tokens["access_token"]

    async def _refresh_token(self) -> str:
        """Renova access_token usando refresh_token (refresh token é de uso único!)"""
        if not self.tokens or not self.tokens.get("refresh_token"):
            raise Exception("Refresh token não disponível — refaça o OAuth")

        url = "https://api.mercadolibre.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.app_id,
            "client_secret": self.client_secret,
            "refresh_token": self.tokens["refresh_token"]
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, data=payload)

            if response.status_code == 200:
                new_tokens = response.json()
                self._save_tokens(new_tokens)
                logger.info("[ML Token] ✅ Token renovado com sucesso!")
                return new_tokens["access_token"]
            else:
                error = response.json()
                msg = error.get("message", response.text)
                logger.error(f"[ML Token] ❌ Falha no refresh: {msg}")
                raise Exception(f"Falha no refresh do token ML: {msg}")


# ==================== HELPER GLOBAL ====================

async def get_ml_token() -> str:
    """
    Helper para obter token ML válido de qualquer parte do código.
    Usa Supabase como storage, renova automaticamente quando necessário.
    """
    from dotenv import load_dotenv
    load_dotenv()

    app_id = os.getenv("ML_APP_ID")
    client_secret = os.getenv("ML_SECRET_KEY")

    if not app_id or not client_secret:
        raise Exception(
            "ML_APP_ID e ML_SECRET_KEY não configurados nas variáveis de ambiente"
        )

    manager = MLTokenManager(app_id, client_secret)
    return await manager.get_valid_token()


# ==================== SCRIPT DE TESTE ====================

async def test_token():
    """Testa se os tokens estão funcionando"""
    print("=" * 70)
    print("TESTE DE TOKENS ML")
    print("=" * 70)

    try:
        token = await get_ml_token()
        print(f"\n✅ Token obtido: {token[:60]}...")

        # Testar chamada à API pública ML (não requer permissões especiais)
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                "https://api.mercadolibre.com/users/me",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ API funcionando!")
                print(f"  User: {data.get('nickname', 'N/A')}")
                print(f"  ID: {data.get('id', 'N/A')}")
            else:
                print(f"\n⚠️  API retornou: {response.status_code}")
                print(response.text[:200])

    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_token())
