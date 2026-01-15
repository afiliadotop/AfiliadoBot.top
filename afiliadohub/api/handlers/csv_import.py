import csv
import io
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from ..utils.supabase_client import get_supabase_manager
from ..utils.link_processor import normalize_link, detect_store, extract_product_info

logger = logging.getLogger(__name__)

class CSVImporter:
    def __init__(self, token: Optional[str] = None):
        self.supabase = get_supabase_manager()
        self.token = token
        self.processed_count = 0
        self.error_count = 0
        self.import_stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        # Cache de stores para lookup rápido
        self.store_cache = self._load_stores()
    
    def _load_stores(self):
        """Carrega stores do banco e cria cache name->id"""
        try:
        try:
            client = self.supabase.get_authenticated_client(self.token) if self.token else self.supabase.client
            result = client.table("stores").select("id, name").execute()
            return {store['name'].lower(): store['id'] for store in result.data}
        except Exception as e:
            logger.warning(f"Erro ao carregar stores: {e}")
            return {}
    
    async def process_csv_upload(self, file_content: io.BytesIO, store: str, replace_existing: bool = False, send_to_telegram: bool = False):
        """Processa upload de CSV em chunks para evitar estouro de memória"""
        try:
            chunk_size = 500  # Processa 500 produtos por vez
            total_processed = 0
            
            # Inicializa Telegram se necessário
            tg_helper = None
            chat_id = None
            if send_to_telegram:
                from .telegram import TelegramBot
                from ..utils.telegram_settings_manager import telegram_settings
                
                # Verifica se Telegram está configurado
                if not telegram_settings.is_configured():
                    logger.warning("Telegram solicitado mas não configurado. Ignorando envio.")
                else:
                    tg_helper = TelegramBot() # Usa settings manager
                    await tg_helper.initialize()
                    chat_id = telegram_settings.get_group_chat_id()

            # Lê o CSV em chunks (iterador)
            # Use encoding='utf-8' ou 'latin-1' dependendo do arquivo, mas pandas geralmente detecta bem
            chunks = pd.read_csv(file_content, chunksize=chunk_size)
            
            logger.info(f"📥 Iniciando importação em stream (chunk_size={chunk_size}), loja: {store}")
            
            for chunk_idx, df in enumerate(chunks):
                chunk_products = []
                
                # Processa linhas do chunk
                for _, row in df.iterrows():
                    try:
                        product = self._parse_csv_row(row, store)
                        if product:
                            chunk_products.append(product)
                    except Exception as e:
                        # logger.warning(f"Erro ao processar linha: {e}")
                        self.error_count += 1
                
                # Insere chunk no banco
                if chunk_products:
                    try:
                        result = await self.supabase.bulk_insert_products(chunk_products, token=self.token)
                        
                        inserted = result.get('inserted', 0)
                        # errors = result.get('errors', 0) 
                        
                        self.import_stats['total'] += len(chunk_products)
                        self.import_stats['imported'] += inserted
                        # self.import_stats['errors'] += errors
                        
                        total_processed += len(chunk_products)
                        
                        # Envia para Telegram se solicitado e configurado
                        if tg_helper and chat_id and inserted > 0:
                            inserted_products = result.get('data', [])
                            # Limita a 5 produtos por chunk para não spamar demais
                            for prod in inserted_products[:5]:
                                await tg_helper.send_product_to_channel(chat_id, prod)
                                await asyncio.sleep(2) # Pausa respeitosa
                                
                        # Log de progresso
                        logger.info(f"[OK] Chunk {chunk_idx+1} processado. Total: {self.import_stats['imported']}")
                        
                    except Exception as e:
                        logger.error(f"[ERRO] Erro ao inserir chunk {chunk_idx+1}: {e}")
                        self.import_stats['errors'] += len(chunk_products)
                else:
                    logger.warning(f"⚠️ Chunk {chunk_idx+1} vazio.")
            
            logger.info(f"🏁 Importação finalizada. Total: {self.import_stats['imported']}")
            if send_to_telegram and tg_helper:
                logger.info(f"📤 Envio para Telegram finalizado.")
                
            return self.import_stats
                
        except Exception as e:
            logger.error(f"[ERRO] Erro ao processar CSV: {e}")
            raise

# Função principal de importação
async def process_csv_upload(file_content, store: str, replace_existing: bool = False, send_to_telegram: bool = False, token: Optional[str] = None):
    """Processa upload de CSV em background"""
    importer = CSVImporter(token=token)
    
    try:
        stats = await importer.process_csv_upload(file_content, store, replace_existing, send_to_telegram)
        
        # Log do resultado
        logger.info(f"""
        📊 Importação Concluída:
        Total processado: {stats['total']}
        Importados: {stats['imported']}
        Atualizados: {stats['updated']}
        Erros: {stats['errors']}
        Loja: {store}
        """)
        
        return stats
        
    except Exception as e:
        logger.error(f"[ERRO] Falha na importação: {e}")
        raise

# Função para importação da Shopee diária
async def import_shopee_daily_csv(url: str, token: Optional[str] = None):
    """Importa CSV diário da Shopee"""
    import requests
    
    try:
        logger.info(f"🔄 Baixando CSV diário da Shopee: {url}")
        
        # Baixa o CSV
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Processa o CSV
        file_content = io.BytesIO(response.content)
        importer = CSVImporter(token=token)
        
        stats = await importer.process_csv_upload(
            file_content,
            store='shopee',
            replace_existing=False
        )
        
        logger.info(f"[OK] CSV Shopee importado: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"[ERRO] Erro ao importar CSV Shopee: {e}")
        return None
