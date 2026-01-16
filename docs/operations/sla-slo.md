# SLA & SLO Definitions

**Framework:** SRE Best Practices  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Conceitos

**SLA (Service Level Agreement):**  
Acordo formal com usuários sobre nível de serviço esperado.

**SLO (Service Level Objective):**  
Objetivo interno de performance/reliability.

**SLI (Service Level Indicator):**  
Métrica específica medida (latency, uptime, etc).

**Error Budget:**  
Quantidade de downtime/errors permitida pelo SLA.

---

## 📊 SLAs Definidos

### API Availability
**SLA:** 99.5% uptime mensal  
**Medição:** Mensal (último dia do mês)  
**Downtime permitido:** ~3.6 horas/mês  
**Penalidade:** N/A (interno)

**Cálculo:**
```
Uptime % = (Total time - Downtime) / Total time * 100
```

**Exclusões (não conta como downtime):**
- Manutenção programada (com 7 dias aviso)
- Problemas de terceiros (Supabase, Render)
- Force majeure

---

### API Response Time
**SLA:** p95 latency < 1000ms  
**Medição:** Semanal (média)  
**Endpoints:** Todos `/api/*`  
**Penalidade:** N/A (interno)

**Nota:** Exclui:
- Uploads de arquivos
- Requests > 10MB
- Timeouts de cliente

---

## 🎯 SLOs Internos

### Availability SLO
**Target:** 99.9% uptime  
**SLI:** Health check success rate  
**Measurement:** 5 min intervals  
**Error Budget:** ~43 min/mês

**Status:** Meeting (atual 99.95%)

---

### Latency SLO
**Target:** p95 < 500ms  
**SLI:** API response time (p95)  
**Measurement:** Real-time (APM)  
**Threshold:** 500ms

**Current:** ~320ms (Meeting)

---

### Error Rate SLO
**Target:** < 1% (5xx errors)  
**SLI:** Ratio of 5xx/total requests  
**Measurement:** Real-time (APM)  
**Threshold:** 1%

**Current:** ~0.3% (Meeting)

---

### Data Freshness SLO
**Target:** Products updated within 24h  
**SLI:** Time since last product update  
**Measurement:** Daily check  
**Threshold:** 24 hours

**Current:** ~6h (Meeting)

---

## 📉 Error Budget

### Calculation
```
Error Budget = (1 - SLO) * Total Time

Example (Availability):
SLO = 99.9%
Total Time = 30 days
Error Budget = (1 - 0.999) * 30 days * 24h = 0.72 hours
```

### Consumption Tracking
**Monthly Report:**
- Budget total: 43 min
- Consumed: 5 min (11%)
- Remaining: 38 min (89%)
- Status: Healthy

**Quarterly Review:**
- Budget total: 2.16 hours
- Consumed: 0.5 hours (23%)
- Remaining: 1.66 hours (77%)
- Status: Healthy

---

## 🚨 Error Budget Policy

### When Budget < 25%
**Action:** Alert team  
**Response:** Review incidents, prioritize reliability

### When Budget Exhausted
**Action:** Freeze non-critical deploys  
**Response:** Focus 100% on reliability until budget recovers

**Exception:** Security patches (always allowed)

---

## 📊 Monitoring

### Dashboard
**URL:** `/api/metrics/slo`

**Panels:**
1. Availability (gauge)
2. Latency p95 (time series)
3. Error rate (time series)
4. Error budget remaining (gauge)

### Alerts
**Trigger:** SLO at risk (< 80% of target for 1h)  
**Action:** Notify team, investigate

---

## 📋 Reporting

### Weekly
- SLO compliance (meeting/at risk/violated)
- Error budget consumption
- Incidents affecting SLOs

### Monthly
- SLA compliance report
- Error budget summary
- Recommendations for next month

### Quarterly
- SLA/SLO review
- Adjust targets if needed
- Long-term trends

---

## 🔗 Related Docs
- [Monitoring](monitoring.md)
- [Alerting](alerting.md)
- [Incident Management](../governance/processes/incident-management.md)

---

**Aprovado por:** [Pending]  
**Próxima revisão:** Trimestral
