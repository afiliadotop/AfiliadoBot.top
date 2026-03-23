import sys
import os

# Adiciona a raiz ao path se necessário
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))  # Raiz do projeto
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import padronizado
from dashboard.utils.supabase_client import get_supabase_client
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Configurar Telegram - AfiliadoHub", page_icon="🤖", layout="wide"
)

st.title("🤖 Configurações do Telegram")


@st.cache_resource
def init_supabase():
    return get_supabase_client()


supabase = init_supabase()

# Tabs
tab1, tab2, tab3 = st.tabs(["🔧 Configuração", "📊 Estatísticas", "📤 Envios Manuais"])

with tab1:
    st.subheader("Configuração do Bot")

    with st.form("telegram_config"):
        bot_token = st.text_input("Token do Bot", type="password")
        group_chat_id = st.text_input("ID do Grupo/Canal")

        # Configurações de envio
        st.subheader("Configurações de Envio")
        col1, col2 = st.columns(2)

        with col1:
            send_interval = st.selectbox(
                "Intervalo de Envio",
                [
                    "5 minutos",
                    "15 minutos",
                    "30 minutos",
                    "1 hora",
                    "2 horas",
                    "6 horas",
                    "12 horas",
                    "1 dia",
                ],
            )

            max_daily_messages = st.number_input(
                "Máximo de Mensagens Diárias", min_value=1, max_value=100, value=20
            )

        with col2:
            min_discount = st.number_input(
                "Desconto Mínimo para Envio (%)", min_value=0, max_value=100, value=20
            )

            avoid_repeats_days = st.number_input(
                "Evitar Repetir Produtos (dias)", min_value=1, max_value=30, value=7
            )

        # Mensagens padrão
        st.subheader("Modelos de Mensagem")
        default_message = st.text_area(
            "Mensagem Padrão",
            value="🔥 NOVA PROMOÇÃO!\n\n{produto}\n\n💰 Preço: R$ {preco}\n🎫 Desconto: {desconto}%\n\n🔗 {link}\n\n🏪 {loja}",
            height=150,
        )

        # Botões
        col1, col2 = st.columns(2)
        with col1:
            test_connection = st.form_submit_button("🔗 Testar Conexão")
        with col2:
            save_config = st.form_submit_button(
                "💾 Salvar Configurações", type="primary"
            )

        if test_connection:
            if bot_token:
                import requests

                try:
                    response = requests.get(
                        f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10
                    )
                    if response.json().get("ok"):
                        st.success("✅ Bot conectado com sucesso!")
                    else:
                        st.error("❌ Token inválido")
                except Exception as e:
                    st.error(f"❌ Erro de conexão: {e}")
            else:
                st.warning("⚠️ Digite o token do bot")

        if save_config:
            # Salva configurações
            config_data = {
                "bot_token": bot_token,
                "group_chat_id": group_chat_id,
                "send_interval": send_interval,
                "max_daily_messages": max_daily_messages,
                "min_discount": min_discount,
                "avoid_repeats_days": avoid_repeats_days,
                "default_message": default_message,
                "updated_at": datetime.now().isoformat(),
            }

            try:
                supabase.table("settings").upsert(
                    {"key": "telegram_config", "value": config_data}, on_conflict="key"
                ).execute()
                st.success("✅ Configurações salvas!")
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

with tab2:
    st.subheader("Estatísticas do Bot")

    try:
        # Busca estatísticas
        response = (
            supabase.table("product_stats")
            .select("telegram_send_count, last_sent")
            .not_.is_("last_sent", "null")
            .order("last_sent", desc=True)
            .limit(100)
            .execute()
        )

        stats_data = response.data if response.data else []

        if stats_data:
            # Total de envios
            total_sends = sum(item["telegram_send_count"] for item in stats_data)

            # Envios por dia (últimos 7 dias)
            week_ago = datetime.now() - timedelta(days=7)
            recent_sends = [
                item
                for item in stats_data
                if datetime.fromisoformat(item["last_sent"].replace("Z", "+00:00"))
                > week_ago
            ]

            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Envios", total_sends)
            with col2:
                st.metric("Envios (7 dias)", len(recent_sends))
            with col3:
                avg_per_day = len(recent_sends) / 7
                st.metric("Média Diária", f"{avg_per_day:.1f}")
            with col4:
                today = datetime.now().date()
                sends_today = len(
                    [
                        item
                        for item in stats_data
                        if datetime.fromisoformat(
                            item["last_sent"].replace("Z", "+00:00")
                        ).date()
                        == today
                    ]
                )
                st.metric("Envios Hoje", sends_today)

            # Gráfico de envios
            st.subheader("📈 Histórico de Envios")

            # Agrupa por data
            if stats_data:
                df = pd.DataFrame(stats_data)
                df["last_sent"] = pd.to_datetime(df["last_sent"])
                df["date"] = df["last_sent"].dt.date

                daily_sends = df.groupby("date").size().reset_index(name="envios")

                st.line_chart(daily_sends.set_index("date"))

            # Produtos mais enviados
            st.subheader("🏆 Produtos Mais Enviados")

            # Busca produtos com estatísticas
            products_response = (
                supabase.table("products")
                .select("id, name, store, current_price")
                .in_(
                    "id",
                    [s["product_id"] for s in stats_data[:10] if "product_id" in s],
                )
                .execute()
            )

            if products_response.data:
                products_df = pd.DataFrame(products_response.data)
                stats_df = pd.DataFrame(stats_data[:10])

                merged_df = pd.merge(
                    stats_df, products_df, left_on="product_id", right_on="id"
                )
                st.dataframe(
                    merged_df[
                        [
                            "name",
                            "store",
                            "current_price",
                            "telegram_send_count",
                            "last_sent",
                        ]
                    ],
                    use_container_width=True,
                )

        else:
            st.info("🤖 Nenhuma estatística disponível ainda.")

    except Exception as e:
        st.error(f"Erro ao buscar estatísticas: {e}")

with tab3:
    st.subheader("Envio Manual")

    # Formulário de envio manual
    with st.form("manual_send"):
        col1, col2 = st.columns(2)

        with col1:
            product_source = st.radio(
                "Fonte do Produto", ["Aleatório", "Por Loja", "Por ID", "Por Categoria"]
            )

            if product_source == "Por Loja":
                store = st.selectbox(
                    "Selecione a loja",
                    [
                        "shopee",
                        "aliexpress",
                        "amazon",
                        "temu",
                        "shein",
                        "magalu",
                        "mercado_livre",
                    ],
                )
            elif product_source == "Por ID":
                product_id = st.number_input("ID do Produto", min_value=1)
            elif product_source == "Por Categoria":
                category = st.text_input("Categoria")

        with col2:
            message_type = st.selectbox(
                "Tipo de Mensagem",
                ["Padrão", "Promocional", "Urgente", "Personalizada"],
            )

            if message_type == "Personalizada":
                custom_message = st.text_area("Mensagem Personalizada", height=100)

        # Preview
        st.subheader("👁️ Visualização")

        # Exemplo de preview
        st.info("""
        🔥 NOVA PROMOÇÃO!
        
        Smartphone XYZ 128GB
        
        💰 Preço: R$ 999,90
        🎫 Desconto: 25% OFF
        ⭐ 4.5/5 (1.234 avaliações)
        
        🔗 https://shope.ee/abc123
        
        🏪 Shopee | ⏰ Válido por 3 dias
        """)

        # Botões
        col1, col2, col3 = st.columns(3)
        with col1:
            preview = st.form_submit_button("👁️ Atualizar Preview")
        with col2:
            test_send = st.form_submit_button("📱 Enviar Teste")
        with col3:
            send_now = st.form_submit_button("🚀 Enviar Agora", type="primary")
