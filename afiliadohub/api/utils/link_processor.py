import re
import json
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from typing import Dict, Any, Optional, Tuple
import requests

class LinkProcessor:
    """Processador inteligente de links de afiliados"""
    
    # Padrões de URLs por loja
    STORE_PATTERNS = {
        'shopee': [
            r'shopee\.(com\.br|com\.my|co\.th|vn|ph|sg|id|tw)',
            r'shope\.ee'  # Links de afiliado da Shopee
        ],
        'aliexpress': [
            r'aliexpress\.(com|ru)',
            r'aliexpress\.us',
            r's\.click\.aliexpress\.com'  # Links de afiliado
        ],
        'amazon': [
            r'amazon\.(com\.br|com|co\.uk|de|fr|it|es|ca|com\.mx)',
            r'amzn\.to'  # Links de afiliado
        ],
        'temu': [
            r'temu\.com',
            r'temu\.to'
        ],
        'shein': [
            r'shein\.(com|fr|de|es|it|ru|au|ca)',
            r'shein\.top'
        ],
        'magalu': [
            r'magazineluiza\.com\.br',
            r'magalu\.link'
        ],
        'mercado_livre': [
            r'mercadolivre\.com\.br',
            r'mercadolivre\.com',
            r'mercadolivre\.top'
        ]
    }
    
    # Parâmetros de tracking para remover
    TRACKING_PARAMS = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'msclkid', 'twclid', 'irclickid',
        'ref', 'source', 'cid', 'pid', 'af', 'aff', 'affiliate',
        'tracking', 'clickid', 'campaign', 'adid',
        '_kx', 'vero_id', 'vero_conv', 'mkcid', 'mkrid', 'mkwid'
    ]
    
    @staticmethod
    def normalize_link(url: str) -> str:
        """
        Normaliza um link removendo parâmetros desnecessários
        e padronizando formato
        """
        try:
            parsed = urlparse(url)
            
            # Remove fragmento
            parsed = parsed._replace(fragment='')
            
            # Remove parâmetros de tracking
            query_params = parse_qs(parsed.query)
            filtered_params = {}
            
            for key, values in query_params.items():
                key_lower = key.lower()
                is_tracking = any(track in key_lower for track in LinkProcessor.TRACKING_PARAMS)
                
                # Mantém parâmetros importantes
                if not is_tracking and key_lower not in ['', ' ']:
                    # Mantém apenas o primeiro valor
                    filtered_params[key] = values[0] if values else ''
            
            # Reconstrói query
            new_query = urlencode(filtered_params) if filtered_params else ''
            parsed = parsed._replace(query=new_query)
            
            # Normaliza http/https
            if parsed.scheme in ['http', 'https']:
                parsed = parsed._replace(scheme='https')
            
            # Remove www.
            netloc = parsed.netloc.replace('www.', '')
            parsed = parsed._replace(netloc=netloc)
            
            # Remove barras extras no final
            path = parsed.path.rstrip('/')
            parsed = parsed._replace(path=path)
            
            normalized = urlunparse(parsed)
            return normalized
            
        except Exception as e:
            print(f"Erro ao normalizar link {url}: {e}")
            return url
    
    @staticmethod
    def detect_store(url: str) -> Optional[str]:
        """
        Detecta a loja a partir do URL
        """
        normalized = LinkProcessor.normalize_link(url)
        
        for store, patterns in LinkProcessor.STORE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized, re.IGNORECASE):
                    return store
        
        return None
    
    @staticmethod
    def extract_product_id(url: str, store: str) -> Optional[str]:
        """
        Extrai ID do produto do URL
        """
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            if store == 'shopee':
                # Padrão: /product/XXXXXX/YYYYYYYY
                for i, part in enumerate(path_parts):
                    if part == 'product' and i + 2 < len(path_parts):
                        return f"{path_parts[i+1]}-{path_parts[i+2]}"
            
            elif store == 'amazon':
                # Padrão: /dp/XXXXXXXXXX
                for i, part in enumerate(path_parts):
                    if part == 'dp' and i + 1 < len(path_parts):
                        return path_parts[i+1].split('?')[0]
            
            elif store == 'aliexpress':
                # Padrão: /item/XXXXXXXXXX.html
                for part in path_parts:
                    if 'item' in part and '.html' in part:
                        return part.replace('item', '').replace('.html', '')
            
            # Tenta extrair do query string
            query_params = parse_qs(parsed.query)
            for key in ['id', 'product_id', 'pid', 'item_id']:
                if key in query_params:
                    return query_params[key][0]
            
            return None
            
        except Exception as e:
            print(f"Erro ao extrair ID: {e}")
            return None
    
    @staticmethod
    def convert_to_affiliate(url: str, store: str) -> str:
        """
        Converte URL normal para link de afiliado
        (quando aplicável)
        """
        # Mapeamento de prefixos de afiliado
        affiliate_prefixes = {
            'shopee': 'https://shope.ee/',
            'aliexpress': 'https://s.click.aliexpress.com/',
            'amazon': 'https://amzn.to/',
            'temu': 'https://temu.to/',
            'shein': 'https://shein.top/',
            'magalu': 'https://magalu.link/',
            'mercado_livre': 'https://mercadolivre.top/'
        }
        
        # Se já for link de afiliado, retorna normalizado
        for store_name, prefix in affiliate_prefixes.items():
            if url.startswith(prefix):
                return LinkProcessor.normalize_link(url)
        
        # Para Shopee: converte usando API deles (exemplo)
        if store == 'shopee':
            # Extrai ID do produto
            product_id = LinkProcessor.extract_product_id(url, store)
            if product_id:
                # Gera link de afiliado (exemplo)
                return f"https://shope.ee/{product_id}"
        
        # Para Amazon: precisa de API da Amazon Associates
        elif store == 'amazon':
            product_id = LinkProcessor.extract_product_id(url, store)
            if product_id:
                # Usar tracking ID do afiliado
                return f"https://amzn.to/{product_id}"
        
        # Retorna original se não conseguir converter
        return LinkProcessor.normalize_link(url)
    
    @staticmethod
    def validate_affiliate_link(url: str) -> Dict[str, Any]:
        """
        Valida se um link de afiliado é válido
        """
        result = {
            'is_valid': False,
            'store': None,
            'normalized_url': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Verifica se é URL válido
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                result['errors'].append('URL inválido')
                return result
            
            # Detecta loja
            store = LinkProcessor.detect_store(url)
            if not store:
                result['errors'].append('Loja não reconhecida')
                return result
            
            result['store'] = store
            
            # Normaliza URL
            normalized = LinkProcessor.normalize_link(url)
            result['normalized_url'] = normalized
            
            # Verifica se é link de afiliado
            is_affiliate = LinkProcessor.is_affiliate_link(url, store)
            if not is_affiliate:
                result['warnings'].append('URL pode não ser link de afiliado')
            
            # Verifica duplicatas básicas (pela URL normalizada)
            # Esta verificação seria feita no banco
            
            result['is_valid'] = True
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            return result
    
    @staticmethod
    def is_affiliate_link(url: str, store: str) -> bool:
        """
        Verifica se é um link de afiliado
        """
        affiliate_domains = {
            'shopee': ['shope.ee'],
            'aliexpress': ['s.click.aliexpress.com'],
            'amazon': ['amzn.to'],
            'temu': ['temu.to'],
            'shein': ['shein.top'],
            'magalu': ['magalu.link'],
            'mercado_livre': ['mercadolivre.top']
        }
        
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        if store in affiliate_domains:
            return any(domain in netloc for domain in affiliate_domains[store])
        
        return False
    
    @staticmethod
    def extract_product_info_from_url(url: str) -> Dict[str, Any]:
        """
        Tenta extrair informações do produto da URL
        (Implementação básica - idealmente usar APIs das lojas)
        """
        info = {
            'product_id': None,
            'store': None,
            'category': None,
            'suggested_tags': []
        }
        
        try:
            store = LinkProcessor.detect_store(url)
            info['store'] = store
            
            product_id = LinkProcessor.extract_product_id(url, store)
            info['product_id'] = product_id
            
            # Extrai informações do path
            parsed = urlparse(url)
            path_parts = parsed.path.lower().split('/')
            
            # Tenta identificar categoria pelo path
            common_categories = {
                'eletronicos': ['celular', 'smartphone', 'tablet', 'notebook', 'fone'],
                'moda': ['roupa', 'camiseta', 'calca', 'tenis', 'sapato'],
                'casa': ['moveis', 'decoracao', 'utensilios', 'cozinha'],
                'beleza': ['cosmeticos', 'perfume', 'maquiagem', 'creme']
            }
            
            for part in path_parts:
                for category, keywords in common_categories.items():
                    if any(keyword in part for keyword in keywords):
                        info['category'] = category
                        info['suggested_tags'].append(category)
                        break
            
            return info
            
        except Exception as e:
            print(f"Erro ao extrair info: {e}")
            return info

# Funções de conveniência
def normalize_link(url: str) -> str:
    return LinkProcessor.normalize_link(url)

def detect_store(url: str) -> Optional[str]:
    return LinkProcessor.detect_store(url)

def extract_product_info(url: str) -> Dict[str, Any]:
    return LinkProcessor.extract_product_info_from_url(url)
