# AfiliadoBot - Documentação

[![ITIL 4](https://img.shields.io/badge/ITIL-4-blue.svg)](https://www.axelos.com/best-practice-solutions/itil)
[![Governança](https://img.shields.io/badge/Governance-COBIT-green.svg)](https://www.isaca.org/resources/cobit)

Documentação oficial do sistema AfiliadoBot, organizada segundo framework **ITIL 4 Service Value Chain** e **Governança de TI**.

---

## 📚 Índice

### 🏗️ Arquitetura
- [Visão Geral](architecture/overview.md)
- [Service Value Chain](architecture/service-value-chain.md)
- [Fluxo de Dados](architecture/data-flow.md)
- [Padrões de Design](architecture/patterns.md)

### 🔌 API
- [Documentação API](api/endpoints.md)
- [OpenAPI/Swagger](api/openapi.yaml)
- [Guia de Integração](api/integration-guide.md)

### 🔧 Operações
- [Runbooks](operations/runbooks/)
- [Incident Management](operations/incidents/)
- [Monitoring](operations/monitoring.md)
- [Deployment](operations/deployment.md)

### 🏛️ Governança
- [Políticas](governance/policies/)
- [Padrões](governance/standards/)
- [Processos](governance/processes/)
- [Papéis e Responsabilidades](governance/roles.md)

### 🔒 Compliance
- [LGPD](compliance/lgpd/)
- [Segurança](compliance/security/)
- [Auditoria](compliance/audit-trail.md)

### 👥 Guias de Usuário
- [Primeiros Passos](user-guides/getting-started.md)
- [Como Usar a API](user-guides/api-usage.md)
- [FAQ](user-guides/faq.md)

---

## 🚀 Quick Start

### Para Desenvolvedores
1. Leia [Arquitetura - Visão Geral](architecture/overview.md)
2. Configure ambiente: [Getting Started](user-guides/getting-started.md)
3. Consulte [Padrões de Código](governance/standards/coding-standards.md)

### Para Operações
1. Veja [Deployment Guide](operations/deployment.md)
2. Configure monitoring: [Monitoring Setup](operations/monitoring.md)
3. Consulte [Runbooks](operations/runbooks/) para incidentes

### Para Gestão
1. [Service Value Chain](architecture/service-value-chain.md)
2. [Governança e Processos](governance/)
3. [Métricas e KPIs](operations/monitoring.md)

---

## 📊 Service Value Chain (ITIL 4)

```
┌─────────────────────────────────────────────────┐
│               SERVICE VALUE CHAIN                │
├─────────────────────────────────────────────────┤
│  Plan → Improve → Engage → Design & Transition │
│  → Obtain/Build → Deliver & Support            │
└─────────────────────────────────────────────────┘
```

Todas as atividades do projeto são mapeadas para o Service Value Chain do ITIL 4.

---

## 🔄 Melhoria Contínua

Este é um documento vivo. Contribuições e melhorias são bem-vindas:

1. Identifique lacunas na documentação
2. Sugira melhorias via Issues
3. Contribua via Pull Requests
4. Siga [Processo de Change Management](governance/processes/change-management.md)

---

## 📞 Suporte

- **Issues**: GitHub Issues
- **Docs**: Este repositório
- **Contato**: Ver [Support Policy](governance/policies/support-policy.md)

---

**Versão:** 2.0.0  
**Última atualização:** 2026-01-16  
**Framework:** ITIL 4 + COBIT
