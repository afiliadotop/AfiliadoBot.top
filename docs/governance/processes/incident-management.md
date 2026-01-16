# Incident Management Process

**Framework:** ITIL 4 Incident Management  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Definição

**Incidente:** Interrupção não planejada ou redução da qualidade de um serviço.

**Objetivo:** Restaurar operação normal o mais rápido possível com mínimo impacto.

---

## 📊 Severity Levels

### P0 - Critical
**Impact:** Serviço completamente down ou security breach  
**Examples:**
- API totalmente indisponível
- Database breach
- Data loss
- Security vulnerability exploited

**Response Time:** 15 minutos  
**Resolution Target:** 4 horas  
**Notification:** Imediata (todos stakeholders)

---

### P1 - High
**Impact:** Funcionalidade crítica severamente degradada  
**Examples:**
- Login falha para todos usuários
- API 50%+ erro rate
- External API integration quebrada (Shopee/ML)

**Response Time:** 1 hora  
**Resolution Target:** 8 horas  
**Notification:** 1 hora (stakeholders)

---

### P2 - Medium
**Impact:** Funcionalidade secundária afetada  
**Examples:**
- Feature específica quebrada
- Performance degradada (latency +50%)
- UI bugs afetando UX

**Response Time:** 4 horas  
**Resolution Target:** 24 horas  
**Notification:** Ticket tracking

---

### P3 - Low
**Impact:** Issues menores, workarounds disponíveis  
**Examples:**
- Typos em UI
- Minor visual glitches
- Non-critical feature bugs

**Response Time:** 24 horas  
**Resolution Target:** 7 dias  
**Notification:** Ticket tracking

---

## 🔄 Incident Lifecycle

```
Detect → Log → Classify → Investigate → Resolve → Close → Review
```

### 1. Detection
**Sources:**
- Monitoring alerts (Sentry, Render)
- User reports (GitHub Issues, email)
- Team discovery
- Health checks

**Action:** Log incident immediately

---

### 2. Logging
**Create incident ticket:**

```markdown
# INC-YYYY-NNN: [Título]

## Severity
- [ ] P0 - Critical
- [ ] P1 - High
- [ ] P2 - Medium
- [ ] P3 - Low

## Description
[Clear description of the issue]

## Impact
- Users affected: [All / Specific / None]
- Services affected: [API / Frontend / DB / etc]
- Started: [Timestamp]

## Steps to Reproduce
1. ...

## Error Messages
```
[Paste errors/logs]
```

## Assigned To
[Name]

## Status
- [ ] New
- [ ] Investigating
- [ ] In Progress
- [ ] Resolved
- [ ] Closed
```

**Location:** `docs/operations/incidents/INC-YYYY-NNN.md`

---

### 3. Classification
**Assess:**
- Severity (P0-P3)
- Urgency
- Impact
- Root cause (initial hypothesis)

**Assign:** Based on expertise

---

### 4. Investigation
**Diagnose root cause:**

**Tools:**
- Sentry (errors)
- Render logs
- Supabase logs
- GitHub commit history
- Health check detailed

**Document findings** in incident ticket

---

### 5. Resolution
**Fix options:**
1. **Quick fix** (workaround)
2. **Hotfix** (code change)
3. **Rollback** (revert deploy)
4. **Configuration change**

**Emergency Change Process:**
- P0/P1: Deploy immediately, review after
- P2/P3: Follow normal change management

**Validation:** Test fix works

---

### 6. Closure
**Before closing:**
- [ ] Issue resolved
- [ ] Users notified
- [ ] Documentation updated
- [ ] Monitoring confirms stability
- [ ] Post-mortem scheduled (P0/P1)

---

### 7. Post-Mortem Review
**For P0 and P1 incidents:**

**Template:** `docs/operations/incidents/post-mortems/PM-YYYY-NNN.md`

```markdown
# Post-Mortem: INC-YYYY-NNN

## Incident Summary
[One paragraph summary]

## Timeline
- **Detection:** YYYY-MM-DD HH:MM
- **Response:** YYYY-MM-DD HH:MM
- **Resolution:** YYYY-MM-DD HH:MM
- **Duration:** X hours

## Root Cause
[Technical root cause]

## What Went Well
- ...

## What Went Wrong
- ...

## Action Items
- [ ] [Action] - [Owner] - [Due Date]
- [ ] [Action] - [Owner] - [Due Date]

## Lessons Learned
[Key takeaways]
```

---

## 🚨 Escalation Matrix

| Severity | L1 (First Response) | L2 (Technical) | L3 (Architecture) |
|----------|---------------------|----------------|-------------------|
| **P0** | On-call → Tech Lead | Tech Lead | CTO/Architect |
| **P1** | On-call → Dev | Tech Lead | - |
| **P2** | Dev | Tech Lead (if needed) | - |
| **P3** | Dev | - | - |

**Escalation Time:**
- P0: 30 min if no progress
- P1: 2h if no progress
- P2/P3: As needed

---

## 📞 Communication

### Internal
**P0/P1:**
- Slack #incidents channel
- Status updates every 30 min (P0) or 1h (P1)

**P2/P3:**
- GitHub Issues

### External (Users)
**P0:**
- Status page update
- Email notification

**P1:**
- Status page update

**P2/P3:**
- None (unless requested)

---

## 📚 Runbooks

Common incident scenarios com procedimentos detalhados:

### API Down
**Runbook:** `docs/operations/runbooks/api-down.md`
1. Check health endpoint
2. Review Render logs
3. Check database connection
4. Rollback if recent deploy
5. Notify users

### Database Issues
**Runbook:** `docs/operations/runbooks/database-issues.md`
1. Check Supabase status
2. Review query performance
3. Check connection pool
4. Restart if needed
5. Restore from backup (if corrupted)

### External API Failure
**Runbook:** `docs/operations/runbooks/external-api-failure.md`
1. Verify which API (Shopee/ML/Telegram)
2. Check their status page
3. Implement fallback
4. Cache responses
5. Notify users

More runbooks: `docs/operations/runbooks/`

---

## 📊 Metrics

### Response Metrics
- **MTTD** (Mean Time To Detect): < 5 min
- **MTTA** (Mean Time To Acknowledge): Per severity SLA
- **MTTR** (Mean Time To Resolve): Per severity SLA

### Incident Metrics
- Incident count by severity
- Resolution time trend
- Repeat incidents (same root cause)
- Post-mortem action item closure rate

**Dashboard:** [TBD - Setup monitoring dashboard]

---

## ✅ Best Practices

### During Incident
- ✅ Stay calm
- ✅ Communicate clearly and often
- ✅ Document everything
- ✅ Focus on resolution, not blame
- ✅ Follow runbooks

### After Incident
- ✅ Blameless post-mortem
- ✅ Action items with owners
- ✅ Update runbooks
- ✅ Share learnings

---

## 🔗 Related Processes
- [Change Management](../governance/processes/change-management.md)
- [Disaster Recovery](disaster-recovery.md)
- [Security Policy](../governance/policies/security-policy.md)

---

**Aprovado por:** [Pending]  
**Próxima revisão:** Trimestral
