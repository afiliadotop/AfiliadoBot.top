# Authentication Scripts

**ITIL Activity:** Obtain/Build  
**Criticidade:** 🟠 ALTA - OAuth e tokens

---

## Scripts Consolidados

### ml_oauth.py ✨ NOVO
**Substitui:** ml_oauth_simple.py, ml_oauth_pkce.py, ml_oauth_server.py, ml_first_auth.py  
**Propósito:** OAuth MercadoLivre consolidado (PKCE, Simple, Server)

```bash
# OAuth simples
python scripts/auth/ml_oauth.py --mode simple

# OAuth PKCE (recomendado)
python scripts/auth/ml_oauth.py --mode pkce

# OAuth com servidor callback
python scripts/auth/ml_oauth.py --mode server --port 8080
```

---

## Utilitários

### verify_token.py
Verifica validade de tokens

```bash
python scripts/auth/verify_token.py
```

### generate_test_token.py
⚠️ **USO INTERNO** - Gera tokens de teste

```bash
python scripts/auth/generate_test_token.py
```

### get_ml_token.py
Obtém token MercadoLivre

```bash
python scripts/auth/get_ml_token.py
```

---

## Segurança

- ✅ Nunca hardcode tokens
- ✅ Use `.env` para credenciais
- ✅ Tokens teste NÃO funcionam em produção
- ⚠️ Revogue tokens comprometidos imediatamente

---

**Nota:** Scripts legados OAuth (ml_oauth_*) serão removidos após consolidação.
