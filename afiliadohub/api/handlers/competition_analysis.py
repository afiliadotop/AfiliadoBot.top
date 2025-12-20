import asyncio
from datetime import datetime, timedelta
import aiohttp
from typing import Dict, List
import json

class CompetitionAnalyzer:
    def __init__(self):
        self.price_update_threshold = 0.10  # 10% de mudança
        
    async def analyze_price_changes(self, product_ids: List[int]) -> Dict:
        """Analisa mudanças de preço de produtos"""
        try:
            from api.utils.supabase_client import get_supabase_manager
            supabase = get_supabase_manager()
            
            # Busca histórico de preços
            response = supabase.client.table("product_logs")\
                .select("*")\
                .in_("product_id", product_ids)\
                .eq("change_type", "price_change")\
                .order("created_at", desc=True)\
                .execute()
            
            logs = response.data if response.data else []
            
            analysis = {}
            for log in logs:
                product_id = log["product_id"]
                
                if product_id not in analysis:
                    analysis[product_id] = {
                        "price_changes": [],
                        "total_changes": 0,
                        "avg_change_percent": 0,
                        "last_price": 0,
                        "first_price": 0
                    }
                
                analysis[product_id]["price_changes"].append({
                    "old_price": log["old_price"],
                    "new_price": log["new_price"],
                    "change_percent": ((log["new_price"] - log["old_price"]) / log["old_price"]) * 100,
                    "timestamp": log["created_at"]
                })
            
            # Calcula estatísticas
            for product_id, data in analysis.items():
                changes = data["price_changes"]
                if len(changes) >= 2:
                    data["total_changes"] = len(changes)
                    data["last_price"] = changes[0]["new_price"]
                    data["first_price"] = changes[-1]["new_price"]
                    
                    # Média das mudanças
                    total_change = sum(c["change_percent"] for c in changes)
                    data["avg_change_percent"] = total_change / len(changes)
                    
                    # Identifica tendência
                    if data["last_price"] > data["first_price"]:
                        data["trend"] = "up"
                    elif data["last_price"] < data["first_price"]:
                        data["trend"] = "down"
                    else:
                        data["trend"] = "stable"
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    async def compare_with_competitors(self, product_url: str) -> Dict:
        """Compara preço com concorrentes"""
        try:
            # Extrai informações do produto
            from api.utils.link_processor import extract_product_info
            product_info = extract_product_info(product_url)
            
            # Busca produtos similares no banco
            from api.utils.supabase_client import get_supabase_manager
            supabase = get_supabase_manager()
            
            response = supabase.client.table("products")\
                .select("*")\
                .ilike("name", f"%{product_info.get('suggested_tags', [''])[0]}%")\
                .eq("store", product_info.get("store"))\
                .neq("affiliate_link", product_url)\
                .limit(10)\
                .execute()
            
            competitors = response.data if response.data else []
            
            if not competitors:
                return {"message": "Nenhum concorrente encontrado"}
            
            # Busca preço atual do produto
            # (Aqui você precisaria de um scraper ou API para buscar o preço atual)
            current_price = await self.get_current_price(product_url)
            
            # Análise comparativa
            analysis = {
                "product_url": product_url,
                "current_price": current_price,
                "competitors_count": len(competitors),
                "price_comparison": [],
                "summary": {
                    "cheaper_than": 0,
                    "more_expensive_than": 0,
                    "avg_competitor_price": 0,
                    "best_price": float('inf'),
                    "worst_price": 0
                }
            }
            
            total_price = 0
            for competitor in competitors:
                comp_price = competitor.get("current_price", 0)
                total_price += comp_price
                
                price_diff = ((current_price - comp_price) / comp_price) * 100
                
                analysis["price_comparison"].append({
                    "competitor_id": competitor["id"],
                    "competitor_name": competitor["name"][:50],
                    "price": comp_price,
                    "price_difference_percent": price_diff,
                    "url": competitor["affiliate_link"]
                })
                
                # Atualiza estatísticas
                if current_price < comp_price:
                    analysis["summary"]["cheaper_than"] += 1
                else:
                    analysis["summary"]["more_expensive_than"] += 1
                
                analysis["summary"]["best_price"] = min(analysis["summary"]["best_price"], comp_price)
                analysis["summary"]["worst_price"] = max(analysis["summary"]["worst_price"], comp_price)
            
            if competitors:
                analysis["summary"]["avg_competitor_price"] = total_price / len(competitors)
                
                # Recomendação
                if current_price < analysis["summary"]["avg_competitor_price"]:
                    analysis["recommendation"] = "good_price"
                    analysis["recommendation_text"] = "Preço competitivo! Mantenha."
                else:
                    analysis["recommendation"] = "high_price"
                    analysis["recommendation_text"] = f"Considere reduzir o preço em {((current_price - analysis['summary']['avg_competitor_price']) / current_price) * 100:.1f}%"
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_current_price(self, url: str) -> float:
        """Obtém preço atual de um URL (simulado)"""
        # Na prática, você implementaria:
        # 1. Web scraping
        # 2. API da loja
        # 3. Serviço terceiro
        
        # Por enquanto, retorna valor aleatório entre 50 e 500
        import random
        return round(random.uniform(50, 500), 2)
    
    async def monitor_competitors(self, store: str, keywords: List[str]) -> Dict:
        """Monitora concorrentes para keywords específicas"""
        try:
            from api.utils.supabase_client import get_supabase_manager
            supabase = get_supabase_manager()
            
            results = {}
            
            for keyword in keywords:
                # Busca produtos relacionados
                response = supabase.client.table("products")\
                    .select("*")\
                    .eq("store", store)\
                    .or_(f"name.ilike.%{keyword}%,category.ilike.%{keyword}%,tags.cs.{{{keyword}}}") \
                    .limit(20)\
                    .execute()
                
                products = response.data if response.data else []
                
                if products:
                    # Análise de preços para esta keyword
                    prices = [p["current_price"] for p in products if p["current_price"]]
                    
                    results[keyword] = {
                        "product_count": len(products),
                        "avg_price": sum(prices) / len(prices) if prices else 0,
                        "min_price": min(prices) if prices else 0,
                        "max_price": max(prices) if prices else 0,
                        "price_range": max(prices) - min(prices) if prices else 0,
                        "sample_products": [
                            {
                                "id": p["id"],
                                "name": p["name"][:30],
                                "price": p["current_price"],
                                "discount": p.get("discount_percentage", 0)
                            }
                            for p in products[:3]
                        ]
                    }
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
