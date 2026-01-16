# Risk Management

**Framework:** COBIT 2019 + ISO 31000  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Objetivo

Identificar, avaliar e mitigar riscos que possam impactar objetivos do AfiliadoBot.

---

## 📋 Risk Register

### R001 - API Key Exposure
**Categoria:** Security  
**Descrição:** Credenciais (Shopee, ML, Telegram) expostas em código/logs  

**Probabilidade:** Medium (3/5)  
**Impacto:** Critical (5/5)  
**Risk Score:** 15 (High)

**Mitigação:**
- ✅ Never hardcode credentials
- ✅ Use environment variables
- ✅ `.gitignore` configured
- ✅ Secret scanning (git-secrets)
- ✅ Regular audits

**Status:** Mitigated (residual risk: Low)

---

### R002 - Database Breach
**Categoria:** Security  
**Descrição:** Acesso não autorizado ao banco de dados

**Probabilidade:** Low (2/5)  
**Impacto:** Critical (5/5)  
**Risk Score:** 10 (Medium-High)

**Mitigação:**
- ✅ RLS (Row Level Security) enabled
- ✅ Strong authentication
- ✅ Encryption at rest/transit
- ✅ Regular backups
- ✅ Access logs monitored
- ⏳ MFA enforcement (pending)

**Status:** Partially Mitigated

---

### R003 - Service Downtime
**Categoria:** Availability  
**Descrição:** API/Frontend indisponíveis

**Probabilidade:** Medium (3/5)  
**Impacto:** High (4/5)  
**Risk Score:** 12 (High)

**Mitigação:**
- ✅ Health checks implemented
- ✅ Monitoring (Sentry)
- ✅ Auto-scaling (Render)
- ⏳ Alerting setup (pending)
- ⏳ Disaster recovery plan (pending)

**Status:** In Progress

---

### R004 - External API Dependency
**Categoria:** Operational  
**Descrição:** Shopee/ML API down ou rate limit

**Probabilidade:** Medium (3/5)  
**Impacto:** Medium (3/5)  
**Risk Score:** 9 (Medium)

**Mitigação:**
- ✅ Rate limiting próprio
- ✅ Error handling robusto
- ✅ Retry logic
- ⏳ Caching layer (futuro)
- ⏳ Fallback strategies

**Status:** Partially Mitigated

---

### R005 - Data Loss
**Categoria:** Data  
**Descrição:** Perda de dados de produtos/usuários

**Probabilidade:** Low (2/5)  
**Impacto:** High (4/5)  
**Risk Score:** 8 (Medium)

**Mitigação:**
- ✅ Daily backups (Supabase)
- ✅ 30-day retention
- ✅ Point-in-time recovery
- ⏳ Backup testing (pending)
- ⏳ Cross-region backup (futuro)

**Status:** Mitigated

---

### R006 - Dependency Vulnerabilities
**Categoria:** Security  
**Descrição:** Vulnerabilidades em dependencies (npm/pip)

**Probabilidade:** High (4/5)  
**Impacto:** Medium (3/5)  
**Risk Score:** 12 (High)

**Mitigação:**
- ✅ Dependabot enabled
- ✅ CI security scan (Trivy)
- ✅ Regular updates
- ⏳ Patch SLA enforcement

**Status:** Partially Mitigated

---

### R007 - LGPD Non-Compliance
**Categoria:** Compliance  
**Descrição:** Violação de LGPD

**Probabilidade:** Medium (3/5)  
**Impacto:** Critical (5/5)  
**Risk Score:** 15 (High)

**Mitigação:**
- ⏳ Privacy policy (pending)
- ⏳ Data inventory (pending)
- ⏳ Consent management (pending)
- ⏳ Data retention policy (pending)

**Status:** High Risk - Requires Immediate Action

---

## 📊 Risk Matrix

```
Impact →
5 |    R002  R001 R007
4 |    R003  R005
3 |    R004  R006
2 |
1 |━━━━━━━━━━━━━━━━━━
  1    2    3    4    5
       ← Probability
```

---

## 🎯 Risk Treatment

### Accept
Aceitar o risco (baixo impacto/probabilidade)

### Mitigate
Reduzir probabilidade ou impacto

### Transfer
Transferir risco (seguro, outsourcing)

### Avoid
Eliminar atividade que causa risco

---

## 🔄 Risk Review Process

### Frequência
- **Mensal:** Review risk register
- **Trimestral:** Strategy review
- **Ad-hoc:** New risks emergentes

### Responsabilidades
- **Tech Lead:** Riscos técnicos
- **Security Lead:** Riscos de segurança
- **Product Owner:** Riscos de negócio

---

## 📞 Escalation

| Risk Score | Action | Response Time |
|------------|--------|---------------|
| **> 15** | Immediate escalation | < 24h |
| **12-15** | Weekly review | < 1 week |
| **8-12** | Monthly review | < 1 month |
| **< 8** | Quarterly review | < 3 months |

---

**Próxima revisão:** 2026-02-16 (mensal)
