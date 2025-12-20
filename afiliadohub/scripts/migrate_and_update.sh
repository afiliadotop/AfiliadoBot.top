#!/bin/bash

# 🚀 Script de migração e atualização do AfiliadoHub

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════╗
║            AFILIADOHUB - MIGRAÇÃO 2.0                ║
║            Sistema Completo de Afiliados             ║
╚══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verifica se está no diretório do projeto
if [ ! -f "api/index.py" ]; then
    echo -e "${RED}❌ Não está no diretório do projeto.${NC}"
    exit 1
fi

# Carrega variáveis de ambiente
if [ -f .env.production ]; then
    source .env.production
elif [ -f .env ]; then
    source .env
else
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    exit 1
fi

# Função para executar SQL no Supabase
execute_sql() {
    local sql_file="$1"
    local description="$2"
    
    echo -e "${BLUE}🔧 Executando: $description${NC}"
    
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
        echo -e "${RED}❌ Variáveis do Supabase não configuradas${NC}"
        return 1
    fi
    
    # Usa a API REST do Supabase para executar SQL
    curl -X POST "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
        -H "apikey: ${SUPABASE_SERVICE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"sql\": \"$(cat $sql_file | tr '\n' ' ' | sed 's/\"/\\\"/g')\"}" \
        --silent \
        --show-error
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $description concluído${NC}"
    else
        echo -e "${RED}❌ Erro em $description${NC}"
        return 1
    fi
}

# Menu principal
PS3="Selecione uma opção: "
options=(
    "Migração Completa 2.0"
    "Apenas Novas Tabelas"
    "Apenas Índices"
    "Apenas Dados Iniciais"
    "Backup de Dados"
    "Restaurar Backup"
    "Verificar Status"
    "Sair"
)

select opt in "${options[@]}"
do
    case $opt in
        "Migração Completa 2.0")
            echo -e "${YELLOW}🚀 Iniciando migração completa...${NC}"
            
            # 1. Cria novas tabelas
            execute_sql "sql/migration_v2_tables.sql" "Criação de novas tabelas"
            
            # 2. Cria índices de performance
            execute_sql "sql/migration_v2_indexes.sql" "Criação de índices"
            
            # 3. Insere dados iniciais
            execute_sql "sql/migration_v2_data.sql" "Inserção de dados iniciais"
            
            # 4. Atualiza estrutura existente
            execute_sql "sql/migration_v2_updates.sql" "Atualização de estrutura"
            
            echo -e "${GREEN}🎉 Migração 2.0 concluída com sucesso!${NC}"
            ;;
        
        "Apenas Novas Tabelas")
            echo -e "${YELLOW}📦 Criando apenas novas tabelas...${NC}"
            execute_sql "sql/migration_v2_tables.sql" "Criação de novas tabelas"
            ;;
        
        "Apenas Índices")
            echo -e "${YELLOW}⚡ Criando índices de performance...${NC}"
            execute_sql "sql/migration_v2_indexes.sql" "Criação de índices"
            ;;
        
        "Apenas Dados Iniciais")
            echo -e "${YELLOW}📊 Inserindo dados iniciais...${NC}"
            execute_sql "sql/migration_v2_data.sql" "Inserção de dados iniciais"
            ;;
        
        "Backup de Dados")
            echo -e "${YELLOW}💾 Fazendo backup dos dados...${NC}"
            
            TIMESTAMP=$(date +%Y%m%d_%H%M%S)
            BACKUP_DIR="backups/$TIMESTAMP"
            mkdir -p "$BACKUP_DIR"
            
            # Exporta cada tabela
            tables=("products" "product_stats" "commissions" "settings" "import_logs")
            
            for table in "${tables[@]}"; do
                echo -e "${BLUE}📋 Exportando $table...${NC}"
                
                curl -X GET "${SUPABASE_URL}/rest/v1/${table}?select=*" \
                    -H "apikey: ${SUPABASE_KEY}" \
                    -H "Authorization: Bearer ${SUPABASE_KEY}" \
                    --silent \
                    -o "${BACKUP_DIR}/${table}.json"
                
                # Converte para CSV também
                python3 -c "
import json, csv
with open('${BACKUP_DIR}/${table}.json') as f:
    data = json.load(f)
if data:
    with open('${BACKUP_DIR}/${table}.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
"
                
                echo -e "${GREEN}✅ $table exportado${NC}"
            done
            
            # Compacta backup
            tar -czf "${BACKUP_DIR}.tar.gz" -C "$BACKUP_DIR" .
            
            echo -e "${GREEN}🎉 Backup concluído: ${BACKUP_DIR}.tar.gz${NC}"
            ;;
        
        "Restaurar Backup")
            echo -e "${YELLOW}🔄 Restaurando backup...${NC}"
            
            read -p "Caminho do arquivo backup.tar.gz: " backup_file
            
            if [ ! -f "$backup_file" ]; then
                echo -e "${RED}❌ Arquivo não encontrado${NC}"
                break
            fi
            
            # Extrai backup
            BACKUP_DIR="backups/restore_$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$BACKUP_DIR"
            tar -xzf "$backup_file" -C "$BACKUP_DIR"
            
            # Restaura cada tabela
            for json_file in "$BACKUP_DIR"/*.json; do
                table=$(basename "$json_file" .json)
                
                echo -e "${BLUE}📋 Restaurando $table...${NC}"
                
                # Limpa tabela existente
                curl -X DELETE "${SUPABASE_URL}/rest/v1/${table}" \
                    -H "apikey: ${SUPABASE_SERVICE_KEY}" \
                    -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
                    --silent
                
                # Insere dados
                curl -X POST "${SUPABASE_URL}/rest/v1/${table}" \
                    -H "apikey: ${SUPABASE_SERVICE_KEY}" \
                    -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
                    -H "Content-Type: application/json" \
                    -H "Prefer: return=minimal" \
                    -d @"$json_file" \
                    --silent
                
                echo -e "${GREEN}✅ $table restaurado${NC}"
            done
            
            echo -e "${GREEN}🎉 Restauração concluída!${NC}"
            ;;
        
        "Verificar Status")
            echo -e "${YELLOW}📊 Verificando status do sistema...${NC}"
            
            # Verifica conexão com Supabase
            response=$(curl -s -o /dev/null -w "%{http_code}" \
                -H "apikey: ${SUPABASE_KEY}" \
                "${SUPABASE_URL}/rest/v1/products?limit=1")
            
            if [ "$response" = "200" ]; then
                echo -e "${GREEN}✅ Supabase: Conectado${NC}"
                
                # Conta registros
                counts=$(curl -s \
                    -H "apikey: ${SUPABASE_KEY}" \
                    -H "Authorization: Bearer ${SUPABASE_KEY}" \
                    "${SUPABASE_URL}/rest/v1/rpc/get_table_counts")
                
                echo "📈 Estatísticas:"
                echo "$counts" | python3 -m json.tool
            else
                echo -e "${RED}❌ Supabase: Erro ${response}${NC}"
            fi
            
            # Verifica Vercel
            if [ -n "$VERCEL_URL" ]; then
                response=$(curl -s -o /dev/null -w "%{http_code}" "${VERCEL_URL}/health")
                if [ "$response" = "200" ]; then
                    echo -e "${GREEN}✅ Vercel API: Online${NC}"
                else
                    echo -e "${RED}❌ Vercel API: Offline (${response})${NC}"
                fi
            fi
            
            # Verifica Telegram
            if [ -n "$BOT_TOKEN" ]; then
                response=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe")
                if echo "$response" | grep -q '"ok":true'; then
                    echo -e "${GREEN}✅ Telegram Bot: Online${NC}"
                else
                    echo -e "${RED}❌ Telegram Bot: Offline${NC}"
                fi
            fi
            ;;
        
        "Sair")
            echo -e "${BLUE}👋 Até logo!${NC}"
            break
            ;;
        
        *)
            echo -e "${RED}❌ Opção inválida${NC}"
            ;;
    esac
done
