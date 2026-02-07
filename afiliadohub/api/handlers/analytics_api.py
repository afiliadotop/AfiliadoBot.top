"""
Analytics API Handler
FastAPI endpoints para analytics e performance metrics
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from afiliadohub.api.services.analytics_service import get_analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

analytics_service = get_analytics_service()


@router.get("/overview")
async def get_performance_overview(
    days: int = Query(default=30, ge=1, le=365, description="Número de dias para análise")
):
    """
    Retorna overview geral de performance
    
    - **total_products**: Total de produtos ativos
    - **total_clicks**: Total de cliques no período
    - **avg_ctr**: CTR médio (%)
    - **avg_quality_score**: Score médio de qualidade
    - **best_store**: Loja com melhor performance
    """
    result = await analytics_service.get_performance_overview(days=days)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Erro ao buscar overview'))
    
    return result['data']


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50, description="Número de produtos"),
    metric: str = Query(default='clicks', regex='^(clicks|telegram_sends|quality_score)$'),
    days: Optional[int] = Query(default=None, ge=1, le=365, description="Filtrar por dias")
):
    """
    Retorna top N produtos por métrica
    
    - **limit**: Quantidade de produtos (1-50)
    - **metric**: Métrica para ordenar - clicks, telegram_sends, quality_score
    - **days**: Opcional - filtrar produtos criados nos últimos N dias
    """
    result = await analytics_service.get_top_products(
        limit=limit,
        metric=metric,
        days=days
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Erro ao buscar top produtos'))
    
    return {
        'products': result['data'],
        'count': result['count'],
        'metric': metric
    }


@router.get("/stores")
async def get_store_comparison():
    """
    Retorna comparativo de performance entre lojas
    
    Para cada loja retorna:
    - **store**: Nome da loja
    - **product_count**: Total de produtos
    - **total_clicks**: Total de cliques
    - **avg_clicks_per_product**: Média de cliques por produto
    - **ctr**: Click-through rate (%)
    """
    result = await analytics_service.get_store_comparison()
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Erro ao buscar comparativo'))
    
    return {
        'stores': result['data'],
        'count': result['count']
    }


@router.get("/trends")
async def get_trends(
    days: int = Query(default=30, ge=7, le=90, description="Número de dias")
):
    """
    Retorna tendências temporais (clicks por dia)
    
    - **days**: Número de dias para buscar (7-90)
    
    Retorna array de objetos:
    - **date**: Data (YYYY-MM-DD)
    - **clicks**: Total de cliques no dia
    """
    result = await analytics_service.get_trends(days=days)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Erro ao buscar tendências'))
    
    return {
        'trends': result['data'],
        'count': result['count'],
        'period_days': days
    }


@router.get("/health")
async def health_check():
    """Health check do serviço de analytics"""
    return {
        'status': 'ok',
        'service': 'analytics',
        'version': '1.0.0'
    }
