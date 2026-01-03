# Script para iniciar Backend + Cloudflare Tunnel
# Uso: .\scripts\start-tunnel.ps1

Write-Host "🚀 Iniciando AfiliadoBot Backend + Cloudflare Tunnel..." -ForegroundColor Cyan

# Verificar se cloudflared existe
if (-not (Test-Path ".\cloudflared.exe")) {
    Write-Host "❌ cloudflared.exe não encontrado!" -ForegroundColor Red
    Write-Host "📥 Baixando cloudflared..." -ForegroundColor Yellow
    
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
    
    Write-Host "✅ Download completo!" -ForegroundColor Green
}

# Ativar venv se existir
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Iniciar backend
Write-Host "🔧 Iniciando backend FastAPI..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m uvicorn afiliadohub.api.index:app --host 0.0.0.0 --port 8000" -NoNewWindow

# Aguardar backend iniciar
Write-Host "⏳ Aguardando backend iniciar (5 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar se backend está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 3
    Write-Host "✅ Backend rodando!" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Backend pode não estar pronto ainda..." -ForegroundColor Yellow
}

# Iniciar tunnel
Write-Host "🌐 Iniciando Cloudflare Tunnel..." -ForegroundColor Yellow
Write-Host "📋 A URL do tunnel aparecerá abaixo:" -ForegroundColor Cyan
Write-Host ""

& .\cloudflared.exe tunnel --url http://localhost:8000

# Se o tunnel parar, avisar
Write-Host ""
Write-Host "⚠️  Tunnel encerrado!" -ForegroundColor Red
