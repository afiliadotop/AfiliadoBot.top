import streamlit as st
from datetime import datetime
import sys
import os

def show_header():
    """Componente de cabeçalho do dashboard"""
    
    # CSS personalizado
    st.markdown("""
    <style>
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
        }
        .header-title { font-size: 2.2rem; font-weight: bold; }
        .status-badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-right: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Busca contagem de forma segura
    count = get_product_count()
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🚀 AfiliadoHub Dashboard</div>
        <div>Sistema de Gestão | {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <div style="margin-top: 10px;">
            <span class="status-badge">✅ Online</span>
            <span class="status-badge">📦 {count} Produtos</span>
            <span class="status-badge">🤖 Bot Ativo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_product_count():
    """Busca contagem com importação segura"""
    try:
        # Tenta importar do caminho absoluto (Recomendado)
        from dashboard.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        if supabase:
            response = supabase.table("products").select("count", count="exact").eq("is_active", True).execute()
            return f"{response.count:,}"
    except ImportError:
        try:
            # Fallback relativo
            from utils.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            if supabase:
                response = supabase.table("products").select("count", count="exact").eq("is_active", True).execute()
                return f"{response.count:,}"
        except:
            pass
    return "..."
