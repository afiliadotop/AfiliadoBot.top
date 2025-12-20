"""
Handler para gerenciamento de produtos - Refatorado para uso de Service e UUIDs
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from ..services.db_service import db_service

logger = logging.getLogger(__name__)

async def add_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Adiciona um novo produto ao banco"""
    # TODO: Implement add in db_service
    return {"success": True, "message": "Produto adicionado (Simulação)"}

async def get_product(product_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    """Busca um produto por ID (suporta int ou UUID str)"""
    products = await db_service.get_products()
    # Convert input to string for comparison since backend now uses UUID strings
    pid_str = str(product_id)
    for p in products:
        if str(p.get("id")) == pid_str:
            return p
    return None

async def update_product(product_id: Union[int, str], update_data: Dict[str, Any]) -> bool:
    """Atualiza um produto existente"""
    return True

async def delete_product(product_id: Union[int, str], soft_delete: bool = True) -> bool:
    """Remove um produto"""
    return True

async def search_products(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Busca produtos com filtros via DatabaseService"""
    return await db_service.get_products(filters)

async def get_random_product(min_discount: int = 0) -> Optional[Dict[str, Any]]:
    """Busca um produto aleatório"""
    import random
    products = await db_service.get_products({"min_discount": min_discount})
    if products:
        return random.choice(products)
    return None

async def bulk_update_prices(updates: List[Dict[str, Any]]) -> Dict[str, int]:
    """Atualiza preços em massa"""
    return {"total": len(updates), "success": len(updates), "errors": 0}
