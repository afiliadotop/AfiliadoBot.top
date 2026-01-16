# Script de migração ITIL 4 - Fase 2
# Move arquivos para estrutura ITIL

Write-Host "🔄 Migrando scripts para estrutura ITIL 4..." -ForegroundColor Cyan

# Development
$devScripts = @(
    "explore_shopee_schema.py",
    "introspect_shopee.py",
    "diagnose-cors.ps1",
    "debug_feed.py",
    "fix_imports.py"
)

# Testing
$testScripts = @(
    "system_verification.py",
    "test_feed_manager.py",
    "test_store_cache.py",
    "send_test_message.py",
    "test_bot_enhanced.py",
    "test_rate_limit_scroll.py",
    "test_ml_affiliate.py"
)

# Utils
$utilScripts = @(
    "start-tunnel.ps1",
    "oracle_arm_retry.py"
)

# OAuth ML (para consolidar depois)
$mlOauthScripts = @(
    "ml_oauth_simple.py",
    "ml_oauth_pkce.py",
    "ml_oauth_server.py",
    "ml_first_auth.py"
)

# Shopee tests (para consolidar depois)
$shopeeTestScripts = @(
    "test_shopee_auth.py",
    "test_shopee_complete.py",
    "test_shopee_offers.py",
    "test_shopee_shortlink.py"
)

# Telegram tests (para consolidar depois)  
$telegramTestScripts = @(
    "test_telegram_simple.py",
    "test_telegram_config.py",
    "test_telegram_bot.py"
)

# Shopee imports
$shopeeImportScripts = @(
    "shopee_import_manual.py"
)

Write-Host "`n[1/5] Movendo scripts de desenvolvimento..."
foreach ($script in $devScripts) {
    $src = "scripts\$script"
    if (Test-Path $src) {
        git mv $src "scripts\development\" 2>$null
        if ($?) { Write-Host "  ✓ $script" -ForegroundColor Green }
    }
}

Write-Host "`n[2/5] Movendo scripts de teste..."
foreach ($script in $testScripts) {
    $src = "scripts\$script"
    if (Test-Path $src) {
        git mv $src "scripts\testing\" 2>$null
        if ($?) { Write-Host "  ✓ $script" -ForegroundColor Green }
    }
}

Write-Host "`n[3/5] Movendo utilitários..."
foreach ($script in $utilScripts) {
    $src = "scripts\$script"
    if (Test-Path $src) {
        git mv $src "scripts\utils\" 2>$null
        if ($?) { Write-Host "  ✓ $script" -ForegroundColor Green }
    }
}

Write-Host "`n[4/5] Movendo OAuth ML para consolidação..."
foreach ($script in $mlOauthScripts) {
    $src = "scripts\$script"
    if (Test-Path $src) {
        git mv $src "scripts\auth\" 2>$null
        if ($?) { Write-Host "  ✓ $script" -ForegroundColor Green }
    }
}

Write-Host "`n[5/5] Movendo testes Shopee/Telegram para consolidação..."
foreach ($script in ($shopeeTestScripts + $telegramTestScripts + $shopeeImportScripts)) {
    $src = "scripts\$script"
    if (Test-Path $src) {
        git mv $src "scripts\testing\" 2>$null
        if ($?) { Write-Host "  ✓ $script" -ForegroundColor Green }
    }
}

# Move cleanup-git-history.ps1 (não está no Git ainda)
if (Test-Path "scripts\cleanup-git-history.ps1") {
    Move-Item "scripts\cleanup-git-history.ps1" "scripts\deployment\" -Force
    Write-Host "`n  ✓ cleanup-git-history.ps1 (move simples)" -ForegroundColor Yellow
}

Write-Host "`n✅ Migração concluída!" -ForegroundColor Green
Write-Host "Próximo passo: Consolidar scripts duplicados" -ForegroundColor Cyan
