"""
Shopee Product Importer
Imports and syncs products from Shopee Affiliates API to Supabase
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..api.utils.shopee_client import create_shopee_client, ShopeeAffiliateClient
from ..api.utils.supabase_client import get_supabase_manager, SupabaseManager


logger = logging.getLogger(__name__)


class ShopeeProductImporter:
    """
    Importador de produtos da Shopee para Supabase
    
    Features:
    - Importação em lote
    - Atualização de produtos existentes
    - Detecção de mudanças de preço
    - Tracking de comissões
    - Logs estruturados
    """
    
    def __init__(
        self,
        shopee_client:  Optional[ShopeeAffiliateClient] = None,
        supabase_manager: Optional[SupabaseManager] = None
    ):
        """
        Inicializa importer
        
        Args:
            shopee_client: Cliente Shopee (cria novo se não fornecido)
            supabase_manager: Manager Supabase (cria novo se não fornecido)
        """
        self.shopee = shopee_client or create_shopee_client()
        self.supabase = supabase_manager or get_supabase_manager()
        
        logger.info("[ShopeeImporter] Importer inicializado")
    
    def _map_shopee_to_product(self, shopee_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia campos da Shopee para schema do Supabase
        
        Args:
            shopee_product: Produto da API Shopee
        
        Returns:
            Dict com campos mapeados para products table
        """
        # Calcula desconto
        original_price = shopee_product.get("originalPrice", 0)
        current_price = shopee_product.get("price", 0)
        
        discount_percentage = 0
        if original_price > 0 and current_price < original_price:
            discount_percentage = int(((original_price - current_price) / original_price) * 100)
        
        # Mapeia campos
        product_data = {
            "store": "shopee",
            "shopee_product_id": shopee_product.get("productId"),
            "name": shopee_product.get("productName", ""),
            "description": shopee_product.get("description", ""),
            "affiliate_link": shopee_product.get("affiliateLink", ""),
            "current_price": float(current_price) if current_price else 0.0,
            "original_price": float(original_price) if original_price else None,
            "discount_percentage": discount_percentage,
            "commission_rate": float(shopee_product.get("commissionRate", 0)),
            "commission_amount": float(shopee_product.get("commissionAmount", 0)),
            "category": shopee_product.get("category", "Não categorizado"),
            "shopee_category": shopee_product.get("category"),
            "image_url": shopee_product.get("imageUrl", ""),
            "sales_count": int(shopee_product.get("sales", 0)),
            "rating": float(shopee_product.get("rating", 0)) if shopee_product.get("rating") else None,
            "review_count": int(shopee_product.get("reviewCount", 0)),
            "stock_available": bool(shopee_product.get("stock", True)),
            "shop_name": shopee_product.get("shopName", ""),
            "shop_rating": float(shopee_product.get("shopRating", 0)) if shopee_product.get("shopRating") else None,
            "is_active": True,
            "is_featured": discount_percentage >= 50 or shopee_product.get("commissionRate", 0) >= 10,
        }
        
        return product_data
    
    async def import_all_products(
        self,
        limit: int = 100,
        min_commission: float = 0.0
    ) -> Dict[str, Any]:
        """
        Importa todos os produtos disponíveis da Shopee
        
        Args:
            limit: Número máximo de produtos a importar
            min_commission: Comissão mínima em % para filtrar
        
        Returns:
            Dict com estatísticas da importação
        """
        logger.info(f"[ShopeeImporter] Iniciando importação (limit={limit}, min_commission={min_commission}%)")
        
        stats = {
            "imported": 0,
            "updated": 0,
            "errors": 0,
            "error_messages": [],
            "start_time": datetime.now()
        }
        
        try:
            # Conecta ao Shopee
            await self.shopee.connect()
            
            # Busca produtos
            shopee_products = await self.shopee.get_products(
                min_commission=min_commission,
                limit=limit
            )
            
            logger.info(f"[ShopeeImporter] {len(shopee_products)} produtos recebidos da API")
            
            # Importa cada produto
            for shopee_product in shopee_products:
                try:
                    product_data = self._map_shopee_to_product(shopee_product)
                    
                    # Verifica se produto já existe
                    existing = await self._find_existing_product(
                        shopee_product.get("productId")
                    )
                    
                    if existing:
                        # Atualiza produto existente
                        await self._update_product(existing["id"], product_data)
                        stats["updated"] += 1
                        logger.debug(f"[ShopeeImporter] Produto {existing['id']} atualizado")
                    else:
                        # Insere novo produto
                        result = await self.supabase.insert_product(product_data)
                        stats["imported"] += 1
                        logger.debug(f"[ShopeeImporter] Produto {result['id']} importado")
                
                except Exception as e:
                    stats["errors"] += 1
                    error_msg = f"Erro ao processar produto {shopee_product.get('productId')}: {e}"
                    stats["error_messages"].append(error_msg)
                    logger.error(f"[ShopeeImporter] {error_msg}")
            
            # Loga resultado no Supabase
            await self._log_sync_result("import_all", stats)
            
            logger.info(
                f"[ShopeeImporter] Importação concluída: "
                f"{stats['imported']} novos, {stats['updated']} atualizados, "
                f"{stats['errors']} erros"
            )
            
        except Exception as e:
            stats["errors"] += 1
            stats["error_messages"].append(f"Erro geral: {e}")
            logger.error(f"[ShopeeImporter] Erro na importação: {e}")
        
        finally:
            await self.shopee.close()
        
        stats["end_time"] = datetime.now()
        stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        return stats
    
    async def update_existing_products(self, hours_old: int = 24) -> Dict[str, Any]:
        """
        Atualiza produtos existentes que estão desatualizados
        
        Args:
            hours_old: Considera desatualizado se não atualizado há X horas
        
        Returns:
            Dict com estatísticas
        """
        logger.info(f"[ShopeeImporter] Atualizando produtos desatualizados (>{hours_old}h)")
        
        stats = {
            "updated": 0,
            "errors": 0,
            "error_messages": [],
            "start_time": datetime.now()
        }
        
        try:
            # Busca produtos desatualizados
            response = self.supabase.client.rpc(
                "get_outdated_shopee_products",
                {"hours_old": hours_old}
            ).execute()
            
            outdated_products = response.data
            logger.info(f"[ShopeeImporter] {len(outdated_products)} produtos para atualizar")
            
            await self.shopee.connect()
            
            # Para cada produto, busca dados atualizados
            # Nota: API Shopee pode não ter endpoint para buscar produto específico
            # Neste caso, reimportamos todos e atualizamos
            shopee_products = await self.shopee.get_products(limit=1000)
            
            # Cria mapa de shopee_product_id -> dados
            shopee_map = {
                p.get("productId"): p
                for p in shopee_products
            }
            
            # Atualiza cada produto
            for old_product in outdated_products:
                shopee_id = old_product.get("shopee_product_id")
                
                if shopee_id in shopee_map:
                    try:
                        new_data = self._map_shopee_to_product(shopee_map[shopee_id])
                        await self._update_product(old_product["id"], new_data)
                        stats["updated"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        stats["error_messages"].append(f"Erro ao atualizar {shopee_id}: {e}")
            
            await self._log_sync_result("update_existing", stats)
            
            logger.info(f"[ShopeeImporter] {stats['updated']} produtos atualizados")
            
        except Exception as e:
            stats["errors"] += 1
            stats["error_messages"].append(f"Erro: {e}")
            logger.error(f"[ShopeeImporter] Erro na atualização: {e}")
        
        finally:
            await self.shopee.close()
        
        stats["end_time"] = datetime.now()
        return stats
    
    async def sync_brand_offers(self) -> Dict[str, Any]:
        """
        Sincroniza ofertas de marca
        
        Returns:
            Dict com estatísticas
        """
        logger.info("[ShopeeImporter] Sincronizando ofertas de marca")
        
        stats = {
            "imported": 0,
            "errors": 0,
            "error_messages": []
        }
        
        try:
            await self.shopee.connect()
            
            # Busca ofertas
            offers = await self.shopee.get_brand_offers(limit=50)
            
            logger.info(f"[ShopeeImporter] {len(offers)} ofertas encontradas")
            
            # Importa produtos de cada oferta
            for offer in offers:
                products = offer.get("products", [])
                
                for product in products:
                    # Adiciona taxa de comissão da oferta
                    product["commissionRate"] = offer.get("commissionRate", 0)
                    
                    try:
                        product_data = self._map_shopee_to_product(product)
                        
                        # Marca como featured (produto em oferta de marca)
                        product_data["is_featured"] = True
                        
                        existing = await self._find_existing_product(product.get("productId"))
                        
                        if existing:
                            await self._update_product(existing["id"], product_data)
                        else:
                            await self.supabase.insert_product(product_data)
                            stats["imported"] += 1
                    
                    except Exception as e:
                        stats["errors"] += 1
                        stats["error_messages"].append(f"Erro: {e}")
            
            await self._log_sync_result("brand_offers", stats)
            
        except Exception as e:
            stats["errors"] += 1
            stats["error_messages"].append(f"Erro: {e}")
            logger.error(f"[ShopeeImporter] Erro: {e}")
        
        finally:
            await self.shopee.close()
        
        return stats
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    async def _find_existing_product(self, shopee_product_id: int) -> Optional[Dict[str, Any]]:
        """Busca produto existente por shopee_product_id"""
        try:
            response = self.supabase.client.table("products")\
                .select("*")\
                .eq("shopee_product_id", shopee_product_id)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    async def _update_product(self, product_id: str, new_data: Dict[str, Any]):
        """Atualiza produto existente"""
        new_data["updated_at"] = datetime.now().isoformat()
        new_data["last_checked"] = datetime.now().isoformat()
        
        self.supabase.client.table("products")\
            .update(new_data)\
            .eq("id", product_id)\
            .execute()
    
    async def _log_sync_result(self, sync_type: str, stats: Dict[str, Any]):
        """Loga resultado da sincronização no Supabase"""
        try:
            self.supabase.client.rpc(
                "log_shopee_sync",
                {
                    "p_sync_type": sync_type,
                    "p_products_imported": stats.get("imported", 0),
                    "p_products_updated": stats.get("updated", 0),
                    "p_errors": stats.get("errors", 0),
                    "p_error_messages": stats.get("error_messages", [])
                }
            ).execute()
        except Exception as e:
            logger.error(f"[ShopeeImporter] Erro ao logar sync: {e}")


# Função auxiliar para executar importação
async def run_shopee_import(
    import_type: str = "all",
    limit: int = 100,
    min_commission: float = 0.0
) -> Dict[str, Any]:
    """
    Executa importação de produtos da Shopee
    
    Args:
        import_type: Tipo de importação ('all', 'update', 'offers')
        limit: Limite de produtos
        min_commission: Comissão mínima
    
    Returns:
        Estatísticas da importação
    """
    importer = ShopeeProductImporter()
    
    if import_type == "all":
        return await importer.import_all_products(limit=limit, min_commission=min_commission)
    elif import_type == "update":
        return await importer.update_existing_products()
    elif import_type == "offers":
        return await importer.sync_brand_offers()
    else:
        raise ValueError(f"Import type inválido: {import_type}")
