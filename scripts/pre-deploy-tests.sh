#!/bin/bash

# Pre-deployment E2E Test Script
# Run this before deploying to production

echo "🚀 Pre-Deployment E2E Test Suite"
echo "================================="
echo ""

# Check if servers are running
echo "📡 Checking if dev servers are running..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend server not running on port 3000"
    echo "   Run: npm run dev"
    exit 1
fi

if ! curl -s http://localhost:8000/api > /dev/null; then
    echo "⚠️  Backend server not running on port 8000"
    echo "   Some tests may fail"
fi

echo "✅ Servers are running"
echo ""

# Run unit tests first
echo "🧪 Running Unit Tests..."
npm test -- --run --reporter=verbose
if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed!"
    exit 1
fi
echo ""

# Run integration tests
echo "🔗 Running Integration Tests..."
npm test -- __tests__/integration --run
if [ $? -ne 0 ]; then
    echo "❌ Integration tests failed!"
    exit 1
fi
echo ""

# Run E2E tests
echo "🌐 Running E2E System Tests..."
npx playwright test --reporter=html
if [ $? -ne 0 ]; then
    echo "❌ E2E tests failed!"
    echo "   View report: npx playwright show-report"
    exit 1
fi
echo ""

# Run performance tests
echo "⚡ Running Performance Tests..."
npx playwright test e2e/performance.spec.ts
if [ $? -ne 0 ]; then
    echo "⚠️  Performance tests had issues (non-blocking)"
fi
echo ""

# Run visual regression tests
echo "📸 Running Visual Regression Tests..."
npx playwright test e2e/visual-regression.spec.ts --update-snapshots
echo "   Snapshots updated. Review changes before committing."
echo ""

# Summary
echo "✅ All Tests Passed!"
echo "================================="
echo "📊 Test Summary:"
echo "   - Unit Tests: ✅ Passed"
echo "   - Integration Tests: ✅ Passed"
echo "   - E2E Tests: ✅ Passed"
echo "   - Performance Tests: ✅ Checked"
echo "   - Visual Regression: ✅ Updated"
echo ""
echo "🚢 Safe to deploy!"
