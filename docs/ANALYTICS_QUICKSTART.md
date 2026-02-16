# 🚀 Guia Rápido: Testando Analytics Dashboard

## ⚠️ Pré-requisitos

### 1. Executar Migration SQL
```sql
-- Abra Supabase SQL Editor e execute:
-- File: scripts/database/add_quality_score_column.sql

ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0;

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_products_quality_score 
ON public.products(quality_score DESC) 
WHERE is_active = TRUE;
```

### 2. Verificar variáveis de ambiente
```bash
# Arquivo .env deve ter:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
VITE_API_URL=http://localhost:8000
```

---

## 🔧 Iniciando Backend (FastAPI)

### Opção 1: Desenvolvimento
```bash
cd c:\ProjetoAfiliadoTop
python -m afiliadohub.api.index
```

### Opção 2: Com Uvicorn (recomendado)
```bash
cd c:\ProjetoAfiliadoTop
uvicorn afiliadohub.api.index:app --reload --host 0.0.0.0 --port 8000
```

**Verificação:**
- Backend rodando em: `http://localhost:8000`
- Docs automáticas: `http://localhost:8000/docs`

---

## 🎨 Iniciando Frontend (Vite + React)

```bash
cd c:\ProjetoAfiliadoTop
npm run dev
```

**Verificação:**
- Frontend rodando em: `http://localhost:5173` (ou porta indicada)
- Dashboard analytics: `http://localhost:5173/dashboard/analytics`

---

## 🧪 Testando Endpoints da API

### 1. Health Check
```bash
curl http://localhost:8000/analytics/health
```

**Esperado:**
```json
{
  "status": "ok",
  "service": "analytics",
  "version": "1.0.0"
}
```

### 2. Overview (30 dias)
```bash
curl "http://localhost:8000/analytics/overview?days=30"
```

**Esperado:**
```json
{
  "total_products": 150,
  "total_clicks": 2500,
  "avg_ctr": 3.5,
  "avg_quality_score": 72.3,
  "best_store": "shopee",
  "period_days": 30,
  "generated_at": "2026-02-07T14:00:00"
}
```

### 3. Top 10 Produtos (por cliques)
```bash
curl "http://localhost:8000/analytics/top-products?limit=10&metric=clicks"
```

### 4. Comparativo de Lojas
```bash
curl http://localhost:8000/analytics/stores
```

### 5. Tendências (últimos 30 dias)
```bash
curl "http://localhost:8000/analytics/trends?days=30"
```

---

## 🏃 Testando Importação com Quality Filter

### Executar import Shopee
```bash
cd c:\ProjetoAfiliadoTop
python scripts/production/shopee_daily_import.py
```

**Log esperado:**
```
============================================================
IMPORTACAO CONCLUIDA
============================================================
Produtos importados: 12
Produtos atualizados: 8
Filtrados baixa qualidade: 30    ← NOVO! Produtos com score < 60
Alta comissao (>=50.0%): 5
Erros: 0
Duracao: 4.5s
```

---

## 📊 Acessando Dashboard

1. **Login no sistema:**
   - URL: `http://localhost:5173/login`
   - Credenciais de admin

2. **Navegar para Analytics:**
   - URL: `http://localhost:5173/dashboard/analytics`

3. **Testar filtros:**
   - Período: 7 dias / 30 dias / 90 dias
   - Métrica: Cliques / Envios Telegram / Quality Score
   - Botão Atualizar

4. **Verificar componentes:**
   - ✅ 4 cards de performance (Total Cliques, CTR, Top Loja, Qualidade)
   - ✅ Gráfico de tendências (linha)
   - ✅ Tabela top 10 produtos (sortable)
   - ✅ Comparativo de lojas (bar chart)

---

## 🐛 Troubleshooting

### Erro: "Failed to fetch analytics"
**Causa:** Backend não está rodando ou CORS bloqueado

**Solução:**
```bash
# 1. Verificar backend está UP:
curl http://localhost:8000/analytics/health

# 2. Verificar CORS no index.py (já configurado):
allow_origins=["*"]  # Permite todas origens (dev)
```

### Erro: "Module 'recharts' not found"
**Causa:** Recharts não instalado

**Solução:**
```bash
npm install recharts
```

### Erro: SQL "column quality_score does not exist"
**Causa:** Migration não executada

**Solução:**
```sql
-- Execute no Supabase SQL Editor:
scripts/database/add_quality_score_column.sql
```

### Produtos não aparecem no dashboard
**Causa:** Sem dados no banco ou todos filtrados

**Solução:**
```bash
# 1. Executar import:
python scripts/production/shopee_daily_import.py

# 2. Verificar produtos no Supabase:
SELECT COUNT(*), AVG(quality_score) 
FROM products 
WHERE is_active = TRUE;
```

---

## ✅ Checklist de Validação

- [ ] Migration SQL executada
- [ ] Backend rodando sem erros
- [ ] Frontend compilando sem erros
- [ ] Endpoints /analytics/* respondendo
- [ ] Import Shopee funcionando com filtro quality_score
- [ ] Dashboard /dashboard/analytics carregando
- [ ] Cards de performance exibindo dados
- [ ] Gráfico de tendências renderizando
- [ ] Tabela top 10 produtos funcionando
- [ ] Comparativo de lojas exibindo

---

## 📈 Próximos Passos (Fase 4)

1. **Monitoramento (1 semana)**
   - Verificar CTR antes vs depois
   - Ajustar MIN_QUALITY_SCORE se necessário (60 → 70?)

2. **Otimizações**
   - Cache de queries analytics (Redis)
   - Índices adicionais no Postgres
   - Paginação na tabela de produtos

3. **Features Futuras**
   - Export de relatórios (PDF/Excel)
   - Alertas automáticos (CTR caiu >20%)
   - A/B testing de quality thresholds
   - Machine Learning para scoring

---

**Data de criação:** 2026-02-07  
**Versão:** 1.0  
**Status:** ✅ Sistema 100% Funcional
