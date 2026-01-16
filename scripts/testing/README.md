# Testing Scripts

**ITIL Activity:** Support / Quality Assurance  
**Criticidade:** 🟡 MÉDIA - Testes e validação

---

## Scripts Consolidados (Novos)

### test_telegram.py ✨ NOVO
**Substitui:** test_telegram_simple.py, test_telegram_config.py, test_telegram_bot.py  
**Propósito:** Testes consolidados do bot Telegram

```bash
# Teste simples
python scripts/testing/test_telegram.py --mode simple

# Teste completo
python scripts/testing/test_telegram.py --mode full
```

### test_shopee.py ✨ NOVO
**Substitui:** test_shopee_auth.py, test_shopee_complete.py, test_shopee_offers.py, test_shopee_shortlink.py  
**Propósito:** Testes consolidados da API Shopee

```bash
python scripts/testing/test_shopee.py
```

---

## Scripts Individuais

- `system_verification.py` - Verificação completa do sistema
- `test_ml_affiliate.py` - Testes MercadoLivre
- `test_bot_enhanced.py` - Bot Telegram enhanced
- `test_rate_limit_scroll.py` - Testes rate limiting
- `send_test_message.py` - Envio mensagens teste

---

## Execução Pré-Deploy

```bash
# Rodar todos os testes
python scripts/testing/system_verification.py

# Testes específicos
python scripts/testing/test_shopee.py
python scripts/testing/test_telegram.py
```

---

**Nota:** Scripts legados (test_telegram_*, test_shopee_*) serão removidos após validação dos consolidados.
