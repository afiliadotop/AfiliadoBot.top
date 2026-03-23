import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
import os

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dashboard.utils.supabase_client import get_supabase_client
from dashboard.components.header import show_header
from dashboard.components.sidebar import show_sidebar

# Configuração da página
st.set_page_config(
    page_title="AfiliadoHub - Painel Administrativo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown(
    """
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
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .success-text { color: #10B981; }
    .warning-text { color: #F59E0B; }
    .danger-text { color: #EF4444; }
    .info-text { color: #3B82F6; }
</style>
""",
    unsafe_allow_html=True,
)


# Inicializa conexão com Supabase
@st.cache_resource
def init_supabase():
    return get_supabase_client()


def main():
    # Mostra cabeçalho
    show_header()

    # Mostra sidebar
    show_sidebar()

    # Página inicial
    st.markdown(
        '<div class="main-header">📊 Dashboard Geral</div>', unsafe_allow_html=True
    )

    # Inicializa Supabase
    supabase = init_supabase()

    # Carrega dados iniciais
    load_dashboard_data(supabase)


def load_dashboard_data(supabase):
    """Carrega dados para o dashboard"""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Total de produtos
        try:
            response = (
                supabase.table("products")
                .select("count", count="exact")
                .eq("is_active", True)
                .execute()
            )
            total_products = response.count or 0
            st.metric(
                label="📦 Produtos Ativos", value=f"{total_products:,}", delta="+12%"
            )
        except:
            st.metric(label="📦 Produtos Ativos", value="0")

    with col2:
        # Total de lojas
        try:
            response = (
                supabase.table("products")
                .select("store")
                .eq("is_active", True)
                .execute()
            )
            stores = (
                len(set([p["store"] for p in response.data])) if response.data else 0
            )
            st.metric(label="🏪 Lojas Ativas", value=stores, delta="+2")
        except:
            st.metric(label="🏪 Lojas Ativas", value="0")

    with col3:
        # Cupons com desconto
        try:
            response = (
                supabase.table("products")
                .select("count", count="exact")
                .eq("is_active", True)
                .gt("discount_percentage", 0)
                .execute()
            )
            coupons = response.count or 0
            st.metric(label="🎫 Cupons com Desconto", value=f"{coupons:,}", delta="+8%")
        except:
            st.metric(label="🎫 Cupons com Desconto", value="0")

    with col4:
        # Envios Telegram (últimos 7 dias)
        try:
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            response = (
                supabase.table("product_stats")
                .select("telegram_send_count")
                .gte("last_sent", week_ago)
                .execute()
            )
            telegram_sends = (
                sum([p.get("telegram_send_count", 0) for p in response.data])
                if response.data
                else 0
            )
            st.metric(
                label="🤖 Envios Telegram", value=f"{telegram_sends:,}", delta="+15%"
            )
        except:
            st.metric(label="🤖 Envios Telegram", value="0")

    # Gráficos
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Produtos por Loja")
        try:
            # Busca contagem por loja
            response = (
                supabase.table("products")
                .select("store")
                .eq("is_active", True)
                .execute()
            )
            if response.data:
                df = pd.DataFrame(response.data)
                store_counts = df["store"].value_counts().reset_index()
                store_counts.columns = ["Loja", "Quantidade"]

                fig = px.pie(
                    store_counts,
                    values="Quantidade",
                    names="Loja",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar gráfico: {e}")

    with col2:
        st.subheader("📊 Distribuição de Preços")
        try:
            response = (
                supabase.table("products")
                .select("current_price")
                .eq("is_active", True)
                .limit(1000)
                .execute()
            )

            if response.data:
                df = pd.DataFrame(response.data)

                # Remove outliers
                Q1 = df["current_price"].quantile(0.25)
                Q3 = df["current_price"].quantile(0.75)
                IQR = Q3 - Q1
                df_filtered = df[
                    (df["current_price"] >= Q1 - 1.5 * IQR)
                    & (df["current_price"] <= Q3 + 1.5 * IQR)
                ]

                fig = px.histogram(
                    df_filtered,
                    x="current_price",
                    nbins=30,
                    title="Distribuição de Preços",
                    labels={"current_price": "Preço (R$)"},
                    color_discrete_sequence=["#3B82F6"],
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar histograma: {e}")

    # Tabela de produtos recentes
    st.markdown("---")
    st.subheader("🆕 Produtos Recentes")

    try:
        response = (
            supabase.table("products")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        if response.data:
            df = pd.DataFrame(response.data)

            # Formata colunas
            if not df.empty:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime(
                    "%d/%m/%Y %H:%M"
                )
                df["current_price"] = df["current_price"].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "v")
                    .replace(".", ",")
                    .replace("v", ".")
                )
                df["discount_percentage"] = (
                    df["discount_percentage"]
                    .fillna(0)
                    .apply(lambda x: f"{int(x)}%" if x > 0 else "")
                )

                # Seleciona colunas para mostrar
                display_cols = [
                    "name",
                    "store",
                    "current_price",
                    "discount_percentage",
                    "created_at",
                ]
                display_df = df[display_cols].copy()
                display_df.columns = [
                    "Produto",
                    "Loja",
                    "Preço",
                    "Desconto",
                    "Adicionado em",
                ]

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Produto": st.column_config.TextColumn(width="large"),
                        "Loja": st.column_config.TextColumn(width="small"),
                        "Preço": st.column_config.TextColumn(width="small"),
                        "Desconto": st.column_config.TextColumn(width="small"),
                        "Adicionado em": st.column_config.TextColumn(width="medium"),
                    },
                )
        else:
            st.info("Nenhum produto encontrado.")

    except Exception as e:
        st.error(f"Erro ao carregar produtos recentes: {e}")

    # Ações rápidas
    st.markdown("---")
    st.subheader("⚡ Ações Rápidas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🆕 Adicionar Produto", use_container_width=True):
            st.switch_page("pages/2_📦_Produtos.py")

    with col2:
        if st.button("📥 Importar CSV", use_container_width=True):
            st.switch_page("pages/4_🔄_Importar.py")

    with col3:
        if st.button("🤖 Enviar Promoção", use_container_width=True):
            # Lógica para enviar promoção imediatamente
            st.info("Enviando promoção...")
            # Aqui você chamaria a API para enviar promoção

    with col4:
        if st.button("📊 Gerar Relatório", use_container_width=True):
            st.switch_page("pages/3_📊_Estatísticas.py")


if __name__ == "__main__":
    main()
