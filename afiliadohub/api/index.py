import os
from dotenv import load_dotenv

load_dotenv()

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, BackgroundTasks, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from telegram import Bot, Update
from telegram.ext import Application

# Imports Internos
from .handlers.commission import CommissionSystem
from .handlers.competition_analysis import CompetitionAnalyzer
from .handlers.advanced_analytics import AdvancedAnalytics
from .handlers.export_reports import ReportExporter
from .handlers.health import router as health_router
from .utils.supabase_client import get_supabase_manager
from .utils.logger import setup_logger
from .utils.scheduler import scheduler

# Configuração de logging
logger = setup_logger()

# Configurações de Ambiente
# TELEGRAM_BOT_TOKEN removido - agora usa banco de dados via telegram_settings_manager
CRON_TOKEN = os.getenv("CRON_TOKEN")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

# Variáveis Globais
telegram_app = None
# bot global será descontinuado em favor de telegram_app.bot ou instanciado sob demanda

# Security
security = HTTPBearer()

# --- LIFECYCLE (Inicialização Inteligente) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup
    logger.info("[STARTUP] Iniciando AfiliadoHub API...")
    
    # Inicia Scheduler (apenas se não estiver em ambiente serverless como Vercel)
    if os.getenv("RUN_SCHEDULER", "False").lower() == "true":
        await scheduler.start()

    # Inicializa Bot Telegram (Tenta carregar configurações do banco)
    try:
        from .handlers.telegram import setup_telegram_handlers
        global telegram_app
        
        # Tenta inicializar. Se não tiver config no banco, retorna None (sem erro)
        telegram_app = await setup_telegram_handlers()
        
        if telegram_app:
            logger.info("[TELEGRAM] Bot inicializado com sucesso via banco de dados")
            
            # Configura webhook para produção (Render)
            render_url = os.getenv("RENDER_EXTERNAL_URL")
            if render_url:
                webhook_url = f"{render_url}/api/telegram/webhook"
                try:
                    await telegram_app.bot.set_webhook(webhook_url)
                    logger.info(f"[TELEGRAM] Webhook configurado: {webhook_url}")
                except Exception as e:
                    logger.error(f"[TELEGRAM] Erro ao configurar webhook: {e}")
            else:
                logger.info("[TELEGRAM] Modo local - sem webhook")
        else:
            logger.warning("[TELEGRAM] Bot não inicializado (Configurações ausentes no DB)")
            
    except Exception as e:
        logger.error(f"[STARTUP] Erro ao inicializar Telegram: {e}")
        
    yield
    
    # 2. Shutdown
    logger.info("[SHUTDOWN] Encerrando servicos...")
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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
    from .handlers.products import add_product
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
    from .handlers.products import search_products
    filters = {"store": store, "limit": limit, "min_discount": min_discount}
    return await search_products(filters)

# ==================== TELEGRAM WEBHOOK ====================

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    """Recebe updates do Telegram via webhook"""
    try:
        if not telegram_app:
            return {"ok": False, "error": "Bot not initialized"}
        
        update_data = await request.json()
        
        # Processar update do Telegram
        from telegram import Update
        # Usar o bot do telegram_app
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"[TELEGRAM WEBHOOK] Erro: {e}")
        return {"ok": False, "error": str(e)}

# ==================== IMPORTAÇÃO CSV ====================

@app.post("/api/import/csv", dependencies=[Depends(verify_admin_token)])
async def import_csv(
    file: UploadFile = File(...),
    store: str = "shopee",
    send_to_telegram: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    from .handlers.csv_import import process_csv_upload
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas CSV permitido")
    
    content = await file.read()
    import io
    file_obj = io.BytesIO(content)
    
    background_tasks.add_task(process_csv_upload, file_obj, store, False, send_to_telegram)
    
    return {"status": "processing", "message": "Importação iniciada em background"}

# ==================== WEBHOOK & AUTOMAÇÃO TELEGRAM ====================

# Import Auth Router
from .handlers.auth import router as auth_router
from .handlers.products import router as products_router
from .handlers.shopee_api import router as shopee_router
from .handlers.mercadolivre_api import router as mercadolivre_router
from .handlers.telegram_settings import router as telegram_settings_router

# Mercado Livre OAuth Callback (temporário para obter tokens)
@app.get("/api/ml/callback")
async def ml_oauth_callback(code: str = Query(...)):
    """Callback OAuth do Mercado Livre - Obter Access Token"""
    import httpx
    
    ML_APP_ID = os.getenv("ML_APP_ID")
    ML_SECRET_KEY = os.getenv("ML_SECRET_KEY")
    REDIRECT_URI = "https://afiliadobot.top/api/ml/callback"
    
    if not ML_APP_ID or not ML_SECRET_KEY:
        return {"error": "ML_APP_ID e ML_SECRET_KEY não configurados no .env"}
    
    # Trocar CODE por ACCESS_TOKEN
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": ML_APP_ID,
        "client_secret": ML_SECRET_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        return {
            "success": True,
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_in": data.get("expires_in"),
            "token_type": data.get("token_type"),
            "instructions": "Copie o access_token e refresh_token e adicione ao .env como ML_ACCESS_TOKEN e ML_REFRESH_TOKEN"
        }
    except Exception as e:
        logger.error(f"ML OAuth error: {e}")
        return {"error": str(e), "success": False}

# Registrar routers
app.include_router(health_router)  # Health check (no prefix - root level)
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(shopee_router, prefix="/api")
app.include_router(mercadolivre_router, prefix="/api")
app.include_router(telegram_settings_router, prefix="/api")

# Feed Router
from .handlers.feed_api import router as feed_router
if feed_router:
    app.include_router(feed_router, prefix="/api")

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
    from .handlers.telegram import TelegramBot
    
    try:
        # Helper para operações do Telegram
        tg_helper = TelegramBot() # Pega token do banco automaticamente se não passado
        
        # Se o payload vier com product_id, busca o produto
        if payload.product_id:
            supabase = get_supabase_manager()
            res = supabase.client.table("products").select("*").eq("id", payload.product_id).single().execute()
            if not res.data:
                return {"status": "skipped", "reason": "product_not_found"}
            
            # Passa a app global se existir, senão o helper se vira
            tg_helper.application = telegram_app
            
            success = await tg_helper.send_product_to_channel(payload.chat_id, res.data)
            status = "sent" if success else "failed"
            return {"status": status, "product": res.data["name"]}
            
        # Caso contrário, envia mensagem de texto pura
        elif payload.message:
            # Inicializa app/bot se precisar (para ter acesso ao bot.send_message)
            if telegram_app:
                bot_instance = telegram_app.bot
            else:
                # Tenta inicializar sob demanda
                app_instance = await tg_helper.initialize()
                if not app_instance:
                     return {"status": "skipped", "reason": "bot_not_configured"}
                bot_instance = app_instance.bot

            await bot_instance.send_message(chat_id=payload.chat_id, text=payload.message)
            return {"status": "sent", "type": "text"}
            
    except Exception as e:
        logger.error(f"Send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS & COMISSÃO ====================

@app.get("/api/stats")
async def stats_endpoint():
    from .handlers.analytics import get_system_statistics
    return await get_system_statistics()



@app.get("/api/stats/dashboard")
async def stats_dashboard_endpoint():
    """Alias for /api/stats - used by frontend dashboard"""
    from .handlers.analytics import get_system_statistics
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
