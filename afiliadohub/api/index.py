import os
from dotenv import load_dotenv

load_dotenv()

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from telegram import Bot, Update
from telegram.ext import Application

# Imports Internos
from api.handlers.commission import CommissionSystem
from api.handlers.competition_analysis import CompetitionAnalyzer
from api.handlers.advanced_analytics import AdvancedAnalytics
from api.handlers.export_reports import ReportExporter
from api.utils.supabase_client import get_supabase_manager
from api.utils.logger import setup_logger
from api.utils.scheduler import scheduler

# Configuração de logging
logger = setup_logger()

# Configurações de Ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRON_TOKEN = os.getenv("CRON_TOKEN")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

# Variáveis Globais
bot = Bot(BOT_TOKEN) if BOT_TOKEN else None
telegram_app = None

# Security
security = HTTPBearer()

# --- LIFECYCLE (Inicialização Inteligente) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup
    logger.info("🚀 Iniciando AfiliadoHub API...")
    
    # Inicia Scheduler (apenas se não estiver em ambiente serverless como Vercel)
    # Se estiver no Vercel, o GitHub Actions (cron.yml) fará o trabalho.
    if os.getenv("RUN_SCHEDULER", "False").lower() == "true":
        await scheduler.start()

    # Inicializa Bot Telegram
    if BOT_TOKEN:
        from api.handlers.telegram import setup_telegram_handlers
        global telegram_app
        telegram_app = await setup_telegram_handlers(BOT_TOKEN)
        
        # Se estiver em modo Polling (VPS local), descomente abaixo:
        # asyncio.create_task(telegram_app.updater.start_polling())
        # asyncio.create_task(telegram_app.start())
        
    yield
    
    # 2. Shutdown
    logger.info("🛑 Encerrando serviços...")
    await scheduler.stop()

# Inicialização do FastAPI
app = FastAPI(
    title="AfiliadoHub API",
    description="API para gestão de afiliados (Shopee/AliExpress/Amazon)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS PYDANTIC ====================

class ProductCreate(BaseModel):
    store: str = Field(..., description="Loja: shopee, aliexpress, etc")
    name: str = Field(..., min_length=3, max_length=500)
    affiliate_link: str = Field(..., min_length=10)
    current_price: float = Field(..., gt=0)
    original_price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    coupon_code: Optional[str] = None
    tags: Optional[List[str]] = []

class TelegramMessage(BaseModel):
    chat_id: str
    message: Optional[str] = None
    product_id: Optional[int] = None

# ==================== DEPENDÊNCIAS DE SEGURANÇA ====================

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica token Bearer para ações administrativas"""
    if not ADMIN_API_KEY:
        return True # Modo dev inseguro se não houver chave
    if credentials.credentials != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Token de administração inválido")
    return credentials.credentials

async def verify_cron_token(request: Request):
    """Verifica token no Header para ações agendadas (GitHub Actions)"""
    token = request.headers.get("X-CRON-TOKEN")
    if not CRON_TOKEN:
        return True # Modo dev
    if not token or token != CRON_TOKEN:
        raise HTTPException(status_code=403, detail="Token CRON inválido")
    return True

# ==================== ROTAS PRINCIPAIS ====================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AfiliadoHub API",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    # Verifica conexão com Supabase
    supabase = get_supabase_manager()
    db_status = "disconnected"
    try:
        supabase.client.table("products").select("count", count="exact").limit(1).execute()
        db_status = "connected"
    except:
        pass

    return {
        "status": "healthy",
        "database": db_status,
        "bot": "ready" if telegram_app else "not_configured"
    }

# ==================== ROTAS DE PRODUTOS ====================

@app.post("/api/products", dependencies=[Depends(verify_admin_token)])
async def create_product(product: ProductCreate):
    from api.handlers.products import add_product
    result = await add_product(product.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.get("/api/products")
async def get_products(
    store: Optional[str] = None,
    limit: int = 50,
    min_discount: int = 0
):
    from api.handlers.products import search_products
    filters = {"store": store, "limit": limit, "min_discount": min_discount}
    return await search_products(filters)

# ==================== IMPORTAÇÃO CSV ====================

@app.post("/api/import/csv", dependencies=[Depends(verify_admin_token)])
async def import_csv(
    file: UploadFile = File(...),
    store: str = "shopee",
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    from api.handlers.csv_import import process_csv_upload
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas CSV permitido")
    
    content = await file.read()
    import io
    file_obj = io.BytesIO(content)
    
    background_tasks.add_task(process_csv_upload, file_obj, store)
    
    return {"status": "processing", "message": "Importação iniciada em background"}

# ==================== WEBHOOK & AUTOMAÇÃO TELEGRAM ====================

# Import Auth Router
from api.handlers.auth import router as auth_router
from api.handlers.products import router as products_router
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Recebe atualizações do Telegram (Mensagens dos usuários)"""
    try:
        data = await request.json()
        if bot and telegram_app:
            update = Update.de_json(data, bot)
            await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "detail": str(e)}

@app.post("/api/telegram/send", dependencies=[Depends(verify_cron_token)])
async def send_cron_message(payload: TelegramMessage):
    """Endpoint chamado pelo GitHub Actions para enviar promoções"""
    from api.handlers.telegram import TelegramBot
    
    try:
        # Se o payload vier com product_id, busca o produto
        if payload.product_id:
            supabase = get_supabase_manager()
            res = supabase.client.table("products").select("*").eq("id", payload.product_id).single().execute()
            if not res.data:
                return {"status": "skipped", "reason": "product_not_found"}
            
            # Instancia bot helper
            tg_helper = TelegramBot(BOT_TOKEN)
            tg_helper.application = telegram_app
            
            await tg_helper.send_product_to_channel(payload.chat_id, res.data)
            return {"status": "sent", "product": res.data["name"]}
            
        # Caso contrário, envia mensagem de texto pura
        elif payload.message and bot:
            await bot.send_message(chat_id=payload.chat_id, text=payload.message, parse_mode=payload.parse_mode)
            return {"status": "sent", "type": "text"}
            
    except Exception as e:
        logger.error(f"Send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS & COMISSÃO ====================

@app.get("/api/stats")
async def stats_endpoint():
    from api.handlers.analytics import get_system_statistics
    return await get_system_statistics()



@app.get("/api/stats/dashboard")
async def stats_dashboard_endpoint():
    """Alias for /api/stats - used by frontend dashboard"""
    from api.handlers.analytics import get_system_statistics
    return await get_system_statistics()

@app.post("/api/commission/calculate", dependencies=[Depends(verify_admin_token)])
async def commission_calc(data: dict):
    commission_system = CommissionSystem()
    return await commission_system.calculate_commission(
        data.get("product_id"), data.get("sale_amount")
    )

# ==================== EXECUÇÃO LOCAL ====================
if __name__ == "__main__":
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
