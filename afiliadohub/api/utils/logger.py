"""
Sistema de logging estruturado
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
import traceback

class JSONFormatter(logging.Formatter):
    """Formatter que produz logs em JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
            "process": record.processName
        }
        
        # Adiciona exception se houver
        if record.exc_info:
            log_object["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Adiciona dados extras
        if hasattr(record, "extra"):
            log_object.update(record.extra)
        
        return json.dumps(log_object, ensure_ascii=False)

class StructuredLogger:
    """Logger com suporte a dados estruturados"""
    
    def __init__(self, name: str = "afiliadohub"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove handlers existentes
        self.logger.handlers.clear()
        
        # Handler para console com formato legível
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo em JSON
        file_handler = logging.FileHandler("afiliadohub.json.log")
        json_formatter = JSONFormatter()
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log com dados estruturados"""
        extra = kwargs.copy()
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        
        # Cria um LogRecord com extra data
        if extra:
            # Para dados extras, precisamos modificar o record
            import copy
            
            # Hack para adicionar dados extras ao record
            old_factory = logging.getLogRecordFactory()
            
            def record_factory(*args, **kwargs):
                record = old_factory(*args, **kwargs)
                for key, value in extra.items():
                    setattr(record, key, value)
                return record
            
            logging.setLogRecordFactory(record_factory)
            
            try:
                log_method(message)
            finally:
                logging.setLogRecordFactory(old_factory)
        else:
            log_method(message)
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log("DEBUG", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.log("CRITICAL", message, **kwargs)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, duration_ms: float, **kwargs):
        """Log estruturado para requisições API"""
        self.info(
            f"{method} {endpoint} - {status_code} ({duration_ms:.2f}ms)",
            type="api_request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_telegram_event(self, event_type: str, user_id: str = None, chat_id: str = None, **kwargs):
        """Log estruturado para eventos do Telegram"""
        self.info(
            f"Telegram {event_type}",
            type="telegram_event",
            event_type=event_type,
            user_id=user_id,
            chat_id=chat_id,
            **kwargs
        )
    
    def log_product_event(self, event_type: str, product_id: int = None, **kwargs):
        """Log estruturado para eventos de produto"""
        self.info(
            f"Product {event_type}",
            type="product_event",
            event_type=event_type,
            product_id=product_id,
            **kwargs
        )
    
    def log_import_event(self, file_name: str, rows_processed: int, **kwargs):
        """Log estruturado para eventos de importação"""
        self.info(
            f"Import {file_name} - {rows_processed} rows",
            type="import_event",
            file_name=file_name,
            rows_processed=rows_processed,
            **kwargs
        )

# Instância global do logger
logger = StructuredLogger()

def setup_logger(name: str = "afiliadohub", level: str = "INFO"):
    """Configura o logger principal"""
    global logger
    logger = StructuredLogger(name)
    
    # Configura nível de log
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    logger.logger.setLevel(level_map.get(level.upper(), logging.INFO))
    
    return logger

# Logger JSON separado para analytics
json_logger = StructuredLogger("afiliadohub_json")
