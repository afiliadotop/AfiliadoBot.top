#!/bin/bash

# 🚀 Script de deploy do Painel Streamlit para o Streamlit Cloud

echo "🚀 Preparando deploy do Painel AfiliadoHub..."

# Verifica se está no diretório correto
if [ ! -f "dashboard/main.py" ]; then
    echo "❌ Diretório do dashboard não encontrado."
    echo "Execute este script da raiz do projeto."
    exit 1
fi

# Verifica dependências
echo "📦 Verificando dependências..."
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado."
    exit 1
fi

# Cria requirements.txt para Streamlit
echo "📝 Criando requirements.txt específico..."
cat > dashboard/requirements.txt << 'EOF'
# Core
streamlit==1.28.0
pandas==2.1.3
numpy==1.24.3

# Supabase
supabase==1.0.3
python-dotenv==1.0.0

# Data Visualization
plotly==5.17.0
matplotlib==3.7.2

# Data Processing
openpyxl==3.1.2
xlrd==2.0.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Requests
requests==2.31.0
aiohttp==3.9.1

# Optional (para web scraping)
beautifulsoup4==4.12.2
selenium==4.15.0
EOF

echo "✅ requirements.txt criado"

# Cria secrets.toml exemplo
echo "🔐 Criando secrets.toml de exemplo..."
cat > dashboard/.streamlit/secrets.toml.example << 'EOF'
# Secrets para o AfiliadoHub Dashboard
# Renomeie para secrets.toml e preencha com seus dados

# Supabase
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua-chave-anon"

# Telegram (opcional)
BOT_TOKEN = "123456:ABC-DEF"

# Configurações
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "senha-segura"

# URLs da API
API_URL = "https://seu-projeto.vercel.app"
CRON_TOKEN = "seu-token-cron"
EOF

echo "✅ secrets.toml.example criado"

# Cria .streamlit/config.toml
echo "⚙️  Criando config.toml..."
mkdir -p dashboard/.streamlit

cat > dashboard/.streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#1E3A8A"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"
EOF

echo "✅ config.toml criado"

# Testa o dashboard localmente
echo "🧪 Testando o dashboard localmente..."
cd dashboard

# Cria virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Criando virtual environment..."
    python -m venv venv
fi

# Ativa virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "🎉 Preparação concluída!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. Configure os secrets:"
echo "   cd dashboard/.streamlit"
echo "   cp secrets.toml.example secrets.toml"
echo "   nano secrets.toml  # Edite com suas credenciais"
echo ""
echo "2. Teste localmente:"
echo "   streamlit run main.py"
echo ""
echo "3. Para deploy no Streamlit Cloud:"
echo "   a. Crie conta em https://streamlit.io/cloud"
echo "   b. Conecte seu repositório GitHub"
echo "   c. Configure o diretório como 'dashboard'"
echo "   d. Adicione os secrets no painel do Streamlit Cloud"
echo ""
echo "4. Secrets necessários no Streamlit Cloud:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_KEY"
echo "   - (Opcional) Outras variáveis do secrets.toml"
echo ""
echo "🌐 URL do dashboard após deploy:"
echo "   https://seuusuario-afiliadohub-dashboard.streamlit.app"
echo ""
echo "📚 Documentação:"
echo "   - Streamlit Cloud: https://docs.streamlit.io/streamlit-cloud"
echo "   - Dashboard: https://seu-projeto.vercel.app/docs"
echo ""

# Pergunta se quer testar agora
read -p "Deseja testar o dashboard localmente agora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando dashboard local..."
    streamlit run main.py
fi
