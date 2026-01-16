# Deployment Scripts

**ITIL Activity:** Plan & Deliver  
**Criticidade:** 🔴 ALTA - CI/CD e deploy

---

## Scripts

### pre-deploy-tests.ps1 (Windows)
Testes pré-deploy para Windows

```powershell
.\scripts\deployment\pre-deploy-tests.ps1
```

### pre-deploy-tests.sh (Unix/Linux)
Testes pré-deploy para Unix/Linux

```bash
bash scripts/deployment/pre-deploy-tests.sh
```

### cleanup_git_history.ps1
Limpeza de histórico Git (uso especial)

⚠️ **CUIDADO:** Reescreve histórico do Git

---

## Processo de Deploy

1. Rodar testes pré-deploy
2. Validar que tudo passa
3. Executar deploy
4. Monitorar

**Change Management:** Ver CHANGELOG.md para histórico
