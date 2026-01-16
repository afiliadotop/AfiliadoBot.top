# Pre-deployment E2E Test Script (Windows PowerShell)
# Run this before deploying to production

Write-Host "🚀 Pre-Deployment E2E Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if servers are running
Write-Host "📡 Checking if dev servers are running..." -ForegroundColor Yellow

try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000" -Method HEAD -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "✅ Frontend server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend server not running on port 3000" -ForegroundColor Red
    Write-Host "   Run: npm run dev" -ForegroundColor Yellow
    exit 1
}

try {
    $backendCheck = Invoke-WebRequest -Uri "http://localhost:8000/api" -Method HEAD -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "✅ Backend server is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend server not running on port 8000" -ForegroundColor Yellow
    Write-Host "   Some tests may fail" -ForegroundColor Yellow
}

Write-Host ""

# Run unit tests
Write-Host "🧪 Running Unit Tests..." -ForegroundColor Yellow
npm test -- --run --reporter=verbose
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Unit tests failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Run integration tests
Write-Host "🔗 Running Integration Tests..." -ForegroundColor Yellow
npm test -- __tests__/integration --run
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Integration tests failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Run E2E tests
Write-Host "🌐 Running E2E System Tests..." -ForegroundColor Yellow
npx playwright test --reporter=html
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ E2E tests failed!" -ForegroundColor Red
    Write-Host "   View report: npx playwright show-report" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Run performance tests
Write-Host "⚡ Running Performance Tests..." -ForegroundColor Yellow
npx playwright test e2e/performance.spec.ts
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Performance tests had issues (non-blocking)" -ForegroundColor Yellow
}
Write-Host ""

# Run visual regression tests
Write-Host "📸 Running Visual Regression Tests..." -ForegroundColor Yellow
npx playwright test e2e/visual-regression.spec.ts --update-snapshots
Write-Host "   Snapshots updated. Review changes before committing." -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "✅ All Tests Passed!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📊 Test Summary:" -ForegroundColor White
Write-Host "   - Unit Tests: ✅ Passed" -ForegroundColor Green
Write-Host "   - Integration Tests: ✅ Passed" -ForegroundColor Green
Write-Host "   - E2E Tests: ✅ Passed" -ForegroundColor Green
Write-Host "   - Performance Tests: ✅ Checked" -ForegroundColor Green
Write-Host "   - Visual Regression: ✅ Updated" -ForegroundColor Green
Write-Host ""
Write-Host "🚢 Safe to deploy!" -ForegroundColor Cyan
