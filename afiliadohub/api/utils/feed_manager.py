
import logging
import asyncio
import aiohttp
import io
import pandas as pd
from datetime import datetime
from typing import Optional, Dict

from ..utils.supabase_client import get_supabase_manager
from ..handlers.csv_import import CSVImporter

logger = logging.getLogger(__name__)

class FeedManager:
    """Gerenciador de feeds de produtos automatizados"""
    
    def __init__(self):
        self.supabase = get_supabase_manager()
        
    async def check_daily_feeds(self):
        """Verifica e processa feeds agendados"""
        logger.info("[FEED] Verificando feeds agendados...")
        
        try:
            # Busca feeds ativos
            # Por enquanto, pegamos todos os ativos. 
            # Futuramente podemos filtrar por schedule_cron se necessário.
            response = self.supabase.client.table("product_feeds")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
                
            feeds = response.data if response.data else []
            
            if not feeds:
                logger.info("[FEED] Nenhum feed ativo encontrado.")
                return
                
            for feed in feeds:
                # Lógica simplificada de agendamento:
                # Se nunca rodou ou rodou há mais de 20 horas (para garantir que rode todo dia)
                should_run = False
                if not feed.get("last_run_at"):
                    should_run = True
                else:
                    last_run = datetime.fromisoformat(feed["last_run_at"].replace('Z', '+00:00'))
                    # Remove timezone info for comparison if needed, or ensure both are offset-aware
                    if last_run.tzinfo:
                        now = datetime.now(last_run.tzinfo)
                    else:
                        now = datetime.now()
                        
                    time_diff = now - last_run
                    if time_diff.total_seconds() > 20 * 3600: # 20 horas
                        should_run = True
                
                if should_run:
                    # Executa em task separada para não bloquear
                    asyncio.create_task(self._process_single_feed(feed))
                    
        except Exception as e:
            logger.error(f"[FEED] Erro ao verificar feeds: {e}")

    async def _process_single_feed(self, feed: Dict):
        """Processa um único feed"""
        feed_id = feed["id"]
        name = feed["name"]
        url = feed["url"]
        store_id = feed["store_id"] # Precisamos mapear id para nome da store se o CSVImporter pedir string
        
        logger.info(f"[FEED] Iniciando processamento do feed: {name}")
        
        try:
            # Atualiza status para running
            self.supabase.client.table("product_feeds")\
                .update({"status": "running", "last_run_at": datetime.now().isoformat()})\
                .eq("id", feed_id)\
                .execute()
                
            # Download do arquivo
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=1800) as resp: # 30 min timeout para arquivos grandes
                    if resp.status != 200:
                        raise Exception(f"Erro no download: HTTP {resp.status}")
                    
                    data = await resp.read()
                    file_content = io.BytesIO(data)
            
            # Identifica nome da store
            store_name = "shopee" # Default fallback
            if store_id:
                store_res = self.supabase.client.table("stores").select("name").eq("id", store_id).single().execute()
                if store_res.data:
                    store_name = store_res.data["name"].lower()
            
            # Processa CSV
            importer = CSVImporter()
            # Feed automatizado geralmente não deve enviar para telegram massivamente (spam)
            # ou podemos configurar isso no banco. Por padrão FALSE.
            stats = await importer.process_csv_upload(
                file_content=file_content, 
                store=store_name, 
                send_to_telegram=False 
            )
            
            # Atualiza status para success
            self.supabase.client.table("product_feeds")\
                .update({
                    "status": "success", 
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("id", feed_id)\
                .execute()
                
            logger.info(f"[FEED] Sucesso no feed {name}: {stats}")
            
        except Exception as e:
            logger.error(f"[FEED] Falha no feed {name}: {e}")
            
            # Atualiza status para failed
            self.supabase.client.table("product_feeds")\
                .update({
                    "status": f"failed: {str(e)}", 
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("id", feed_id)\
                .execute()

# Instância global
feed_manager = FeedManager()
