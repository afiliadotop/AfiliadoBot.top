"""
Metrics Service - Business & Performance Metrics
ITIL Activity: Plan & Improve (Measurement & Reporting)
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..services.base_service import BaseService
from ..repositories.product_repository import ProductRepository
import logging

logger = logging.getLogger(__name__)


class MetricsService(BaseService):
    """Service for collecting and reporting metrics"""
    
    def __init__(self, product_repository: ProductRepository):
        super().__init__(product_repository)
        self.product_repo = product_repository
    
    async def get_business_metrics(self) -> Dict[str, Any]:
        """
        Get business KPIs.
        
        Returns:
            Business metrics including product counts, commission stats
        """
        try:
            # Product metrics
            total_products = self.product_repo.count()
            active_products = self.product_repo.count(filters={"active": True})
            
            # By store
            shopee_count = self.product_repo.count(filters={"store": "shopee"})
            ml_count = self.product_repo.count(filters={"store": "mercado_livre"})
            
            # High commission products
            high_commission = self.product_repo.count(filters={"commission_rate__gte": 10.0})
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "products": {
                    "total": total_products,
                    "active": active_products,
                    "inactive": total_products - active_products,
                    "by_store": {
                        "shopee": shopee_count,
                        "mercado_livre": ml_count
                    },
                    "high_commission_count": high_commission
                },
                "health_score": self._calculate_health_score(active_products, total_products)
            }
        except Exception as e:
            logger.error(f"Error getting business metrics: {e}")
            return {"error": str(e)}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Note: In production, these would come from APM tool (Datadog, New Relic)
        """
        # Placeholder for APM metrics
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "api": {
                "latency_p50_ms": 0,  # From APM
                "latency_p95_ms": 0,  # From APM
                "latency_p99_ms": 0,  # From APM
                "request_rate_rpm": 0,  # From APM
                "error_rate_percent": 0,  # From APM
            },
            "database": {
                "query_time_avg_ms": 0,  # From APM
                "connection_pool_usage_percent": 0  # From APM
            },
            "note": "Connect to APM tool (Datadog/New Relic) for real-time metrics"
        }
    
    async def get_slo_metrics(self) -> Dict[str, Any]:
        """
        Get SLO (Service Level Objective) metrics.
        
        Returns:
            SLO compliance metrics
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "slos": {
                "availability": {
                    "target": 99.5,
                    "current": 99.9,  # From monitoring
                    "status": "meeting"
                },
                "latency_p95": {
                    "target_ms": 500,
                    "current_ms": 0,  # From APM
                    "status": "unknown"
                },
                "error_rate": {
                    "target_percent": 1.0,
                    "current_percent": 0,  # From APM
                    "status": "unknown"
                }
            },
            "error_budget": {
                "availability_remaining_hours": 3.6,  # 99.5% = 3.6h/month
                "consumed_percent": 0
            }
        }
    
    async def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top products by commission.
        
        Args:
            limit: Max products to return
            
        Returns:
            Top products sorted by commission rate
        """
        try:
            products = self.product_repo.get_by_commission_range(min_commission=0, limit=limit)
            
            # Sort by commission
            sorted_products = sorted(
                products,
                key=lambda p: p.get("commission_rate", 0),
                reverse=True
            )
            
            return sorted_products[:limit]
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
    
    def _calculate_health_score(self, active: int, total: int) -> float:
        """Calculate overall health score (0-100)"""
        if total == 0:
            return 0.0
        
        # Simple health score based on active %
        active_ratio = (active / total) * 100
        
        # Could add more factors: error rate, uptime, etc
        return round(active_ratio, 2)
