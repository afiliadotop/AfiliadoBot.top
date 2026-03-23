import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# --- Ajuste de Path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

st.set_page_config(
    page_title="Estatísticas - AfiliadoHub", page_icon="📊", layout="wide"
)

st.title("📊 Análise de Performance")

# --- Dados de Exemplo (Mock) ---
# Em produção, substituiremos isso por: supabase.table("sales").select("*").execute()
data_vendas = {
    "Data": pd.date_range(start="2024-01-01", periods=7),
    "Vendas": [10, 15, 8, 22, 18, 25, 30],
    "Comissao": [50, 75, 40, 110, 90, 125, 150],
}
df = pd.DataFrame(data_vendas)

# --- Layout dos Gráficos ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vendas nos Últimos 7 Dias")
    fig_vendas = px.line(df, x="Data", y="Vendas", markers=True)
    st.plotly_chart(fig_vendas, use_container_width=True)

with col2:
    st.subheader("Comissões (R$)")
    fig_comissao = px.bar(df, x="Data", y="Comissao", color="Comissao")
    st.plotly_chart(fig_comissao, use_container_width=True)

st.markdown("### 🏆 Top Produtos")
st.dataframe(
    pd.DataFrame(
        {
            "Produto": ["iPhone 15 Case", "Garrafa Térmica", "Fone Bluetooth Lenovo"],
            "Cliques": [1500, 980, 850],
            "Conversão": ["2.5%", "1.8%", "3.0%"],
        }
    ),
    use_container_width=True,
)
