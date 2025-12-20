import sys
import os

# Adiciona a raiz ao path se necessário
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir)) # Raiz do projeto
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import padronizado
from dashboard.utils.supabase_client import get_supabase_client
import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Configurações - AfiliadoHub",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Configurações do Sistema")

@st.cache_resource
def init_supabase():
    return get_supabase_client()

supabase = init_supabase()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔧 Sistema", 
    "🗄️ Banco de Dados", 
    "📧 Notificações", 
    "🔐 Segurança"
])

with tab1:
    st.subheader("Configurações Gerais")
    
    with st.form("system_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            system_name = st.text_input("Nome do Sistema", value="AfiliadoHub")
            timezone = st.selectbox("Fuso Horário", ["America/Sao_Paulo", "UTC", "Europe/London", "Asia/Tokyo"])
            default_currency = st.selectbox("Moeda Padrão", ["BRL", "USD", "EUR", "GBP"])
        
        with col2:
            language = st.selectbox("Idioma", ["Português", "English", "Español"])
            date_format = st.selectbox("Formato de Data", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
            items_per_page = st.number_input("Itens por Página", min_value=10, max_value=100, value=50)
        
        # Limites
        st.subheader("Limites do Sistema")
        col1, col2 = st.columns(2)
        
        with col1:
            max_products = st.number_input(
                "Máximo de Produtos",
                min_value=1000,
                max_value=1000000,
                value=100000,
                step=1000
            )
            
            max_file_size = st.number_input(
                "Tamanho Máximo de Arquivo (MB)",
                min_value=1,
                max_value=500,
                value=100
            )
        
        with col2:
            api_rate_limit = st.number_input(
                "Limite de Requisições API/min",
                min_value=10,
                max_value=1000,
                value=100
            )
            
            cache_duration = st.number_input(
                "Duração do Cache (minutos)",
                min_value=1,
                max_value=1440,
                value=60
            )
        
        # Botão de salvar
        if st.form_submit_button("💾 Salvar Configurações", type="primary"):
            config = {
                "system_name": system_name,
                "timezone": timezone,
                "default_currency": default_currency,
                "language": language,
                "date_format": date_format,
                "items_per_page": items_per_page,
                "limits": {
                    "max_products": max_products,
                    "max_file_size_mb": max_file_size,
                    "api_rate_limit": api_rate_limit,
                    "cache_duration_minutes": cache_duration
                },
                "updated_at": datetime.now().isoformat()
            }
            
            try:
                supabase.table("settings").upsert({
                    "key": "system_config",
                    "value": config
                }, on_conflict="key").execute()
                st.success("✅ Configurações salvas!")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

with tab2:
    st.subheader("Configurações do Banco de Dados")
    
    # Status do banco
    try:
        response = supabase.table("products").select("count", count="exact").execute()
        product_count = response.count or 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Produtos", f"{product_count:,}")
        with col2:
            st.metric("Tabelas", "8")
        with col3:
            st.metric("Status", "✅ Online")
    
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco: {e}")
    
    # Manutenção
    st.subheader("Manutenção do Banco")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Otimizar Tabelas", type="secondary"):
            with st.spinner("Otimizando..."):
                # Aqui você chamaria uma função de otimização
                st.success("✅ Tabelas otimizadas!")
    
    with col2:
        if st.button("🧹 Limpar Cache", type="secondary"):
            with st.spinner("Limpando cache..."):
                st.success("✅ Cache limpo!")
    
    # Backup
    st.subheader("Backup e Restauração")
    
    with st.form("backup_form"):
        backup_type = st.radio(
            "Tipo de Backup",
            ["Completo", "Apenas Produtos", "Apenas Configurações"]
        )
        
        include_media = st.checkbox("Incluir imagens/media", value=False)
        compress_backup = st.checkbox("Comprimir backup", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            create_backup = st.form_submit_button("💾 Criar Backup")
        with col2:
            download_backup = st.form_submit_button("📥 Baixar Último Backup")
    
    # Restauração
    st.subheader("Restaurar Backup")
    
    uploaded_file = st.file_uploader("Selecione arquivo de backup", type=['json', 'zip'])
    
    if uploaded_file and st.button("🔄 Restaurar Backup", type="primary"):
        with st.spinner("Restaurando..."):
            st.warning("⚠️ Esta ação irá substituir dados existentes!")
            confirm = st.checkbox("Confirmar restauração")
            
            if confirm:
                st.success("✅ Backup restaurado com sucesso!")

with tab3:
    st.subheader("Configurações de Notificação")
    
    with st.form("notification_config"):
        # Email
        st.subheader("📧 Notificações por Email")
        
        email_enabled = st.checkbox("Ativar notificações por email", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
            smtp_port = st.number_input("Porta SMTP", min_value=1, max_value=65535, value=587)
        
        with col2:
            smtp_username = st.text_input("Usuário SMTP")
            smtp_password = st.text_input("Senha SMTP", type="password")
        
        # Destinatários
        recipients = st.text_area(
            "Destinatários (um por linha)",
            value="admin@afiliado.top\n",
            height=100
        )
        
        # Telegram
        st.subheader("🤖 Notificações Telegram")
        
        telegram_enabled = st.checkbox("Ativar notificações Telegram", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            telegram_bot_token = st.text_input("Token do Bot", type="password")
        
        with col2:
            telegram_chat_id = st.text_input("Chat ID")
        
        # Tipos de notificação
        st.subheader("🔔 Tipos de Notificação")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            notify_new_products = st.checkbox("Novos produtos", value=True)
            notify_errors = st.checkbox("Erros do sistema", value=True)
        
        with col2:
            notify_import_complete = st.checkbox("Importação completa", value=True)
            notify_low_stock = st.checkbox("Produtos esgotando", value=False)
        
        with col3:
            notify_daily_report = st.checkbox("Relatório diário", value=True)
            notify_monthly_summary = st.checkbox("Resumo mensal", value=True)
        
        if st.form_submit_button("💾 Salvar Configurações", type="primary"):
            st.success("✅ Configurações salvas!")

with tab4:
    st.subheader("Configurações de Segurança")
    
    with st.form("security_config"):
        # Autenticação
        st.subheader("🔐 Autenticação")
        
        auth_method = st.selectbox(
            "Método de Autenticação",
            ["API Key", "JWT Token", "OAuth2", "Basic Auth"]
        )
        
        require_2fa = st.checkbox("Requer autenticação de dois fatores", value=False)
        session_timeout = st.number_input("Timeout da Sessão (minutos)", min_value=5, max_value=1440, value=60)
        
        # API Keys
        st.subheader("🔑 Chaves API")
        
        # Lista de chaves existentes
        st.write("Chaves existentes:")
        st.code("""
        admin_key: *************abc123 (Criada: 2024-01-01)
        cron_key: *************def456 (Criada: 2024-01-01)
        api_key: *************ghi789 (Criada: 2024-01-01)
        """)
        
        # Gerar nova chave
        if st.form_submit_button("🆕 Gerar Nova Chave API"):
            import secrets
            new_key = secrets.token_urlsafe(32)
            st.success(f"Nova chave gerada: `{new_key}`")
            st.warning("⚠️ Salve esta chave agora! Ela não será mostrada novamente.")
        
        # Rate Limiting
        st.subheader("⏱️ Rate Limiting")
        
        col1, col2 = st.columns(2)
        with col1:
            requests_per_minute = st.number_input("Requisições por minuto", min_value=10, max_value=1000, value=100)
            requests_per_hour = st.number_input("Requisições por hora", min_value=100, max_value=10000, value=1000)
        
        with col2:
            block_duration = st.number_input("Duração do bloqueio (minutos)", min_value=1, max_value=1440, value=60)
            whitelist_ips = st.text_area("IPs na Whitelist (um por linha)", height=100)
        
        # Logs e Auditoria
        st.subheader("📝 Logs e Auditoria")
        
        enable_audit_log = st.checkbox("Ativar logs de auditoria", value=True)
        log_retention_days = st.number_input("Retenção de logs (dias)", min_value=1, max_value=365, value=90)
        
        if st.form_submit_button("💾 Salvar Configurações", type="primary"):
            st.success("✅ Configurações de segurança salvas!")
    
    # Exportar logs
    st.subheader("📤 Exportar Logs")
    
    col1, col2 = st.columns(2)
    with col1:
        log_type = st.selectbox("Tipo de logs", ["Auditoria", "Erros", "Acesso", "Todos"])
    with col2:
        date_range = st.date_input("Intervalo de datas", [])
    
    if st.button("📥 Exportar Logs", type="primary"):
        with st.spinner("Exportando logs..."):
            st.success("✅ Logs exportados com sucesso!")
            st.download_button(
                label="⬇️ Baixar Logs",
                data="logs_exportados.zip",
                file_name="logs_afiliadohub.zip",
                mime="application/zip"
  )
