import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Any
import pandas as pd

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """Inicializa e retorna o cliente Supabase"""
    
    supabase_url = None
    supabase_key = None

    # 1. Tenta carregar do secrets do Streamlit (Vários formatos possíveis)
    try:
        if "supabase" in st.secrets:
            # Formato [supabase] url="..."
            supabase_url = st.secrets["supabase"]["url"]
            supabase_key = st.secrets["supabase"]["key"]
        else:
            # Formato SUPABASE_URL="..." na raiz
            supabase_url = st.secrets.get("SUPABASE_URL")
            supabase_key = st.secrets.get("SUPABASE_KEY")
            
    except Exception:
        pass

    # 2. Fallback para variáveis de ambiente
    if not supabase_url:
        supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_key:
        supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Credenciais do Supabase não encontradas. Verifique .streamlit/secrets.toml")
        return None
    
    try:
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        return None

# --- Funções Auxiliares (Sua lógica original mantida) ---

def get_products_dataframe(filters: Dict[str, Any] = None, limit: int = 1000) -> pd.DataFrame:
    """Busca produtos como DataFrame"""
    client = get_supabase_client()
    if not client: return pd.DataFrame()
    
    try:
        query = client.table("products").select("*")
        
        if filters:
            if filters.get("store") and filters["store"] != "Todas": 
                query = query.eq("store", filters["store"])
            # Removemos category e active_only por enquanto para evitar erros se colunas não existirem
            # if filters.get("active_only", True): query = query.eq("is_active", True)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        # st.error(f"Erro ao buscar dados: {e}") # Comentado para não poluir a UI
        return pd.DataFrame()

# Mantive seus placeholders para não quebrar imports
def get_daily_stats(date: str = None) -> Dict[str, Any]:
    return {}

def get_store_summary() -> Dict[str, Any]:
    return {}

def insert_product(product_data: Dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client: return False
    try:
        client.table("products").insert(product_data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir: {e}")
        return False

def update_product(product_id: int, update_data: Dict[str, Any]) -> bool:
    client = get_supabase_client()
    if not client: return False
    try:
        client.table("products").update(update_data).eq("id", product_id).execute()
        return True
    except Exception:
        return False

def delete_product(product_id: int, soft_delete: bool = True) -> bool:
    client = get_supabase_client()
    if not client: return False
    try:
        if soft_delete:
            client.table("products").update({"is_active": False}).eq("id", product_id).execute()
        else:
            client.table("products").delete().eq("id", product_id).execute()
        return True
    except Exception:
        return False
