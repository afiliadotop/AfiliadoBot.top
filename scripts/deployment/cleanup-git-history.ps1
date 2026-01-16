# Script para limpar configure-telegram.ps1 do histórico do Git
# ATENÇÃO: Este script reescreve o histórico do Git

Write-Host "🔥 LIMPANDO HISTÓRICO DO GIT - Token Telegram" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Yellow

# Navegar para o diretório do projeto
Set-Location "c:\ProjetoAfiliadoTop"

Write-Host "`n[1/5] Fazendo backup do repositório..." -ForegroundColor Cyan
$backupPath = "c:\ProjetoAfiliadoTop_BACKUP_" + (Get-Date -Format "yyyyMMdd_HHmmss")
Copy-Item -Path "c:\ProjetoAfiliadoTop\.git" -Destination "$backupPath\.git" -Recurse
Write-Host "      Backup criado em: $backupPath" -ForegroundColor Green

Write-Host "`n[2/5] Removendo configure-telegram.ps1 do histórico..." -ForegroundColor Cyan
git filter-branch --force --index-filter `
  "git rm --cached --ignore-unmatch scripts/configure-telegram.ps1" `
  --prune-empty --tag-name-filter cat -- --all

Write-Host "`n[3/5] Limpando referências antigas..." -ForegroundColor Cyan
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "`n[4/5] Verificando se arquivo foi removido..." -ForegroundColor Cyan
$result = git log --all --full-history --oneline -- scripts/configure-telegram.ps1
if ($result) {
    Write-Host "      ⚠️  AVISO: Arquivo ainda aparece no histórico!" -ForegroundColor Red
} else {
    Write-Host "      ✅ Arquivo removido com sucesso do histórico!" -ForegroundColor Green
}

Write-Host "`n[5/5] PRÓXIMO PASSO (MANUAL):" -ForegroundColor Yellow
Write-Host "      Execute: git push origin --force --all" -ForegroundColor White
Write-Host "      Depois:  git push origin --force --tags" -ForegroundColor White

Write-Host "`n================================================" -ForegroundColor Yellow
Write-Host "⚠️  IMPORTANTE: Revoque o token ANTES do force push!" -ForegroundColor Red
Write-Host "================================================`n" -ForegroundColor Yellow
