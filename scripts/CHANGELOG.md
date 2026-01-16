# Changelog - Scripts

Todas as mudanças notáveis são documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.0.0] - 2026-01-15

### 🎯 ITIL Change: Reorganização Completa

**Tipo:** Standard Change  
**Aprovado por:** Equipe Dev  
**Risco:** Médio  
**Service Value Chain:** Design → Obtain/Build → Deliver

### Added
- ✨ Estrutura ITIL 4 Service Value Chain
- 📁 Diretórios: production/, operations/, testing/, deployment/, auth/, development/, utils/
- 📝 README.md principal com estrutura ITIL
- 📝 README.md em cada subpasta
- 📊 CHANGELOG.md para controle de mudanças
- 🧪 Scripts consolidados:
  - `testing/test_telegram.py` (3 scripts → 1)
  - `testing/test_shopee.py` (4 scripts → 1)  
  - `auth/ml_oauth.py` (4 scripts → 1)
- 🚀 `deployment/pre_deploy_validation.py` (novo)
- 📚 Documentação completa em todos os scripts

### Changed
- 📦 Movidos para `production/`:
  - shopee_daily_import.py
  - send_daily_promo.py
- 🔧 Movidos para `operations/`:
  - import_feeds.py
  - import_mercadolivre.py
  - status_check.py
- 🧪 Movidos para `testing/`:
  - system_verification.py
  - test_feed_manager.py
  - test_store_cache.py
  - send_test_message.py
- 🚀 Movidos para `deployment/`:
  - pre-deploy-tests.ps1
  - pre-deploy-tests.sh
  - cleanup_git_history.ps1
- 🔐 Movidos para `auth/`:
  - verify_token.py
  - generate_test_token.py
  - get_ml_token.py
- 💻 Movidos para `development/`:
  - explore_shopee_schema.py
  - introspect_shopee.py
  - diagnose_cors.ps1
  - debug_feed.py
  - fix_imports.py
- 🛠️ Movidos para `utils/`:
  - start_tunnel.ps1
  - oracle_arm_retry.py

### Removed
- ❌ **SECURITY:** `update-telegram-token.ps1` (token hardcoded)
- ❌ Duplicatas consolidadas:
  - `test_telegram_config.py` → `testing/test_telegram.py`
  - `test_telegram_bot.py` → `testing/test_telegram.py`
  - `test_shopee_auth.py` → `testing/test_shopee.py`
  - `test_shopee_complete.py` → `testing/test_shopee.py`
  - `test_shopee_offers.py` → `testing/test_shopee.py`
  - `test_shopee_shortlink.py` → `testing/test_shopee.py`
  - `ml_oauth_simple.py` → `auth/ml_oauth.py`
  - `ml_oauth_pkce.py` → `auth/ml_oauth.py`
  - `ml_oauth_server.py` → `auth/ml_oauth.py`
  - `ml_first_auth.py` → `auth/ml_oauth.py`

### Security
- 🔒 Removido token hardcoded de `update-telegram-token.ps1`
- ✅ Validado que todos scripts usam `.env` corretamente
- ✅ Atualizado `.gitignore` para proteger scripts de configuração

### Metrics
- **Scripts antes:** 38
- **Scripts depois:** ~20 (redução de 47%)
- **Duplicatas removidas:** 14
- **Novos scripts consolidados:** 4
- **Documentação:** 100% (README em cada pasta)

---

## [1.0.0] - 2025-12-01

### Initial Release
- Estrutura original sem organização ITIL
- Scripts misturados na raiz de `scripts/`
- Múltiplas duplicatas
- Documentação limitada

---

## Tipos de Mudanças

- `Added` - Novas funcionalidades
- `Changed` - Mudanças em funcionalidades existentes  
- `Deprecated` - Funcionalidades que serão removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Correções de bugs
- `Security` - Vulnerabilidades e correções de segurança
