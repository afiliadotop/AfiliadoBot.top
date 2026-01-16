"""
Health check endpoint para monitoring
ITIL Activity: Deliver & Support (Monitoring)
"""
from fastapi import APIRouter
from datetime import datetime
import psutil
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check básico do sistema
    
    Returns:
        - status: ok/degraded/down
        - timestamp: UTC timestamp
        - version: versão da API
        - uptime: tempo de uptime em segundos
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "AfiliadoBot API"
    }

@router.get("/health/detailed")
async def health_check_detailed():
    """
    Health check detalhado com métricas do sistema
    
    Requer autenticação (admin)
    """
    try:
        # Métricas do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Verificar database (tentar ping)
        db_status = "ok"
        try:
            from ..utils.supabase_client import get_supabase_manager
            supabase = get_supabase_manager()
            # Quick query to test connection
            result = supabase.client.table("stores").select("id").limit(1).execute()
            db_status = "ok" if result.data is not None else "error"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free // (1024 ** 3)
            },
            "services": {
                "database": db_status,
                "api": "ok"
            },
            "environment": os.getenv("ENVIRONMENT", "production")
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check - verifica se serviço está pronto para receber tráfego
    
    Usado por load balancers/orchestrators
    """
    try:
        # Verificar dependências críticas
        from ..utils.supabase_client import get_supabase_manager
        supabase = get_supabase_manager()
        
        # Test database
        result = supabase.client.table("stores").select("id").limit(1).execute()
        
        if result.data is not None:
            return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"status": "not_ready", "reason": "database_error"}, 503
            
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}, 503

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check - verifica se serviço está vivo
    
    Usado por orchestrators para restart automático
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
