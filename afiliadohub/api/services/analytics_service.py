"""
Analytics Service
Lógica de negócio para analytics e performance metrics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from afiliadohub.api.repositories.analytics_repository import AnalyticsRepository
from afiliadohub.api.utils.supabase_client import get_supabase_manager


class AnalyticsService:
    """Service para processar analytics e métricas"""
    
    def __init__(self):
        supabase = get_supabase_manager()
        self.repository = AnalyticsRepository(supabase.client)
    
    async def get_performance_overview(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Retorna overview completo de performance
        
        Returns:
            - total_products: Total de produtos ativos
            - total_clicks: Total de cliques no período
            - avg_ctr: CTR médio
            - avg_quality_score: Score médio de qualidade  
            - best_store: Loja com melhor performance
            - period_days: Número de dias do período
        """
        try:
            overview = await self.repository.get_overview_stats(days=days)
            return {
                'success': True,
                'data': overview
            }
        except Exception as e:
            print(f"[ERRO] get_performance_overview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_top_products(
        self,
        limit: int = 10,
        metric: str = 'clicks',
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retorna top N produtos por métrica
        
        Args:
            limit: Número de produtos
            metric: 'clicks', 'telegram_sends', 'quality_score'
            days: Filtrar produtos criados nos últimos N dias
        """
        try:
            date_from = datetime.now() - timedelta(days=days) if days else None
            
            products = await self.repository.get_top_products(
                limit=limit,
                order_by=metric,
                date_from=date_from
            )
            
            # Formata resposta
            formatted = []
            for p in products:
                formatted.append({
                    'id': p.get('id'),
                    'name': p.get('name'),
                    'store': p.get('store'),
                    'image_url': p.get('image_url'),
                    'affiliate_link': p.get('affiliate_link'),
                    'current_price': p.get('current_price'),
                    'discount_percentage': p.get('discount_percentage', 0),
                    'quality_score': p.get('quality_score', 0),
                    'click_count': p.get('click_count', 0),
                    'telegram_send_count': p.get('telegram_send_count', 0),
                    # Calcular CTR individual
                    'ctr': round(
                        (p.get('click_count', 0) / p.get('telegram_send_count', 1)) * 100,
                        2
                    ) if p.get('telegram_send_count', 0) > 0 else 0
                })
            
            return {
                'success': True,
                'data': formatted,
                'count': len(formatted)
            }
            
        except Exception as e:
            print(f"[ERRO] get_top_products: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    async def get_store_comparison(self) -> Dict[str, Any]:
        """
        Retorna comparativo de performance entre lojas
        
        Returns:
            Lista de lojas com métricas:
            - store: Nome da loja
            - product_count: Total de produtos
            - total_clicks: Total de cliques
            - avg_clicks_per_product: Média de cliques por produto
            - ctr: Click-through rate
        """
        try:
            stores = await self.repository.get_performance_by_store()
            
            return {
                'success': True,
                'data': stores,
                'count': len(stores)
            }
            
        except Exception as e:
            print(f"[ERRO] get_store_comparison: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    async def get_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Retorna tendências temporais (clicks por dia)
        
        Args:
            days: Número de dias para buscar
        """
        try:
            daily_data = await self.repository.get_daily_clicks(days=days)
            
            # Preencher dias faltantes com zero
            all_days = []
            current_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
            
            # Criar dict para lookup rápido
            data_dict = {item['date']: item['clicks'] for item in daily_data}
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                all_days.append({
                    'date': date_str,
                    'clicks': data_dict.get(date_str, 0)
                })
                current_date += timedelta(days=1)
            
            return {
                'success': True,
                'data': all_days,
                'count': len(all_days)
            }
            
        except Exception as e:
            print(f"[ERRO] get_trends: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def calculate_product_quality_score(self, product: Dict[str, Any]) -> int:
        """
        Calcula score de qualidade de um produto (0-100)
        
        Critérios:
        - Rating (0-30 pts)
        - Sales volume (0-30 pts)  
        - Commission rate (0-25 pts)
        - Price stability/discount (0-15 pts)
        """
        score = 0
        
        # Rating (0-30 pontos)
        rating = product.get('ratingStar', product.get('rating', 0))
        if rating > 0:
            score += int((rating / 5.0) * 30)
        
        # Sales volume (0-30 pontos)
        sales = product.get('sales', product.get('sold', 0))
        if sales >= 1000:
            score += 30
        elif sales >= 500:
            score += 20
        elif sales >= 100:
            score += 10
        elif sales >= 50:
            score += 5
        
        # Commission (0-25 pontos)
        # Assume commissionRate em decimal (0.30 = 30%)
        commission = product.get('commissionRate', 0)
        if isinstance(commission, str):
            # Tenta parsear se vier como string
            try:
                commission = float(commission.strip('%')) / 100
            except:
                commission = 0
        
        commission_pct = commission * 100
        if commission_pct >= 50:
            score += 25
        elif commission_pct >= 40:
            score += 20
        elif commission_pct >= 30:
            score += 15
        elif commission_pct >= 20:
            score += 10
        
        # Price stability (0-15 pontos)
        # Descontos moderados são melhores (mais confiáveis)
        discount = product.get('discount_percentage', 0)
        if 10 <= discount <= 50:
            score += 15
        elif discount > 50:
            score += 5  # Desconto muito alto pode ser suspeito
        
        return min(score, 100)
    
    def should_import_product(self, product: Dict[str, Any], min_quality: int = 60) -> tuple[bool, int]:
        """
        Decide se um produto deve ser importado baseado em quality score
        
        Args:
            product: Dados do produto
            min_quality: Score mínimo para importar (padrão: 60)
        
        Returns:
            (should_import: bool, quality_score: int)
        """
        quality_score = self.calculate_product_quality_score(product)
        should_import = quality_score >= min_quality
        
        return (should_import, quality_score)


# Singleton instance
_analytics_service = None

def get_analytics_service() -> AnalyticsService:
    """Retorna instância singleton do AnalyticsService"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
