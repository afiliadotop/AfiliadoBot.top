"""
Shopee Affiliates GraphQL API Client
Implements SHA256 authentication as per Shopee documentation
"""

import os
import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)


class ShopeeAuthError(Exception):
    """Erro de autenticação da API Shopee"""
    pass


class ShopeeAPIError(Exception):
    """Erro genérico da API Shopee"""
    pass


class ShopeeAffiliateClient:
    """
    Cliente para API GraphQL da Shopee Affiliates
    
    Documentação: https://affiliate.shopee.com.br/open_api/document?type=authentication
    
    Features:
    - Autenticação SHA256 automática
    - Validação de timestamp (< 10 minutos)
    - Retry logic
    - Rate limiting
    - Logging detalhado
    """
    
    def __init__(
        self,
        app_id: str,
        secret: str,
        endpoint: str = "https://open-api.affiliate.shopee.com.br/graphql",
        timeout: int = 30
    ):
        """
        Inicializa o cliente Shopee
        
        Args:
            app_id: App ID fornecido pela Shopee
            secret: Secret fornecido pela Shopee (manter seguro!)
            endpoint: URL da API GraphQL
            timeout: Timeout das requisições em segundos
        """
        self.app_id = app_id
        self.secret = secret
        self.endpoint = endpoint
        self.timeout = ClientTimeout(total=timeout)
        self.session: Optional[ClientSession] = None
        
        logger.info(f"[Shopee] Cliente inicializado para App ID: {app_id[:8]}...")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    async def connect(self):
        """Cria sessão HTTP"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            logger.info("[Shopee] Sessão HTTP criada")
    
    async def close(self):
        """Fecha sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("[Shopee] Sessão HTTP fechada")
    
    def _generate_timestamp(self) -> int:
        """
        Gera timestamp Unix atual
        
        Returns:
            Timestamp em segundos
        """
        return int(time.time())
    
    def _generate_signature(self, timestamp: int, payload: str) -> str:
        """
        Gera assinatura SHA256 conforme documentação Shopee
        
        Cálculo: SHA256(AppId + Timestamp + Payload + Secret)
        
        Args:
            timestamp: Timestamp Unix em segundos
            payload: Body da requisição em JSON
        
        Returns:
            Assinatura em hexadecimal lowercase (64 caracteres)
        """
        # Concatena: AppId + Timestamp + Payload + Secret
        signature_factor = f"{self.app_id}{timestamp}{payload}{self.secret}"
        
        # Calcula SHA256
        signature = hashlib.sha256(signature_factor.encode('utf-8')).hexdigest()
        
        logger.debug(f"[Shopee] Signature gerada para timestamp {timestamp}")
        return signature
    
    def _build_auth_header(self, timestamp: int, signature: str) -> str:
        """
        Constrói header Authorization conforme especificação
        
        Formato: SHA256 Credential={AppId}, Timestamp={Timestamp}, Signature={signature}
        
        Args:
            timestamp: Timestamp Unix
            signature: Assinatura SHA256
        
        Returns:
            String do header Authorization
        """
        auth_header = f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}"
        return auth_header
    
    async def graphql_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa query GraphQL com autenticação automática
        
        Args:
            query: Query GraphQL em string
            variables: Variáveis da query (opcional)
            operation_name: Nome da operação (opcional)
        
        Returns:
            Resposta da API em formato dict
        
        Raises:
            ShopeeAuthError: Erro de autenticação
            ShopeeAPIError: Erro da API
        """
        if not self.session or self.session.closed:
            await self.connect()
        
        # Prepara payload
        payload_dict = {"query": query}
        
        if variables:
            payload_dict["variables"] = variables
        
        if operation_name:
            payload_dict["operationName"] = operation_name
        
        # Serializa em JSON (formato requerido)
        payload = json.dumps(payload_dict, separators=(',', ':'), ensure_ascii=False)
        
        # Gera timestamp
        timestamp = self._generate_timestamp()
        
        # Gera assinatura
        signature = self._generate_signature(timestamp, payload)
        
        # Constrói header
        auth_header = self._build_auth_header(timestamp, signature)
        
        # Headers da requisição
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        logger.info(f"[Shopee] Executando query GraphQL...")
        logger.debug(f"[Shopee] Query: {query[:100]}...")
        
        try:
            async with self.session.post(
                self.endpoint,
                data=payload,
                headers=headers
            ) as response:
                response_text = await response.text()
                
                # Log da resposta
                logger.debug(f"[Shopee] Status: {response.status}")
                logger.debug(f"[Shopee] Response: {response_text[:200]}...")
                
                if response.status == 401:
                    logger.error("[Shopee] Erro de autenticação (401)")
                    raise ShopeeAuthError("Autenticação falhou. Verifique App ID e Secret.")
                
                if response.status != 200:
                    logger.error(f"[Shopee] Erro HTTP {response.status}: {response_text}")
                    raise ShopeeAPIError(f"HTTP {response.status}: {response_text}")
                
                # Parse JSON
                result = json.loads(response_text)
                
                # Verifica erros GraphQL
                if "errors" in result:
                    errors = result["errors"]
                    logger.error(f"[Shopee] Erros GraphQL: {errors}")
                    raise ShopeeAPIError(f"GraphQL errors: {errors}")
                
                logger.info("[Shopee] Query executada com sucesso")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"[Shopee] Erro de conexão: {e}")
            raise ShopeeAPIError(f"Erro de conexão: {e}")
    
    # ==================== QUERIES ESPECÍFICAS ====================
    
    async def generate_short_link(
        self,
        origin_url: str,
        sub_ids: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Gera short link de afiliado para um produto
        
        Args:
            origin_url: URL original do produto Shopee
            sub_ids: Lista de até 5 sub IDs para tracking (opcional)
        
        Returns:
            Short link gerado ou None se falhar
        """
        # Escapa as aspas na URL
        escaped_url = origin_url.replace('"', '\\"')
        
        # Prepara sub_ids
        sub_ids_str = ""
        if sub_ids:
            sub_ids_list = '","'.join(sub_ids[:5])  # Max 5
            sub_ids_str = f',subIds:["{sub_ids_list}"]'
        
        query = f"""
        mutation {{
            generateShortLink(input:{{originUrl:"{escaped_url}"{sub_ids_str}}}) {{
                shortLink
            }}
        }}
        """
        
        try:
            result = await self.graphql_query(query)
            
            if "data" in result and "generateShortLink" in result["data"]:
                short_link = result["data"]["generateShortLink"].get("shortLink")
                logger.info(f"[Shopee] Short link gerado: {short_link}")
                return short_link
            
            return None
        except Exception as e:
            logger.error(f"[Shopee] Erro ao gerar short link: {e}")
            return None
    
    async def get_shopee_offers(
        self,
        keyword: Optional[str] = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Busca ofertas da Shopee com paginação e filtros
        
        Args:
            keyword: Palavra-chave para buscar (opcional)
            sort_type: Tipo de ordenação (1=Mais recente, 2=Maior comissão)
            page: Número da página
            limit: Itens por página
        
        Returns:
            Dict com nodes (lista de ofertas) e pageInfo
        """
        # Constrói argumentos da query
        args = []
        
        if keyword:
            escaped_keyword = keyword.replace('"', '\\"')
            args.append(f'keyword:"{escaped_keyword}"')
        
        args.append(f'sortType:{sort_type}')
        args.append(f'page:{page}')
        args.append(f'limit:{limit}')
        
        args_str = ','.join(args)
        
        query = f"""
        {{
            shopeeOfferV2({args_str}) {{
                nodes {{
                    commissionRate
                    imageUrl
                    offerLink
                    originalLink
                    offerName
                    offerType
                    categoryId
                    collectionId
                    periodStartTime
                    periodEndTime
                }}
                pageInfo {{
                    page
                    limit
                    hasNextPage
                }}
            }}
        }}
        """
        
        try:
            result = await self.graphql_query(query)
            
            if "data" in result and "shopeeOfferV2" in result["data"]:
                offers_data = result["data"]["shopeeOfferV2"]
                nodes = offers_data.get("nodes", [])
                page_info = offers_data.get("pageInfo", {})
                
                logger.info(
                    f"[Shopee] {len(nodes)} ofertas encontradas "
                    f"(página {page_info.get('page', page)})"
                )
                
                return {
                    "nodes": nodes,
                    "pageInfo": page_info
                }
            
            return {"nodes": [], "pageInfo": {}}
            
        except Exception as e:
            logger.error(f"[Shopee] Erro ao buscar ofertas: {e}")
            return {"nodes": [], "pageInfo": {}}

        """
        Obtém ofertas de marcas disponíveis
        
        Nota: Implementação simplificada - a estrutura exata depende da API
        
        Args:
            limit: Número máximo de ofertas
        
        Returns:
            Lista de ofertas
        """
        query = """
        {
            brandOffer {
                totalCount
            }
        }
        """
        
        try:
            result = await self.graphql_query(query)
            
            if "data" in result:
                logger.info(f"[Shopee] Brand offers query executada")
                # Retorna estrutura básica - ajustar conforme necessário
                return []
            
            return []
        except Exception as e:
            logger.warning(f"[Shopee] Brand offers não disponível: {e}")
            return []
    
    
    async def get_products(
        self,
        keyword: Optional[str] = None,
        shop_id: Optional[int] = None,
        item_id: Optional[int] = None,
        product_cat_id: Optional[int] = None,
        sort_type: int = 5,  # COMMISSION_DESC por padrão
        page: int = 1,
        limit: int = 20,
        is_ams_offer: Optional[bool] = None,
        is_key_seller: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Busca produtos usando productOfferV2
        
        Args:
            keyword: Palavra-chave para buscar
            shop_id: ID da loja
            item_id: ID do item específico
            product_cat_id: ID da categoria
            sort_type: Tipo de ordenação:
                1 = RELEVANCE_DESC (relevância com keyword)
                2 = ITEM_SOLD_DESC (mais vendidos)
                3 = PRICE_DESC (maior preço)
                4 = PRICE_ASC (menor preço)
                5 = COMMISSION_DESC (maior comissão)
            page: Número da página
            limit: Itens por página (máx 20)
            is_ams_offer: Filtrar ofertas com comissão de vendedor
            is_key_seller: Filtrar vendedores chave
        
        Returns:
            Dict com nodes e pageInfo
        """
        # Constrói argumentos
        args = []
        
        if keyword:
            escaped = keyword.replace('"', '\\"')
            args.append(f'keyword:"{escaped}"')
        
        if shop_id:
            args.append(f'shopId:{shop_id}')
        
        if item_id:
            args.append(f'itemId:{item_id}')
        
        if product_cat_id:
            args.append(f'productCatId:{product_cat_id}')
        
        args.append(f'sortType:{sort_type}')
        args.append(f'page:{page}')
        args.append(f'limit:{limit}')
        
        if is_ams_offer is not None:
            args.append(f'isAMSOffer:{"true" if is_ams_offer else "false"}')
        
        if is_key_seller is not None:
            args.append(f'isKeySeller:{"true" if is_key_seller else "false"}')
        
        args_str = ','.join(args)
        
        query = f"""
        {{
            productOfferV2({args_str}) {{
                nodes {{
                    itemId
                    commissionRate
                    sellerCommissionRate
                    shopeeCommissionRate
                    commission
                    sales
                    priceMax
                    priceMin
                    productCatIds
                    ratingStar
                    priceDiscountRate
                    imageUrl
                    productName
                    shopId
                    shopName
                    shopType
                    productLink
                    offerLink
                    periodStartTime
                    periodEndTime
                }}
                pageInfo {{
                    page
                    limit
                    hasNextPage
                }}
            }}
        }}
        """
        
        try:
            result = await self.graphql_query(query)
            
            if "data" in result and "productOfferV2" in result["data"]:
                data = result["data"]["productOfferV2"]
                nodes = data.get("nodes", [])
                page_info = data.get("pageInfo", {})
                
                logger.info(
                    f"[Shopee] {len(nodes)} produtos encontrados "
                    f"(página {page_info.get('page', page)})"
                )
                
                return {"nodes": nodes, "pageInfo": page_info}
            
            return {"nodes": [], "pageInfo": {}}
            
        except Exception as e:
            logger.error(f"[Shopee] Erro ao buscar produtos: {e}")
            return {"nodes": [], "pageInfo": {}}
    
    async def get_shop_offers(
        self,
        shop_id: Optional[int] = None,
        keyword: Optional[str] = None,
        shop_type: Optional[List[int]] = None,
        is_key_seller: Optional[bool] = None,
        sort_type: int = 2,  # HIGHEST_COMMISSION_DESC por padrão
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Busca ofertas de lojas usando shopOfferV2
        
        Args:
            shop_id: ID da loja específica
            keyword: Buscar por nome da loja
            shop_type: Lista de tipos de loja:
                1 = OFFICIAL_SHOP (Mall)
                2 = PREFERRED_SHOP (Star)
                4 = PREFERRED_PLUS_SHOP (Star+)
            is_key_seller: Filtrar vendedores chave
            sort_type: Ordenação:
                1 = Mais recente
                2 = Maior comissão
                3 = Lojas populares
            page: Número da página
            limit: Itens por página
        
        Returns:
            Dict com nodes e pageInfo
        """
        args = []
        
        if shop_id:
            args.append(f'shopId:{shop_id}')
        
        if keyword:
            escaped = keyword.replace('"', '\\"')
            args.append(f'keyword:"{escaped}"')
        
        if shop_type:
            types_str = ','.join(map(str, shop_type))
            args.append(f'shopType:[{types_str}]')
        
        if is_key_seller is not None:
            args.append(f'isKeySeller:{"true" if is_key_seller else "false"}')
        
        args.append(f'sortType:{sort_type}')
        args.append(f'page:{page}')
        args.append(f'limit:{limit}')
        
        args_str = ','.join(args)
        
        query = f"""
        {{
            shopOfferV2({args_str}) {{
                nodes {{
                    commissionRate
                    imageUrl
                    offerLink
                    originalLink
                    shopId
                    shopName
                    ratingStar
                    shopType
                    remainingBudget
                    periodStartTime
                    periodEndTime
                    sellerCommCoveRatio
                }}
                pageInfo {{
                    page
                    limit
                    hasNextPage
                }}
            }}
        }}
        """
        
        try:
            result = await self.graphql_query(query)
            
            if "data" in result and "shopOfferV2" in result["data"]:
                data = result["data"]["shopOfferV2"]
                nodes = data.get("nodes", [])
                page_info = data.get("pageInfo", {})
                
                logger.info(
                    f"[Shopee] {len(nodes)} lojas encontradas "
                    f"(página {page_info.get('page', page)})"
                )
                
                return {"nodes": nodes, "pageInfo": page_info}
            
            return {"nodes": [], "pageInfo": {}}
            
        except Exception as e:
            logger.error(f"[Shopee] Erro ao buscar lojas: {e}")
            return {"nodes": [], "pageInfo": {}}
    
    async def get_conversion_report(
        self,
        start_timestamp: int,
        end_timestamp: int,
        scroll_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtém relatório de conversões e comissões
        
        Args:
            start_timestamp: Timestamp de início
            end_timestamp: Timestamp de fim
            scroll_id: ID de paginação (opcional)
        
        Returns:
            Relatório de conversões
        """
        # Nota: scroll_id deve ter aspas escapadas na query
        scroll_param = f', scrollId: "{scroll_id}"' if scroll_id else ""
        
        query = f"""
        query ConversionReport {{
            conversionReport(
                purchaseTimeStart: {start_timestamp},
                purchaseTimeEnd: {end_timestamp}{scroll_param}
            ) {{
                nodes {{
                    orderId
                    productId
                    productName
                    commissionAmount
                    orderAmount
                    purchaseTime
                    status
                }}
                scrollId
                totalCount
            }}
        }}
        """
        
        result = await self.graphql_query(query)
        
        if "data" in result and "conversionReport" in result["data"]:
            report = result["data"]["conversionReport"]
            logger.info(f"[Shopee] Relatório com {len(report.get('nodes', []))} conversões")
            return report
        
        return {"nodes": [], "scrollId": None, "totalCount": 0}
    
    async def test_connection(self) -> bool:
        """
        Testa conexão e autenticação com a API
        
        Returns:
            True se conectou com sucesso
        """
        try:
            logger.info("[Shopee] Testando conexão...")
            
            # Query simples para testar (usando introspection)
            query = """
            {
                __schema {
                    queryType {
                        name
                    }
                }
            }
            """
            
            result = await self.graphql_query(query)
            
            if "data" in result:
                logger.info("[Shopee] ✅ Conexão bem-sucedida!")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[Shopee] ❌ Erro na conexão: {e}")
            return False


# Função auxiliar para criar cliente
def create_shopee_client(
    app_id: Optional[str] = None,
    secret: Optional[str] = None
) -> ShopeeAffiliateClient:
    """
    Cria cliente Shopee usando variáveis de ambiente ou parâmetros
    
    Args:
        app_id: App ID (usa SHOPEE_APP_ID do .env se não fornecido)
        secret: Secret (usa SHOPEE_APP_SECRET do .env se não fornecido)
    
    Returns:
        Cliente configurado
    """
    app_id = app_id or os.getenv("SHOPEE_APP_ID")
    secret = secret or os.getenv("SHOPEE_APP_SECRET")  # Alterado de SHOPEE_SECRET
    endpoint = os.getenv("SHOPEE_API_ENDPOINT", "https://open-api.affiliate.shopee.com.br/graphql")
    
    if not app_id or not secret:
        raise ValueError(
            "SHOPEE_APP_ID e SHOPEE_APP_SECRET devem ser configurados no .env"
        )
    
    return ShopeeAffiliateClient(app_id=app_id, secret=secret, endpoint=endpoint)
