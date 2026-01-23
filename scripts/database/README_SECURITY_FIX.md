# Correção de Vulnerabilidades de Segurança

**Data:** 2026-01-22  
**Status:** PRONTO PARA EXECUTAR  
**Classificação:** Emergency Change (P0)

---

## 📋 Checklist de Execução

### Pré-Execução
- [ ] **BACKUP DO BANCO DE DADOS**
  - Ir em Supabase Dashboard > Database > Backups
  - Criar backup manual antes de continuar
  
- [ ] Revisar script SQL: `scripts/database/fix_security_vulnerabilities.sql`
- [ ] Confirmar ambiente correto (Production)

### Execução do Script
- [ ] Ir em Supabase Dashboard > SQL Editor
- [ ] Copiar conteúdo de `fix_security_vulnerabilities.sql`
- [ ] Colar no editor
- [ ] Executar (Run)
- [ ] Verificar mensagens de sucesso

### Migração Manual de Usuários Admin
- [ ] Ir em Authentication > Users
- [ ] Para cada usuário admin (ex: seu email):
  1. Clicar em "Edit user"
  2. Rolar até "Raw App Meta Data"
  3. Adicionar:
     ```json
     {
       "role": "admin"
     }
     ```
  4. Salvar

### Validação
- [ ] Database Linter:
  - Ir em Database > Linter
  - Confirmar **0 erros de segurança**
  
- [ ] Testar login como admin
  - Fazer login
  - Verificar acesso a `telegram_settings`
  - Verificar acesso a `product_feeds`
  
- [ ] Testar login como usuário normal
  - Criar usuário teste
  - Confirmar que NÃO tem acesso a áreas admin
  
- [ ] Verificar RLS:
  ```sql
  SELECT tablename, rowsecurity 
  FROM pg_tables 
  WHERE schemaname = 'public' 
  AND tablename IN ('settings', 'telegram_settings', 'product_feeds');
  ```
  - Todas devem ter `rowsecurity = t` (true)

### Pós-Execução
- [ ] Documentar no CHANGELOG
- [ ] Atualizar Security Incident log
- [ ] Notificar equipe (se houver)
- [ ] Agendar review em 7 dias

---

## 🚨 Em Caso de Problemas

**Se algo der errado:**

1. **Rollback imediato:**
   - Se dentro de transação (BEGIN/COMMIT): executa-se automaticamente
   - Se já commitado: restaurar backup manual

2. **Sintomas comuns:**
   - "Admins não conseguem acessar" → Verificar app_metadata dos usuários
   - "View não funciona" → Verificar permissões na tabela products
   - "RLS bloqueia tudo" → Verificar policies criadas corretamente

3. **Suporte:**
   - Documentação: `docs/governance/policies/security-policy.md`
   - Incident Management: `docs/governance/processes/incident-management.md`

---

## ✅ Critérios de Sucesso

- ✅ Database Linter: 0 erros
- ✅ RLS habilitado em `settings`
- ✅ View sem SECURITY DEFINER
- ✅ Policies usando `app_metadata`
- ✅ Admin login funciona
- ✅ User normal bloqueado

---

## 📊 Antes vs Depois

| Métrica | Antes | Depois |
|---------|-------|--------|
| Vulnerabilidades | 9 | 0 |
| RLS em settings | ❌ | ✅ |
| Policies seguras | ❌ | ✅ |
| Privilege escalation | Possível | Bloqueado |
| Security Score | 50/100 | 95/100 |

---

**Tempo estimado:** 30-45 minutos  
**Risco:** Baixo (com backup)  
**Impacto:** Nenhum downtime
