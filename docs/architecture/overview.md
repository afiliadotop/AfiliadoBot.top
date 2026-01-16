# Visão Geral da Arquitetura

## 🎯 Objetivo do Sistema

O **AfiliadoBot** é uma plataforma de gestão de links de afiliados focada em:
- Agregação de produtos de múltiplas lojas (Shopee, MercadoLivre,...)
- Geração automática de links de afiliado
- Distribuição via Telegram
- Gestão de comissões

---

## 🏗️ Arquitetura Geral

### Visão de Alto Nível

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│   Usuários  │────▶ │   Web Frontend   │────▶ │   Backend   │
│             │      │  (Next.js/React) │      │  (FastAPI)  │
└─────────────┘      └──────────────────┘      └──────┬──────┘
                                                        │
                     ┌──────────────────────────────────┼────────────┐
                     │                                  │            │
                     ▼                                  ▼            ▼
            ┌─────────────────┐              ┌──────────────┐  ┌─────────┐
            │  External APIs  │              │   Supabase   │  │Telegram │
            │ (Shopee, ML)    │              │  (Database)  │  │   Bot   │
            └─────────────────┘              └──────────────┘  └─────────┘
```

---

## 📦 Componentes Principais

### 1. Frontend (Next.js + React)
**Responsabilidade:** Interface do usuário, autenticação, visualização

**Tecnologias:**
- Next.js 14 (App Router)
- React 18
- TailwindCSS
- Sentry (error tracking)

**Localização:** `afiliadohub-nextjs/`

---

### 2. Backend API (FastAPI)
**Responsabilidade:** Lógica de negócio, integração com APIs externas, autenticação

**Tecnologias:**
- Python 3.13
- FastAPI
- Uvicorn
- Supabase Client

**Localização:** `afiliadohub/api/`

**Estrutura:**
```
api/
├── handlers/       # API endpoints (Engage)
├── utils/          # Utilities (Support)
├── index.py        # Main application
└── middleware/     # CORS, auth, etc
```

---

### 3. Banco de Dados (Supabase/PostgreSQL)
**Responsabilidade:** Persistência, autenticação, RLS

**Schema Principal:**
- `users` - Usuários do sistema
- `products` - Catálogo de produtos
- `stores` - Lojas (Shopee, ML, etc)
- `telegram_groups` - Canais Telegram
- `commission_rates` - Taxas de comissão

**Segurança:** Row Level Security (RLS) ativado

---

### 4. Integrações Externas

#### Shopee Affiliate API
- Busca de produtos
- Geração de shortlinks
- Comissões

#### MercadoLivre API
- OAuth 2.0 (PKCE)
- Busca de produtos
- Links de afiliado

#### Telegram Bot
- Envio de produtos
- Gerenciamento de grupos
- Notificações

---

## 🔄 ITIL 4 Service Value Chain

### Mapeamento de Componentes

| Componente | Atividade ITIL | Descrição |
|------------|----------------|-----------|
| Frontend | **Engage** | Interface com usuário |
| API Handlers | **Engage** | Endpoints de API |
| Business Logic | **Deliver & Support** | Serviços core |
| Database | **Obtain/Build** | Dados e persistência |
| External APIs | **Obtain/Build** | Integração externa |
| Scripts | **Plan/Improve** | Automação e testes |
| Monitoring | **Deliver & Support** | Observabilidade |

---

## 🌊 Fluxo de Dados Principal

### 1. Importação de Produtos

```
Shopee/ML API → Backend Handler → Parser/Normalizer 
    → Supabase (products) → Frontend (display)
```

### 2. Geração de Link de Afiliado

```
User Request → Frontend → API /generate-link 
    → External API (Shopee/ML) → Shortlink → Database 
    → Response → User
```

### 3. Envio para Telegram

```
Product Selection → API /send-to-telegram 
    → Telegram Bot API → Channel → Users
```

---

## 🔐 Segurança

### Camadas de Segurança

1. **Autenticação:** Supabase Auth (JWT)
2. **Autorização:** RLS (Row Level Security)
3. **API:** Rate limiting, CORS
4. **Secrets:** Environment variables (.env)
5. **HTTPS:** TLS 1.3 (Render/Vercel)

### Fluxo de Autenticação

```
User Login → Supabase Auth → JWT Token 
    → Frontend (localStorage) → API Requests (Bearer token)
    → Backend validates → RLS enforced → Data
```

---

## 📊 Padrões de Design

### 1. Repository Pattern
Abstração da camada de dados

### 2. Service Layer
Lógica de negócio separada de endpoints

### 3. Dependency Injection
FastAPI dependencies para auth, db

### 4. Factory Pattern
Criação de clientes (Shopee, ML)

Ver: [Padrões de Design](patterns.md)

---

## 🚀 Deploy e Infraestrutura

### Ambientes

| Ambiente | Frontend | Backend | Database |
|----------|----------|---------|----------|
| **Production** | Vercel | Render | Supabase |
| **Staging** | Vercel Preview | - | Supabase Dev |
| **Development** | localhost:3000 | localhost:8000 | Supabase |

### CI/CD

```
Git Push → GitHub Actions → Tests → Build → Deploy
    → Smoke Tests → Monitor
```

---

## 📈 Escalabilidade

### Horizontal Scaling
- Frontend: Edge CDN (Vercel)
- Backend: Auto-scale (Render)
- Database: Supabase managed

### Bottlenecks Identificados
- External API rate limits (Shopee, ML)
- Database connections pool

### Mitigação
- Caching (Redis - futuro)
- Connection pooling
- Rate limiting próprio

---

## 🔍 Observabilidade

### Logs
- Backend: Python logging → stdout
- Frontend: Sentry

### Métricas
- Render metrics (CPU, Memory)
- Supabase dashboard

### Alertas
- Sentry (errors)
- Render (downtime)

---

## 📚 Próximos Passos

1. Ver [Fluxo de Dados Detalhado](data-flow.md)
2. Consultar [Padrões de Design](patterns.md)
3. Entender [Service Value Chain](service-value-chain.md)

---

**Versão:** 2.0.0  
**Atualizado:** 2026-01-16
