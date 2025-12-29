# Shopee Integration - Setup Guide

## Step 1: Add Shopee Secret to .env

**Action Required:** Add the Shopee credentials to your `.env` file

1. Open `c:\ProjetoAfiliadoTop\.env` in your editor
2. Add these lines:

```env
# Shopee Affiliates API
SHOPEE_APP_ID=18353920154
SHOPEE_SECRET=4QXAWPSDFWOFIGUNROLYOQFTQJEODXRU
SHOPEE_API_ENDPOINT=https://affiliate.shopee.com.br/api/v3/graphql

# Shopee Import Settings
SHOPEE_AUTO_SYNC_ENABLED=true
SHOPEE_SYNC_INTERVAL_HOURS=24
SHOPEE_MIN_COMMISSION_RATE=5.0
```

3. Save the file

---

## Step 2: Apply SQL Migration in Supabase

**Action Required:** Run the migration in Supabase SQL Editor

1. Go to your Supabase project: https://app.supabase.com/project/YOUR_PROJECT/sql/new

2. Copy the entire content from: `c:\ProjetoAfiliadoTop\afiliadohub\sql\shopee_schema_migration.sql`

3. Paste it into the SQL Editor

4. Click "Run" button

5. You should see: "✅ Shopee migration completed successfully!"

**What this does:**
- Adds 10 new columns to `products` table for Shopee data
- Creates `shopee_sync_log` table for tracking imports
- Adds RPC functions for queries
- Creates indexes for performance
- Adds settings for Shopee configuration

---

## Step 3: Test Shopee Authentication

**Run this command:**

```powershell
cd c:\ProjetoAfiliadoTop
python scripts\test_shopee_auth.py
```

**Expected Output:**
```
OK: SHOPEE_APP_ID configurado: 18353920154
OK: SHOPEE_SECRET configurado: 4QXAWPSD...

TESTANDO SHOPEE API
============================================================

1. Criando cliente Shopee...
   OK: Cliente criado

2. Testando autenticacao...
   OK: Autenticacao bem-sucedida!

3. Buscando ofertas de marca...
   OK: 15 ofertas encontradas

4. Buscando produtos...
   OK: 42 produtos encontrados

TESTE CONCLUIDO COM SUCESSO!
```

**If you see errors:**
- Check that credentials are correct in `.env`
- Verify internet connection
- Check Supabase credentials are also in `.env`

---

## Step 4: Import Shopee Products

**Run this command:**

```powershell
cd c:\ProjetoAfiliadoTop
python scripts\shopee_import_manual.py
```

**Interactive Menu:**
```
Opcoes de importacao:
1. Importar todos os produtos (limit: 100)
2. Atualizar produtos existentes
3. Importar ofertas de marca

Escolha uma opcao (1-3): 1
Limite de produtos (enter para 100): 50
Comissao minima % (enter para 5.0): 5
```

**Expected Output:**
```
Iniciando importacao...
Tipo: all
Limite: 50
Comissao minima: 5.0%

============================================================
RESULTADO DA IMPORTACAO
============================================================

Produtos Importados: 42
Produtos Atualizados: 3
Erros: 0
Duracao: 12.3s

Importacao concluida!
```

---

## Step 5: Test Telegram Bot

**In Telegram, send these commands:**

```
/shopee_sync
```

**Expected Response:**
```
🔄 Iniciando sincronização com Shopee API...
Isso pode levar alguns minutos.

✅ Sincronização Concluída!

📦 Produtos Importados: 15
🔄 Produtos Atualizados: 8
❌ Erros: 0
⏱️ Duração: 8.2s

💰 Comissão Mínima: 5%

💡 Use /top_comissao para ver produtos com melhor comissão!
```

**Then try:**
```
/shopee_stats
```

**Expected:**
```
📊 Estatísticas Shopee

📦 Produtos Totais: 150
✅ Produtos Ativos: 142
💰 Comissão Média: 7.35%
🛒 Total de Vendas: 12,450

🔄 Última Sincronização: 27/12/2024 18:30
⚙️ Sync Automático: Ativado
```

**And:**
```
/top_comissao
```

**Expected:**
```
💰 TOP 5 - Maiores Comissões Shopee

#1 - 12.5% de comissão
💵 R$ 18.75 por venda

🛍️ Shopee
🛍️ Fone de Ouvido Bluetooth Premium...
💰 Preço: R$ 89,90
📦 Categoria: Eletrônicos
⭐ Avaliação: 4.8/5 (1,234 reviews)
🔗 [Ver Produto](link)
```

---

## Troubleshooting

### Error: "BOT_TOKEN não encontrado"
**Solution:** Make sure you have `BOT_TOKEN` configured in `.env`

### Error: "SUPABASE_URL e SUPABASE_KEY devem ser configurados"
**Solution:** Add Supabase credentials to `.env`

### Error: Authentication failed (401)
**Solution:** 
- Verify `SHOPEE_SECRET` is correct
- Check `SHOPEE_APP_ID` matches: 18353920154
- Ensure no extra spaces in `.env`

### Error: "Nenhum produto encontrado"
**Solution:**
- Run `/shopee_sync` first to import products
- Check Supabase migration was applied
- Verify internet connection to Shopee API

### Products not showing in bot
**Solution:**
- Check products table in Supabase has `store = 'shopee'`
- Verify `is_active = TRUE`
- Run `/shopee_sync` to import

---

## Verification Checklist

- [ ] `.env` has all Shopee credentials
- [ ] SQL migration applied in Supabase
- [ ] `test_shopee_auth.py` runs successfully  
- [ ] Products imported via `shopee_import_manual.py`
- [ ] `/shopee_sync` works in Telegram
- [ ] `/shopee_stats` shows data
- [ ] `/top_comissao` displays products

---

## Next Steps After Setup

### Automatic Daily Sync (Optional)

**Windows Task Scheduler:**
```powershell
# Create daily task at 6 AM
schtasks /create /tn "ShopeeSync" /tr "python c:\ProjetoAfiliadoTop\scripts\shopee_import_manual.py" /sc daily /st 06:00
```

### Monitor Performance

**Check import logs:**
```sql
-- In Supabase SQL Editor
SELECT * FROM shopee_sync_log 
ORDER BY started_at DESC 
LIMIT 10;
```

**View statistics:**
```sql
SELECT * FROM get_shopee_statistics();
```

### Customize Settings

**In Supabase settings table:**
```sql
UPDATE settings 
SET value = jsonb_set(value, '{min_commission_rate}', '10.0')
WHERE key = 'shopee_api';
```

---

## Support

If you encounter any issues:
1. Check the logs in terminal
2. Verify all credentials in `.env`
3. Ensure Supabase migration was applied
4. Test authentication first before importing

🎉 **You're all set! Enjoy your Shopee integration!**
