"""
Utilitários do Dashboard AfiliadoHub
"""

from .supabase_client import get_supabase_client
from .data_processor import DataProcessor

__all__ = [
    'get_supabase_client',
    'DataProcessor'
]
