"""
Middleware de logging estruturado para todas as requisições HTTP.
Regista método, path, status code e duração em ms.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Loga automaticamente cada requisição: método, path, status e duração."""

    # Paths que não precisam de log (ruído desnecessário)
    SKIP_PATHS = {"/health", "/health/live", "/health/ready", "/", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            raise exc
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            log_fn = logger.warning if status_code >= 400 else logger.info
            log_fn(
                f"{request.method} {request.url.path} -> {status_code} ({duration_ms:.1f}ms)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 1),
                },
            )
