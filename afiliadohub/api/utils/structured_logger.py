"""
Structured Logger - Enterprise Logging
ITIL Activity: Support (Operational Excellence)
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import uuid
import contextvars

# Context variable for correlation ID (thread-safe)
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)


class StructuredLogger:
    """
    Structured logger with JSON output and correlation IDs.
    
    Features:
    - JSON formatted logs (easy parsing)
    - Correlation IDs (track requests across services)
    - Structured context (key-value pairs)
    - Multiple log levels
    """
    
    def __init__(self, name: str, correlation_id: Optional[str] = None):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically __name__)
            correlation_id: Optional correlation ID for request tracking
        """
        self.logger = logging.getLogger(name)
        self.name = name
        
        # Set correlation ID
        if correlation_id:
            correlation_id_var.set(correlation_id)
        elif not correlation_id_var.get():
            correlation_id_var.set(str(uuid.uuid4()))
    
    def _format_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Format log entry as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "message": message,
            "correlation_id": correlation_id_var.get(),
            "service": "afiliadohub-api",
            "environment": "production"  # Could be from env var
        }
        
        # Add context
        if context:
            log_entry["context"] = context
        
        # Add extra fields
        if kwargs:
            log_entry.update(kwargs)
        
        return json.dumps(log_entry)
    
    def debug(self, message: str, context: Optional[Dict] = None, **kwargs):
        """Log DEBUG level"""
        self.logger.debug(self._format_log("DEBUG", message, context, **kwargs))
    
    def info(self, message: str, context: Optional[Dict] = None, **kwargs):
        """Log INFO level"""
        self.logger.info(self._format_log("INFO", message, context, **kwargs))
    
    def warning(self, message: str, context: Optional[Dict] = None, **kwargs):
        """Log WARNING level"""
        self.logger.warning(self._format_log("WARNING", message, context, **kwargs))
    
    def error(self, message: str, context: Optional[Dict] = None, **kwargs):
        """Log ERROR level"""
        self.logger.error(self._format_log("ERROR", message, context, **kwargs))
    
    def critical(self, message: str, context: Optional[Dict] = None, **kwargs):
        """Log CRITICAL level"""
        self.logger.critical(self._format_log("CRITICAL", message, context, **kwargs))
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get current correlation ID"""
        return correlation_id_var.get()
    
    @staticmethod
    def set_correlation_id(correlation_id: str):
        """Set correlation ID for current context"""
        correlation_id_var.set(correlation_id)


# Convenience function
def get_logger(name: str, correlation_id: Optional[str] = None) -> StructuredLogger:
    """
    Get structured logger instance.
    
    Args:
        name: Logger name (use __name__)
        correlation_id: Optional correlation ID
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, correlation_id)
