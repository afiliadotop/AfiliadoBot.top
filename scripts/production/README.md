# Production Scripts

**ITIL Activity:** Deliver & Support  
**Criticidade:** 🔴 **ALTA** - Scripts de produção

---

## Scripts

### shopee_daily_import.py
**Versão:** 2.0  
**Propósito:** Import diário automático de produtos Shopee  
**Schedule:** Diário 02:00 UTC  
**Dependências:** `.env` (SHOPEE_APP_ID, SHOPEE_APP_SECRET)

**Execução:**
```bash
python scripts/production/shopee_daily_import.py
```

**Métricas:**
- Produtos importados/dia: ~1000-2000
- Tempo médio execução: 5-15 min
- Taxa de sucesso: >95%

---

### send_daily_promo.py
**Versão:** 1.5  
**Propósito:** Envia promoções diárias ao canal Telegram  
**Schedule:** Diário 09:00 BRT  
**Dependências:** `.env` (TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID)

**Execução:**
```bash
python scripts/production/send_daily_promo.py
```

**Métricas:**
- Mensagens/dia: 5-10
- Engagement rate: Monitorado no Telegram

---

## Monitoramento

Ver logs em: `logs/production/`

**Alertas:**
- Falha em execução → Notificar equipe
- Taxa sucesso < 90% → Investigar
- Tempo execução > 30min → Otimizar

---

## Manutenção

**Backup:** Diário automático  
**Rollback:** Git tags (ex: v2.0.0)  
**Support:** Ver `scripts/operations/status_check.py`
