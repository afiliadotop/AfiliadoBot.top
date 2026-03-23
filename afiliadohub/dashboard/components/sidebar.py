import streamlit as st
from datetime import datetime


def show_sidebar():
    """Sidebar com navegação segura"""

    with st.sidebar:
        st.title("🚀 AfiliadoHub")
        st.caption("Painel Administrativo")
        st.markdown("---")

        # Menu de Navegação
        pages = [
            {"icon": "🏠", "name": "Dashboard", "page": "1_🏠_Dashboard.py"},
            {"icon": "📦", "name": "Produtos", "page": "2_📦_Produtos.py"},
            {"icon": "📊", "name": "Estatísticas", "page": "3_📊_Estatísticas.py"},
            {"icon": "🔄", "name": "Importar", "page": "4_🔄_Importar.py"},
            {"icon": "🤖", "name": "Telegram", "page": "5_🤖_Telegram.py"},
        ]

        current_page = str(st.session_state.get("current_page", "Dashboard"))

        st.markdown("### 📁 Navegação")
        for page in pages:
            # Botão que troca de página
            if st.button(
                f"{page['icon']} {page['name']}",
                use_container_width=True,
                key=f"btn_{page['page']}",
            ):
                try:
                    st.switch_page(f"pages/{page['page']}")
                except Exception:
                    st.warning(f"Página {page['name']} ainda não criada.")

        st.markdown("---")

        # Métricas Rápidas (Seguras)
        st.markdown("### 📊 Status")
        try:
            # Importação Segura
            try:
                from dashboard.utils.supabase_client import get_supabase_client
            except ImportError:
                from utils.supabase_client import get_supabase_client

            supabase = get_supabase_client()
            if supabase:
                # Tenta buscar dados, se falhar mostra zeros (não quebra o app)
                try:
                    res = (
                        supabase.table("products")
                        .select("count", count="exact")
                        .eq("is_active", True)
                        .execute()
                    )
                    count = res.count
                except:
                    count = 0
                st.metric("📦 Produtos", count)
        except:
            st.caption("Banco desconectado")

        st.markdown("---")
        if st.button("🔄 Reload", use_container_width=True):
            st.rerun()
