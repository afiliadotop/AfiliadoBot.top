import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, timedelta

# Importa seus módulos
from header import show_header
from charts import create_sales_funnel_chart, create_store_performance_chart, create_daily_trend_chart
from api.utils.supabase_client import get_supabase_manager
from api.handlers.advanced_analytics import AdvancedAnalytics

# Configuração da Página
st.set_page_config(page_title="AfiliadoHub Admin", layout="wide", page_icon="🚀")

# CSS Global
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-left: 5px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 24px; font-weight: bold; }
    .metric-label { font-size: 14px; color: #666; }
</style>
""", unsafe_allow_html=True)

async def load_dashboard_data():
    """Carrega todos os dados necessários de forma assíncrona"""
    analytics = AdvancedAnalytics()
    
    # Executa análises em paralelo se possível, ou sequencial
    funnel = await analytics.get_sales_funnel_analysis(days=30)
    
    # Gera dados de tendência (mock ou real se implementado)
    daily_trends = await analytics._generate_daily_trends(
        (datetime.now() - timedelta(days=7)).isoformat(),
        datetime.now().isoformat()
    )
    
    return funnel, daily_trends

def main():
    # 1. Renderiza Header
    show_header()
    
    # 2. Inicializa Loop Assíncrono para buscar dados
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        funnel_data, daily_trends = loop.run_until_complete(load_dashboard_data())
    except Exception as e:
        st.error(f"Erro de conexão com o Supabase: {e}")
        return

    # 3. Métricas Principais
    st.markdown("### 📈 Performance Geral (30 dias)")
    c1, c2, c3, c4 = st.columns(4)
    
    funnel_metrics = funnel_data.get('funnel', {})
    
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{funnel_metrics.get('products_added', 0)}</div>
            <div class="metric-label">Novos Produtos</div>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{funnel_metrics.get('products_viewed', 0)}</div>
            <div class="metric-label">Visualizações</div>
        </div>""", unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{funnel_metrics.get('products_clicked', 0)}</div>
            <div class="metric-label">Cliques no Link</div>
        </div>""", unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">R$ {funnel_metrics.get('total_sales', 0):.2f}</div>
            <div class="metric-label">Vendas Estimadas</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 4. Gráficos
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.plotly_chart(create_sales_funnel_chart(funnel_metrics), use_container_width=True)
        
    with col_right:
        # Pega dados por loja do analytics
        store_data = funnel_data.get('by_store', {})
        st.plotly_chart(create_store_performance_chart(store_data), use_container_width=True)

    # 5. Tabela de Produtos Recentes
    st.markdown("### 📦 Últimos Produtos Cadastrados")
    
    db = get_supabase_manager()
    # Pequeno hack síncrono para o componente de tabela
    products = loop.run_until_complete(db.get_products(limit=10))
    
    if products:
        df_products = pd.DataFrame(products)
        # Seleciona e renomeia colunas para exibição
        display_df = df_products[['name', 'store', 'current_price', 'discount_percentage', 'created_at']].copy()
        display_df.columns = ['Nome', 'Loja', 'Preço (R$)', 'Desconto (%)', 'Data']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Nenhum produto encontrado.")

if __name__ == "__main__":
    main()
