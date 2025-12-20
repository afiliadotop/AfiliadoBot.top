import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

class DataProcessor:
    @staticmethod
    def process_csv_data(df: pd.DataFrame, store: str) -> List[Dict[str, Any]]:
        """Processa dados CSV para formato do banco"""
        processed = []
        
        for _, row in df.iterrows():
            try:
                # Extrai dados básicos
                name = DataProcessor._extract_field(row, ['name', 'product', 'title', 'nome'])
                link = DataProcessor._extract_field(row, ['link', 'url', 'affiliate_link'])
                price = DataProcessor._extract_price(row, ['price', 'current_price', 'preco'])
                
                if not name or not link or not price:
                    continue
                
                # Cria produto
                product = {
                    'store': store,
                    'name': str(name)[:500],
                    'affiliate_link': str(link),
                    'current_price': float(price),
                    'original_price': DataProcessor._extract_price(row, ['original_price', 'old_price', 'preco_original']),
                    'category': DataProcessor._extract_field(row, ['category', 'categoria']),
                    'image_url': DataProcessor._extract_field(row, ['image', 'image_url', 'imagem']),
                    'source': 'csv_import',
                    'is_active': True,
                    'tags': DataProcessor._extract_tags(row, name)
                }
                
                # Calcula desconto
                if product['original_price'] and product['original_price'] > product['current_price']:
                    discount = ((product['original_price'] - product['current_price']) / product['original_price']) * 100
                    product['discount_percentage'] = int(discount)
                
                processed.append(product)
                
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue
        
        return processed
    
    @staticmethod
    def _extract_field(row, possible_keys):
        """Extrai campo do DataFrame"""
        for key in possible_keys:
            if key in row and pd.notna(row[key]):
                return str(row[key]).strip()
        return None
    
    @staticmethod
    def _extract_price(row, possible_keys):
        """Extrai e converte preço"""
        price_str = DataProcessor._extract_field(row, possible_keys)
        if price_str:
            try:
                # Remove caracteres não numéricos
                price_str = price_str.replace('R$', '').replace('$', '').replace(',', '.').strip()
                return float(price_str)
            except:
                return None
        return None
    
    @staticmethod
    def _extract_tags(row, product_name):
        """Extrai tags do produto"""
        tags = []
        
        # Tags do campo específico
        tags_field = DataProcessor._extract_field(row, ['tags', 'keywords'])
        if tags_field:
            tags.extend([tag.strip() for tag in str(tags_field).split(',')[:5]])
        
        # Tags baseadas no nome
        name_lower = str(product_name).lower()
        
        keyword_tags = {
            'smartphone': ['celular', 'telefone'],
            'notebook': ['laptop', 'computador'],
            'fone': ['headphone', 'headset'],
            'bluetooth': ['wireless'],
            'relogio': ['watch'],
            'tenis': ['sneaker', 'calcado'],
            'camiseta': ['tshirt', 'roupa']
        }
        
        for keyword, tag_list in keyword_tags.items():
            if keyword in name_lower:
                tags.extend(tag_list)
        
        return list(set(tags))[:10]
    
    @staticmethod
    def aggregate_daily_stats(data: List[Dict]) -> Dict:
        """Agrega estatísticas diárias"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        stats = {
            'date': datetime.now().date().isoformat(),
            'total_products': len(df),
            'active_products': df['is_active'].sum() if 'is_active' in df.columns else 0,
            'avg_price': df['current_price'].mean() if 'current_price' in df.columns else 0,
            'total_value': df['current_price'].sum() if 'current_price' in df.columns else 0,
            'with_discount': df['discount_percentage'].notnull().sum() if 'discount_percentage' in df.columns else 0,
            'avg_discount': df['discount_percentage'].mean() if 'discount_percentage' in df.columns else 0
        }
        
        return stats
