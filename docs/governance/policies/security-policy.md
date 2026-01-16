# Security Policy

**Versão:** 1.0.0  
**Atualizado:** 2026-01-16  
**Framework:** ITIL 4 + ISO 27001 principles

---

## 🎯 Objetivo

Proteger confidencialidade, integridade e disponibilidade dos dados e sistemas do AfiliadoBot.

---

## 🔒 Princípios de Segurança

### 1. Security by Design
- Segurança integrada desde o design
- Revisão de segurança em todas mudanças
- Threat modeling para features críticas

### 2. Defense in Depth
- Múltiplas camadas de segurança
- Falha de uma camada não compromete sistema
- Redundância de controles

### 3. Least Privilege
- Acesso mínimo necessário
- Segregação de funções
- Revisão trimestral de acessos

### 4. Zero Trust
- Nunca confiar, sempre verificar
- Autenticação e autorização em todas requisições
- Logs de todas ações sensíveis

---

## 🛡️ Controles de Segurança

### Application Security

#### Authentication
- **Método:** JWT via Supabase Auth
- **MFA:** Obrigatório para admin
- **Session:** 7 dias com refresh token
- **Password:** Mínimo 12 caracteres, complexidade alta

#### Authorization
- **Model:** RBAC (Role-Based Access Control)
- **Enforcement:** Supabase RLS (Row Level Security)
- **Roles:** 
  - `admin` - Acesso total
  - `user` - Acesso limitado aos próprios dados
  - `readonly` - Apenas leitura

#### Input Validation
- **Sanitização:** Todos inputs do usuário
- **XSS Prevention:** Output encoding
- **SQL Injection:** Prepared statements/parametrized queries
- **CSRF:** FastAPI CSRF protection

#### API Security
- **Rate Limiting:** 100 req/min por IP
- **HTTPS Only:** TLS 1.3
- **CORS:** Whitelist específico
- **API Keys:** Rotation a cada 90 dias

### Infrastructure Security

#### Network
- **Firewall:** Render managed
- **DDoS:** Cloudflare (futuro)
- **VPN:** Não aplicável (cloud-native)

#### Secrets Management
- **Production:** Render environment variables
- **Development:** `.env` (gitignored)
- **Never:** Hardcoded credentials
- **Rotation:** Trimestral para secrets críticos

#### Backup
- **Database:** Diário via Supabase (retenção 30 dias)
- **Code:** Git (GitHub)
- **Configurations:** Versionadas no repo

### Data Security

#### Encryption
- **In Transit:** TLS 1.3 (HTTPS)
- **At Rest:** Supabase encryption
- **Sensitive Data:** Hashed (bcrypt para passwords)

#### Data Classification
- **Public:** Produtos, catálogo
- **Internal:** Analytics, métricas
- **Confidential:** Dados de usuário
- **Restricted:** Credentials, API keys

#### Data Retention
- **Logs:** 90 dias
- **User Data:** Enquanto conta ativa
- **Backups:** 30 dias

---

## 🚨 Incident Response

### Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| **P0 - Critical** | Serviço down | 15 min | Database breach, API down |
| **P1 - High** | Funcionalidade crítica afetada | 1h | Auth failure, payment issues |
| **P2 - Medium** | Funcionalidade secundária | 4h | Report export broken |
| **P3 - Low** | Issues menores | 24h | UI glitches |

### Response Process

1. **Detect** - Monitoring/alerts/report
2. **Assess** - Severity classification
3. **Contain** - Stop the damage
4. **Investigate** - Root cause analysis
5. **Remediate** - Fix the issue
6. **Document** - Post-mortem
7. **Improve** - Update runbooks/policies

### Security Incidents

**Immediate actions:**
- Isolar sistema afetado
- Notificar stakeholders (< 1h)
- Preservar evidências (logs)
- Iniciar investigação

**Post-incident:**
- Post-mortem obrigatório
- Update threat model
- Patch/fix deployed
- Comunicação transparente

---

## 🔍 Vulnerability Management

### Scanning
- **Dependency Scan:** Dependabot (GitHub)
- **SAST:** Bandit (Python), ESLint
- **DAST:** OWASP ZAP (mensal)
- **Container Scan:** Trivy (CI/CD)

### Patch Management

| Severity | SLA | Process |
|----------|-----|---------|
| **Critical** | 24h | Emergency patch |
| **High** | 7 days | Planned patch |
| **Medium** | 30 days | Regular update |
| **Low** | 90 days | Maintenance window |

### Disclosure
- **Private:** Security issues reportadas via email seguro
- **Response:** Acknowledgment < 48h
- **Fix Timeline:** Conforme severity SLA
- **Public Disclosure:** Após fix + 7 dias

---

## 👥 Access Control

### Production Access
- **Who:** Admin only
- **How:** MFA obrigatório
- **When:** Com approval + logging
- **Audit:** Revisão mensal

### Code Access
- **Who:** Development team
- **How:** GitHub (SSO)
- **Branch Protection:** main/develop require PR
- **Review:** Mínimo 1 approval

### Database Access
- **Who:** Admin apenas
- **How:** Supabase console (MFA)
- **Read-only:** Via dashboard
- **Write:** Migrations apenas

---

## 📋 Compliance

### Security Training
- **Onboarding:** Mandatory security training
- **Refresher:** Anual
- **Topics:** OWASP Top 10, secure coding, phishing

### Security Reviews
- **Code Review:** Todo PR
- **Architecture Review:** Features novas/major changes
- **Pen Test:** Anual (external)
- **Audit:** Compliance audit (conforme necessário)

---

## 🚫 Prohibited Actions

- ❌ Hardcoding secrets
- ❌ Committing .env files
- ❌ Using weak/default passwords
- ❌ Disabling security controls without approval
- ❌ Sharing credentials
- ❌ Accessing production without MFA
- ❌ Testing em produção sem approval

---

## 📞 Security Contacts

- **Security Lead:** [TBD]
- **Report Issue:** security@afiliadobot.top
- **Emergency:** [Emergency contact]

---

## 📊 Security Metrics

### KPIs
- Mean Time to Detect (MTTD)
- Mean Time to Respond (MTTR)
- Vulnerability Patch Rate
- Security Training Completion %

### Reporting
- **Dashboard:** Monthly security report
- **Incidents:** Immediate notification
- **Trends:** Quarterly review

---

**Aprovado por:** [Pending]  
**Próxima revisão:** 2026-07-16 (6 meses)
