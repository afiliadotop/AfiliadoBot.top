from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/v2", tags=["extended"])

# ==================== NOVOS ENDPOINTS ====================

@router.get("/analytics/funnel")
async def get_sales_funnel(
    days: int = Query(30, ge=1, le=365),
    store: Optional[str] = None
):
    """Retorna análise do funil de vendas"""
    from api.handlers.advanced_analytics import AdvancedAnalytics
    
    analytics = AdvancedAnalytics()
    result = await analytics.get_sales_funnel_analysis(days)
    
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result

@router.get("/competition/analyze")
async def analyze_competition(
    product_url: str = Query(..., description="URL do produto para análise"),
    competitor_limit: int = Query(10, ge=1, le=50)
):
    """Analisa concorrência para um produto"""
    from api.handlers.competition_analysis import CompetitionAnalyzer
    
    analyzer = CompetitionAnalyzer()
    result = await analyzer.compare_with_competitors(product_url)
    
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result

@router.post("/recommendations/generate")
async def generate_recommendations(
    user_id: str,
    limit: int = Query(5, ge=1, le=20),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Gera recomendações personalizadas para um usuário"""
    from api.handlers.telegram_recommendations import TelegramRecommendationEngine
    
    background_tasks.add_task(
        generate_recommendations_background,
        user_id,
        limit
    )
    
    return {
        "status": "processing",
        "message": "Recomendações sendo geradas em background",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }

async def generate_recommendations_background(user_id: str, limit: int):
    """Tarefa em background para gerar recomendações"""
    try:
        from api.handlers.telegram_recommendations import TelegramRecommendationEngine
        from api.utils.supabase_client import get_supabase_manager
        
        engine = TelegramRecommendationEngine()
        supabase = get_supabase_manager()
        
        # Busca histórico do usuário
        response = supabase.client.table("user_interactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=True)\
            .limit(100)\
            .execute()
        
        chat_history = response.data if response.data else []
        
        # Gera recomendações
        recommendations = []
        for _ in range(limit):
            product = await engine.get_personalized_recommendation(int(user_id), chat_history)
            if product:
                recommendations.append(product)
        
        # Salva recomendações
        if recommendations:
            rec_data = {
                "user_id": user_id,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            supabase.client.table("user_recommendations").insert(rec_data).execute()
        
        return recommendations
        
    except Exception as e:
        print(f"Erro ao gerar recomendações: {e}")
        return []

@router.get("/reports/export")
async def export_report(
    report_type: str = Query(..., description="Tipo: products, sales, analytics"),
    format: str = Query("excel", description="Formato: excel, pdf, csv"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Exporta relatório em diferentes formatos"""
    from api.handlers.export_reports import ReportExporter
    
    if not end_date:
        end_date = datetime.now().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    exporter = ReportExporter()
    
    if report_type == "comprehensive":
        result = await exporter.generate_comprehensive_report(start_date, end_date, format)
    else:
        # Busca dados específicos
        from api.utils.supabase_client import get_supabase_manager
        supabase = get_supabase_manager()
        
        if report_type == "products":
            response = supabase.client.table("products")\
                .select("*")\
                .gte("created_at", start_date)\
                .lte("created_at", end_date)\
                .execute()
            
            data = {"products": response.data} if response.data else {}
            
        elif report_type == "sales":
            response = supabase.client.table("commissions")\
                .select("*")\
                .gte("calculated_at", start_date)\
                .lte("calculated_at", end_date)\
                .execute()
            
            data = {"commissions": response.data} if response.data else {}
            
        else:
            raise HTTPException(status_code=400, detail="Tipo de relatório inválido")
        
        # Exporta
        if format == "excel":
            content = await exporter.export_to_excel(data, report_type)
            filename = f"{report_type}_{start_date[:10]}_{end_date[:10]}.xlsx"
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        elif format == "pdf":
            content = await exporter.export_to_pdf(data, report_type)
            filename = f"{report_type}_{start_date[:10]}_{end_date[:10]}.pdf"
            content_type = 'application/pdf'
        
        elif format == "csv":
            content = await exporter.export_to_csv(data, report_type)
            filename = f"{report_type}_{start_date[:10]}_{end_date[:10]}.csv"
            content_type = 'text/csv'
        
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado")
        
        result = {
            "filename": filename,
            "content": content,
            "content_type": content_type
        }
    
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result

@router.get("/monitoring/health")
async def detailed_health_check():
    """Verificação detalhada da saúde do sistema"""
    from api.utils.supabase_client import get_supabase_manager
    
    checks = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "services": {},
        "metrics": {}
    }
    
    # Verifica Supabase
    try:
        supabase = get_supabase_manager()
        response = supabase.client.table("products").select("count", count="exact").limit(1).execute()
        checks["services"]["supabase"] = {
            "status": "connected",
            "product_count": response.count
        }
    except Exception as e:
        checks["services"]["supabase"] = {
            "status": "disconnected",
            "error": str(e)
        }
        checks["status"] = "degraded"
    
    # Verifica API Externa (Telegram)
    try:
        import requests
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        if BOT_TOKEN:
            response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5)
            checks["services"]["telegram"] = {
                "status": "connected" if response.status_code == 200 else "disconnected",
                "response_time": response.elapsed.total_seconds()
            }
        else:
            checks["services"]["telegram"] = {"status": "not_configured"}
    except Exception as e:
        checks["services"]["telegram"] = {
            "status": "disconnected",
            "error": str(e)
        }
    
    # Coleta métricas
    try:
        from api.handlers.advanced_analytics import AdvancedAnalytics
        analytics = AdvancedAnalytics()
        funnel = await analytics.get_sales_funnel_analysis(7)
        
        if 'funnel' in funnel:
            checks["metrics"] = {
                "products_added_7d": funnel["funnel"].get("products_added", 0),
                "products_sold_7d": funnel["funnel"].get("products_sold", 0),
                "conversion_rate": funnel["funnel"].get("conversion_rates", {}).get("sale_to_click", 0)
            }
    except Exception as e:
        checks["metrics_error"] = str(e)
    
    # Verifica espaço em disco (simulado)
    checks["storage"] = {
        "status": "normal",
        "estimated_records": checks["services"].get("supabase", {}).get("product_count", 0),
        "estimated_size_mb": checks["services"].get("supabase", {}).get("product_count", 0) * 0.5  # 0.5KB por produto
    }
    
    return checks
