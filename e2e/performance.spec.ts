import { test, expect } from '@playwright/test';

/**
 * Performance Tests
 * Measures Core Web Vitals and performance metrics
 */

test.describe('Performance Metrics', () => {
    test('landing page should load quickly', async ({ page }) => {
        const startTime = Date.now();
        await page.goto('/');
        await page.waitForLoadState('networkidle');
        const loadTime = Date.now() - startTime;

        // Should load in under 3 seconds
        expect(loadTime).toBeLessThan(3000);
    });

    test('login page should be performant', async ({ page }) => {
        const startTime = Date.now();
        await page.goto('/login');
        await page.waitForLoadState('domcontentloaded');
        const loadTime = Date.now() - startTime;

        expect(loadTime).toBeLessThan(2000);
    });

    test('dashboard should load within acceptable time', async ({ page }) => {
        // Login
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');

        const startTime = Date.now();
        await page.waitForURL(/dashboard/);
        await page.waitForLoadState('networkidle');
        const loadTime = Date.now() - startTime;

        // Dashboard with data should load in under 4 seconds
        expect(loadTime).toBeLessThan(4000);
    });

    test('should measure Core Web Vitals', async ({ page }) => {
        await page.goto('/');

        // Measure Web Vitals
        const metrics = await page.evaluate(() => {
            return new Promise((resolve) => {
                // @ts-ignore
                if (window.performance && window.performance.getEntriesByType) {
                    const navigation = performance.getEntriesByType('navigation')[0] as any;
                    resolve({
                        // @ts-ignore
                        FCP: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                        domContentLoaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
                        loadComplete: navigation?.loadEventEnd - navigation?.loadEventStart,
                    });
                } else {
                    resolve({ FCP: 0, domContentLoaded: 0, loadComplete: 0 });
                }
            });
        });

        console.log('Performance Metrics:', metrics);

        // FCP should be under 1.8 seconds (good)
        // @ts-ignore
        if (metrics.FCP > 0) {
            // @ts-ignore
            expect(metrics.FCP).toBeLessThan(1800);
        }
    });

    test('products page should handle large lists efficiently', async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');

        const startTime = Date.now();
        await page.goto('/dashboard/products');
        await page.waitForLoadState('networkidle');
        const loadTime = Date.now() - startTime;

        // Even with many products, should load in under 5 seconds
        expect(loadTime).toBeLessThan(5000);
    });

    test('search/filter should be responsive', async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');
        await page.goto('/dashboard/products');

        const searchInput = page.locator('input[placeholder*="Buscar"]').first();

        if (await searchInput.isVisible()) {
            const startTime = Date.now();
            await searchInput.fill('test');
            await page.waitForTimeout(500); // Debounce
            const filterTime = Date.now() - startTime;

            // Filter should apply in under 1 second
            expect(filterTime).toBeLessThan(1000);
        }
    });

    test('modal open/close should be smooth', async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');
        await page.goto('/dashboard/products');

        const startTime = Date.now();
        await page.click('text=/adicionar/i');
        await page.waitForSelector('[role="dialog"], .modal', { state: 'visible' });
        const openTime = Date.now() - startTime;

        // Modal should open instantly (under 300ms)
        expect(openTime).toBeLessThan(300);
    });

    test('should not have memory leaks on navigation', async ({ page }) => {
        // Get initial memory
        const initialMemory = await page.evaluate(() => {
            // @ts-ignore
            return performance.memory?.usedJSHeapSize || 0;
        });

        // Navigate multiple times
        await page.goto('/');
        await page.goto('/login');
        await page.goto('/');
        await page.goto('/login');

        // Check memory after navigation
        const finalMemory = await page.evaluate(() => {
            // @ts-ignore
            return performance.memory?.usedJSHeapSize || 0;
        });

        // Memory should not grow excessively (less than 50MB increase)
        if (initialMemory > 0 && finalMemory > 0) {
            const memoryIncrease = (finalMemory - initialMemory) / 1024 / 1024;
            expect(memoryIncrease).toBeLessThan(50);
        }
    });
});
