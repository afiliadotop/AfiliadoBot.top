import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

class SupabaseManager:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa o cliente Supabase"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser configurados")
        
        try:
            # Simplificando opções para evitar erros de compatibilidade com versões recentes do supabase-py
            self._client = create_client(url, key)
            print("[INFO] Cliente Supabase inicializado")
        except Exception as e:
            print(f"[ERROR] Erro ao inicializar Supabase: {e}")
            raise
    
    @property
    def client(self) -> Client:
        if self._client is None:
            self._initialize()
        return self._client
    
    # ==================== MÉTODOS PARA PRODUTOS ====================
    
    async def insert_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insere um novo produto"""
        try:
            # Valida dados obrigatórios
            required_fields = ['store', 'name', 'affiliate_link', 'current_price']
            for field in required_fields:
                if field not in product_data:
                    raise ValueError(f"Campo obrigatório faltando: {field}")
            
            # Adiciona timestamps
            now = datetime.now().isoformat()
            product_data['created_at'] = now
            product_data['updated_at'] = now
            product_data['last_checked'] = now
            
            # Insere no banco
            response = self.client.table("products").insert(product_data).execute()
            
            if response.data:
                # Cria registro de estatísticas
                stats_data = {
                    "product_id": response.data[0]["id"],
                    "created_at": now
                }
                self.client.table("product_stats").insert(stats_data).execute()
                
                return response.data[0]
            else:
                raise Exception("Nenhum dado retornado ao inserir produto")
                
        except Exception as e:
            print(f"[ERRO] Erro ao inserir produto: {e}")
            raise
    
    async def bulk_insert_products(self, products: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        """Insere múltiplos produtos em lote"""
        results = {
            "total": len(products),
            "inserted": 0,
            "updated": 0,
            "errors": 0,
            "error_messages": []
        }
        
        # Processa em lotes
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            try:
                # Prepara batch com timestamps
                now = datetime.now().isoformat()
                for product in batch:
                    product['created_at'] = now
                    product['updated_at'] = now
                    product['last_checked'] = now
                
                # Upsert (insere ou atualiza se existir)
                response = self.client.table("products").upsert(
                    batch,
                    on_conflict='affiliate_link'
                ).execute()
                
                results["inserted"] += len(response.data)
                
            except Exception as e:
                results["errors"] += len(batch)
                results["error_messages"].append(str(e))
                print(f"[ERRO] Erro no batch {i//batch_size + 1}: {e}")
        
        return results
    
    async def get_products(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Busca produtos com filtros"""
        try:
            query = self.client.table("products").select("*")
            
            # Aplica filtros
            if filters:
                store = filters.get("store")
                category = filters.get("category")
                min_price = filters.get("min_price")
                max_price = filters.get("max_price")
                min_discount = filters.get("min_discount")
                
                if store:
                    query = query.eq("store", store)
                if category:
                    query = query.eq("category", category)
                if min_price:
                    query = query.gte("current_price", min_price)
                if max_price:
                    query = query.lte("current_price", max_price)
                if min_discount:
                    query = query.gte("discount_percentage", min_discount)
                
                # Apenas produtos ativos
                query = query.eq("is_active", True)
            
            # Ordena e limita
            query = query.order("created_at", desc=True).limit(limit).offset(offset)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar produtos: {e}")
            return []
    
    async def get_random_product(self, store: Optional[str] = None, min_discount: int = 0) -> Optional[Dict[str, Any]]:
        """Busca um produto aleatório"""
        try:
            # Usa função do PostgreSQL para aleatoriedade
            query = """
            SELECT * FROM products 
            WHERE is_active = TRUE 
            AND (%(store)s IS NULL OR store = %(store)s)
            AND (%(min_discount)s = 0 OR discount_percentage >= %(min_discount)s)
            ORDER BY RANDOM()
            LIMIT 1
            """
            
            params = {
                "store": store,
                "min_discount": min_discount
            }
            
            response = self.client.rpc("get_random_product", params).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar produto aleatório: {e}")
            return None
    
    async def update_product_price(self, product_id: int, new_price: float) -> bool:
        """Atualiza o preço de um produto"""
        try:
            update_data = {
                "current_price": new_price,
                "last_checked": datetime.now().isoformat()
            }
            
            response = self.client.table("products").update(update_data).eq("id", product_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"[ERRO] Erro ao atualizar preço: {e}")
            return False
    
    # ==================== MÉTODOS PARA ESTATÍSTICAS ====================
    
    async def increment_product_stats(self, product_id: int, stat_type: str = "click_count", increment: int = 1) -> bool:
        """Incrementa estatísticas de um produto"""
        try:
            # Usa RPC para incremento atômico
            response = self.client.rpc(
                "increment_stat",
                {
                    "p_product_id": product_id,
                    "p_stat_type": stat_type,
                    "p_increment": increment
                }
            ).execute()
            
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao incrementar estatística: {e}")
            return False
    
    async def get_daily_stats(self, date: datetime) -> Dict[str, Any]:
        """Busca estatísticas do dia"""
        try:
            # Formata data
            date_str = date.strftime("%Y-%m-%d")
            
            # Busca estatísticas usando a função do banco
            response = self.client.rpc("get_daily_stats", {"p_date": date_str}).execute()
            
            if response.data:
                return response.data[0]
            else:
                return {
                    "date": date_str,
                    "total_products": 0,
                    "new_products": 0,
                    "telegram_sent": 0
                }
                
        except Exception as e:
            print(f"[ERRO] Erro ao buscar estatísticas diárias: {e}")
            return {}
    
    # ==================== MÉTODOS UTILITÁRIOS ====================
    
    async def cleanup_old_products(self, days_old: int = 30):
        """Remove produtos inativos antigos"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            response = self.client.table("products")\
                .delete()\
                .lt("updated_at", cutoff_date)\
                .eq("is_active", False)\
                .execute()
            
            deleted_count = len(response.data) if response.data else 0
            print(f"🧹 {deleted_count} produtos antigos removidos")
            return deleted_count
            
        except Exception as e:
            print(f"[ERRO] Erro ao limpar produtos antigos: {e}")
            return 0
    
    async def get_system_summary(self) -> Dict[str, Any]:
        """Retorna resumo do sistema"""
        try:
            # Conta produtos por loja
            stores_response = self.client.table("products")\
                .select("store, count")\
                .eq("is_active", True)\
                .group("store")\
                .execute()
            
            # Total de produtos
            total_response = self.client.table("products")\
                .select("count", count="exact")\
                .eq("is_active", True)\
                .execute()
            
            # Produtos com desconto
            discount_response = self.client.table("products")\
                .select("count", count="exact")\
                .gt("discount_percentage", 0)\
                .eq("is_active", True)\
                .execute()
            
            return {
                "total_products": total_response.count,
                "products_with_discount": discount_response.count,
                "stores": {item["store"]: item["count"] for item in stores_response.data},
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar resumo: {e}")
            return {}
    
    # ==================== MÉTODOS PARA LOJAS ====================
    
    async def get_active_stores(self) -> List[Dict[str, Any]]:
        """Retorna todas as lojas ativas do banco de dados"""
        try:
            response = self.client.table("stores")\
                .select("*")\
                .eq("is_active", True)\
                .order("name")\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar lojas ativas: {e}")
            return []
    
    async def get_store_by_name(self, store_name: str) -> Optional[Dict[str, Any]]:
        """Busca uma loja específica por nome"""
        try:
            response = self.client.table("stores")\
                .select("*")\
                .eq("name", store_name.lower())\
                .eq("is_active", True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar loja {store_name}: {e}")
            return None
    
    async def get_stores_with_product_count(self) -> List[Dict[str, Any]]:
        """Retorna lojas com contagem de produtos ativos"""
        try:
            # Busca lojas
            stores = await self.get_active_stores()
            
            # Para cada loja, conta produtos
            for store in stores:
                response = self.client.table("products")\
                    .select("id", count="exact")\
                    .eq("store", store["name"])\
                    .eq("is_active", True)\
                    .execute()
                
                store["product_count"] = response.count or 0
            
            return stores
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar lojas com contagem: {e}")
            return []
    
    # ==================== MÉTODOS PARA PREFERÊNCIAS DE USUÁRIO ====================
    
    async def get_user_preferences(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """Busca preferências de um usuário"""
        try:
            response = self.client.rpc(
                "get_user_preference_summary",
                {"p_telegram_user_id": telegram_user_id}
            ).execute()
            
            if response.data:
                return response.data
            return {"has_preferences": False}
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar preferências do usuário: {e}")
            return {"has_preferences": False}
    
    async def save_user_preference(
        self,
        telegram_user_id: int,
        telegram_username: Optional[str] = None,
        telegram_first_name: Optional[str] = None,
        preferred_stores: Optional[List[str]] = None,
        preferred_categories: Optional[List[str]] = None,
        min_discount: Optional[int] = None,
        max_price: Optional[float] = None,
        notification_enabled: Optional[bool] = None
    ) -> bool:
        """Salva ou atualiza preferências de usuário"""
        try:
            params = {
                "p_telegram_user_id": telegram_user_id,
                "p_telegram_username": telegram_username,
                "p_telegram_first_name": telegram_first_name,
                "p_preferred_stores": preferred_stores,
                "p_preferred_categories": preferred_categories,
                "p_min_discount": min_discount,
                "p_max_price": max_price,
                "p_notification_enabled": notification_enabled
            }
            
            response = self.client.rpc("upsert_user_preference", params).execute()
            return True
            
        except Exception as e:
            print(f"[ERRO] Erro ao salvar preferências: {e}")
            return False
    
    async def get_recommended_products(
        self,
        telegram_user_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retorna produtos recomendados baseados nas preferências do usuário"""
        try:
            response = self.client.rpc(
                "get_recommended_products",
                {
                    "p_telegram_user_id": telegram_user_id,
                    "p_limit": limit
                }
            ).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar recomendações: {e}")
            return []
    
    # ==================== MÉTODOS DE BUSCA AVANÇADA ====================
    
    async def search_products_fulltext(
        self,
        search_term: str,
        store: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_discount: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Busca produtos usando full-text search"""
        try:
            # Usa a busca vetorial se disponível, senão usa ILIKE
            query = self.client.table("products").select("*")
            
            # Busca por nome ou descrição
            query = query.or_(f"name.ilike.%{search_term}%,description.ilike.%{search_term}%")
            
            # Aplica filtros
            query = query.eq("is_active", True)
            
            if store:
                query = query.eq("store", store)
            if category:
                query = query.eq("category", category)
            if min_price is not None:
                query = query.gte("current_price", min_price)
            if max_price is not None:
                query = query.lte("current_price", max_price)
            if min_discount is not None:
                query = query.gte("discount_percentage", min_discount)
            
            # Ordena por relevância (desconto primeiro)
            query = query.order("discount_percentage", desc=True).limit(limit)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"[ERRO] Erro na busca full-text: {e}")
            return []
    
    async def get_top_deals(
        self,
        limit: int = 10,
        min_discount: int = 20,
        store: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retorna os melhores deals (maior desconto)"""
        try:
            query = self.client.table("products")\
                .select("*")\
                .eq("is_active", True)\
                .gte("discount_percentage", min_discount)
            
            if store:
                query = query.eq("store", store)
            
            query = query.order("discount_percentage", desc=True)\
                .order("created_at", desc=True)\
                .limit(limit)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar top deals: {e}")
            return []
    
    async def get_categories(self, store: Optional[str] = None) -> List[str]:
        """Retorna lista de categorias únicas"""
        try:
            query = self.client.table("products")\
                .select("category")\
                .eq("is_active", True)\
                .not_.is_("category", "null")
            
            if store:
                query = query.eq("store", store)
            
            response = query.execute()
            
            # Extrai categorias únicas
            categories = list(set([p["category"] for p in response.data if p.get("category")]))
            categories.sort()
            
            return categories
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar categorias: {e}")
            return []

# Singleton para acesso global
def get_supabase() -> Client:
    return SupabaseManager().client

def get_supabase_manager() -> SupabaseManager:
    return SupabaseManager()
