"""
Shopee API - Rate Limiting & ScrollId Extensions
Adiciona funcionalidades avançadas ao cliente Shopee
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter para API Shopee (2000 requests/hora)
    """
    
    MAX_REQUESTS_PER_HOUR = 2000
    WINDOW_SECONDS = 3600  # 1 hora
    
    def __init__(self):
        self._requests: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Aguarda até que seja seguro fazer uma request
        Bloqueia automaticamente se limite atingido
        """
        async with self._lock:
            now = time.time()
            cutoff = now - self.WINDOW_SECONDS
            
            # Remove requests antigas
            self._requests = [ts for ts in self._requests if ts > cutoff]
            
            # Se atingiu limite, aguarda
            if len(self._requests) >= self.MAX_REQUESTS_PER_HOUR:
                oldest = self._requests[0]
                wait_time = self.WINDOW_SECONDS - (now - oldest)
                
                if wait_time > 0:
                    logger.warning(
                        f"⚠️ Rate limit atingido! "
                        f"Aguardando {wait_time:.0f}s..."
                    )
                    await asyncio.sleep(wait_time + 1)
                    self._requests.clear()
            
            # Registra request
            self._requests.append(time.time())
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do rate limit"""
        now = time.time()
        cutoff = now - self.WINDOW_SECONDS
        
        valid = [ts for ts in self._requests if ts > cutoff]
        used = len(valid)
        remaining = self.MAX_REQUESTS_PER_HOUR - used
        
        reset_in = 0
        if valid:
            oldest = min(valid)
            reset_in = max(0, self.WINDOW_SECONDS - (now - oldest))
        
        return {
            "used": used,
            "remaining": remaining,
            "total": self.MAX_REQUESTS_PER_HOUR,
            "reset_in_seconds": int(reset_in),
            "percentage_used": (used / self.MAX_REQUESTS_PER_HOUR) * 100
        }


class ScrollIdPaginator:
    """
    Paginador usando scrollId (válido por 30 segundos)
    Para queries como conversionReport
    """
    
    SCROLL_ID_TTL = 30  # segundos
    
    def __init__(self, client, query_fn):
        """
        Args:
            client: ShopeeAffiliateClient instance
            query_fn: Função async que aceita scroll_id como parâmetro
        """
        self.client = client
        self.query_fn = query_fn
        self.last_scroll_time = None
    
    async def fetch_all_pages(
        self,
        max_pages: Optional[int] = None,
        delay_between_pages: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Busca todas as páginas usando scrollId
        
        Args:
            max_pages: Número máximo de páginas (None = todas)
            delay_between_pages: Delay entre requests (segundos)
        
        Returns:
            Lista com todos os nodes de todas as páginas
        """
        all_nodes = []
        scroll_id = None
        page = 1
        
        while True:
            logger.info(f"[Paginator] Buscando página {page}...")
            
            # Verifica tempo desde último scroll
            if scroll_id and self.last_scroll_time:
                elapsed = time.time() - self.last_scroll_time
                if elapsed > self.SCROLL_ID_TTL:
                    logger.warning(
                        f"⚠️ ScrollId expirou ({elapsed:.0f}s > {self.SCROLL_ID_TTL}s)! "
                        "Reiniciando paginação..."
                    )
                    scroll_id = None
                    page = 1
            
            # Faz request
            try:
                result =await self.query_fn(scroll_id=scroll_id)
            except Exception as e:
                logger.error(f"Erro na página {page}: {e}")
                break
            
            # Extrai dados
            nodes = result.get("nodes", [])
            new_scroll_id = result.get("scrollId")
            
            if nodes:
                all_nodes.extend(nodes)
                logger.info(f"✓ Página {page}: {len(nodes)} items")
            
            # Atualiza scroll tracking
            if new_scroll_id:
                scroll_id = new_scroll_id
                self.last_scroll_time = time.time()
            
            # Para se não há mais páginas
            if not new_scroll_id or not nodes:
                logger.info(f"✓ Paginação completa: {len(all_nodes)} items totais")
                break
            
            # Para se atingiu limite
            if max_pages and page >= max_pages:
                logger.info(f"✓ Limite de páginas atingido: {page}")
                break
            
            # Delay antes da próxima página
            logger.debug(f"Aguardando {delay_between_pages}s...")
            await asyncio.sleep(delay_between_pages)
            
            page += 1
        
        return all_nodes


# Exemplo de uso com conversionReport
async def get_all_conversions(
    client,
    start_timestamp: int,
    end_timestamp: int,
    max_pages: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Busca todas as conversões usando paginação scrollId
    
    Args:
        client: ShopeeAffiliateClient
        start_timestamp: Início do período
        end_timestamp: Fim do período
        max_pages: Máximo de páginas (None = todas)
    
    Returns:
        Lista com todas as conversões
    """
    async def query_fn(scroll_id=None):
        return await client.get_conversion_report(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            scroll_id=scroll_id
        )
    
    paginator = ScrollIdPaginator(client, query_fn)
    return await paginator.fetch_all_pages(max_pages=max_pages)


# Integração no cliente
def add_rate_limiting(client):
    """
    Adiciona rate limiting a um ShopeeAffiliateClient existente
    
    Usage:
        client = create_shopee_client()
        add_rate_limiting(client)
    """
    if not hasattr(client, '_rate_limiter'):
        client._rate_limiter = RateLimiter()
        
        # Wrap graphql_query original
        original_query = client.graphql_query
        
        async def rate_limited_query(query, variables=None, operation_name=None):
            await client._rate_limiter.acquire()
            return await original_query(query, variables, operation_name)
        
        client.graphql_query = rate_limited_query
        client.get_rate_limit_status = lambda: client._rate_limiter.get_status()
        
        logger.info("✅ Rate limiting ativado (2000 req/h)")
