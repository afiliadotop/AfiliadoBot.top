# Alerting Policy

**Framework:** ITIL 4 Incident Management + SRE  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Objetivo

Alerting proativo para detectar e resolver problemas antes de impactar usuários.

---

## 🚨 Alert Rules

### Critical (P0)

#### Rule: API Down
**Condition:** Health check fails for 2+ minutes  
**Alert:** Immediate (PagerDuty/phone)  
**SLA:** 15 min response  
**Action:** Check [runbooks/api-down.md](../operations/runbooks/api-down.md)

#### Rule: Database Unavailable
**Condition:** DB connection fails  
**Alert:** Immediate  
**SLA:** 15 min response  
**Action:** Check [disaster-recovery.md](disaster-recovery.md)

#### Rule: Error Rate Spike
**Condition:** 5xx errors > 5% for 5 min  
**Alert:** Immediate  
**SLA:** 15 min response  
**Action:** Check logs, rollback if recent deploy

---

### High (P1)

#### Rule: High Latency
**Condition:** p95 latency > 1000ms for 10 min  
**Alert:** Slack + Email  
**SLA:** 1 hour response  
**Action:** Investigate slow queries, scale if needed

#### Rule: High Error Rate
**Condition:** 4xx errors > 10% for 15 min  
**Alert:** Slack + Email  
**SLA:** 1 hour response  
**Action:** Check recent changes, validate APIs

---

### Medium (P2)

#### Rule: Disk Space Low
**Condition:** Disk usage > 85%  
**Alert:** Email  
**SLA:** 4 hours response  
**Action:** Clean old logs, scale disk

#### Rule: Memory High
**Condition:** Memory > 90% for 30 min  
**Alert:** Email  
**SLA:** 4 hours response  
**Action:** Check memory leaks, restart if needed

---

### Low (P3)

#### Rule: Health Score Degraded
**Condition:** Health score < 70 for 1 hour  
**Alert:** Email  
**SLA:** 24 hours response  
**Action:** Review inactive products

---

##  Notification Channels

### By Severity
| Severity | Channel | Who |
|----------|---------|-----|
| **P0** | PagerDuty + Phone + Slack | On-call engineer |
| **P1** | Slack #incidents + Email | On-call + Team lead |
| **P2** | Email | Team |
| **P3** | Email | Team |

### Escalation
**P0/P1:** If no response in SLA time, escalate to next level

**Levels:**
1. On-call engineer
2. Team lead
3. Engineering manager
4. CTO

---

## 📋 Alert Response Checklist

### When Alert Fires
- [ ] Acknowledge alert
- [ ] Check severity
- [ ] Review alert details (metric, time, value)
- [ ] Check dashboards for context
- [ ] Follow runbook (if exists)
- [ ] Create incident ticket (P0/P1)
- [ ] Update incident status regularly

### After Resolution
- [ ] Close incident
- [ ] Document root cause
- [ ] Update runbook (if gaps found)
- [ ] Schedule post-mortem (P0/P1)

---

## 🔧 Alert Configuration

### Infrastructure Alerts
**Tool:** Render dashboard  
**Metrics:** CPU, Memory, Disk, Network

### Application Alerts
**Tool:** APM (Datadog/New Relic) + Sentry  
**Metrics:** Latency, Error rate, Request rate

### Business Alerts
**Tool:** Custom (via `/api/metrics`)  
**Metrics:** Health score, Active products %

---

## 📊 Alert Metrics

### Monthly Review
- Total alerts fired
- False positive rate (target < 10%)
- Mean time to acknowledge (MTTA)
- Mean time to resolve (MTTR)
- Alerts by severity

**Goal:** Reduce alert fatigue, improve signal/noise ratio

---

## 🔗 Related Docs
- [Incident Management](../governance/processes/incident-management.md)
- [Runbooks](runbooks/)
- [Monitoring](monitoring.md)
- [SLA/SLO](sla-slo.md)

---

**Aprovado por:** [Pending]  
**Próxima revisão:** Trimestral
