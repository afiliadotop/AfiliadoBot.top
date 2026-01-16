# Disaster Recovery Plan

**Framework:** ISO 22301 (Business Continuity)  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Objetivos

- **RPO (Recovery Point Objective):** 1 hora
- **RTO (Recovery Time Objective):** 4 horas
- **Uptime Target:** 99.5%

---

## 📊 Business Impact Analysis

### Critical Services

| Service | Impact if Down | Max Downtime | Priority |
|---------|----------------|--------------|----------|
| **Backend API** | Alto - Funcionalidade principal | 4h | P0 |
| **Database** | Crítico - Perda de dados | 1h | P0 |
| **Frontend** | Médio - Acesso impossível | 8h | P1 |
| **Telegram Bot** | Baixo - Canal secundário | 24h | P2 |

---

## 💾 Backup Strategy

### Database (Supabase/PostgreSQL)

**Automated Backups:**
- **Frequency:** Diário (daily)
- **Retention:** 30 dias
- **Type:** Full snapshot
- **Location:** Supabase managed (multi-region)
- **Cost:** Incluído no plano

**Point-in-Time Recovery (PITR):**
- **Enabled:** Sim
- **Window:** Últimas 7 dias
- **Recovery:** Qualquer timestamp

**Manual Backups:**
- **Frequency:** Antes de major changes
- **Method:** `pg_dump` via Supabase CLI
- **Storage:** S3 (futuro) ou local + Git LFS

### Code & Configuration

**Git Repository:**
- **Platform:** GitHub
- **Branches:** main (protected), develop
- **Backup:** GitHub's infrastructure (redundant)
- **Local:** Team clones

**Environment Variables:**
- **Production:** Render secrets (encrypted)
- **Backup:** 1Password vault (encrypted)
- **Documentation:** `.env.example` (no secrets)

### Application State

**Logs:**
- **Backend:** Render logs (30 dias)
- **Frontend:** Vercel logs (7 dias)
- **Errors:** Sentry (90 dias)

**Sessions:**
- **Storage:** Supabase (incluído em backup DB)

---

## 🔄 Recovery Procedures

### Scenario 1: Database Corruption

**Symptoms:**
- Queries falham
- Data inconsistency
- RLS errors

**Recovery:**
```bash
# 1. Assess damage
supabase db inspect

# 2. Stop writes (maintenance mode)
# Set MAINTENANCE_MODE=true em Render

# 3. Restore from backup
supabase db restore --backup-id <backup_id>

# 4. Verify integrity
supabase db test-connections

# 5. Resume operations
# Remove MAINTENANCE_MODE

# RTO: 1-2 horas
```

---

### Scenario 2: API Outage (Render)

**Symptoms:**
- API endpoints down
- 502/503 errors
- Health check fails

**Recovery:**
```bash
# 1. Check Render status
curl https://status.render.com

# 2. Review logs
render logs -t api

# 3. Rollback to last known good
git revert HEAD
git push origin main
# Auto-deploy triggered

# 4. If Render issue, wait or migrate

# RTO: 30 min (rollback) ou 4h (migration)
```

---

### Scenario 3: Complete Data Loss

**Symptoms:**
- Database inacessível
- Backups corrompidos
- Catastrophic failure

**Recovery:**
```bash
# 1. Create new Supabase project
supabase init

# 2. Restore schema
supabase db push

# 3. Restore data from latest valid backup
pg_restore -d postgres backup.sql

# 4. Update connection strings
# Render → SUPABASE_URL, SUPABASE_KEY

# 5. Test thoroughly
pytest tests/

# 6. Switch DNS/deploy

# RTO: 4-8 horas
```

---

### Scenario 4: GitHub Repository Loss

**Symptoms:**
- Repository deleted/inacessível
- Force-push destructive
- Account compromise

**Recovery:**
```bash
# 1. Team local clones
git log # Verify integrity

# 2. Create new repo
gh repo create afiliadotop/AfiliadoBot-Recovery

# 3. Push from latest valid clone
git remote add recovery <new-repo>
git push recovery --all

# 4. Update CI/CD webhooks
# Render, Vercel → new repo

# RTO: 1-2 horas
```

---

### Scenario 5: Ransomware/Security Breach

**Symptoms:**
- Unauthorized access
- Data encryption
- Suspicious activity

**Recovery:**
```bash
# 1. ISOLATE IMMEDIATELY
# Disable all API keys, rotate secrets

# 2. Assess damage
# Review logs, access patterns

# 3. Clean restore
# From backup BEFORE breach

# 4. Security hardening
# Update all credentials
# Patch vulnerabilities
# Enable MFA everywhere

# 5. Notify affected users (LGPD)

# 6. Post-incident review

# RTO: 8-24 horas (investigation time)
```

---

## 🚨 Emergency Contacts

### Internal
- **Tech Lead:** [Phone/Email]
- **DevOps:** [Phone/Email]
- **Security:** [Phone/Email]

### External
- **Supabase Support:** support@supabase.com
- **Render Support:** support@render.com
- **Vercel Support:** support@vercel.com
- **GitHub Support:** support@github.com

---

## 📋 Recovery Checklist

### Pre-Disaster
- [x] Automated backups configured
- [x] Backup retention policy set
- [ ] Backup restoration tested (monthly)
- [ ] DR plan documented
- [ ] Team trained on procedures
- [ ] Emergency contacts updated

### During Disaster
- [ ] Assess severity
- [ ] Notify stakeholders
- [ ] Activate DR plan
- [ ] Document all actions
- [ ] Communicate status updates

### Post-Recovery
- [ ] Verify system integrity
- [ ] Run comprehensive tests
- [ ] Update documentation
- [ ] Post-mortem
- [ ] Update DR plan

---

## 📊 Testing Schedule

### Backup Restoration Test
**Frequency:** Mensal  
**Scope:** Restore DB backup to staging  
**Validation:** Data integrity checks

**Last Test:** [Pending]  
**Next Test:** [TBD]

### Full DR Drill
**Frequency:** Trimestral  
**Scope:** Complete failover simulation  
**Validation:** RTO/RPO met

**Last Drill:** [Pending]  
**Next Drill:** [TBD]

---

## 📈 Metrics

### SLAs
- **RPO:** < 1h (data loss)
- **RTO:** < 4h (downtime)
- **Backup Success Rate:** > 99%
- **Recovery Test Success:** 100%

### Monitoring
- Backup completion (daily check)
- RTO/RPO achievement (quarterly)
- Test success rate

---

## 🔗 Related Documents
- [Incident Management](../governance/processes/incident-management.md)
- [Security Policy](../governance/policies/security-policy.md)
- [Risk Management](../governance/risk-management.md)

---

**Aprovado por:** [Pending]  
**Próxima revisão:** Trimestral  
**Próximo teste:** [TBD - Agendar]
