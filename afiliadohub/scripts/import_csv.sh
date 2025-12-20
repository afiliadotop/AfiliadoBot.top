#!/bin/bash

# 📦 Script para importar CSVs em massa para o AfiliadoHub
# Uso: ./import_csv.sh arquivo.csv [loja] [--replace]

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica argumentos
if [ $# -lt 1 ]; then
    echo "Uso: $0 <arquivo_csv> [loja] [--replace]"
    echo ""
    echo "Lojas disponíveis:"
    echo "  shopee, aliexpress, amazon, temu, shein, magalu, mercado_livre"
    echo ""
    echo "Exemplos:"
    echo "  $0 produtos_shopee.csv shopee"
    echo "  $0 ofertas_amazon.csv amazon --replace"
    exit 1
fi

CSV_FILE="$1"
STORE="${2:-shopee}"
REPLACE="${3:---replace}"

# Verifica se arquivo existe
if [ ! -f "$CSV_FILE" ]; then
    error "Arquivo não encontrado: $CSV_FILE"
    exit 1
fi

# Verifica se é CSV
if [[ "$CSV_FILE" != *.csv ]]; then
    warning "O arquivo não tem extensão .csv. Continuando mesmo assim..."
fi

# Carrega variáveis de ambiente
if [ -f .env.production ]; then
    source .env.production
elif [ -f .env ]; then
    source .env
else
    error "Arquivo .env não encontrado"
    exit 1
fi

# Verifica variáveis necessárias
if [ -z "$VERCEL_URL" ] || [ -z "$ADMIN_API_KEY" ]; then
    error "Variáveis VERCEL_URL e ADMIN_API_KEY não configuradas"
    exit 1
fi

# Remove http:// ou https:// da URL
VERCEL_URL=${VERCEL_URL#https://}
VERCEL_URL=${VERCEL_URL#http://}
VERCEL_URL="https://$VERCEL_URL"

log "Iniciando importação..."
log "Arquivo: $CSV_FILE"
log "Loja: $STORE"
log "URL API: $VERCEL_URL"

# Verifica tamanho do arquivo
FILE_SIZE=$(stat -f%z "$CSV_FILE" 2>/dev/null || stat -c%s "$CSV_FILE" 2>/dev/null)
FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))

if [ $FILE_SIZE_MB -gt 100 ]; then
    warning "Arquivo muito grande: ${FILE_SIZE_MB}MB"
    warning "Recomendado: dividir em arquivos menores de 100MB"
    
    read -p "Deseja continuar? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Conta linhas do CSV
log "Analisando arquivo..."
TOTAL_LINES=$(wc -l < "$CSV_FILE" | tr -d ' ')
HEADER_LINES=1
DATA_LINES=$((TOTAL_LINES - HEADER_LINES))

if [ $DATA_LINES -le 0 ]; then
    error "Arquivo CSV vazio ou sem dados"
    exit 1
fi

success "Arquivo analisado: ${DATA_LINES} produtos encontrados"

# Verifica estrutura do CSV
log "Verificando estrutura do CSV..."
HEADER=$(head -1 "$CSV_FILE")

REQUIRED_FIELDS=("name" "link" "price")
MISSING_FIELDS=()

for field in "${REQUIRED_FIELDS[@]}"; do
    if [[ ! "$HEADER" =~ $field ]]; then
        MISSING_FIELDS+=("$field")
    fi
done

if [ ${#MISSING_FIELDS[@]} -gt 0 ]; then
    warning "Campos não encontrados no CSV: ${MISSING_FIELDS[*]}"
    warning "O arquivo pode não ser processado corretamente"
    
    read -p "Deseja continuar? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
else
    success "Estrutura do CSV OK"
fi

# Prepara upload
log "Preparando upload..."

# Cria payload
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${CSV_FILE%.csv}_processed_${TIMESTAMP}.json"

# Converte CSV para JSON (primeiras 10 linhas para teste)
log "Convertendo CSV para JSON..."
python3 -c "
import csv, json, sys

input_file = '$CSV_FILE'
output_file = '$OUTPUT_FILE'
store = '$STORE'

products = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        # Limita para teste
        if i >= 10000:  # Processa no máximo 10k por vez
            break
            
        # Prepara produto
        product = {
            'store': store,
            'name': row.get('name', row.get('product', row.get('title', '')))[:500],
            'affiliate_link': row.get('link', row.get('url', row.get('affiliate_link', ''))),
            'current_price': float(row.get('price', row.get('current_price', 0)) or 0),
            'original_price': float(row.get('original_price', row.get('old_price', 0)) or 0),
            'category': row.get('category', row.get('categoria', '')),
            'image_url': row.get('image', row.get('image_url', row.get('imagem', ''))),
            'source': 'csv_import',
            'source_file': '$CSV_FILE'
        }
        
        # Calcula desconto se houver preço original
        if product['original_price'] > product['current_price']:
            discount = ((product['original_price'] - product['current_price']) / product['original_price']) * 100
            product['discount_percentage'] = int(discount)
        
        products.append(product)

print(f'Processados: {len(products)} produtos')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)
"

if [ ! -f "$OUTPUT_FILE" ]; then
    error "Falha ao converter CSV para JSON"
    exit 1
fi

PROCESSED_COUNT=$(python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); print(len(data))")
success "Convertidos: ${PROCESSED_COUNT} produtos para JSON"

# Envia para API
log "Enviando para API..."
START_TIME=$(date +%s)

RESPONSE=$(curl -s -X POST "$VERCEL_URL/api/import/csv" \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CSV_FILE" \
  -F "store=$STORE" \
  -F "replace_existing=false")

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if echo "$RESPONSE" | grep -q '"status":"processing"'; then
    success "Importação iniciada com sucesso!"
    log "Tempo: ${DURATION} segundos"
    
    # Extrai informações da resposta
    echo ""
    echo "📊 Detalhes da importação:"
    echo "$RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'Status: {data.get(\"status\", \"N/A\")}')
    print(f'Mensagem: {data.get(\"message\", \"N/A\")}')
    print(f'Loja: {data.get(\"store\", \"N/A\")}')
    print(f'Timestamp: {data.get(\"timestamp\", \"N/A\")}')
except:
    print(sys.stdin.read())
    "
    
    # Monitora status (opcional)
    echo ""
    log "A importação está sendo processada em background."
    log "Verifique os logs em: $VERCEL_URL/docs"
    
else
    error "Erro ao enviar para API"
    echo "Resposta: $RESPONSE"
    exit 1
fi

# Limpeza
rm -f "$OUTPUT_FILE"

echo ""
success "✅ Importação agendada com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Acompanhe o processamento nos logs da Vercel"
echo "2. Verifique os produtos em: $VERCEL_URL/api/products"
echo "3. Teste o bot com: /cupom ou /$STORE"
echo ""
echo "💡 Dica: Para importar arquivos grandes, divida em partes:"
echo "   split -l 10000 grande_arquivo.csv parte_"
echo "   for file in parte_*; do ./import_csv.sh \"\$file\" $STORE; done"
