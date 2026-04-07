"""
Health check endpoints para monitoring.
ITIL Activity: Deliver & Support (Monitoring)
"""

import os
import logging
from fastapi import APIRouter, Depends
from datetime import datetime
import psutil

from .auth import get_current_admin

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """
    Health check básico do sistema — sem autenticação (para load balancers).

    Returns:
        - status: ok
        - timestamp: UTC timestamp
        - version: versão da API
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "AfiliadoBot API",
    }


@router.get("/health/detailed", dependencies=[Depends(get_current_admin)])
async def health_check_detailed():
    """
    Health check detalhado com métricas do sistema — SOMENTE ADMIN.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        db_status = "ok"
        try:
            from ..utils.supabase_client import get_supabase_manager

            supabase = get_supabase_manager()
            result = supabase.client.table("stores").select("id").limit(1).execute()
            db_status = "ok" if result.data is not None else "error"
        except Exception as e:
            logger.error(f"[Health] DB check falhou: {e}")
            db_status = "error"  # Não expõe detalhes ao cliente

        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free // (1024**3),
            },
            "services": {"database": db_status, "api": "ok"},
            "environment": os.getenv("ENVIRONMENT", "production"),
        }
    except Exception as e:
        logger.error(f"[Health] Erro no health check detalhado: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check — verifica se o serviço está pronto para receber tráfego.
    Usado por load balancers / orchestrators.
    """
    try:
        from ..utils.supabase_client import get_supabase_manager

        supabase = get_supabase_manager()
        result = supabase.client.table("stores").select("id").limit(1).execute()

        if result.data is not None:
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        return {"status": "not_ready", "reason": "database_error"}, 503

    except Exception as e:
        logger.error(f"[Health] Readiness check falhou: {e}")
        return {"status": "not_ready", "reason": "dependency_unavailable"}, 503


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check — verifica se o serviço está vivo.
    Usado por orchestrators para restart automático.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
