"""
Sistema de agendamento para tarefas periódicas
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)

class Scheduler:
    """Agendador de tarefas periódicas"""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        
    async def start(self):
        """Inicia o agendador"""
        if self.running:
            return
        
        self.running = True
        logger.info("[SCHEDULER] Agendador iniciado")
        
        # Agenda tarefas padrão
        await self.schedule_default_tasks()
    
    async def schedule_default_tasks(self):
        """Agenda tarefas padrão do sistema"""
        # Verificação de preços a cada hora
        await self.schedule_task(
            "price_check",
            self.check_prices,
            interval_minutes=60
        )
        
        # Limpeza de produtos inativos diariamente
        await self.schedule_task(
            "cleanup",
            self.cleanup_old_products,
            interval_hours=24
        )
        
        # Backup semanal
        await self.schedule_task(
            "backup",
            self.create_backup,
            interval_days=7
        )
    
    async def schedule_task(
        self,
        task_id: str,
        task_func: Callable,
        interval_minutes: int = None,
        interval_hours: int = None,
        interval_days: int = None,
        cron_expression: str = None
    ):
        """Agenda uma tarefa periódica"""
        
        if task_id in self.tasks:
            logger.warning(f"Tarefa {task_id} já está agendada")
            return
        
        self.tasks[task_id] = {
            "func": task_func,
            "last_run": None,
            "next_run": None,
            "interval_minutes": interval_minutes,
            "interval_hours": interval_hours,
            "interval_days": interval_days,
            "cron_expression": cron_expression
        }
        
        logger.info(f"[OK] Tarefa {task_id} agendada")
        
        # Inicia a execução em background
        asyncio.create_task(self._run_task(task_id))
    
    async def _run_task(self, task_id: str):
        """Executa uma tarefa em loop"""
        while self.running and task_id in self.tasks:
            try:
                task = self.tasks[task_id]
                
                # Calcula quando executar
                if task["last_run"] is None:
                    # Primeira execução imediata
                    await self._execute_task(task_id)
                else:
                    # Calcula próximo horário
                    next_run = self._calculate_next_run(task)
                    
                    if datetime.now() >= next_run:
                        await self._execute_task(task_id)
                    else:
                        # Aguarda até o próximo horário
                        wait_seconds = (next_run - datetime.now()).total_seconds()
                        await asyncio.sleep(min(wait_seconds, 60))  # Verifica a cada minuto
                
                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro na tarefa {task_id}: {e}")
                await asyncio.sleep(60)  # Aguarda antes de tentar novamente
    
    def _calculate_next_run(self, task: Dict[str, Any]) -> datetime:
        """Calcula o próximo horário de execução"""
        last_run = task["last_run"]
        
        if task["interval_minutes"]:
            return last_run + timedelta(minutes=task["interval_minutes"])
        elif task["interval_hours"]:
            return last_run + timedelta(hours=task["interval_hours"])
        elif task["interval_days"]:
            return last_run + timedelta(days=task["interval_days"])
        else:
            # Default: a cada hora
            return last_run + timedelta(hours=1)
    
    async def _execute_task(self, task_id: str):
        """Executa uma tarefa"""
        try:
            task = self.tasks[task_id]
            logger.info(f"[RUN] Executando tarefa: {task_id}")
            
            # Atualiza timestamps
            task["last_run"] = datetime.now()
            task["next_run"] = self._calculate_next_run(task)
            
            # Executa a função
            if asyncio.iscoroutinefunction(task["func"]):
                await task["func"]()
            else:
                task["func"]()
            
            logger.info(f"[OK] Tarefa {task_id} concluída")
            
        except Exception as e:
            logger.error(f"[ERRO] Erro na execução da tarefa {task_id}: {e}")
    
    async def check_prices(self):
        """Verifica e atualiza preços dos produtos"""
        try:
            from api.utils.supabase_client import get_supabase_manager
            supabase = get_supabase_manager()
            
            logger.info("[PRICE CHECK] Verificando precos...")
            
            # Busca produtos que precisam de verificação
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            response = supabase.client.table("products")\
                .select("id, affiliate_link, current_price")\
                .eq("is_active", True)\
                .lt("last_checked", week_ago)\
                .limit(50)\
                .execute()
            
            products = response.data if response.data else []
            
            if not products:
                logger.info("[INFO] Nenhum produto precisa de verificacao")
                return
            
            logger.info(f"[INFO] Verificando precos de {len(products)} produtos")
            
            # Aqui você implementaria a lógica real de verificação de preços
            # Por enquanto, apenas atualiza o timestamp
            for product in products:
                supabase.client.table("products")\
                    .update({"last_checked": datetime.now().isoformat()})\
                    .eq("id", product["id"])\
                    .execute()
            
            logger.info(f"[OK] Verificação de preços concluída")
            
        except Exception as e:
            logger.error(f"Erro na verificação de preços: {e}")
    
    async def cleanup_old_products(self):
        """Remove produtos inativos antigos"""
        try:
            from api.utils.supabase_client import get_supabase_manager
            supabase = get_supabase_manager()
            
            logger.info("[CLEANUP] Limpando produtos antigos...")
            
            # Remove produtos inativos com mais de 30 dias
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            response = supabase.client.table("products")\
                .delete()\
                .eq("is_active", False)\
                .lt("updated_at", month_ago)\
                .execute()
            
            deleted_count = len(response.data) if response.data else 0
            
            logger.info(f"[CLEANUP] {deleted_count} produtos antigos removidos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de produtos: {e}")
    
    async def create_backup(self):
        """Cria backup do banco de dados"""
        try:
            logger.info("[BACKUP] Criando backup...")
            
            # Aqui você implementaria a lógica de backup
            # Por enquanto, apenas registra no log
            logger.info("[OK] Backup concluído (simulado)")
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
    
    async def stop(self):
        """Para o agendador"""
        self.running = False
        
        # Cancela todas as tarefas
        for task_id in list(self.tasks.keys()):
            await self.remove_task(task_id)
        
        logger.info("[SCHEDULER] Agendador parado")
    
    async def remove_task(self, task_id: str):
        """Remove uma tarefa agendada"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"[SCHEDULER] Tarefa {task_id} removida")
    
    async def get_task_status(self) -> Dict[str, Any]:
        """Retorna status de todas as tarefas"""
        status = {}
        
        for task_id, task in self.tasks.items():
            status[task_id] = {
                "last_run": task["last_run"].isoformat() if task["last_run"] else None,
                "next_run": task["next_run"].isoformat() if task["next_run"] else None,
                "running": True
            }
        
        return status

# Instância global do agendador
scheduler = Scheduler()
