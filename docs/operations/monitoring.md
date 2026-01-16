# Monitoring Guide

**Framework:** ITIL 4 Deliver & Support + SRE  
**Versão:** 1.0.0  
**Atualizado:** 2026-01-16

---

## 🎯 Objetivo

Garantir observability completa do sistema com monitoring proativo.

---

## 📊 Níveis de Monitoring

### 1. Infrastructure (Infraestrutura)
**O que:** Servidores, rede, storage  
**Ferramentas:** Render metrics, Supabase dashboard  
**Métricas:**
- CPU usage (< 80%)
- Memory usage (< 85%)
- Disk usage (< 90%)
- Network I/O

### 2. Application (Aplicação)
**O que:** API, services, handlers  
**Ferramentas:** APM (Datadog/New Relic recomendado), Sentry  
**Métricas:**
- Request rate (RPM)
- Latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Throughput

### 3. Business (Negócio)
**O que:** KPIs de negócio  
**Endpoints:** `/api/metrics/business`  
**Métricas:**
- Total products
- Active products %
- Products by store
- High commission products
- Health score

---

## 🔍 Endpoints de Métricas

### Business Metrics
```bash
GET /api/metrics/business
```

**Response:**
```json
{
  "timestamp": "2026-01-16T00:00:00Z",
  "products": {
    "total": 1250,
    "active": 1100,
    "inactive": 150,
    "by_store": {
      "shopee": 700,
      "mercado_livre": 550
    },
    "high_commission_count": 420
  },
  "health_score": 88.0
}
```

### Performance Metrics
```bash
GET /api/metrics/performance
```

**Response:**
```json
{
  "api": {
    "latency_p50_ms": 120,
    "latency_p95_ms": 450,
    "latency_p99_ms": 890,
    "request_rate_rpm": 150,
    "error_rate_percent": 0.3
  },
  "database": {
    "query_time_avg_ms": 45,
    "connection_pool_usage_percent": 65
  }
}
```

### SLO Metrics
```bash
GET /api/metrics/slo
```

**Response:**
```json
{
  "slos": {
    "availability": {
      "target": 99.5,
      "current": 99.9,
      "status": "meeting"
    },
    "latency_p95": {
      "target_ms": 500,
      "current_ms": 320,
      "status": "meeting"
    }
  },
  "error_budget": {
    "availability_remaining_hours": 3.2,
    "consumed_percent": 11
  }
}
```

---

## 📈 Dashboards

### Operational Dashboard
**URL:** [Configure in monitoring tool]

**Panels:**
1. **Health Status** - Overall health (Green/Yellow/Red)
2. **API Latency** - p50, p95, p99 (time series)
3. **Error Rate** - 4xx, 5xx (time series)
4. **Request Rate** - RPM (gauge)
5. **Uptime** - Current uptime % (gauge)

### Business Dashboard
**URL:** [Configure in BI tool]

**Panels:**
1. **Total Products** - Count (big number)
2. **Active Products** - % active (pie chart)
3. **Products by Store** - Shopee vs ML (bar chart)
4. **Commission Trend** - 30 days (line chart)
5. **Top 10 Products** - By commission (table)

---

## 🚨 Alerting

Ver [alerting.md](alerting.md) para políticas de alertas.

---

## 🔧 Setup

### 1. Structured Logging
```python
from afiliadohub.api.utils.structured_logger import get_logger

logger = get_logger(__name__)
logger.info("User login", context={"user_id": 123})
```

### 2. APM Integration (Recomendado)
**Datadog:**
```bash
# Install
pip install ddtrace

# Run
ddtrace-run python main.py
```

**New Relic:**
```bash
# Install
pip install newrelic

# Run
newrelic-admin run-program python main.py
```

### 3. Metrics Collection
Endpoints já configurados em `/api/metrics/*`

---

## 📊 SLAs/SLOs

Ver [sla-slo.md](sla-slo.md) para definições completas.

**Quick Reference:**
- **Availability:** 99.5% uptime
- **Latency p95:** < 500ms
- **Error Rate:** < 1% (5xx)

---

## 🔗 Related Docs
- [Alerting](alerting.md)
- [SLA/SLO](sla-slo.md)
- [Dashboards](dashboards.md)
- [Incident Management](../governance/processes/incident-management.md)

---

**Aprovado por:** [Pending]  
**Próxima revisão:** Trimestral
