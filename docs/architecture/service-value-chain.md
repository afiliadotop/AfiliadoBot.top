# Service Value Chain - Mapeamento ITIL 4

## 🔄 ITIL 4 Service Value Chain

```
┌──────────────────────────────────────────────────────────────┐
│                   GUIDING PRINCIPLES                          │
│  • Focus on value  • Start where you are  • Progress it      │
│  • Collaborate  • Think holistically  • Keep it simple       │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                  SERVICE VALUE CHAIN                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   Plan ──▶ Improve ──▶ Engage ──▶ Design & Transition ──▶  │
│                                                               │
│   ──▶ Obtain/Build ──▶ Deliver & Support ──▶                │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    GOVERNANCE                                 │
│              (Evaluation, Direction, Monitoring)              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Atividades do Service Value Chain

### 1. Plan (Planejar)
**Objetivo:** Criar entendimento compartilhado de visão, status e melhoria

**No AfiliadoBot:**

| Atividade | Componente | Responsável |
|-----------|------------|-------------|
| **Product Roadmap** | `docs/roadmap.md` | Product Owner |
| **Architecture Planning** | `docs/architecture/` | Tech Lead |
| **Capacity Planning** | Render metrics review | DevOps |
| **Risk Assessment** | `docs/governance/risk-register.md` | Security Lead |

**Artefatos:**
- Roadmap trimestral
- Architecture Decision Records (ADRs)
- Capacity forecasts
- Risk register

---

### 2. Improve (Melhorar)
**Objetivo:** Melhoria contínua de produtos, serviços e práticas

**No AfiliadoBot:**

| Atividade | Componente | Frequência |
|-----------|------------|------------|
| **Post-Mortems** | `docs/operations/incidents/post-mortems/` | Após incidentes |
| **Retrospectivas** | Sprint reviews | Quinzenal |
| **Code Reviews** | GitHub Pull Requests | Contínuo |
| **Performance Optimization** | Profiling, benchmarks | Mensal |
| **Security Audits** | Dependabot, Snyk | Semanal |

**Métricas:**
- Lead time for changes
- Deployment frequency
- Change failure rate
- Time to restore service (MTTR)

---

### 3. Engage (Engajar)
**Objetivo:** Entender necessidades dos stakeholders e promover engajamento

**No AfiliadoBot:**

| Stakeholder | Interface | Componente |
|-------------|-----------|------------|
| **Usuários Finais** | Web Frontend | `afiliadohub-nextjs/` |
| **Desenvolvedores** | API REST | `api/handlers/` |
| **Administradores** | Admin Panel | `afiliadohub-nextjs/admin/` |
| **Integradores** | API Docs | `docs/api/` |

**Touchpoints:**
- Website/App
- API endpoints
- Documentation
- Support (GitHub Issues)
- Telegram bot

---

### 4. Design & Transition (Desenhar e Transicionar)
**Objetivo:** Garantir produtos/serviços atendem expectativas de qualidade

**No AfiliadoBot:**

| Fase | Atividade | Output |
|------|-----------|--------|
| **Design** | Architecture design | ADRs, diagrams |
| **Development** | Coding, testing | Code, tests |
| **Testing** | Unit, integration, E2E | Test reports |
| **Transition** | Deployment | Release notes |

**Práticas:**
- Design patterns (Repository, Service Layer)
- Code reviews obrigatórios
- Automated testing (CI)
- Staging environment
- Progressive rollout

**Localização:**
- `docs/architecture/patterns.md`
- `scripts/testing/`
- `.github/workflows/`

---

### 5. Obtain/Build (Obter/Construir)
**Objetivo:** Componentes e serviços disponíveis quando necessário

**No AfiliadoBot:**

| Categoria | Componente | Origem |
|-----------|------------|--------|
| **External Services** | Shopee API | Obtido (API externa) |
| **External Services** | MercadoLivre API | Obtido (API externa) |
| **External Services** | Telegram Bot API | Obtido (API externa) |
| **External Services** | Supabase | Obtido (SaaS) |
| **Internal** | Backend API | Construído |
| **Internal** | Frontend | Construído |
| **Internal** | Scripts | Construído |

**Build Pipeline:**
```
Code → Lint → Test → Build → Package → Deploy
```

**Ferramentas:**
- Python/pip (backend)
- Node/npm (frontend)
- Docker (containerização)
- GitHub Actions (CI/CD)

**Localização:**
- `afiliadohub/` (backend build)
- `afiliadohub-nextjs/` (frontend build)
- `scripts/` (automation)

---

### 6. Deliver & Support (Entregar e Suportar)
**Objetivo:** Serviços entregues e suportados conforme acordado

**No AfiliadoBot:**

#### Delivery (Entrega)

| Serviço | Plataforma | SLA |
|---------|------------|-----|
| **Backend API** | Render | 99.5% uptime |
| **Frontend** | Vercel | 99.9% uptime |
| **Database** | Supabase | 99.9% uptime |
| **Telegram Bot** | Render | Best effort |

#### Support (Suporte)

| Nível | Responsabilidade | Response Time |
|-------|------------------|---------------|
| **L1** | GitHub Issues | < 24h |
| **L2** | Bug fixes | < 48h |
| **L3** | Architecture changes | < 1 semana |

**Práticas:**
- Monitoring (Sentry, Render metrics)
- Alerting (erros críticos)
- Incident management (runbooks)
- On-call rotation (futuro)

**Localização:**
- `docs/operations/runbooks/`
- `docs/operations/monitoring.md`
- Sentry dashboard

---

## 🗺️ Mapeamento Completo de Componentes

### Backend (`afiliadohub/api/`)

| Componente | Atividade ITIL | Descrição |
|------------|----------------|-----------|
| `handlers/` | **Engage** | API endpoints (interface externa) |
| `utils/` | **Support** | Utilities, helpers |
| `middleware/` | **Support** | CORS, auth, logging |
| `index.py` | **Deliver** | Main application |
| Tests | **Design & Transition** | Quality assurance |

### Frontend (`afiliadohub-nextjs/`)

| Componente | Atividade ITIL | Descrição |
|------------|----------------|-----------|
| `app/` | **Engage** | User interface |
| `components/` | **Design** | UI components |
| `lib/` | **Obtain/Build** | Client libraries |
| `public/` | **Deliver** | Static assets |

### Scripts (`scripts/`)

| Pasta | Atividade ITIL | Descrição |
|-------|----------------|-----------|
| `production/` | **Deliver** | Serviços em produção |
| `operations/` | **Support** | Operações administrativas |
| `testing/` | **Design & Transition** | Testes e QA |
| `deployment/` | **Deliver** | CI/CD, deploy |
| `auth/` | **Obtain** | OAuth, tokens |
| `development/` | **Improve** | Ferramentas dev |

### Documentação (`docs/`)

| Pasta | Atividade ITIL | Descrição |
|-------|----------------|-----------|
| `architecture/` | **Plan** | Design do sistema |
| `api/` | **Engage** | Interface docs |
| `operations/` | **Support** | Runbooks, monitoring |
| `governance/` | **Plan** | Políticas, processos |

---

## 🎯 Flows Principais Mapeados

### 1. Feature Development Flow

```
Plan → Design → Build → Test → Deploy → Support

1. Roadmap (Plan)
2. Architecture design (Design)
3. Code implementation (Build)
4. Automated tests (Transition)
5. CI/CD deploy (Deliver)
6. Monitoring & incidents (Support)
7. Retrospective (Improve)
```

### 2. Incident Management Flow

```
Detect → Respond → Resolve → Review → Improve

1. Monitoring alerts (Support)
2. Runbook execution (Support)
3. Fix deployed (Deliver)
4. Post-mortem (Improve)
5. Update runbooks (Improve)
```

### 3. Change Management Flow

```
Request → Assess → Approve → Implement → Review

1. RFC created (Plan)
2. Impact analysis (Plan)
3. CAB approval (Governance)
4. Implementation (Deliver)
5. Post-implementation review (Improve)
```

---

## 📊 Métricas por Atividade

### Plan
- Roadmap items completed vs planned
- Architecture decisions made
- Risks identified and mitigated

### Improve
- Incidents with post-mortems
- Improvement actions closed
- Code coverage trend

### Engage
- API usage (requests/day)
- User feedback responses
- Documentation page views

### Design & Transition
- Test coverage %
- Build success rate
- Deployment frequency

### Obtain/Build
- Dependency updates
- Build time
- Artifact size

### Deliver & Support
- Uptime %
- MTTR (Mean Time To Repair)
- Incident count

---

**Versão:** 2.0.0  
**Framework:** ITIL 4  
**Atualizado:** 2026-01-16
