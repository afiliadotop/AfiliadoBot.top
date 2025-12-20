"""
Utilitários do AfiliadoHub API
"""

from .supabase_client import get_supabase, get_supabase_manager, SupabaseManager
from .link_processor import (
    normalize_link,
    detect_store,
    extract_product_info,
    LinkProcessor
)
from .scheduler import Scheduler, scheduler
from .logger import setup_logger, logger, json_logger

__all__ = [
    'get_supabase',
    'get_supabase_manager',
    'SupabaseManager',
    'normalize_link',
    'detect_store',
    'extract_product_info',
    'LinkProcessor',
    'Scheduler',
    'scheduler',
    'setup_logger',
    'logger',
    'json_logger'
]
