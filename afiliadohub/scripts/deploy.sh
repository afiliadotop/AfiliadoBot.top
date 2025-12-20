#!/bin/bash

# 🚀 Script de deploy completo para AfiliadoHub
# Autor: Sistema AfiliadoHub
# Versão: 1.0.0

set -e  # Para em erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    commands=("python3" "pip3" "git" "curl" "jq")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd não encontrado. Instale antes de continuar."
            exit 1
        fi
    done
    
    log_success "Dependências verificadas"
}

# Configura ambiente
setup_environment() {
    log_info "Configurando ambiente..."
    
    # Cria arquivo de ambiente se não existir
    if [ ! -f ".env.production" ]; then
        log_warning "Arquivo .env.production não encontrado"
        
        if [ -f ".env.example" ]; then
            cp .env.example .env.production
            log_info "Arquivo .env.production criado a partir do exemplo"
            log_warning "Edite o arquivo .env.production com suas configurações"
            exit 1
        else
            log_error "Arquivo .env.example não encontrado"
            exit 1
        fi
    fi
    
    # Carrega variáveis do .env.production
    set -a
    source .env.production
    set +a
    
    log_success "Ambiente configurado"
}

# Configura Supabase
setup_supabase() {
    log_info "Configurando Supabase..."
    
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
        log_error "Variáveis SUPABASE_URL e SUPABASE_KEY não configuradas"
        exit 1
    fi
    
    # Testa conexão com Supabase
    log_info "Testando conexão com Supabase..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "apikey: $SUPABASE_KEY" \
        -H "Authorization: Bearer $SUPABASE_KEY" \
        "$SUPABASE_URL/rest/v1/products?limit=1")
    
    if [ "$response" = "200" ]; then
        log_success "Conexão com Supabase estabelecida"
    else
        log_warning "Não foi possível conectar ao Supabase (HTTP $response)"
        log_info "Certifique-se de que:"
        log_info "1. O projeto Supabase está ativo"
        log_info "2. A tabela 'products' existe"
        log_info "3. As permissões estão configuradas corretamente"
        
        read -p "Deseja continuar mesmo assim? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    fi
}

# Configura Telegram
setup_telegram() {
    log_info "Configurando Telegram Bot..."
    
    if [ -z "$BOT_TOKEN" ]; then
        log_error "BOT_TOKEN não configurado"
        exit 1
    fi
    
    # Testa o token do bot
    log_info "Validando token do Telegram..."
    
    response=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe")
    
    if echo "$response" | grep -q '"ok":true'; then
        bot_name=$(echo "$response" | jq -r '.result.first_name')
        log_success "Bot Telegram validado: $bot_name"
    else
        log_error "Token do Telegram inválido"
        exit 1
    fi
}

# Deploy na Vercel
deploy_vercel() {
    log_info "Iniciando deploy na Vercel..."
    
    # Verifica se Vercel CLI está instalado
    if ! command -v vercel &> /dev/null; then
        log_warning "Vercel CLI não encontrado"
        log_info "Instalando Vercel CLI..."
        npm install -g vercel
    fi
    
    # Faz deploy
    log_info "Executando deploy..."
    
    if [ "$1" = "--prod" ]; then
        vercel --prod --yes --env-file=.env.production
    else
        vercel --yes --env-file=.env.production
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Deploy na Vercel concluído"
    else
        log_error "Erro no deploy da Vercel"
        exit 1
    fi
}

# Configura webhook do Telegram
setup_webhook() {
    log_info "Configurando webhook do Telegram..."
    
    # Obtém URL do deploy mais recente
    DEPLOY_URL=$(vercel ls --json | jq -r '.projects[0].latestDeployment.url' 2>/dev/null || echo "")
    
    if [ -z "$DEPLOY_URL" ]; then
        log_warning "Não foi possível obter URL do deploy"
        log_info "Configure manualmente:"
        log_info "curl -F \"url=https://SEU_PROJETO.vercel.app/api/telegram/webhook\" https://api.telegram.org/bot\${BOT_TOKEN}/setWebhook"
        return 1
    fi
    
    WEBHOOK_URL="https://${DEPLOY_URL}/api/telegram/webhook"
    
    log_info "Configurando webhook para: $WEBHOOK_URL"
    
    response=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}")
    
    if echo "$response" | grep -q '"ok":true'; then
        log_success "Webhook configurado com sucesso"
        
        # Verifica informações do webhook
        curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | jq .
    else
        log_error "Erro ao configurar webhook"
        echo "$response" | jq .
        return 1
    fi
}

# Configura GitHub Secrets (interativo)
setup_github_secrets() {
    log_info "Configuração de GitHub Secrets"
    log_info "-----------------------------"
    
    echo
    log_info "No GitHub, vá até:"
    log_info "Seu Repositório → Settings → Secrets and variables → Actions"
    echo
    log_info "Adicione os seguintes secrets:"
    echo
    
    # Gera valores sugeridos
    CRON_TOKEN=$(openssl rand -hex 32 2>/dev/null || echo "altere-este-token-por-um-seguro")
    
    cat <<EOF
🔐 BOT_TOKEN = $BOT_TOKEN
🔐 SUPABASE_URL = $SUPABASE_URL
🔐 SUPABASE_KEY = $SUPABASE_KEY
🔐 SUPABASE_SERVICE_KEY = ${SUPABASE_SERVICE_KEY:-"sua-service-key"}
🔐 CRON_TOKEN = $CRON_TOKEN
🔐 ADMIN_API_KEY = $(openssl rand -hex 32 2>/dev/null || echo "admin-token-seguro")
🌐 VERCEL_URL = https://$(vercel ls --json | jq -r '.projects[0].latestDeployment.url' 2>/dev/null || echo "seu-projeto.vercel.app")
🛍️ SHOPEE_CSV_URL = ${SHOPEE_CSV_URL:-"https://exemplo.com/produtos.csv"}
EOF
    
    echo
    read -p "Pressione Enter quando tiver configurado os secrets..."
}

# Executa testes
run_tests() {
    log_info "Executando testes básicos..."
    
    # Testa API
    DEPLOY_URL=$(vercel ls --json | jq -r '.projects[0].latestDeployment.url' 2>/dev/null || echo "")
    
    if [ -n "$DEPLOY_URL" ]; then
        log_info "Testando endpoint de saúde..."
        curl -s "https://${DEPLOY_URL}/health" | jq .
        
        log_info "Testando listagem de produtos..."
        curl -s "https://${DEPLOY_URL}/api/products?limit=1" | jq .
    fi
    
    log_success "Testes concluídos"
}

# Menu principal
show_menu() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════╗"
    echo "║      🚀 AFILIADOHUB DEPLOY           ║"
    echo "╠══════════════════════════════════════╣"
    echo "║ 1. Deploy Completo (Recomendado)     ║"
    echo "║ 2. Apenas Configurar Ambiente        ║"
    echo "║ 3. Apenas Deploy na Vercel           ║"
    echo "║ 4. Configurar Webhook Telegram       ║"
    echo "║ 5. Configurar GitHub Secrets         ║"
    echo "║ 6. Executar Testes                   ║"
    echo "║ 7. Sair                              ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
    
    read -p "Selecione uma opção [1-7]: " choice
    echo
    
    case $choice in
        1)
            check_dependencies
            setup_environment
            setup_supabase
            setup_telegram
            deploy_vercel --prod
            setup_webhook
            setup_github_secrets
            run_tests
            show_summary
            ;;
        2)
            check_dependencies
            setup_environment
            setup_supabase
            setup_telegram
            ;;
        3)
            deploy_vercel --prod
            ;;
        4)
            setup_webhook
            ;;
        5)
            setup_github_secrets
            ;;
        6)
            run_tests
            ;;
        7)
            log_info "Saindo..."
            exit 0
            ;;
        *)
            log_error "Opção inválida"
            show_menu
            ;;
    esac
}

# Mostra resumo
show_summary() {
    echo
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                      🎉 DEPLOY CONCLUÍDO!                           ${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════${NC}"
    echo
    
    DEPLOY_URL=$(vercel ls --json | jq -r '.projects[0].latestDeployment.url' 2>/dev/null || echo "N/A")
    
    cat <<EOF
📋 RESUMO DA INSTALAÇÃO:

🌐 URL do Projeto: https://${DEPLOY_URL}
📊 Painel Admin: https://${DEPLOY_URL}/docs
🩺 Health Check: https://${DEPLOY_URL}/health

🤖 Bot Telegram:
   - Comandos: /start, /cupom, /promo, /buscar, etc.
   - Webhook: Configurado automaticamente

🗄️ Banco de Dados:
   - Supabase: Conectado
   - Tabelas: products, product_stats, product_logs
   - Backup: Automático diário

⚡ Automações (GitHub Actions):
   - Envio de promoções: A cada 5 minutos
   - Atualização de preços: A cada hora
   - Importação Shopee: Diária às 2h
   - Backup: Diário às 4h
   - Limpeza: Diária às 3h

🔧 Próximos Passos:
   1. Adicione produtos via:
      - CSV: ${DEPLOY_URL}/docs#/default/import_csv_api_import_csv_post
      - API: ${DEPLOY_URL}/docs#/default/create_product_api_products_post
      - Manual: Painel admin
    
   2. Configure o grupo do Telegram:
      - Adicione o bot ao grupo
      - Torne-o administrador
      - Configure GROUP_CHAT_ID no .env.production
    
   3. Teste os comandos:
      - No bot: /cupom, /shopee, /buscar celular
      - Na API: ${DEPLOY_URL}/api/products

❓ Suporte:
   - Logs: vercel logs ${DEPLOY_URL#https://}
   - Issues: GitHub do projeto
   - Monitoramento: Painel Vercel

💡 Dica: Use o script de importação para carregar seus CSVs:
   ./scripts/import_csv.sh seus_produtos.csv shopee
EOF
    
    echo
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════════${NC}"
    echo
}

# Ponto de entrada principal
main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
    ╔══════════════════════════════════════════════════════╗
    ║                🚀 AFILIADOHUB 1.0                    ║
    ║       Plataforma Completa de Afiliados              ║
    ║                                                      ║
    ║  📦 Shopee | 📚 Amazon | 📦 AliExpress              ║
    ║  🎯 Temu   | 👗 Shein  | 🏬 Magalu                  ║
    ║  🚀 Mercado Livre                                   ║
    ║                                                      ║
    ║  Gerencie milhões de produtos com performance!      ║
    ╚══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    show_menu
}

# Executa script
main "$@"
