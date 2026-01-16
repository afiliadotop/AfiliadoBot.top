"""
Metrics API Handler
ITIL Activity: Engage (Metrics Exposure)
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..services.metrics_service import MetricsService
from ..repositories.product_repository import ProductRepository
from ..utils.supabase_client import get_supabase_manager

router = APIRouter()


def get_metrics_service() -> MetricsService:
    """Get MetricsService instance"""
    supabase = get_supabase_manager()
    product_repo = ProductRepository(supabase.client)
    return MetricsService(product_repo)


@router.get("/metrics/business", response_model=Dict[str, Any])
async def get_business_metrics(
    service: MetricsService = Depends(get_metrics_service)
):
    """
    Get business KPIs.
    
    Returns product counts, store distribution, health score.
    """
    return await service.get_business_metrics()


@router.get("/metrics/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    service: MetricsService = Depends(get_metrics_service)
):
    """
    Get performance metrics.
    
    Note: Connect to APM tool for real-time data.
    """
    return await service.get_performance_metrics()


@router.get("/metrics/slo", response_model=Dict[str, Any])
async def get_slo_metrics(
    service: MetricsService = Depends(get_metrics_service)
):
    """
    Get SLO compliance metrics.
    
    Returns availability, latency, error rate SLOs.
    """
    return await service.get_slo_metrics()


@router.get("/metrics/top-products")
async def get_top_products(
    limit: int = 10,
    service: MetricsService = Depends(get_metrics_service)
):
    """Get top products by commission rate"""
    return await service.get_top_products(limit)
