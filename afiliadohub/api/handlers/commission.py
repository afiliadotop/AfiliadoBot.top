import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from api.utils.supabase_client import get_supabase_manager

class CommissionSystem:
    def __init__(self):
        self.supabase = get_supabase_manager()
        self.commission_rates = {
            'shopee': Decimal('0.05'),      # 5%
            'aliexpress': Decimal('0.08'),   # 8%
            'amazon': Decimal('0.04'),       # 4%
            'temu': Decimal('0.10'),         # 10%
            'shein': Decimal('0.06'),        # 6%
            'magalu': Decimal('0.03'),       # 3%
            'mercado_livre': Decimal('0.02') # 2%
        }
    
    async def calculate_commission(self, product_id: int, sale_amount: Decimal) -> Dict:
        """Calcula comissão para uma venda"""
        try:
            # Busca produto
            response = self.supabase.client.table("products")\
                .select("store, current_price")\
                .eq("id", product_id)\
                .single()\
                .execute()
            
            if not response.data:
                return {"error": "Produto não encontrado"}
            
            store = response.data["store"]
            commission_rate = self.commission_rates.get(store, Decimal('0.05'))
            
            # Calcula comissão
            commission = sale_amount * commission_rate
            
            # Registra no histórico
            commission_record = {
                "product_id": product_id,
                "store": store,
                "sale_amount": float(sale_amount),
                "commission_rate": float(commission_rate),
                "commission_amount": float(commission),
                "status": "pending",
                "calculated_at": datetime.now().isoformat()
            }
            
            # Salva no banco
            self.supabase.client.table("commissions").insert(commission_record).execute()
            
            return {
                "success": True,
                "commission": float(commission),
                "rate": float(commission_rate),
                "store": store
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_user_commissions(self, user_id: str, period_days: int = 30) -> Dict:
        """Busca comissões de um usuário"""
        try:
            start_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            response = self.supabase.client.table("commissions")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("calculated_at", start_date)\
                .execute()
            
            commissions = response.data if response.data else []
            
            # Calcula totais
            total_sales = sum(c["sale_amount"] for c in commissions)
            total_commission = sum(c["commission_amount"] for c in commissions)
            
            # Agrupa por loja
            by_store = {}
            for c in commissions:
                store = c["store"]
                if store not in by_store:
                    by_store[store] = {
                        "sales": 0,
                        "commission": 0,
                        "count": 0
                    }
                by_store[store]["sales"] += c["sale_amount"]
                by_store[store]["commission"] += c["commission_amount"]
                by_store[store]["count"] += 1
            
            return {
                "period_days": period_days,
                "total_sales": total_sales,
                "total_commission": total_commission,
                "commission_by_store": by_store,
                "commissions": commissions[:50]  # Limita histórico
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_commission_report(self, start_date: str, end_date: str) -> Dict:
        """Gera relatório de comissões para um período"""
        try:
            response = self.supabase.client.table("commissions")\
                .select("*")\
                .gte("calculated_at", start_date)\
                .lte("calculated_at", end_date)\
                .execute()
            
            commissions = response.data if response.data else []
            
            if not commissions:
                return {"message": "Nenhuma comissão no período"}
            
            # Processa dados
            df_data = []
            for c in commissions:
                df_data.append({
                    "Data": c["calculated_at"][:10],
                    "Loja": c["store"],
                    "Venda (R$)": c["sale_amount"],
                    "Comissão (%)": c["commission_rate"] * 100,
                    "Comissão (R$)": c["commission_amount"],
                    "Status": c["status"]
                })
            
            # Agregações
            summary = {
                "period": f"{start_date[:10]} a {end_date[:10]}",
                "total_sales": sum(c["sale_amount"] for c in commissions),
                "total_commission": sum(c["commission_amount"] for c in commissions),
                "commission_by_store": {},
                "daily_totals": {}
            }
            
            # Por loja
            for c in commissions:
                store = c["store"]
                if store not in summary["commission_by_store"]:
                    summary["commission_by_store"][store] = {
                        "sales": 0,
                        "commission": 0,
                        "count": 0
                    }
                summary["commission_by_store"][store]["sales"] += c["sale_amount"]
                summary["commission_by_store"][store]["commission"] += c["commission_amount"]
                summary["commission_by_store"][store]["count"] += 1
            
            # Por dia
            for c in commissions:
                date = c["calculated_at"][:10]
                if date not in summary["daily_totals"]:
                    summary["daily_totals"][date] = {
                        "sales": 0,
                        "commission": 0
                    }
                summary["daily_totals"][date]["sales"] += c["sale_amount"]
                summary["daily_totals"][date]["commission"] += c["commission_amount"]
            
            return {
                "summary": summary,
                "data": df_data,
                "count": len(commissions)
            }
            
        except Exception as e:
            return {"error": str(e)}
