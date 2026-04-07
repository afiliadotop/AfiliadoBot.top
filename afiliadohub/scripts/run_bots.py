#!/usr/bin/env python3
"""
Orquestrador Central dos Bots
Roda simultaneamente a integração oficial da Shopee e do Scraper da Amazon.
Otimizado para execução diária na Render Cloud.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Adiciona ao path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "afiliadohub"))

from scripts.production.shopee_daily_import import main as shopee_import
from scripts.amazon_scraper_bot import main as amazon_scraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("*"*60)
    logger.info("INICIANDO ORQUESTRADOR MULTI-BOTS (SHOPEE + AMAZON)")
    logger.info("*"*60)
    
    start_time = datetime.now()
    
    # Rodar os dois de forma paralela usando Gather
    logger.info("Disparando processos Assíncronos...")
    
    shopee_task = asyncio.create_task(shopee_import())
    amazon_task = asyncio.create_task(amazon_scraper())
    
    # Aguarda a finalização de ambos os bots
    results = await asyncio.gather(shopee_task, amazon_task, return_exceptions=True)
    
    # Parse dos resultados
    shopee_stats = results[0] if not isinstance(results[0], Exception) else {"errors": 1, "imported": 0}
    amazon_stats = results[1] if not isinstance(results[1], Exception) else {"errors": 1, "imported": 0}
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("*"*60)
    logger.info("BATERIA DE BOTS CONCLUÍDA")
    logger.info(f"DURAÇÃO TOTAL: {duration:.1f} segundos")
    logger.info("*"*60)
    logger.info(f"Shopee Stats -> Inseridos/Atualizados: {shopee_stats.get('imported', 0)} | Erros: {shopee_stats.get('errors', 0)}")
    logger.info(f"Amazon Stats -> Inseridos/Atualizados: {amazon_stats.get('imported', 0)} | Erros: {amazon_stats.get('errors', 0)}")
    logger.info("*"*60)
    
    # Retorna falha se algum deles teve falhas que abortam o processo inteiro
    if shopee_stats.get('errors', 0) > 200 or amazon_stats.get('errors', 0) > 100:
         logger.warning("Muitos erros registrados. Verifique os logs detalhados.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Orquestrador interrompido manualmente pelo usuário.")
        sys.exit(0)
