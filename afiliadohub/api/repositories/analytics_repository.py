"""
Analytics Repository
Queries otimizadas para métricas de performance e analytics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from supabase import Client


class AnalyticsRepository:
    """Repository para queries de analytics e performance"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get_total_clicks(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> int:
        """Retorna total de cliques no período"""
        try:
            query = self.client.table("product_stats").select("click_count", count="exact")
            
            if date_from:
                query = query.gte("updated_at", date_from.isoformat())
            if date_to:
                query = query.lte("updated_at", date_to.isoformat())
            
            response = query.execute()
            
            # Soma todos os click_counts
            total = sum(item.get('click_count', 0) for item in response.data) if response.data else 0
            return total
            
        except Exception as e:
            print(f"[ERRO] get_total_clicks: {e}")
            return 0
    
    async def get_top_products(
        self,
        limit: int = 10,
        order_by: str = 'clicks',
        date_from: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna top N produtos ordenados por métrica
        order_by: 'clicks', 'telegram_sends', 'quality_score'
        """
        try:
            # Mapeia order_by para campo correto
            order_field_map = {
                'clicks': 'click_count',
                'telegram_sends': 'telegram_send_count',
                'quality_score': 'quality_score'
            }
            
            order_field = order_field_map.get(order_by, 'click_count')
            
            # Query produtos com stats usando JOIN
            query = self.client.table("products")\
                .select("*, product_stats(click_count, telegram_send_count, last_sent)")\
                .eq("is_active", True)
            
            if date_from:
                query = query.gte("created_at", date_from.isoformat())
            
            response = query.limit(200).execute()
            
            if not response.data:
                return []
            
            # Processar e ordenar em Python (Supabase não ordena por JOIN facilmente)
            products = response.data
            for p in products:
                stats = p.get('product_stats', [])
                if stats and len(stats) > 0:
                    p['click_count'] = stats[0].get('click_count', 0)
                    p['telegram_send_count'] = stats[0].get('telegram_send_count', 0)
                else:
                    p['click_count'] = 0
                    p['telegram_send_count'] = 0
            
            # Ordenar por campo escolhido
            if order_by == 'quality_score':
                products.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            elif order_by == 'telegram_sends':
                products.sort(key=lambda x: x.get('telegram_send_count', 0), reverse=True)
            else:  # clicks
                products.sort(key=lambda x: x.get('click_count', 0), reverse=True)
            
            return products[:limit]
            
        except Exception as e:
            print(f"[ERRO] get_top_products: {e}")
            return []
    
    async def get_performance_by_store(self) -> List[Dict[str, Any]]:
        """Retorna performance agregada por loja"""
        try:
            # Busca todos os produtos ativos com stats
            response = self.client.table("products")\
                .select("store, product_stats(click_count, telegram_send_count)")\
                .eq("is_active", True)\
                .execute()
            
            if not response.data:
                return []
            
            # Agregar por loja em Python
            stores = {}
            for p in response.data:
                store = p.get('store', 'unknown')
                stats = p.get('product_stats', [])
                
                if store not in stores:
                    stores[store] = {
                        'store': store,
                        'product_count': 0,
                        'total_clicks': 0,
                        'total_telegram_sends': 0
                    }
                
                stores[store]['product_count'] += 1
                
                if stats and len(stats) > 0:
                    stores[store]['total_clicks'] += stats[0].get('click_count', 0)
                    stores[store]['total_telegram_sends'] += stats[0].get('telegram_send_count', 0)
            
            # Calcular médias e CTR
            result = []
            for store_data in stores.values():
                product_count = store_data['product_count']
                if product_count > 0:
                    store_data['avg_clicks_per_product'] = round(store_data['total_clicks'] / product_count, 2)
                    
                    # CTR = clicks / telegram_sends (estimativa)
                    if store_data['total_telegram_sends'] > 0:
                        store_data['ctr'] = round(
                            (store_data['total_clicks'] / store_data['total_telegram_sends']) * 100,
                            2
                        )
                    else:
                        store_data['ctr'] = 0
                
                result.append(store_data)
            
            # Ordenar por total de cliques
            result.sort(key=lambda x: x['total_clicks'], reverse=True)
            
            return result
            
        except Exception as e:
            print(f"[ERRO] get_performance_by_store: {e}")
            return []
    
    async def get_daily_clicks(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Retorna série temporal de cliques diários
        Nota: Requer log de cliques por dia (pode não existir ainda)
        Fallback: agrupa por updated_at
        """
        try:
            date_from = datetime.now() - timedelta(days=days)
            
            # Busca stats atualizados no período
            response = self.client.table("product_stats")\
                .select("click_count, updated_at")\
                .gte("updated_at", date_from.isoformat())\
                .order("updated_at", desc=False)\
                .execute()
            
            if not response.data:
                return []
            
            # Agregar por dia
            daily_stats = {}
            for stat in response.data:
                updated_at = stat.get('updated_at', '')
                if not updated_at:
                    continue
                
                # Extrai data (YYYY-MM-DD)
                date_str = updated_at.split('T')[0]
                
                if date_str not in daily_stats:
                    daily_stats[date_str] = {
                        'date': date_str,
                        'clicks': 0
                    }
                
                daily_stats[date_str]['clicks'] += stat.get('click_count', 0)
            
            # Converter para lista ordenada
            result = sorted(daily_stats.values(), key=lambda x: x['date'])
            
            return result
            
        except Exception as e:
            print(f"[ERRO] get_daily_clicks: {e}")
            return []
    
    async def get_overview_stats(self, days: int = 30) -> Dict[str, Any]:
        """Retorna estatísticas gerais para overview do dashboard"""
        try:
            date_from = datetime.now() - timedelta(days=days)
            
            # Total de produtos ativos
            products_response = self.client.table("products")\
                .select("id", count="exact")\
                .eq("is_active", True)\
                .execute()
            
            total_products = products_response.count or 0
            
            # Total de cliques (período)
            total_clicks = await self.get_total_clicks(date_from=date_from)
            
            # Loja com melhor performance
            stores = await self.get_performance_by_store()
            best_store = stores[0] if stores else None
            
            # Qualidade média dos produtos
            quality_response = self.client.table("products")\
                .select("quality_score")\
                .eq("is_active", True)\
                .not_.is_("quality_score", "null")\
                .execute()
            
            if quality_response.data:
                avg_quality = sum(p.get('quality_score', 0) for p in quality_response.data) / len(quality_response.data)
            else:
                avg_quality = 0
            
            # CTR médio (estimativa global)
            stats_response = self.client.table("product_stats")\
                .select("click_count, telegram_send_count")\
                .execute()
            
            if stats_response.data:
                total_sends = sum(s.get('telegram_send_count', 0) for s in stats_response.data)
                total_all_clicks = sum(s.get('click_count', 0) for s in stats_response.data)
                avg_ctr = (total_all_clicks / total_sends * 100) if total_sends > 0 else 0
            else:
                avg_ctr = 0
            
            return {
                'total_products': total_products,
                'total_clicks': total_clicks,
                'avg_ctr': round(avg_ctr, 2),
                'avg_quality_score': round(avg_quality, 1),
                'best_store': best_store['store'] if best_store else 'N/A',
                'period_days': days,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERRO] get_overview_stats: {e}")
            return {
                'total_products': 0,
                'total_clicks': 0,
                'avg_ctr': 0,
                'avg_quality_score': 0,
                'best_store': 'N/A',
                'period_days': days
            }
