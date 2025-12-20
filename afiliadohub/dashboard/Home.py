import streamlit as st
import sys
import os

# --- BLOCO DE CONFIGURAÇÃO DE PATH (CRÍTICO) ---
# Isso garante que o Python encontre a pasta 'dashboard' e a raiz,
# não importa de onde você rode o comando.
current_dir = os.path.dirname(os.path.abspath(__file__)) # Pasta dashboard
root_dir = os.path.dirname(current_dir) # Pasta afiliadohub (raiz)

if root_dir not in sys.path:
    sys.path.append(root_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# --- IMPORTS ---
# Agora podemos usar o caminho absoluto ou relativo com segurança
try:
    from dashboard.utils.supabase_client import get_supabase_client
    from dashboard.components.header import show_header
    from dashboard.components.sidebar import show_sidebar
except ImportError:
    # Fallback caso esteja rodando de dentro da pasta dashboard
    from utils.supabase_client import get_supabase_client
    from components.header import show_header
    from components.sidebar import show_sidebar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="AfiliadoHub - Painel",
    page_icon="🚀",
    layout="wide"
)

def main():
    show_sidebar()
    show_header()

    st.title("🚀 Painel de Controle")

    supabase = get_supabase_client()
    if not supabase:
        st.error("❌ Erro: Segredos não configurados. Verifique .streamlit/secrets.toml")
        st.stop()

    # Métricas Rápidas
    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            # Tenta contar produtos ativos
            response = supabase.table("products").select("id", count="exact").eq("is_active", True).execute()
            count = response.count if response.count is not None else 0
            st.metric("📦 Produtos Ativos", count)
        except Exception as e:
            st.metric("📦 Produtos Ativos", "Erro")
            st.warning(f"Erro de conexão: {e}")

    st.info("👋 Bem-vindo ao AfiliadoHub! Use o menu lateral para navegar.")

if __name__ == "__main__":
    main()
