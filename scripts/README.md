# Scripts - Gerenciamento de Serviços ITIL 4

[![ITIL 4](https://img.shields.io/badge/ITIL-4-blue.svg)](https://www.axelos.com/best-practice-solutions/itil)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Organização baseada em **Service Value Chain** do ITIL 4.

---

## 📋 Estrutura por Atividade ITIL

| Pasta | Atividade ITIL | Descrição |
|-------|---------------|-----------|
| **production/** | Deliver & Support | ⚡ Serviços em produção |
| **operations/** | Support | 🔧 Operações administrativas |
| **testing/** | Support (QA) | 🧪 Testes e validação |
| **deployment/** | Plan & Deliver | 🚀 CI/CD e deploy |
| **auth/** | Obtain/Build | 🔐 OAuth e autenticação |
| **development/** | Design | 💻 Ferramentas desenvolvimento |
| **utils/** | - | 🛠️ Utilitários gerais |

---

## 🚀 Quick Start

### Scripts de Produção (Críticos)
```bash
# Import diário Shopee
python scripts/production/shopee_daily_import.py

# Enviar promoções Telegram
python scripts/production/send_daily_promo.py
```

### Testes
```bash
# Teste completo integração
python scripts/testing/test_integration.py

# Testes específicos
python scripts/testing/test_shopee.py
python scripts/testing/test_telegram.py
```

### Pré-Deploy
```bash
# Validação antes de deploy
python scripts/deployment/pre_deploy_validation.py

# Windows
.\scripts\deployment\pre-deploy-tests.ps1

# Unix/Linux
bash scripts/deployment/pre-deploy-tests.sh
```

---

## 📚 Documentação

Cada subpasta contém seu próprio `README.md` com detalhes específicos:

- [production/README.md](production/README.md) - Scripts de produção
- [operations/README.md](operations/README.md) - Operações
- [testing/README.md](testing/README.md) - Testes
- [deployment/README.md](deployment/README.md) - Deploy
- [auth/README.md](auth/README.md) - Autenticação
- [development/README.md](development/README.md) - Desenvolvimento

---

## 🔄 Controle de Mudanças (ITIL Change Management)

Ver [CHANGELOG.md](CHANGELOG.md) para histórico completo de mudanças.

**Processo:**
1. Propor mudança → PR/Issue
2. Revisar impacto
3. Testar em dev
4. Aprovar
5. Deploy controlado
6. Documentar no CHANGELOG

---

## 🔒 Segurança

- ✅ **Nenhum token/secret hardcoded** nos scripts
- ✅ Todos os scripts usam `.env` para credenciais
- ✅ `.gitignore` protege arquivos sensíveis
- ⚠️ Nunca commitar arquivos `.env*` 

---

## 📊 Métricas (Continual Improvement)

Scripts em produção incluem métricas ITIL:
- Tempo de execução
- Taxa de sucesso/falha
- Registros processados
- Última execução

---

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verificar logs em `logs/`
2. Executar `python scripts/operations/status_check.py`
3. Revisar [troubleshooting.md](troubleshooting.md)

---

## 📝 Contribuindo

1. Seguir estrutura ITIL 4
2. Adicionar docstrings completas
3. Atualizar README da pasta
4. Atualizar CHANGELOG.md
5. Testar antes de commit

---

**Última atualização:** 2026-01-15  
**Versão:** 2.0.0  
**Framework:** ITIL 4
