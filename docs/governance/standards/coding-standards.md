# Coding Standards

## 🎯 Objetivo

Garantir qualidade, consistência e manutenibilidade através de padrões de código uniformes.

---

## 🐍 Python Standards

### Style Guide: PEP 8 + Extensions

#### Formatação
- **Tool:** `black` (line length: 100)
- **Imports:** `isort` (automatic sorting)
- **Linting:** `flake8`
- **Type checking:** `mypy` (gradual adoption)

```python
# BOM ✅
from typing import Optional, List
import os

def calculate_commission(
    price: float,
    rate: float,
    discount: Optional[float] = None
) -> float:
    """Calcula comissão sobre preço.
    
    Args:
        price: Preço do produto
        rate: Taxa de comissão (0-100)
        discount: Desconto opcional
        
    Returns:
        Valor da comissão
    """
    if discount:
        price = price * (1 - discount / 100)
    return price * (rate / 100)
```

#### Naming Conventions

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Variáveis | snake_case | `user_id`, `product_name` |
| Funções | snake_case | `get_products()`, `send_to_telegram()` |
| Classes | PascalCase | `ProductRepository`, `ShopeeClient` |
| Constantes | UPPER_SNAKE | `MAX_RETRIES`, `API_TIMEOUT` |
| Privados | _prefixed | `_internal_method()` |

#### Docstrings
- **Style:** Google format
- **Required:** All public functions/classes
- **Include:** Args, Returns, Raises

```python
def import_products(file_path: str, batch_size: int = 100) -> dict:
    """Importa produtos de arquivo CSV em batches.
    
    Args:
        file_path: Caminho para arquivo CSV
        batch_size: Tamanho do batch para processamento
        
    Returns:
        Dict com estatísticas de importação:
            - total: produtos processados
            - success: importações bem-sucedidas
            - errors: erros encontrados
            
    Raises:
        FileNotFoundError: Se arquivo não existe
        ValueError: Se formato CSV inválido
    """
    ...
```

---

## ⚛️ TypeScript/React Standards

### Style Guide: Airbnb + Extensions

#### Formatação
- **Tool:** `prettier` (2 spaces, single quotes)
- **Linting:** `eslint` (airbnb config)

```typescript
// BOM ✅
import { useState, useEffect } from 'react';
import type { Product } from '@/types';

interface ProductCardProps {
  product: Product;
  onSelect?: (id: string) => void;
}

export function ProductCard({ product, onSelect }: ProductCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleClick = () => {
    if (onSelect) {
      setIsLoading(true);
      onSelect(product.id);
    }
  };
  
  return (
    <div className="product-card" onClick={handleClick}>
      <h3>{product.name}</h3>
      <p>R$ {product.price.toFixed(2)}</p>
    </div>
  );
}
```

#### Naming Conventions

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Variáveis | camelCase | `userId`, `productList` |
| Funções | camelCase | `getProduct()`, `handleSubmit()` |
| Components | PascalCase | `ProductCard`, `LoginForm` |
| Types/Interfaces | PascalCase | `Product`, `UserData` |
| Constants | UPPER_SNAKE | `API_BASE_URL` |

#### Component Structure
```tsx
// 1. Imports
import { useState } from 'react';

// 2. Types
interface Props {...}

// 3. Component
export function Component({ prop }: Props) {
  // 3.1. Hooks
  const [state, setState] = useState();
  
  // 3.2. Functions
  const handleAction = () => {...};
  
  // 3.3. Effects
  useEffect(() => {...}, []);
  
  // 3.4. Render
  return <div>...</div>;
}
```

---

## 🗄️ Database Standards

### Naming Conventions

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Tables | snake_case (plural) | `products`, `user_sessions` |
| Columns | snake_case | `created_at`, `user_id` |
| Foreign Keys | `{table}_id` | `store_id`, `category_id` |
| Indexes | `idx_{table}_{columns}` | `idx_products_store_id` |
| Constraints | `{table}_{column}_{type}` | `products_price_check` |

### SQL Style
```sql
-- BOM ✅
SELECT
    p.id,
    p.name,
    p.price,
    s.name AS store_name
FROM products p
INNER JOIN stores s ON p.store_id = s.id
WHERE p.active = TRUE
    AND p.price > 10.00
ORDER BY p.created_at DESC
LIMIT 100;
```

### Migrations
- **Tool:** Supabase migrations
- **Naming:** `YYYYMMDDHHMMSS_description.sql`
- **Practice:** Always reversible (up/down)

---

## 📋 Git Workflow

### Commit Messages (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação (não afeta código)
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

**Examples:**
```
feat(shopee): add product filtering by commission rate

fix(telegram): resolve bot timeout on large messages

docs(api): update endpoint documentation for /products

refactor(auth): extract OAuth logic to service layer
```

### Branch Strategy

```
main (production)
  │
  ├── develop (integration)
  │    │
  │    ├── feature/shopee-filters
  │    ├── feature/telegram-improvements
  │    └── bugfix/api-timeout
  │
  └── hotfix/critical-security-fix
```

**Naming:**
- `feature/description`
- `bugfix/description`
- `hotfix/description`
- `docs/description`

---

## ✅ Code Review Checklist

### Antes de PR

- [ ] Código segue standards (lint pass)
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Commit messages claros
- [ ] Sem secrets hardcoded

### Review Checklist

- [ ] **Funcionalidade:** Código faz o que deveria?
- [ ] **Design:** Boa arquitetura? Patterns corretos?
- [ ] **Complexidade:** Simples e legível?
- [ ] **Testes:** Coverage adequado?
- [ ] **Naming:** Nomes claros e consistentes?
- [ ] **Documentação:** Docstrings/comments adequados?
- [ ] **Segurança:** Sem vulnerabilidades?
- [ ] **Performance:** Sem problemas óbvios?

---

## 🔍 Static Analysis

### Automated Tools

#### Python
```bash
# Formatting
black afiliadohub/
isort afiliadohub/

# Linting
flake8 afiliadohub/
pylint afiliadohub/

# Type checking
mypy afiliadohub/

# Security
bandit -r afiliadohub/
```

#### TypeScript
```bash
# Formatting
prettier --write "**/*.{ts,tsx}"

# Linting
eslint "**/*.{ts,tsx}"

# Type checking
tsc --noEmit
```

#### SQL
```bash
# Linting
sqlfluff lint migrations/
```

---

## 📊 Code Quality Metrics

### Targets

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | > 80% | - |
| Cyclomatic Complexity | < 10 | - |
| Code Duplication | < 5% | - |
| Lint Pass Rate | 100% | - |
| Type Coverage (mypy) | > 70% | - |

---

## 🚫 Anti-Patterns to Avoid

### General
- ❌ Magic numbers (use constants)
- ❌ Deep nesting (> 3 levels)
- ❌ Long functions (> 50 lines)
- ❌ God objects (too many responsibilities)
- ❌ Premature optimization

### Python
- ❌ Mutable default arguments
- ❌ Bare `except:` clauses
- ❌ Global variables
- ❌ `import *`

### TypeScript/React
- ❌ Props drilling (use context/state management)
- ❌ Huge components (split)
- ❌ Missing key props in lists
- ❌ Side effects in render

---

## 📚 Resources

- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Versão:** 1.0.0  
**Atualizado:** 2026-01-16
