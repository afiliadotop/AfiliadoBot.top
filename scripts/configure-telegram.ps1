# Script para configurar Telegram no .env
# Adiciona as variáveis necessárias para o envio de produtos ao Telegram

$envFile = "c:\ProjetoAfiliadoTop\.env"
$botToken = "7436127848:AAE4a_W_OMRribiXe0NKFsQfNslNgchTMnw"
$channelId = "-1002499912192"

Write-Host "🤖 Configurando Telegram..." -ForegroundColor Cyan

# Lê o arquivo .env atual
$content = Get-Content $envFile -Raw -ErrorAction SilentlyContinue

# Remove configurações antigas do Telegram se existirem
$content = $content -replace "TELEGRAM_BOT_TOKEN=.*\r?\n?", ""
$content = $content -replace "TELEGRAM_CHANNEL_ID=.*\r?\n?", ""

# Adiciona as novas configurações
$telegramConfig = @"

# Telegram Configuration
TELEGRAM_BOT_TOKEN=$botToken
TELEGRAM_CHANNEL_ID=$channelId
"@

$content = $content.TrimEnd() + $telegramConfig

# Salva o arquivo
Set-Content -Path $envFile -Value $content -NoNewline

Write-Host "✅ Telegram configurado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configurações adicionadas:" -ForegroundColor Yellow
Write-Host "  Bot Token: $botToken" -ForegroundColor White
Write-Host "  Channel ID: $channelId" -ForegroundColor White
Write-Host "  Canal: @cupomedescont0" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Reinicie o backend para aplicar as mudanças!" -ForegroundColor Red
Write-Host ""
