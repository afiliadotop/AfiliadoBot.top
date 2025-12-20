import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
import os

# --- CORREÇÃO DE PATH (CRÍTICO) ---
# Garante que imports da raiz funcionem dentro da pasta pages
current_dir = os.path.dirname(os.path.abspath(__file__)) # Pasta pages
dashboard_dir = os.path.dirname(current_dir) # Pasta dashboard
root_dir = os.path.dirname(dashboard_dir) # Pasta afiliadohub (raiz)

if root_dir not in sys.path:
    sys.path.append(root_dir)

# --- IMPORTS SEGUROS ---
try:
    from dashboard.utils.supabase_client import get_supabase_client
    from dashboard.components.header import show_header
    from dashboard.components.sidebar import show_sidebar
except ImportError:
    # Tenta importar direto se o path estiver confuso
    sys.path.append(dashboard_dir)
    from utils.supabase_client import get_supabase_client
    from components.header import show_header
    from components.sidebar import show_sidebar

# Configuração da página
st.set_page_config(
    page_title="Dashboard - AfiliadoHub",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializa conexão com Supabase
@st.cache_resource
def init_supabase():
    return get_supabase_client()

def main():
    # Header e Sidebar (Componentes reutilizáveis)
    # show_header() # Opcional: Se já tiver header na Home, pode comentar aqui para não duplicar
    
    st.title("🏠 Dashboard Operacional")
    
    # Inicializa Supabase
    supabase = init_supabase()
    
    # Carrega dados
    if supabase:
        load_dashboard_data(supabase)
    else:
        st.error("Erro ao conectar com Supabase. Verifique .streamlit/secrets.toml")

def load_dashboard_data(supabase):
    """Carrega dados para o dashboard"""
    
    # --- MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            response = supabase.table("products").select("count", count="exact").eq("is_active", True).execute()
            total_products = response.count or 0
            st.metric("📦 Produtos Ativos", f"{total_products:,}")
        except:
            st.metric("📦 Produtos Ativos", "0")
    
    with col2:
        try:
            # Conta lojas únicas
            response = supabase.table("products").select("store").eq("is_active", True).execute()
            stores = len(set([p['store'] for p in response.data])) if response.data else 0
            st.metric("🏪 Lojas Ativas", stores)
        except:
            st.metric("🏪 Lojas Ativas", "0")
    
    with col3:
        try:
            # Cupons
            response = supabase.table("products").select("count", count="exact").gt("discount_percentage", 0).execute()
            coupons = response.count or 0
            st.metric("🎫 Ofertas", f"{coupons:,}")
        except:
            st.metric("🎫 Ofertas", "0")
            
    with col4:
         st.metric("🤖 Status Bot", "Online", delta="OK")
    
    st.markdown("---")
    
    # --- GRÁFICOS ---
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("📈 Produtos por Loja")
        try:
            response = supabase.table("products").select("store").eq("is_active", True).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                if not df.empty:
                    store_counts = df['store'].value_counts().reset_index()
                    store_counts.columns = ['Loja', 'Quantidade']
                    fig = px.pie(store_counts, values='Quantidade', names='Loja', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados de lojas.")
        except Exception as e:
            st.error(f"Erro no gráfico: {e}")

    with col_graf2:
        st.subheader("💰 Distribuição de Preços")
        try:
            response = supabase.table("products").select("current_price").limit(500).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                if not df.empty:
                    fig = px.histogram(df, x="current_price", nbins=20, title="Faixa de Preço")
                    st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Sem dados de preço.")

    # --- TABELA RECENTE ---
    st.markdown("### 🆕 Últimos Produtos Adicionados")
    try:
        response = supabase.table("products").select("*").order("created_at", desc=True).limit(5).execute()
        if response.data:
            df_recent = pd.DataFrame(response.data)
            # Simplificando colunas para exibição
            cols_to_show = ['name', 'store', 'current_price', 'discount_percentage']
            # Garante que as colunas existem antes de mostrar
            existing_cols = [c for c in cols_to_show if c in df_recent.columns]
            st.dataframe(df_recent[existing_cols], use_container_width=True)
        else:
            st.info("Nenhum produto encontrado no banco.")
    except Exception as e:
        st.error(f"Erro ao carregar tabela: {e}")

if __name__ == "__main__":
    main()
