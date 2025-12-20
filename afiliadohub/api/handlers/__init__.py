"""
Handlers do AfiliadoHub API
"""

from .telegram import TelegramBot, setup_telegram_handlers
from .products import (
    add_product,
    get_product,
    update_product,
    delete_product,
    search_products,
    get_random_product
)
from .csv_import import CSVImporter, process_csv_upload
from .analytics import (
    get_system_statistics,
    get_daily_statistics,
    get_product_analytics
)
from .commission import CommissionSystem
from .competition_analysis import CompetitionAnalyzer
from .advanced_analytics import AdvancedAnalytics
from .export_reports import ReportExporter
from .api_extensions import router as extensions_router

__all__ = [
    'TelegramBot',
    'setup_telegram_handlers',
    'add_product',
    'get_product',
    'update_product',
    'delete_product',
    'search_products',
    'get_random_product',
    'CSVImporter',
    'process_csv_upload',
    'get_system_statistics',
    'get_daily_statistics',
    'get_product_analytics',
    'CommissionSystem',
    'CompetitionAnalyzer',
    'AdvancedAnalytics',
    'ReportExporter',
    'extensions_router'
]
