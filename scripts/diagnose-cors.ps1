# Script de diagnóstico para problemas de CORS e Autenticação

Write-Host ""
Write-Host "=== Diagnóstico AfiliadoHub ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar backend
Write-Host "1. Verificando Backend (porta 8000)..." -ForegroundColor Yellow
$backend = netstat -ano | findstr :8000
if ($backend) {
    Write-Host "   OK Backend esta rodando" -ForegroundColor Green
} else {
    Write-Host "   ERRO Backend NAO esta rodando!" -ForegroundColor Red
}

# 2. Verificar frontend  
Write-Host ""
Write-Host "2. Verificando Frontend (porta 3000)..." -ForegroundColor Yellow
$frontend = netstat -ano | findstr :3000
if ($frontend) {
    Write-Host "   OK Frontend esta rodando" -ForegroundColor Green
} else {
    Write-Host "   ERRO Frontend NAO esta rodando!" -ForegroundColor Red
}

# 3. Verificar .env
Write-Host ""
Write-Host "3. Verificando configuracao .env..." -ForegroundColor Yellow
$envFiles = @()
if (Test-Path ".env") { $envFiles += ".env" }
if (Test-Path ".env.local") { $envFiles += ".env.local" }

if ($envFiles.Count -eq 0) {
    Write-Host "   INFO Nenhum arquivo .env encontrado" -ForegroundColor Yellow
    Write-Host "   Usando configuracao padrao (BASE_URL = '/api')" -ForegroundColor Gray
} else {
    foreach ($file in $envFiles) {
        Write-Host "   Encontrado: $file" -ForegroundColor Gray
        $content = Get-Content $file | Select-String "VITE_API_URL"
        if ($content) {
            $value = $content -replace ".*=", ""
            if ($value -match "http://localhost:8000" -or $value -match "http://127.0.0.1:8000") {
                Write-Host "   ERRO PROBLEMA ENCONTRADO!" -ForegroundColor Red
                Write-Host "   $content" -ForegroundColor Red
                Write-Host "   Altere para: VITE_API_URL=/api" -ForegroundColor Yellow
            } elseif ($value -match "^/api") {
                Write-Host "   OK Configuracao correta!" -ForegroundColor Green
            } else {
                Write-Host "   AVISO Valor inesperado: $content" -ForegroundColor Yellow
            }
        }
    }
}

# 4. Testar backend
Write-Host ""
Write-Host "4. Testando conexao com backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -ErrorAction Stop
    Write-Host "   OK Backend respondendo!" -ForegroundColor Green
} catch {
    Write-Host "   ERRO Backend nao esta respondendo" -ForegroundColor Red
}

# 5. Testar proxy
if ($frontend) {
    Write-Host ""
    Write-Host "5. Testando proxy do Vite..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/shopee/test" -UseBasicParsing -ErrorAction Stop
        Write-Host "   OK Proxy do Vite funcionando!" -ForegroundColor Green
    } catch {
        Write-Host "   ERRO Proxy do Vite nao esta funcionando" -ForegroundColor Red
        Write-Host "   Dica: Reinicie o Vite apos alterar .env" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Resumo ===" -ForegroundColor Cyan
Write-Host "1. Certifique-se que VITE_API_URL=/api" -ForegroundColor Gray
Write-Host "2. Reinicie o Vite: Ctrl+C e depois 'npm run dev'" -ForegroundColor Gray
Write-Host "3. Faca login na aplicacao" -ForegroundColor Gray
Write-Host "4. Limpe cache do navegador: Ctrl+Shift+R" -ForegroundColor Gray
Write-Host ""
