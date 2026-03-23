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
import io
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="Importar Dados - AfiliadoHub", page_icon="🔄", layout="wide"
)

st.title("🔄 Importar Dados")


# Inicializa Supabase
@st.cache_resource
def init_supabase():
    return get_supabase_client()


supabase = init_supabase()

# Tabs
tab1, tab2, tab3 = st.tabs(
    ["📤 Upload CSV", "🔗 Importar da Shopee", "⚙️ Configurações de Importação"]
)

with tab1:
    st.subheader("Importar Arquivo CSV")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV",
            type=["csv"],
            help="Arquivo CSV com colunas: name, link, price, etc.",
        )

    with col2:
        store = st.selectbox(
            "Loja",
            [
                "shopee",
                "aliexpress",
                "amazon",
                "temu",
                "shein",
                "magalu",
                "mercado_livre",
            ],
            index=0,
        )

        replace_existing = st.checkbox("Substituir existentes", value=False)

    if uploaded_file is not None:
        # Pré-visualização
        try:
            df = pd.read_csv(uploaded_file)

            st.success(
                f"✅ Arquivo carregado: {len(df)} linhas, {len(df.columns)} colunas"
            )

            # Mostra preview
            st.subheader("📋 Pré-visualização")
            st.dataframe(df.head(10), use_container_width=True)

            # Mapeamento de colunas
            st.subheader("🗺️ Mapeamento de Colunas")

            col1, col2, col3 = st.columns(3)

            with col1:
                name_col = st.selectbox(
                    "Coluna do Nome",
                    df.columns.tolist(),
                    index=df.columns.get_loc("name") if "name" in df.columns else 0,
                )
                price_col = st.selectbox(
                    "Coluna do Preço",
                    df.columns.tolist(),
                    index=df.columns.get_loc("price") if "price" in df.columns else 0,
                )

            with col2:
                link_col = st.selectbox(
                    "Coluna do Link",
                    df.columns.tolist(),
                    index=df.columns.get_loc("link") if "link" in df.columns else 0,
                )
                category_col = st.selectbox(
                    "Coluna da Categoria", [""] + df.columns.tolist()
                )

            with col3:
                image_col = st.selectbox("Coluna da Imagem", [""] + df.columns.tolist())
                coupon_col = st.selectbox("Coluna do Cupom", [""] + df.columns.tolist())

            # Botão de importação
            if st.button("🚀 Iniciar Importação", type="primary"):
                with st.spinner("Processando importação..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Processa em lotes
                        batch_size = 100
                        total_batches = (len(df) // batch_size) + 1
                        imported_count = 0
                        error_count = 0

                        for i in range(0, len(df), batch_size):
                            batch = df.iloc[i : i + batch_size]

                            # Converte batch para formato do banco
                            products = []
                            for _, row in batch.iterrows():
                                try:
                                    product = {
                                        "store": store,
                                        "name": str(row.get(name_col, ""))[:500],
                                        "affiliate_link": str(row.get(link_col, "")),
                                        "current_price": (
                                            float(row.get(price_col, 0))
                                            if pd.notnull(row.get(price_col, 0))
                                            else 0.0
                                        ),
                                        "category": (
                                            str(row.get(category_col, ""))
                                            if category_col
                                            and pd.notnull(row.get(category_col, ""))
                                            else None
                                        ),
                                        "image_url": (
                                            str(row.get(image_col, ""))
                                            if image_col
                                            and pd.notnull(row.get(image_col, ""))
                                            else None
                                        ),
                                        "coupon_code": (
                                            str(row.get(coupon_col, ""))
                                            if coupon_col
                                            and pd.notnull(row.get(coupon_col, ""))
                                            else None
                                        ),
                                        "source": "csv_import",
                                        "source_file": uploaded_file.name,
                                        "is_active": True,
                                    }

                                    # Validação básica
                                    if (
                                        product["name"]
                                        and product["affiliate_link"]
                                        and product["current_price"] > 0
                                    ):
                                        products.append(product)
                                        imported_count += 1
                                    else:
                                        error_count += 1

                                except Exception as e:
                                    error_count += 1

                            # Insere batch no Supabase
                            if products:
                                supabase.table("products").upsert(
                                    products, on_conflict="affiliate_link"
                                ).execute()

                            # Atualiza progresso
                            progress = min((i + batch_size) / len(df), 1.0)
                            progress_bar.progress(progress)
                            status_text.text(
                                f"Processados: {min(i + batch_size, len(df))}/{len(df)} | Importados: {imported_count} | Erros: {error_count}"
                            )

                        # Resultado final
                        progress_bar.empty()
                        status_text.empty()

                        st.success(f"""
                        ✅ Importação concluída!
                        
                        📊 **Resultados:**
                        - Total processado: {len(df):,}
                        - Produtos importados: {imported_count:,}
                        - Erros: {error_count:,}
                        - Loja: {store}
                        """)

                        # Log da importação
                        log_data = {
                            "timestamp": datetime.now().isoformat(),
                            "file": uploaded_file.name,
                            "store": store,
                            "total_rows": len(df),
                            "imported": imported_count,
                            "errors": error_count,
                        }

                        # Salva log
                        supabase.table("import_logs").insert(log_data).execute()

                    except Exception as e:
                        st.error(f"❌ Erro durante importação: {str(e)}")

        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo CSV: {str(e)}")

with tab2:
    st.subheader("Importação Automática da Shopee")

    st.info("""
    🔗 **Importe automaticamente da Shopee usando:**
    1. API Oficial (requer credenciais)
    2. Web scraping (automático)
    3. CSV diário (link fixo)
    """)

    import_method = st.radio(
        "Método de importação:", ["CSV Diário", "API Shopee", "Web Scraping"]
    )

    if import_method == "CSV Diário":
        csv_url = st.text_input(
            "URL do CSV diário:",
            value="https://exemplo.com/produtos_shopee.csv",
            help="Link para o CSV atualizado diariamente",
        )

        schedule = st.selectbox(
            "Agendar importação:",
            ["Apenas uma vez", "Diariamente", "Semanalmente", "Mensalmente"],
        )

        if st.button("📥 Importar Agora", type="primary"):
            with st.spinner("Importando da Shopee..."):
                try:
                    # Simulação de importação
                    time.sleep(2)

                    # Aqui você implementaria a lógica real
                    # df = pd.read_csv(csv_url)
                    # Processar e salvar...

                    st.success("✅ Importação da Shopee agendada!")
                    st.info("Os produtos serão processados em background.")

                except Exception as e:
                    st.error(f"Erro: {e}")

    elif import_method == "API Shopee":
        st.warning("🔐 Esta funcionalidade requer credenciais da API da Shopee")

        col1, col2 = st.columns(2)

        with col1:
            api_key = st.text_input("API Key", type="password")
            partner_id = st.text_input("Partner ID")

        with col2:
            shop_id = st.text_input("Shop ID")
            limit = st.number_input(
                "Limite de produtos", min_value=1, max_value=1000, value=100
            )

        if st.button("🔗 Conectar à API", type="primary"):
            if api_key and partner_id:
                with st.spinner("Conectando à API Shopee..."):
                    try:
                        # Aqui você implementaria a conexão real
                        time.sleep(2)
                        st.success("✅ Conectado com sucesso!")
                        st.info(f"Pronto para importar até {limit} produtos")
                    except:
                        st.error("❌ Falha na conexão. Verifique as credenciais.")
            else:
                st.warning("⚠️ Preencha todas as credenciais")

    else:  # Web Scraping
        st.warning("⚠️ Web scraping pode violar termos de serviço. Use com cuidado.")

        search_query = st.text_input("Termo de busca:", value="smartphone")
        max_pages = st.slider("Número de páginas:", 1, 10, 3)

        if st.button("🕷️ Iniciar Scraping", type="primary"):
            with st.spinner(f"Buscando '{search_query}' na Shopee..."):
                try:
                    # Simulação
                    progress_bar = st.progress(0)

                    for i in range(max_pages):
                        time.sleep(0.5)
                        progress_bar.progress((i + 1) / max_pages)

                    progress_bar.empty()

                    # Resultados simulados
                    sample_data = [
                        {
                            "produto": "Smartphone XYZ",
                            "preco": 999.90,
                            "desconto": "15%",
                        },
                        {
                            "produto": "Fone Bluetooth",
                            "preco": 89.90,
                            "desconto": "30%",
                        },
                        {
                            "produto": "Capa para Celular",
                            "preco": 29.90,
                            "desconto": "10%",
                        },
                    ]

                    st.success(
                        f"✅ Encontrados {len(sample_data) * max_pages} produtos!"
                    )
                    st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

                except Exception as e:
                    st.error(f"Erro: {e}")

with tab3:
    st.subheader("Configurações de Importação")

    # Configurações gerais
    with st.expander("⚙️ Configurações Gerais", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            max_file_size = st.number_input(
                "Tamanho máximo de arquivo (MB):", min_value=1, max_value=500, value=100
            )

            default_store = st.selectbox(
                "Loja padrão:",
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

        with col2:
            auto_approve = st.checkbox("Aprovar produtos automaticamente", value=True)
            deduplicate = st.checkbox("Remover duplicados automaticamente", value=True)
            validate_links = st.checkbox("Validar links antes de importar", value=True)

    # Configurações de processamento
    with st.expander("🔄 Processamento em Lote"):
        batch_size = st.slider("Tamanho do lote:", 10, 1000, 100, 10)
        delay_between_batches = st.slider("Delay entre lotes (segundos):", 0, 10, 1)

        st.info(
            f"⚡ Processamento: {batch_size} produtos por lote com {delay_between_batches} segundos de intervalo"
        )

    # Configurações de mapeamento
    with st.expander("🗺️ Mapeamento de Campos"):
        st.write("Defina o mapeamento padrão para colunas CSV:")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.text_input("Nome →", value="name", disabled=True)
            st.text_input("Preço →", value="price", disabled=True)

        with col2:
            st.text_input("Link →", value="link", disabled=True)
            st.text_input("Categoria →", value="category", disabled=True)

        with col3:
            st.text_input("Imagem →", value="image", disabled=True)
            st.text_input("Cupom →", value="coupon", disabled=True)

    # Configurações de notificação
    with st.expander("🔔 Notificações"):
        email_notifications = st.checkbox("Enviar email após importação", value=True)
        telegram_notifications = st.checkbox("Notificar no Telegram", value=True)

        if email_notifications:
            email_address = st.text_input(
                "Email para notificações:", value="seu@email.com"
            )

        if telegram_notifications:
            chat_id = st.text_input("Chat ID do Telegram:", value="-1001234567890")

    # Botão para salvar configurações
    if st.button("💾 Salvar Configurações", type="primary"):
        settings = {
            "max_file_size_mb": max_file_size,
            "default_store": default_store,
            "auto_approve": auto_approve,
            "deduplicate": deduplicate,
            "validate_links": validate_links,
            "batch_size": batch_size,
            "delay_between_batches": delay_between_batches,
            "notifications": {
                "email": email_notifications,
                "telegram": telegram_notifications,
                "email_address": email_address if email_notifications else None,
                "telegram_chat_id": chat_id if telegram_notifications else None,
            },
        }

        try:
            # Salva no Supabase
            supabase.table("settings").upsert(
                {
                    "key": "import_settings",
                    "value": settings,
                    "updated_at": datetime.now().isoformat(),
                },
                on_conflict="key",
            ).execute()

            st.success("✅ Configurações salvas com sucesso!")

        except Exception as e:
            st.error(f"❌ Erro ao salvar configurações: {e}")

# Footer
st.markdown("---")
st.caption("🔄 Sistema de Importação - AfiliadoHub v1.0")
